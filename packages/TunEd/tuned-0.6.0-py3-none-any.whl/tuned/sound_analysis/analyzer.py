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
import numpy as np
from .strategies import AnalysisStrategy


class AudioAnalyzer:
    """
    Un moteur d'analyse audio générique.
    Cette classe gère un tampon audio glissant et délègue toute la logique d'analyse
    à une 'stratégie' interchangeable qui lui est fournie à l'initialisation.
    Elle est conçue pour être utilisée dans un thread de traitement dédié.
    """

    def __init__(self,
                 strategy: AnalysisStrategy,
                 sampling_rate: int,
                 chunk_size: int,
                 buffer_times: int):
        """
        Initialise le moteur d'analyse.

        :param strategy: L'objet 'cerveau' qui effectuera l'analyse.
        :param sampling_rate: Le taux d'échantillonnage du flux audio.
        :param chunk_size: La taille de chaque segment audio reçu.
        :param buffer_times: Le multiplicateur pour déterminer la taille du tampon global.
        """
        self.strategy = strategy
        self.SAMPLING_RATE = sampling_rate
        self.CHUNK_SIZE = chunk_size
        self.BUFFER_TIMES = buffer_times

        # Initialise le tampon audio.
        self.buffer = np.zeros(self.CHUNK_SIZE * self.BUFFER_TIMES, dtype=np.float32)

    def analyze(self, decoded_frame: np.ndarray, timestamp: float) -> dict:
        """
        Traite un nouveau segment de données audio.

        Cette méthode met à jour le tampon interne, puis appelle la stratégie
        d'analyse pour effectuer le travail réel.

        :param decoded_frame: Le dernier segment de données audio reçu du flux.
        :param timestamp: Le timestamp de haute précision associé à ce segment.
        :return: Un dictionnaire contenant les résultats de l'analyse de la stratégie.
        """
        # 1. Met à jour le tampon interne en y ajoutant le nouveau segment.
        self.buffer = np.roll(self.buffer, -self.CHUNK_SIZE)
        self.buffer[-self.CHUNK_SIZE:] = decoded_frame

        # 2. Appelle la stratégie pour qu'elle analyse les données et retourne le résultat.
        return self.strategy.analyze(
            full_buffer=self.buffer,
            latest_chunk=decoded_frame,
            timestamp=timestamp,
            sampling_rate=self.SAMPLING_RATE
        )