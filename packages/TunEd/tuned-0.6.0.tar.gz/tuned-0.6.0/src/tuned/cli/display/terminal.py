"""
Copyright (C) 2025 drd <drd.ltt000@gmail.com>

This file is part of TunEd.

TunEd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TunEd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import math
import random
from ...sound_analysis.stream import Sound
from ...sound_analysis.chord import Chord
from ...sound_analysis.attack import Attack
from .color import Color
from ...sound_analysis.theory import CHORD_FORMULAS, frequency_to_midi

GRADIENTS = {
    5: Color.fg.green,
    10: Color.fg.rgb(63, 192, 0),
    15: Color.fg.rgb(127, 128, 0),
    20: Color.fg.rgb(192, 63, 0),
    21: Color.fg.red
}
LEVELS = [" ", " ", "▂", "▃", "▄", "▅", "▇", "█"]
EGGS = ['🯅', '🯆', '🯇', '🯈']
# 𝅝 𝅗𝅥 𝅘𝅥 𝅘𝅥𝅮 𝅘𝅥𝅯 𝅘𝅥𝅰 𝅘𝅥𝅱 𝅘𝅥𝅲
TIME_UNIT = {1: '𝅝', 2: '𝅗𝅥', 4: '𝅘𝅥', 8: '𝅘𝅥𝅮', 16: '𝅘𝅥𝅯', 32: '𝅘𝅥𝅰', 64: '𝅘𝅥𝅱'}

class TerminalDisplay:
    
    def __init__(self, to_display_items: list[str], detection_mode: str = 'note', beats_per_bar: int = 4, flow_rate: int = 4):
        self.to_display_items = to_display_items
        self.detection_mode = detection_mode
        self.beats_per_bar = beats_per_bar
        self.flow_rate = flow_rate
        self.newline_needed = False

        # --- Configuration du défilement de la partition ---
        self.staff_width = 80  # Largeur de la ligne de partition
        self.playback_head_pos = self.staff_width // 4  # Tête de lecture au quart

        # Le motif de base pour une mesure.
        # Le `flow_rate` est une résolution (ex: 8 = croche) basée sur une mesure 4/4.
        # On doit ajuster le nombre de ticks réel en fonction de la signature rythmique.
        ticks_per_quarter_note = self.flow_rate / 4
        effective_flow_rate = int(ticks_per_quarter_note * self.beats_per_bar)

        if effective_flow_rate > 0 and self.beats_per_bar > 0:
            base_ticks_per_beat = effective_flow_rate // self.beats_per_bar
            extra_ticks = effective_flow_rate % self.beats_per_bar
            
            pattern_parts = []
            for i in range(self.beats_per_bar):
                ticks_for_this_beat = base_ticks_per_beat + (1 if i < extra_ticks else 0)
                
                if ticks_for_this_beat > 0:
                    beat_char = 'M' if i == 0 else 'B'
                    pattern_parts.append(beat_char + '.' * (ticks_for_this_beat - 1))

            self.staff_bar_pattern = "".join(pattern_parts)
        else:
            self.staff_bar_pattern = ' '
        
        # On crée une chaîne de travail assez longue pour y découper n'importe quelle "tranche"
        # de largeur `staff_width` sans se soucier de déborder.
        if self.staff_bar_pattern and len(self.staff_bar_pattern) > 0:
            repeats = (self.staff_width // len(self.staff_bar_pattern)) + 2
            self.staff_loop_for_slicing = self.staff_bar_pattern * repeats
        else:
            self.staff_loop_for_slicing = ' ' * self.staff_width

        self.formatters = {
            'note': self.format_note,
            'chord': self.format_chord,
            'metronome': self._format_scrolling_staff,
            'pulsed': self._format_pulsed_staff,
        }

        # --- Configuration de l'animation de l'easter egg ---
        self.egg_position = 0
        self.egg_direction = 1

    def _format_pulsed_staff(self, tick, offset_ms) -> str:
        """
        Affiche la partition défilante du métronome et y superpose
        un marqueur indiquant le décalage de l'attaque de l'utilisateur.
        """
        # --- 1. Génération de la partition de base (logique de _format_scrolling_staff) ---
        pulse = tick.pulse - 1
        pattern_len = len(self.staff_bar_pattern)
        start_pos = (pulse - self.playback_head_pos) % pattern_len
        visible_staff_list = list(self.staff_loop_for_slicing[start_pos : start_pos + self.staff_width])

        # --- 2. Calcul et placement du marqueur d'attaque ---
        ticks_per_beat = self.flow_rate / self.beats_per_bar
        is_on_beat = (tick.pulse - 1) % ticks_per_beat == 0

        if offset_ms is not None:
            # Convertit l'offset en ms en un décalage en caractères
            # Un caractère représente la durée d'un tick
            tick_duration_ms = tick.beat_interval * 1000
            char_offset = 0
            if tick_duration_ms > 0:
                char_offset = round(offset_ms / tick_duration_ms)
            
            marker_pos = self.playback_head_pos + char_offset

            # S'assure que le marqueur est dans les limites de l'affichage
            if 0 <= marker_pos < self.staff_width:
                # Choisit la couleur en fonction de la précision
                abs_offset_ms = abs(offset_ms)
                color = Color.fg.red
                if abs_offset_ms <= 15: color = GRADIENTS[5]
                elif abs_offset_ms <= 30: color = GRADIENTS[10]
                elif abs_offset_ms <= 50: color = GRADIENTS[15]
                else: color = GRADIENTS[20]
                
                visible_staff_list[marker_pos] = f"{color}▼{Color.reset}"
        
        elif is_on_beat:
            # Si on est sur un temps mais qu'aucune attaque n'a été détectée,
            # on affiche un marqueur de "beat manqué".
            marker_pos = self.playback_head_pos
            if 0 <= marker_pos < self.staff_width:
                visible_staff_list[marker_pos] = f"{Color.fg.red}×{Color.reset}"

        # --- 3. Formatage de la tête de lecture (comme dans _format_scrolling_staff) ---
        visible_staff = "".join(visible_staff_list)
        head_pos = self.playback_head_pos
        before = visible_staff[:head_pos]
        at_head = visible_staff[head_pos:head_pos + 1]
        after = visible_staff[head_pos + 1:]

        before = before.replace('M', f'{Color.bold}|{Color.reset}').replace('B', '∣')
        after = after.replace('M', f'{Color.bold}|{Color.reset}').replace('B', '∣')
        at_head_char = at_head.replace('M', '|').replace('B', '∣').replace('▼', ' ').replace('×', ' ') # Le curseur a priorité

        if is_on_beat:
            beat = tick.beat
            brightness_value = 150 if beat == 1 else 90
            pulse_color = Color.bg.rgb(brightness_value, brightness_value, brightness_value)
            formatted_at_head = f"{pulse_color}{Color.fg.black}{at_head_char}{Color.reset}"
        else:
            formatted_at_head = f"{Color.bg.darkgrey}{Color.fg.white}{at_head_char}{Color.reset}"
        
        formatted_staff = f"{before}{formatted_at_head}{after}"
        heartbeat = self._format_heartbeat_pulse(tick, show_beat=True)
        
        offset_str = f"{offset_ms:+7.2f} ms" if offset_ms is not None else " " * 11
        return f"[{heartbeat} {formatted_staff}] {offset_str}"

    def _format_scrolling_staff(self, result) -> str:
        """
        Génère la ligne de partition défilante avec une tête de lecture fixe.
        Le viseur s'illumine sur chaque temps, comme un battement de cœur.
        """
        pulse = result.pulse - 1
        pattern_len = len(self.staff_bar_pattern)

        # Calcule la position de départ dans notre chaîne de travail.
        start_pos = (pulse - self.playback_head_pos) % pattern_len
        
        # Découpe la tranche visible de la partition
        visible_staff = self.staff_loop_for_slicing[start_pos : start_pos + self.staff_width]

        # Sépare la chaîne pour formater la tête de lecture
        head_pos = self.playback_head_pos
        before = visible_staff[:head_pos]
        at_head = visible_staff[head_pos:head_pos + 1]
        after = visible_staff[head_pos + 1:]

        # Remplace les placeholders par les bons caractères et styles
        before = before.replace('M', f'{Color.bold}|{Color.reset}').replace('B', '∣')
        after = after.replace('M', f'{Color.bold}|{Color.reset}').replace('B', '∣')
        at_head_char = at_head.replace('M', '|').replace('B', '∣')

        # --- Logique de pulsation pour la tête de lecture ---
        ticks_per_beat = self.flow_rate / self.beats_per_bar
        is_on_beat = (result.pulse - 1) % ticks_per_beat == 0

        if is_on_beat:
            # Sur un temps : fond clair (plus brillant sur le 1er temps)
            beat = result.beat
            brightness_value = 150 if beat == 1 else 90
            pulse_color = Color.bg.rgb(brightness_value, brightness_value, brightness_value)
            # Texte en noir pour le contraste
            formatted_at_head = f"{pulse_color}{Color.fg.black}{at_head_char}{Color.reset}"
        else:
            # Sur une subdivision : style par défaut
            formatted_at_head = f"{Color.bg.darkgrey}{Color.fg.white}{at_head_char}{Color.reset}"
        
        formatted_staff = f"{before}{formatted_at_head}{after}"

        bpm = self._display_bpm(result)
        heartbeat = self._format_heartbeat_pulse(result, show_beat=True)
        return f"[{bpm}][{heartbeat}   {formatted_staff}]"

    def format_output(self, analysis_result, execution_time: float) -> str:
        """
        Formate la chaîne de caractères complète pour la sortie.
        """
        attack = analysis_result.get('attack')
        attack_detected = attack.detected if attack else False
        self.newline_needed = False

        # --- Formatage principal basé sur le mode ---
        main_display = ""
        formatter = self.formatters.get(self.detection_mode)
        if formatter:
            if self.detection_mode == 'chord':
                chord = analysis_result.get('chord')
                if chord:
                    if attack_detected and chord.quality and chord.quality.strip():
                        self.newline_needed = True
                    main_display = formatter(chord, attack_detected)
            elif self.detection_mode == 'note':
                sound = analysis_result.get('sound')
                if sound:
                    main_display = formatter(sound)
            elif self.detection_mode == 'metronome':
                tick = analysis_result.get('tick')
                if tick:
                    main_display = formatter(tick)
            elif self.detection_mode == 'pulsed':
                tick = analysis_result.get('tick')
                offset_ms = analysis_result.get('offset_ms')
                if tick:
                    main_display = formatter(tick, offset_ms)

        # --- Formatage des items supplémentaires (verbose) ---
        data_for_pulse = analysis_result.get('tick')
        to_display_dict = {
            'attack': self._display_is_attack(attack_detected, attack),
            'heart_beat': self._format_heartbeat_pulse(data_for_pulse, False),
            'bpm': self._display_bpm(data_for_pulse),
            'real_bpm': self._display_real_bpm(data_for_pulse),
            'execution_time': self._display_execution_time(execution_time),
            'egg': self._display_egg()
        }
        
        active_display_items = [f"[{to_display_dict[d]}]" for d in self.to_display_items if d in to_display_dict and to_display_dict[d]]
        
        # --- Formatage du message MIDI ---
        midi_message = analysis_result.get('midi_message')
        midi_display = self._format_midi_message(midi_message)

        output_str = f"{main_display} {midi_display} {''.join(active_display_items)}"

        # Si une attaque est détectée, on met un fond blanc sur toute la ligne.
        if attack_detected:
            output_str = output_str.replace(Color.reset, f"{Color.reset}{Color.bg.white}")
            return f"{Color.bg.white}{output_str}{Color.reset}"
        
        return output_str
    
    def _format_midi_message(self, message: dict | None) -> str:
        """
        Formate la chaîne de sortie pour le dernier message MIDI reçu
        en se basant sur un dictionnaire structuré.
        """
        if not message:
            return ""

        msg_type = message.get('type', '')
        port = message.get('port', '')
        formatted_msg = ""

        # --- Formate le message en fonction de son type ---
        if msg_type == 'control_change':
            control = message.get('control', 0)
            value = message.get('value', 0)
            formatted_msg = f"CC {control:<3} Val {value:<3}"
        elif msg_type == 'note_on':
            note = message.get('note', 0)
            velocity = message.get('velocity', 0)
            formatted_msg = f"NoteOn {note:<3} Vel {velocity:<3}"
        elif msg_type == 'note_off':
            note = message.get('note', 0)
            formatted_msg = f"NoteOff {note:<3}"
        else:
            # Pour tous les autres types, on affiche juste le type
            formatted_msg = msg_type.replace('_', ' ').title()

        # --- Ajoute le nom du port ---
        full_message = f"{formatted_msg} @{port}"

        # --- Tronque et padde pour une largeur constante ---
        max_len = 35
        if len(full_message) > max_len:
            full_message = full_message[:max_len - 3] + "..."
        padded_message = f"{full_message:<{max_len}}"

        return f"[{Color.fg.blue}MIDI{Color.reset}: {padded_message}]"
    
    def _format_metronome(self, result) -> str:
        """
        Formate la chaîne de sortie visuelle pour le mode métronome.
        """
        bar = result.bar
        beat = result.beat

        # Créer la barre visuelle
        beats_display = []
        for i in range(1, self.beats_per_bar + 1):
            if i == beat:
                # Le premier temps (downbeat) est en vert, les autres en blanc
                color = Color.fg.green if i == 1 else Color.fg.white
                beats_display.append(f"{color}{Color.bold}■{Color.reset}")
            else:
                beats_display.append(f"{Color.fg.darkgrey}─{Color.reset}")
        
        visual_bar = f" [ {' | '.join(beats_display)} ] "
        
        # Créer le texte d'information
        info_text = f"Bar: {bar:03d} Beat: {beat}/{self.beats_per_bar}"
        
        return f"{visual_bar}{info_text}"
    
    def format_note(self, sound: Sound) -> str:
        """
        Formate la chaîne de sortie complète pour le mode note.
        """
        to_display_dict = {
            'tuner': self._display_tuner(sound),
            'precision': self._display_precision(sound),
            'frequency': self._display_frequency(sound),
            'phase': self._display_phase(sound),
            'signal_level': self._display_signal_level(sound),
        }
        active_display_items = [f"[{to_display_dict[d]}]" for d in self.to_display_items if d in to_display_dict and to_display_dict[d]]
                
        return "".join(active_display_items)
    
    def format_chord(self, chord: Chord, attack_detected: bool) -> str:
        """
        Formate la chaîne de sortie complète pour le mode accord.
        """
        to_display_dict = {
            'chord': self._display_identified_chord(chord, attack_detected),
            'notes': self._display_chord_notes(chord)
        }
        
        active_display_items = [f"{to_display_dict[d]}" for d in self.to_display_items if d in to_display_dict and to_display_dict[d]]
        
        return "".join(active_display_items)
        
    def _display_tuner(self, sound: Sound) -> str:
        """
        Génère la chaîne de caractères de l'accordeur visuel.
        """
        abs_offset = abs(sound.offset)
        color = Color.fg.red
        if 0 <= abs_offset <= 5: color = GRADIENTS[5]
        elif 6 <= abs_offset <= 10: color = GRADIENTS[10]
        elif 11 <= abs_offset <= 15: color = GRADIENTS[15]
        elif 16 <= abs_offset <= 20: color = GRADIENTS[20]

        if abs_offset > 45: abs_offset = 45
        add = 45 - abs_offset
        left_offset = right_offset = 0
        right_add = left_add = 45
        l_arrow_color = l_max_color = r_max_color = r_arrow_color = Color.fg.darkgrey
        if sound.offset < 0:
            left_offset, right_offset = abs_offset, 0
            left_add, right_add = add, 45
            l_arrow_color = color
            if sound.offset <= -45: l_max_color = color
        elif sound.offset > 0:
            left_offset, right_offset = 0, abs_offset
            left_add, right_add = 45, add
            r_arrow_color = color
            if sound.offset >= 45: r_max_color = color

        l_arrow = f"{l_arrow_color}❱{Color.reset}"
        l_max = f"{l_max_color}₋₄₅{Color.reset}"
        l_offset = f"{Color.fg.darkgrey}{'│' * left_add}{color}{'┃' * left_offset}{Color.reset}"
        r_offset = f"{color}{'┃' * right_offset}{Color.fg.darkgrey}{'│' * right_add}{Color.reset}"
        c_note = f"{color}{sound.note:^2}{Color.reset}"
        c_octave = f"{color}{sound.octave:1}{Color.reset}"
        r_max = f"{r_max_color}₊₄₅{Color.reset}"
        r_arrow = f"{r_arrow_color}❰{Color.reset}"

        return f"{l_arrow} {l_max} {l_offset} {c_note}{c_octave} {r_offset} {r_max} {r_arrow}"
    
    def _display_identified_chord(self, chord: Chord, attack_detected: bool) -> str:
        """
        Formate la chaîne de sortie pour l'accord identifié.
        """
        chord_name = f"[{Color.fg.red}¯\\_(ツ)_/¯{Color.reset}]"
        
        if chord.quality and chord.quality.strip():
            chord_name_str = f"{chord.name:^10}"
            if attack_detected:
                chord_name = f"[{Color.fg.green}{chord_name_str}{Color.reset}]"
            else:
                chord_name = f"[{chord_name_str}]"
            
        return f"{Color.bold}{chord_name}{Color.reset}"
    
    def _display_chord_notes(self, chord: Chord) -> str:
        """
        Formate la chaîne de sortie pour les notes composant l'accord.
        Affiche d'abord les notes de l'accord triées, puis les notes restantes.
        """
        notes_to_display = chord.notes

        # On ne peut trier que si on a une fondamentale et une qualité d'accord identifiées.
        if chord.root and chord.quality and chord.quality in CHORD_FORMULAS:
            try:
                root_midi = frequency_to_midi(chord.root.frequency, chord.ref_freq)
                formula = CHORD_FORMULAS[chord.quality]

                # Crée un dictionnaire qui mappe chaque intervalle (en demi-tons) à la note correspondante.
                interval_map = {
                    (frequency_to_midi(s.frequency, chord.ref_freq) - root_midi) % 12: s
                    for s in chord.notes
                }

                # Récupère les notes de l'accord, triées selon la formule.
                sorted_chord_notes = [interval_map[interval] for interval in formula if interval in interval_map]

                # Récupère les notes qui ne font PAS partie de l'accord.
                chord_notes_set = set(sorted_chord_notes)
                other_notes = [s for s in chord.notes if s not in chord_notes_set]
                other_notes.sort(key=lambda s: s.frequency)  # On trie les notes restantes par fréquence.

                # La liste finale est la concaténation des deux.
                notes_to_display = sorted_chord_notes + other_notes

            except Exception:
                # En cas d'erreur inattendue, on se rabat sur l'affichage par défaut (trié par fréquence).
                notes_to_display = sorted(chord.notes, key=lambda s: s.frequency)

        chord_parts = []
        for sound in notes_to_display:
            abs_offset = abs(sound.offset)
            color = Color.fg.red
            if 0 <= abs_offset <= 5: color = GRADIENTS[5]
            elif 6 <= abs_offset <= 10: color = GRADIENTS[10]
            elif 11 <= abs_offset <= 15: color = GRADIENTS[15]
            elif 16 <= abs_offset <= 20: color = GRADIENTS[20]

            note_str = f"{Color.bold}{color}{sound.note:^2}{sound.octave:1}{Color.reset}"

            to_display_dict = {
                'precision': self._display_precision(sound),
                'frequency': self._display_frequency(sound),
                'phase': self._display_phase(sound),
                'signal_level': self._display_signal_level(sound),
            }

            active_display_items = [f"{to_display_dict[d]}" for d in self.to_display_items if d in to_display_dict and to_display_dict[d]]
            chord_parts.append(f"[{note_str} {' '.join(active_display_items)}]")

        notes_display = "".join(chord_parts)

        return f"{notes_display}"
    
    @staticmethod
    def _display_precision(sound: Sound) -> str:
        """
        Formate la chaîne de sortie pour la précision.
        """
        abs_offset = abs(sound.offset)
        color = Color.fg.red
        if 0 <= abs_offset <= 5: color = GRADIENTS[5]
        elif 6 <= abs_offset <= 10: color = GRADIENTS[10]
        elif 11 <= abs_offset <= 15: color = GRADIENTS[15]
        elif 16 <= abs_offset <= 20: color = GRADIENTS[20]
        
        return f"{color}{sound.offset:+3}¢{Color.reset}"
    
    @staticmethod
    def _display_frequency(sound: Sound) -> str:
        """
        Formate la chaîne de sortie pour la fréquence.
        """
        return f"∿ {sound.frequency:6.2f}㎐"
    
    @staticmethod
    def _display_signal_level(sound: Sound) -> str:
        """
        Formate la chaîne de sortie pour le niveau du signal.
        """
        db = round(sound.magnitude_to_db, 0)
        level_index = min(int(abs(db // 15)), len(LEVELS) - 1)
        
        return f"{LEVELS[level_index]} {db:5}㏈"
    
    @staticmethod
    def _display_is_attack(attack_detected, attack) -> str:
        """
        Formate la chaîne de sortie pour la détection d'une attaque.
        """
        attack_str = f" "
        if attack_detected:
            attack_str = f"{Color.fg.red}🗲 {round(attack.novelty_score, 1):+3}{Color.reset}"
        return f"{attack_str:5}"
    
    @staticmethod    
    def _display_phase(sound: Sound) -> str:
        """
        Formate la chaîne de sortie pour la phase.
        """
        return f"φ {round(sound.phase, 0):+2}㎭"
    
    @staticmethod
    def _display_execution_time(execution_time) -> str:
        """
        Formate la chaîne de sortie pour le temps d'exécution.
        """
        return f"⧖ {execution_time:8}″"
    
    def _display_egg(self) -> str:
        """
        Génère une animation de 4 caractères avec un personnage
        se déplaçant de gauche à droite et changeant de couleur.
        """
        width = 4
        display_list = [' '] * width
        
        egg_char = random.choice(EGGS)
        random_color = random.choice(list(GRADIENTS.values()))
        
        # Place le personnage à la position actuelle
        display_list[self.egg_position] = f"{random_color}{egg_char}{Color.reset}"
        
        # Calcule la position suivante pour vérifier les limites
        next_position = self.egg_position + self.egg_direction
        
        # Inverse la direction si on atteint ou dépasse les bords
        if not 0 <= next_position < width:
            self.egg_direction *= -1
        
        # Met à jour la position pour le prochain appel
        self.egg_position += self.egg_direction
        
        return "".join(display_list)

    def _display_bpm(self, result):
        """
        Formate la chaîne de sortie pour le nombre de beats par minutes.
        """
        if not result:
            return ""
        return f"{Color.bold}{round(result.bpm, 0)} Bpm{Color.reset}"
        
    def _display_real_bpm(self, result):
        """
        Formate la chaîne de sortie pour le nombre de ticks par minutes.
        """
        if not result:
            return ""
        return f"{round(result.real_bpm, 0)} Tpm"

    def _format_heartbeat_pulse(self, result, show_beat: bool = True) -> str:
        """
        Génère un effet de pulsation en "V" à l'intérieur de chaque temps
        en se basant sur la progression (0.0 à 1.0) fournie.
        """
        if not result:
            return "   "

        # --- Niveaux de luminosité ---
        downbeat_brightness = 200  # Pic du 1er temps (blanc cassé)
        other_beat_brightness = 120 # Pic des autres temps (gris clair)
        min_brightness = 40        # Point le plus bas (gris foncé)

        progress = result.beat_progress
        
        # --- Détermination du pic de luminosité pour le temps actuel et le suivant ---
        current_peak = downbeat_brightness if result.beat == 1 else other_beat_brightness
        
        next_beat = result.beat % self.beats_per_bar + 1
        next_peak = downbeat_brightness if next_beat == 1 else other_beat_brightness

        # --- Interpolation pour créer la forme en "V" ---
        if progress <= 0.5:
            # Phase de descente (de current_peak à min_brightness)
            # On normalise la progression sur l'intervalle [0, 0.5] -> [0, 1]
            p = progress / 0.5
            brightness_value = current_peak + (min_brightness - current_peak) * p
        else:
            # Phase de remontée (de min_brightness à next_peak)
            # On normalise la progression sur l'intervalle [0.5, 1] -> [0, 1]
            p = (progress - 0.5) / 0.5
            brightness_value = min_brightness + (next_peak - min_brightness) * p
        
        # --- Formatage de la sortie ---
        pulse_color = Color.bg.rgb(int(brightness_value), int(brightness_value), int(brightness_value))
        
        if show_beat:
            # Adapte la couleur du texte au fond pour une lisibilité maximale
            text_color = Color.fg.black if brightness_value > 100 else Color.fg.white
            beat_str = f" {result.beat} "
            return f"{pulse_color}{text_color}{Color.bold}{beat_str}{Color.reset}"
        else:
            return f"{pulse_color}   {Color.reset}"
    
    def print_line(self, text: str):
        """Affiche une ligne de texte dans la console, en écrasant la ligne actuelle."""
        # Utilise le code d'échappement ANSI \033[K pour effacer la ligne du curseur à la fin
        print(f"\r{text}\033[K", end='')

    def end_current_line(self):
        """Force le curseur à passer à la ligne suivante."""
        print()

    def print_startup_message(self, ref_freq: int, bpm: int):
        """Affiche le message initial au démarrage de l'application."""
        if self.detection_mode == 'metronome':
            info = f"{bpm}Bpm 𝅘𝅥𝅮"
        else:
            info = f"{ref_freq}㎐"
        print(f"{Color.bold} {self.detection_mode} @ {info}{Color.reset}")