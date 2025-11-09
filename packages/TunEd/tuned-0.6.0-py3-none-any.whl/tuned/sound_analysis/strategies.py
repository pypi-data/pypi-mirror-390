"""
Copyright (C) 2025 drd <drd.ltt000@gmail.com>

This file is part of TunEd.

TunEd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free software Foundation, either version 3 of the License, or
(at your option) any later version.

TunEd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from abc import ABC, abstractmethod
from collections import deque
import numpy as np
import scipy.fft
import librosa
import aubio
from scipy.signal import find_peaks

from .attack import Attack
from .chord import Chord
from .stream import Sound
from .theory import frequency_to_midi, midi_to_ansi_note, midi_to_frequency


# --- CLASSE DE BASE RACINE ---

class AnalysisStrategy(ABC):
    """
    Classe de base abstraite pour toutes les stratégies d'analyse.
    Définit le contrat qu'une stratégie doit remplir pour être utilisée par un AudioAnalyzer.
    """
    @abstractmethod
    def analyze(self, full_buffer: np.ndarray, latest_chunk: np.ndarray, timestamp: float, sampling_rate: int) -> dict:
        """
        Analyse les données audio et retourne un dictionnaire de résultats.
        La clé du dictionnaire doit être unique à la stratégie pour permettre la fusion.
        """
        pass


# --- STRATÉGIE DE DÉTECTION D'ATTAQUE ---

class AttackAnalysisStrategy(AnalysisStrategy):
    """
    Stratégie dédiée à la détection des attaques musicales (onsets) dans le signal audio.
    Utilise l'algorithme de force spectrale de Librosa et est entièrement configurable.
    """
    def __init__(self,
                 sampling_rate: int,
                 n_fft: int = 512,
                 hop_length: int = 256,
                 n_mels: int = 80,
                 threshold_offset: float = 0.80,  # 0.35
                 cooldown_frames: int = 4):
        """
        Initialise la stratégie de détection d'attaque.

        :param sampling_rate: Taux d'échantillonnage.
        :param n_fft: Taille de la fenêtre FFT. Valeurs typiques : 256, 512, 1024.
                      Une valeur plus petite améliore la précision temporelle (réactivité)
                      au détriment de la précision fréquentielle.
        :param hop_length: Pas entre deux fenêtres d'analyse. Typiquement n_fft / 2 ou n_fft / 4.
                           Une valeur plus petite augmente la résolution temporelle et la charge CPU.
        :param n_mels: Nombre de bandes de Mel à utiliser. Doit être adapté à n_fft.
        :param threshold_offset: Seuil de sensibilité. C'est le réglage le plus important.
                                 Plage utile : 0.1 (très sensible) à 1.0 (peu sensible).
        :param cooldown_frames: Nombre de cycles à ignorer après une détection (anti-rebond).
                                Plage utile : 2 (jeu rapide) à 10 (jeu lent).
        """
        self.sampling_rate = sampling_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.threshold_offset = threshold_offset
        self.cooldown_frames = cooldown_frames
        self.cooldown_counter = 0
        self.novelty_history = deque(maxlen=10)
        self.moving_avg_history = deque(maxlen=100)

    def analyze(self, full_buffer: np.ndarray, latest_chunk: np.ndarray, timestamp: float, sampling_rate: int) -> dict:
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1
            return {'attack': Attack(detected=False, timestamp=timestamp)}

        onset_env = librosa.onset.onset_strength(
            y=latest_chunk, sr=sampling_rate, n_fft=self.n_fft, hop_length=self.hop_length, n_mels=self.n_mels)
        current_novelty = np.max(onset_env)

        self.novelty_history.append(current_novelty)
        self.moving_avg_history.append(current_novelty)

        threshold = np.mean(self.moving_avg_history) + self.threshold_offset
        
        if len(self.novelty_history) < self.novelty_history.maxlen:
            return {'attack': Attack(detected=False, timestamp=timestamp, novelty_score=current_novelty, threshold=threshold)}

        is_peak = current_novelty >= max(self.novelty_history)
        is_above_threshold = current_novelty > threshold

        attack_detected = is_peak and is_above_threshold
        if attack_detected:
            self.cooldown_counter = self.cooldown_frames

        return {'attack': Attack(detected=attack_detected, timestamp=timestamp, novelty_score=current_novelty, threshold=threshold)}


class AmplitudeAttackStrategy(AnalysisStrategy):
    """
    Stratégie de détection d'attaque basée sur les pics d'amplitude locaux.
    Détecte une attaque lorsqu'un nouveau pic de volume est atteint au-dessus d'un
    seuil de bruit de fond, permettant la détection de notes rapides successives.
    """
    def __init__(self, db_threshold: float = 30.0, cooldown_frames: int = 2, peak_window_size: int = 3):
        """
        Initialise la stratégie de détection par pics d'amplitude.

        :param db_threshold: Le seuil de bruit de fond en dB (positif). Une attaque ne peut
                             être détectée que si le volume est supérieur à ce seuil.
        :param cooldown_frames: Le nombre de cycles à ignorer après une détection.
        :param peak_window_size: La taille de la fenêtre de mémoire pour détecter un pic local.
        """
        self.db_threshold = -abs(db_threshold)
        self.cooldown_frames = cooldown_frames
        self.cooldown_counter = 0
        # Mémoire des dernières valeurs de dB pour la détection de pic
        self.db_history = deque(maxlen=peak_window_size)

    def analyze(self, full_buffer: np.ndarray, latest_chunk: np.ndarray, timestamp: float, sampling_rate: int) -> dict:
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1
            return {'attack': Attack(detected=False, timestamp=timestamp)}

        rms = np.sqrt(np.mean(latest_chunk**2))
        db = 20 * np.log10(rms + 1e-9)
        self.db_history.append(db)

        if len(self.db_history) < self.db_history.maxlen:
            return {'attack': Attack(detected=False, timestamp=timestamp)}

        # Conditions : le signal doit être au-dessus du bruit de fond ET
        # la valeur actuelle doit être la plus forte de l'histoire récente (pic local).
        is_above_threshold = db > self.db_threshold
        is_peak = db >= max(self.db_history)

        attack_detected = False
        if is_above_threshold and is_peak:
            attack_detected = True
            self.cooldown_counter = self.cooldown_frames

        return {'attack': Attack(detected=attack_detected, timestamp=timestamp)}


class HybridAttackStrategy(AnalysisStrategy):
    """
    Stratégie de détection d'attaque hybride qui combine l'analyse spectrale et
    l'analyse d'amplitude pour une détection plus robuste et musicale.
    Une attaque n'est validée que si les deux méthodes sont d'accord.
    """
    # def __init__(self, sampling_rate: int, **kwargs):
    def __init__(self, spectral_strategy: AttackAnalysisStrategy, amplitude_strategy: AmplitudeAttackStrategy):
        """
        Initialise la stratégie hybride.
        Accepte une strategie spectral et une strategie amplitude.
        """
        # Crée des instances des deux stratégies de base
        self.spectral_strategy = spectral_strategy
        self.amplitude_strategy = amplitude_strategy


    def analyze(self, full_buffer: np.ndarray, latest_chunk: np.ndarray, timestamp: float, sampling_rate: int) -> dict:
        # L'analyse spectrale a besoin de contexte (avant/après), on lui donne le tampon complet.
        # Note : on passe full_buffer deux fois car la stratégie spectrale attend `latest_chunk`
        # mais pour elle, le "dernier segment" pertinent est l'ensemble du contexte.
        spectral_result = self.spectral_strategy.analyze(full_buffer, full_buffer, timestamp, sampling_rate)
        
        # L'analyse d'amplitude est plus rapide et réactive sur le dernier segment.
        amplitude_result = self.amplitude_strategy.analyze(full_buffer, latest_chunk, timestamp, sampling_rate)

        # On récupère les informations de l'analyse spectrale
        spectral_attack_info = spectral_result['attack']
        
        # Règle de fusion :
        # 1. L'amplitude doit détecter un pic (déclencheur).
        # 2. La nouveauté spectrale doit dépasser son propre seuil adaptatif (confirmation).
        is_amplitude_detected = amplitude_result['attack'].detected
        is_spectrally_confirmed = spectral_attack_info.novelty_score >= spectral_attack_info.threshold
        
        is_attack_detected = is_amplitude_detected and is_spectrally_confirmed

        # On propage le score de nouveauté pour information, uniquement si l'attaque est validée.
        final_novelty_score = spectral_attack_info.novelty_score if is_attack_detected else 0.0

        return {'attack': Attack(
            detected=is_attack_detected,
            timestamp=timestamp,
            novelty_score=final_novelty_score,
            threshold=spectral_attack_info.threshold
        )}


class AubioAttackStrategy(AnalysisStrategy):
    """
    Stratégie de détection d'attaque basée sur la bibliothèque Aubio.
    Offre une détection rapide et configurable avec différents algorithmes.
    """
    def __init__(self,
                 sampling_rate: int,
                 win_s: int = 512,
                 hop_s: int = 256,
                 method: str = "specdiff"):
        """
        Initialise la stratégie de détection d'attaque avec Aubio.

        :param sampling_rate: Taux d'échantillonnage.
        :param win_s: Taille de la fenêtre d'analyse (en échantillons).
        :param hop_s: Pas entre deux fenêtres d'analyse (en échantillons).
        :param method: Algorithme de détection d'Aubio à utiliser.
                       Options : "energy", "hfc", "complex", "phase", "specdiff", "kl", "mkl".
        """
        self.hop_s = hop_s
        # Aubio a besoin de types natifs Python, pas de types numpy
        self.onset_detector = aubio.onset(method, int(win_s), int(hop_s), int(sampling_rate))

    def analyze(self, full_buffer: np.ndarray, latest_chunk: np.ndarray, timestamp: float, sampling_rate: int) -> dict:
        """
        Analyse le dernier segment audio pour une attaque.
        """
        # Aubio travaille avec des flottants 32 bits
        samples = latest_chunk.astype(np.float32)
        
        attack_detected = False
        # L'objet onset d'Aubio retourne la position de l'attaque (en échantillons) si détectée, sinon 0.
        # On le convertit simplement en booléen pour savoir SI une attaque a eu lieu.
        if self.onset_detector(samples):
            attack_detected = True

        return {'attack': Attack(detected=attack_detected, timestamp=timestamp)}


class AubioNoteDetectionStrategy(AnalysisStrategy):
    """
    Stratégie de détection de note basée sur l'algorithme YIN d'Aubio.
    Rapide, robuste et optimisée pour la détection de la fréquence fondamentale.
    """
    def __init__(self,
                 sampling_rate: int,
                 ref_freq: int = 440,
                 win_s: int = 2048,
                 hop_s: int = 1024,
                 confidence_threshold: float = 0.8,
                 db_silence_threshold: float = -80.0):
        """
        Initialise la stratégie de détection de note avec Aubio.

        :param sampling_rate: Taux d'échantillonnage.
        :param ref_freq: Fréquence de référence pour le La4 (A4).
        :param win_s: Taille de la fenêtre d'analyse (en échantillons).
        :param hop_s: Pas entre deux fenêtres (doit correspondre à la taille du chunk audio).
        :param confidence_threshold: Seuil de confiance (0 à 1) pour valider une détection.
        :param db_silence_threshold: Seuil de silence en dB. Aubio ne tentera pas de
                                     détecter une note si le volume est inférieur.
        """
        self.ref_freq = ref_freq
        self.confidence_threshold = confidence_threshold
        self.pitch_detector = aubio.pitch("yin", int(win_s), int(hop_s), int(sampling_rate))
        self.pitch_detector.set_unit("Hz")
        self.pitch_detector.set_silence(db_silence_threshold)

    def _compute_frequency_offset(self, frequency, midi_note):
        """Calcule l'écart en cents par rapport à la note MIDI la plus proche."""
        nearest_midi_note_frequency = midi_to_frequency(midi_note, self.ref_freq)
        frequency_offset = nearest_midi_note_frequency - frequency
        if frequency_offset == 0:
            return 0

        # Détermine la note suivante pour calculer l'intervalle d'un demi-ton
        next_note = midi_note + (1 if frequency_offset > 0 else -1)
        semitone_step = abs((nearest_midi_note_frequency - midi_to_frequency(next_note, self.ref_freq)) / 100)
        if semitone_step == 0:
            return 0

        # Calcul de l'offset et vérification de validité (anti-NaN)
        offset = frequency_offset / semitone_step
        if not np.isfinite(offset):
            return 0

        return round(offset)

    def analyze(self, full_buffer: np.ndarray, latest_chunk: np.ndarray, timestamp: float, sampling_rate: int) -> dict:
        """Analyse le dernier segment audio pour trouver la fréquence fondamentale."""
        try:
            samples = latest_chunk.astype(np.float32)
            frequency = self.pitch_detector(samples)[0]
            confidence = self.pitch_detector.get_confidence()

            # Calcul du volume (magnitude) pour l'affichage
            rms_magnitude = np.sqrt(np.mean(latest_chunk ** 2))
            db = 20 * np.log10(rms_magnitude + 1e-9)

            # Conversion de la fréquence en informations musicales
            midi_note = frequency_to_midi(frequency, self.ref_freq)
            note, octave = midi_to_ansi_note(midi_note)
            offset = self._compute_frequency_offset(frequency, midi_note)

            sound = Sound(
                timestamp=timestamp,
                confidence=confidence,
                magnitude=rms_magnitude,
                magnitude_to_db=0 if np.isnan(db) else db,
                phase=0.0,  # La phase n'est pas directement disponible avec cette méthode
                frequency=round(frequency, 2),
                note=note,
                octave=octave,
                offset=offset
            )
            return {'sound': sound}
        except (ValueError, TypeError):
            # En cas d'erreur de conversion (NaN), on crée un objet Sound "invalide"
            # avec une confiance de 0, que l'affichage saura ignorer.
            sound = Sound(
                timestamp=timestamp, confidence=0.0, magnitude=0.0, magnitude_to_db=-np.inf,
                phase=0.0, frequency=0.0, note="", octave=0, offset=0
            )
            return {'sound': sound}


