"""
Copyright (C) 2025 drd <drd.ltt000@gmail.com>

This file is part of TunEd.

TunEd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TunEd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS for A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import time
import json
from multiprocessing import Process
import mido
import importlib.resources as pkg_resources


class MidiController(Process):
    """
    Un processus qui écoute les messages MIDI, les traduit en commandes
    selon un fichier de configuration, et les envoie au ClockGenerator.
    """

    def __init__(self, pipe, ui_queue=None, config_path=None, *args, **kwargs):
        """
        Initialise le contrôleur MIDI.

        Args:
            pipe: Le Pipe multiprocessing pour envoyer les commandes.
            ui_queue: Une Queue multiprocessing pour envoyer les messages bruts à l'UI.
            config_path (str): Le chemin vers le fichier de configuration JSON.
                               Si None, charge 'midi_mapping.json' depuis le package.
        """
        super().__init__(*args, **kwargs)
        self.pipe = pipe
        self.ui_queue = ui_queue
        self.config_path = config_path
        self.config = None
        self.port_name = None
        self._keep_running = True

        # Attributs pour la limitation des messages de BPM (throttling).
        # Cela évite de surcharger le système avec trop de messages lors de la rotation d'un potentiomètre,
        # assurant une mise à jour fluide et réactive du BPM.
        self.last_bpm_update_time = 0
        self.bpm_update_interval = 0.05  # 50 ms

        self._load_config()

    def _load_config(self):
        """Charge et valide le fichier de configuration JSON."""
        try:
            if self.config_path:
                # Si un chemin est fourni, l'utiliser directement.
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                print(f"Configuration MIDI chargée depuis '{self.config_path}'")
            else:
                # Sinon, charger la configuration par défaut du package.
                with pkg_resources.path('tuned.midi', 'midi_mapping.json') as p:
                    with open(p, 'r') as f:
                        self.config = json.load(f)
                    print(f"Configuration MIDI par défaut chargée depuis le package.")

            self.port_name = self.config.get('port_name')

        except FileNotFoundError:
            print(f"Erreur : Fichier de configuration MIDI '{self.config_path}' non trouvé.")
            self.config = {'mappings': []}
        except json.JSONDecodeError:
            print(f"Erreur : Fichier de configuration MIDI '{self.config_path}' n'est pas un JSON valide.")
            self.config = {'mappings': []}
        except Exception as e:
            print(f"Une erreur inattendue est survenue en chargeant la configuration MIDI : {e}")
            self.config = {'mappings': []}

    def _map_cc_to_value(self, cc_value, value_range):
        """Mappe une valeur CC (0-127) à une plage de valeurs donnée."""
        min_val, max_val = value_range
        value = min_val + (cc_value / 127.0) * (max_val - min_val)
        return round(value, 2)

    def run(self):
        """
        La boucle principale : ouvre le(s) port(s) MIDI et traite les messages
        selon la configuration chargée.
        """
        open_ports = []
        try:
            ports_to_try = []
            if self.port_name:
                # Si un port est spécifié, on n'essaie que celui-là.
                ports_to_try.append(self.port_name)
            else:
                # Sinon, on essaie tous les ports disponibles.
                ports_to_try = mido.get_input_names()
                if not ports_to_try:
                    print("Aucun port MIDI d'entrée trouvé.")
                    return

            # --- Ouvre tous les ports demandés ---
            for name in ports_to_try:
                try:
                    port = mido.open_input(name)
                    open_ports.append(port)
                    print(f"Contrôleur MIDI en écoute sur le port : {port.name}")
                except (IOError, OSError) as e:
                    print(f"Avertissement : Impossible d'ouvrir le port MIDI '{name}': {e}")

            if not open_ports:
                print("Aucun port MIDI n'a pu être ouvert.")
                return

            # --- Boucle d'écoute sur tous les ports ouverts ---
            while self._keep_running:
                for port in open_ports:
                    for msg in port.iter_pending():
                        # Envoie le message brut à l'UI pour affichage
                        if self.ui_queue:
                            try:
                                # Envoie un dictionnaire pour un parsing facile côté UI
                                data = msg.dict()
                                data['port'] = port.name.split(':')[0]
                                self.ui_queue.put_nowait(data)
                            except Exception:
                                pass

                        command = self._process_message(msg)
                        if command:
                            self.pipe.send(command)
                time.sleep(0.01)

        except KeyboardInterrupt:
            pass
        finally:
            for port in open_ports:
                port.close()
            print("Contrôleur MIDI arrêté, tous les ports sont fermés.")

    def _process_message(self, msg):
        """
        Compare un message MIDI aux règles du fichier de configuration.
        Retourne une commande si une correspondance est trouvée, sinon None.
        """
        for mapping in self.config.get('mappings', []):
            # --- Correspondance pour Control Change ---
            if (msg.type == 'control_change' and
                    mapping.get('type') == 'control_change' and
                    msg.control == mapping.get('control')):

                action = mapping.get('action')
                if action == 'set_bpm':
                    current_time = time.time()
                    if current_time - self.last_bpm_update_time > self.bpm_update_interval:
                        self.last_bpm_update_time = current_time
                        value_range = mapping.get('params', {}).get('range', [60, 180])
                        bpm = self._map_cc_to_value(msg.value, value_range)
                        return {'command': 'set_bpm', 'value': bpm}

            # --- Correspondance pour Note On ---
            elif (msg.type == 'note_on' and
                  mapping.get('type') == 'note_on' and
                  msg.note == mapping.get('note')):
                
                action = mapping.get('action')
                if action in ['start', 'stop']:
                    return {'command': action}
        
        return None

    def stop(self):
        """Arrête la boucle d'écoute."""
        self._keep_running = False

