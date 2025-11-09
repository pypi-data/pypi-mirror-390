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
import bisect
from dataclasses import replace

from .stream import Sound
from .theory import frequency_to_midi, CHORD_FORMULAS


class Chord:
    """
    Represents a musical chord, analyzed from a list of sounds.
    It can identify which sounds are harmonics and stores this information
    within each Sound object.
    """

    def __init__(self, timestamp: float, sounds: list[Sound], ref_freq: int = 440, identify_harmonics: bool = True):
        self.timestamp = timestamp
        self.sounds: list[Sound] = sorted(sounds, key=lambda s: s.frequency)
        self.ref_freq = ref_freq
        
        if identify_harmonics and self.sounds:
            self.sounds = self._identify_harmonics_optimized(self.sounds)

        self.notes = [s for s in self.sounds if not s.is_harmonic]
        self.harmonics = [s for s in self.sounds if s.is_harmonic]
        
        self.bass_note: Sound | None = self.notes[0] if self.notes else None
        self.root: Sound | None = None
        self.quality: str | None = None
        self.name: str = "Unknown"

        if len(self.notes) >= 2:  # We need at least 2 notes for a chord
            self._analyze()
        elif self.bass_note:
            self.name = f"Note {self.bass_note.note}"

    def _identify_harmonics_optimized(self, sounds: list[Sound], tolerance_cents=30, max_harmonics=5) -> list[Sound]:
        """
        Identifie les fréquences harmoniques à partir d'une liste de sons.
        Utilise une tolérance en cents musicaux pour une meilleure précision sur tout le spectre.
        Vérifie également que l'amplitude d'une harmonique est inférieure à celle de sa fondamentale.
        Retourne une nouvelle liste d'objets Sound avec l'attribut `is_harmonic` mis à jour.
        """
        if len(sounds) < 2:
            return sounds

        # Calcul du ratio de fréquence à partir des cents. Fait une seule fois pour l'efficacité.
        ratio = 2 ** (tolerance_cents / 1200)
        harmonic_freqs = set()

        # Itère sur chaque son, le considérant comme une fondamentale potentielle
        for i, fundamental in enumerate(sounds):
            # Si ce son a déjà été identifié comme une harmonique, on le saute.
            if fundamental.frequency in harmonic_freqs:
                continue

            # Pour la fondamentale actuelle, on cherche ses harmoniques dans le reste de la liste.
            for n in range(2, max_harmonics + 1):
                target_harmonic = fundamental.frequency * n
                
                # Définit la fenêtre de recherche basée sur la tolérance en cents
                lower_bound = target_harmonic / ratio
                upper_bound = target_harmonic * ratio

                # Recherche binaire (bisect) pour trouver les correspondances potentielles efficacement.
                remaining_sounds = sounds[i + 1:]
                sorted_freqs = [s.frequency for s in remaining_sounds]
                
                start_index = bisect.bisect_left(sorted_freqs, lower_bound)

                # Vérifie tous les sons depuis l'index de départ jusqu'à ce qu'ils dépassent la borne supérieure.
                for j in range(start_index, len(remaining_sounds)):
                    candidate = remaining_sounds[j]
                    
                    if candidate.frequency > upper_bound:
                        # On a dépassé la fenêtre de recherche pour cette harmonique.
                        break
                    
                    # CONDITION : Une harmonique doit être plus faible que sa fondamentale.
                    if candidate.magnitude < fundamental.magnitude:
                        # C'est une harmonique.
                        harmonic_freqs.add(candidate.frequency)

        # Construit la liste finale avec les objets Sound mis à jour
        final_sounds = []
        for s in sounds:
            if s.frequency in harmonic_freqs:
                final_sounds.append(replace(s, is_harmonic=True))
            else:
                final_sounds.append(s)
        
        return final_sounds

    def _analyze(self):
        """
        The main logic to identify the root and quality of the chord.
        This method operates on the fundamental notes.
        It also handles naming for inverted chords (e.g., "C Maj / E").
        """
        # Get the unique MIDI numbers of each fundamental note
        midi_notes = sorted(list(set([frequency_to_midi(s.frequency, self.ref_freq) for s in self.notes])))

        # Try each note as a potential root
        for i, potential_root_midi in enumerate(midi_notes):
            # Calculate the intervals relative to this root
            intervals = tuple(sorted([(note - potential_root_midi) % 12 for note in midi_notes]))

            # Compare with our known formulas
            for quality, formula in CHORD_FORMULAS.items():
                if intervals == formula:
                    # We found a match!
                    self.quality = quality
                    
                    # The root is the note corresponding to the MIDI we were testing.
                    # We need to find the original Sound object for the root.
                    for note_sound in self.notes:
                        if frequency_to_midi(note_sound.frequency, self.ref_freq) == potential_root_midi:
                            self.root = note_sound
                            break
                    
                    # Determine the chord name, accounting for inversions.
                    if self.root and self.bass_note and self.root.note != self.bass_note.note:
                        # It's an inversion.
                        self.name = f"{self.root.note} {self.quality} / {self.bass_note.note}"
                    elif self.root:
                        # It's in root position.
                        self.name = f"{self.root.note} {self.quality}"
                    
                    return  # Stop the analysis

        # If we didn't find anything, name the chord by its bass note
        if self.bass_note:
            self.name = f"Chord bass {self.bass_note.note}"
