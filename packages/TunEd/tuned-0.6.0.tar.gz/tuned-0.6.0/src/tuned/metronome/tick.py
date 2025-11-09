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
from dataclasses import dataclass, field


@dataclass(frozen=True, order=True)
class Tick:
    pulse: int  # Compteur séquentiel pour chaque tick généré (la plus petite division de temps).
    beat: int  # Numéro du temps actuel dans la mesure (ex: 1, 2, 3, 4).
    bar: int  # Numéro de la mesure actuelle, commençant à 1.
    bpm: float  # Le tempo actuel en battements par minute.
    beat_progress: float  # Progression à l'intérieur du temps actuel (de 0.0 à 1.0).
    beat_interval: float  # Durée d'un seul temps, en secondes.
    total_time: float  # Temps total écoulé en secondes depuis le démarrage de l'horloge.
    process_monotonic_time: float  # Horodatage précis (monotonic) de la génération du tick.
    real_bpm: float = field(default=0.0, compare=False)  # Ticks réels par minute.
    