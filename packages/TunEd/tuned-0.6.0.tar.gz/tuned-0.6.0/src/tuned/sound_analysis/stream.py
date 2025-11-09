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
class Sound:
    """Représente un son musical détecté avec ses propriétés."""
    timestamp: float
    magnitude: float = field(repr=False, compare=False)
    magnitude_to_db: float
    phase: float = field(repr=False, compare=False)
    frequency: float
    note: str
    octave: int
    offset: int = field(default=0, repr=False, compare=False)
    is_harmonic: bool = field(default=False, repr=False, compare=False)
    confidence: float = field(default=0.0, repr=False, compare=False)

    def is_in_tune(self, tolerance_cents: int = 10) -> bool:
        """Vérifie si la note est juste à l'intérieur d'une tolérance donnée."""
        return abs(self.offset) <= tolerance_cents