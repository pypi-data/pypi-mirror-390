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
import sys
import threading
import time
import multiprocessing
from queue import Queue, Empty
from typing import Any, Type

import sounddevice as sd

from .analyzer import AudioAnalyzer
from .strategies import (
    AnalysisStrategy,
    NoteDetectionStrategy,
    AubioNoteDetectionStrategy,
    ChordDetectionStrategy,
    AubioAttackStrategy,
    SpectrumAnalysisStrategy
)

# --- Constantes et Configuration ---
SAMPLING_RATE = 48000
CHUNK_SIZE = 1024
# Un long tampon pour l'analyse spectrale, un court pour l'attaque
SPECTRAL_BUFFER_TIMES = 50
ATTACK_BUFFER_TIMES = 2

# Fenêtre temporelle (en secondes) après une attaque pour valider un accord.
SPECTRAL_BUFFER_DURATION = (SPECTRAL_BUFFER_TIMES * CHUNK_SIZE) / SAMPLING_RATE
ANALYSIS_WINDOW_SECONDS = SPECTRAL_BUFFER_DURATION * 1.4

# --- Profils de Détection d'Attaque par Instrument ---
INSTRUMENT_PROFILES = {
    'guitar': {
        'amplitude_settings': {'db_threshold': 40.0, 'cooldown_frames': 3, 'peak_window_size': 3},
        'spectral_settings': {'threshold_offset': 0.1}  # Très sensible pour capter les nuances
    },
    'bass': {
        'amplitude_settings': {'db_threshold': 25.0, 'cooldown_frames': 8, 'peak_window_size': 5},
        'spectral_settings': {'threshold_offset': 0.5}  # Moins sensible pour ignorer les bruits de frette
    }
}