# --- STRATÉGIES D'ANALYSE SPECTRALE ---

class SpectrumAnalysisStrategy(AnalysisStrategy, ABC):
    """
    Classe de base abstraite pour les stratégies basées sur l'analyse spectrale (FFT, HPS).
    Contient la logique commune de traitement du signal.
    """
    ZERO_PADDING = 3
    NUM_HPS = 3

    def __init__(self, ref_freq: int = 440):
        self.ref_freq = ref_freq

    def analyze(self, full_buffer: np.ndarray, latest_chunk: np.ndarray, timestamp: float, sampling_rate: int) -> dict:
        hanning_window = np.hanning(len(full_buffer))
        pad = np.pad(full_buffer * hanning_window, (0, len(full_buffer) * self.ZERO_PADDING), "constant")
        fft_data = scipy.fft.fft(pad)
        
        fft_len = len(full_buffer) * (1 + self.ZERO_PADDING)
        frequencies = scipy.fft.fftfreq(fft_len, 1. / sampling_rate)
        
        magnitude_data = abs(fft_data)
        magnitude_data = magnitude_data[:len(magnitude_data) // 2]

        magnitude_data_orig = magnitude_data.copy()
        for i in range(2, self.NUM_HPS + 1):
            hps_len = int(np.ceil(len(magnitude_data) / i))
            magnitude_data[:hps_len] *= magnitude_data_orig[::i]

        return self._detect_from_spectrum(magnitude_data, frequencies, fft_data, timestamp)

    def _compute_frequency_offset(self, frequency, midi_note):
        nearest_midi_note_frequency = midi_to_frequency(midi_note, self.ref_freq)
        frequency_offset = nearest_midi_note_frequency - frequency
        if frequency_offset == 0: return 0
        
        next_note = midi_note + (1 if frequency_offset > 0 else -1)
        semitone_step = abs((nearest_midi_note_frequency - midi_to_frequency(next_note, self.ref_freq)) / 100)
        if semitone_step == 0: return 0
        
        return round(frequency_offset / semitone_step)

    @abstractmethod
    def _detect_from_spectrum(self, magnitude_data, frequencies, fft_data, timestamp) -> dict:
        """
        Méthode abstraite que les sous-classes doivent implémenter pour interpréter le spectre.
        Doit retourner un dictionnaire avec une clé sémantique unique.
        """
        pass


class NoteDetectionStrategy(SpectrumAnalysisStrategy):
    """
    Stratégie concrète pour détecter une seule note (la plus forte) à partir du spectre.
    """
    def _detect_from_spectrum(self, magnitude_data, frequencies, fft_data, timestamp) -> dict:
        magnitude = np.max(magnitude_data)
        magnitude_to_db = 20 * np.log10(magnitude + 1e-9)
        index_loudest = np.argmax(magnitude_data)
        frequency = round(frequencies[index_loudest], 2)
        phase = np.angle(fft_data[index_loudest])
        midi_note = frequency_to_midi(frequency, self.ref_freq)
        note, octave = midi_to_ansi_note(midi_note)
        offset = self._compute_frequency_offset(frequency, midi_note)
        
        sound = Sound(
            timestamp=timestamp,
            magnitude=magnitude,
            magnitude_to_db=0 if np.isnan(magnitude_to_db) else magnitude_to_db,
            phase=phase,
            frequency=frequency,
            note=note,
            octave=octave,
            offset=offset
        )
        return {'sound': sound}


class ChordDetectionStrategy(SpectrumAnalysisStrategy):
    """
    Stratégie concrète pour détecter plusieurs notes et former un accord à partir du spectre.
    """
    def __init__(self, ref_freq: int = 440, identify_harmonics: bool = True):
        super().__init__(ref_freq)
        self.identify_harmonics = identify_harmonics

    def _detect_from_spectrum(self, magnitude_data, frequencies, fft_data, timestamp) -> dict:
        peaks, _ = find_peaks(magnitude_data, prominence=10000, distance=50)

        detected_sounds = []
        for peak_index in peaks:
            frequency = round(frequencies[peak_index], 2)
            if frequency == 0: continue

            magnitude = magnitude_data[peak_index]
            magnitude_to_db = 20 * np.log10(magnitude + 1e-9)
            phase = np.angle(fft_data[peak_index])
            midi_note = frequency_to_midi(frequency, self.ref_freq)
            note, octave = midi_to_ansi_note(midi_note)
            offset = self._compute_frequency_offset(frequency, midi_note)

            sound = Sound(
                timestamp=timestamp,
                magnitude=magnitude,
                magnitude_to_db=0 if np.isnan(magnitude_to_db) else magnitude_to_db,
                phase=phase,
                frequency=frequency,
                note=note,
                octave=octave,
                offset=offset
            )
            detected_sounds.append(sound)

        chord = Chord(
            timestamp=timestamp,
            sounds=detected_sounds,
            ref_freq=self.ref_freq,
            identify_harmonics=self.identify_harmonics
        )
        return {'chord': chord}