class AudioStreamReader:
    """
    Gère le flux audio de sounddevice. Lit les données brutes et leur timestamp,
    les place dans les files d'attente pour les threads d'analyse, et peut
    également rediriger l'audio d'entrée vers la sortie pour un monitoring en temps réel.
    """
    def __init__(self, data_queues: list[Queue], monitoring: bool = False, latency: str | None = None):
        self.data_queues = data_queues
        self.monitoring = monitoring
        self.running = False

        # On utilise un flux bidirectionnel si le monitoring est activé
        self.stream = sd.Stream(
            samplerate=SAMPLING_RATE, blocksize=CHUNK_SIZE,
            channels=1, dtype='float32',
            callback=self._callback,
            # Le flux est seulement en entrée (InputStream) si monitoring=False
            device=(None, None) if self.monitoring else (None, sd.default.device[1]),
            latency=latency
        )
        
        # NOTE: Ce print s'exécute dans le processus enfant. Pour le voir, il faut
        # soit le rediriger vers stderr, soit (mieux) l'envoyer au parent via la queue.
        print(f"DEBUG: Monitoring={self.monitoring}, Latence demandée='{latency}', Latence obtenue={self.stream.latency}")


    def _callback(self, indata, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        
        # Si le monitoring est activé, on copie l'entrée vers la sortie
        if self.monitoring:
            outdata[:] = indata

        if self.running:
            # On envoie toujours les données d'entrée aux threads d'analyse
            for q in self.data_queues:
                q.put((indata.copy(), time.inputBufferAdcTime))

    def start(self):
        self.running = True
        self.stream.start()

    def stop(self):
        self.running = False
        time.sleep(0.1)
        self.stream.stop()
        self.stream.close()


class AnalysisThread(threading.Thread):
    """
    Thread de travail qui consomme des données audio d'une file, les traite
    via un AudioAnalyzer, et place les résultats dans une autre file.
    """
    def __init__(self, data_queue: Queue, results_queue: Queue, analyzer: AudioAnalyzer):
        super().__init__()
        self.data_queue = data_queue
        self.results_queue = results_queue
        self.analyzer = analyzer
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                raw_frame, timestamp = self.data_queue.get(timeout=0.1)
                decoded_frame = raw_frame.squeeze()
                analysis_result = self.analyzer.analyze(decoded_frame, timestamp)
                self.results_queue.put(analysis_result)
            except Empty:
                continue

    def stop(self):
        self.running = False


class AnalysisProcess(multiprocessing.Process):
    """
    Processus générique et configurable pour l'analyse audio.
    Il gère le flux audio et orchestre un nombre variable de threads d'analyse
    en se basant sur une liste de configurations fournie à l'initialisation.
    """
    def __init__(self, results_queue: multiprocessing.Queue, shutdown_event: multiprocessing.Event,
                 analyzer_configs: list[dict[str, Any]], monitoring: bool = False, latency: str | None = None):
        super().__init__()
        self.results_queue = results_queue
        self.shutdown_event = shutdown_event
        self.analyzer_configs = analyzer_configs  # La liste des "recettes" d'analyse
        self.monitoring = monitoring
        self.latency = latency

    def run(self):
        """
        Le cœur du processus. Cette méthode s'exécute lorsque le processus est démarré.
        Elle met en place dynamiquement les threads d'analyse, le flux audio,
        et gère la communication des résultats.
        """
        try:
            data_queues = []
            threads = []
            internal_results_queue = Queue() # Tous les threads écrivent dans cette file unique
            stream_reader = None

            try:
                # 1. Création dynamique des threads d'analyse à partir de la configuration
                for config in self.analyzer_configs:
                    # Pour chaque configuration, on crée une file de données dédiée
                    data_queue = Queue()
                    data_queues.append(data_queue)

                    # On instancie la classe de stratégie spécifiée...
                    strategy_class: Type[AnalysisStrategy] = config['strategy_class']
                    strategy_params: dict[str, Any] = config.get('strategy_params', {})
                    # ...avec les paramètres fournis.
                    strategy = strategy_class(**strategy_params)

                    # On crée l'analyseur avec sa propre configuration de buffer.
                    analyzer = AudioAnalyzer(
                        strategy=strategy,
                        sampling_rate=SAMPLING_RATE,
                        chunk_size=CHUNK_SIZE,
                        buffer_times=config['buffer_times']
                    )

                    # On crée le thread de travail qui utilisera cet analyseur.
                    thread = AnalysisThread(data_queue, internal_results_queue, analyzer)
                    threads.append(thread)

                # 2. Création du lecteur de flux qui alimente TOUS les threads
                stream_reader = AudioStreamReader(data_queues, monitoring=self.monitoring, latency=self.latency)
                
                # Envoi des informations de latence au processus parent pour le débogage
                self.results_queue.put({
                    'debug': 'latency_info',
                    'monitoring': self.monitoring,
                    'latency_requested': self.latency,
                    'latency_obtained': stream_reader.stream.latency
                })

                # 3. Démarrage de tous les threads et du flux audio
                for thread in threads:
                    thread.start()
                stream_reader.start()

                # 4. Boucle principale : relaie les résultats des threads internes vers le processus parent.
                last_analysis_results = {}
                while not self.shutdown_event.is_set():
                    try:
                        # On récupère le résultat partiel d'un des threads
                        new_result_part = internal_results_queue.get(timeout=0.1)
                        # On met à jour le dictionnaire global des résultats
                        last_analysis_results.update(new_result_part)
                        # On envoie une copie du dictionnaire consolidé au processus principal
                        self.results_queue.put(last_analysis_results.copy())
                    except Empty:
                        continue

            except Exception as e:
                # En cas d'erreur, on l'envoie au processus principal pour l'afficher
                self.results_queue.put({'error': str(e)})
            finally:
                # 5. Arrêt propre de tous les threads et du flux
                if stream_reader: stream_reader.stop()
                for thread in threads:
                    thread.stop()
                for thread in threads:
                    thread.join()
        except KeyboardInterrupt:
            # Le processus principal gère l'arrêt, on ignore donc l'interruption ici.
            pass

    def stop(self):
        """Méthode pour signaler l'arrêt du processus depuis l'extérieur."""
        self.shutdown_event.set()
