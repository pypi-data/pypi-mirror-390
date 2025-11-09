# -*- coding: utf-8 -*-
"""
Une implémentation simple du tap-tempo.
"""
import time
from collections import deque
from typing import Optional


class TapTempo:
    """
    Calcule les BPM (Battements Par Minute) à partir d'une série de "taps".

    Cette classe enregistre les timestamps des taps et calcule la moyenne des BPM
    à partir des intervalles entre eux. Elle utilise un deque pour stocker un
    historique limité des taps récents, rendant le calcul des BPM réactif aux
    changements de tempo.

    :param max_taps: Le nombre maximum de taps récents à conserver pour le calcul.
                     Un nombre plus élevé donne un BPM plus stable mais s'adapte
                     moins vite aux changements de tempo.
    """

    def __init__(self, max_taps: int = 5):
        if max_taps < 2:
            raise ValueError("max_taps doit être au moins 2 pour calculer un intervalle.")
        self._timestamps = deque(maxlen=max_taps)

    def tap(self) -> None:
        """
        Enregistre un "tap" au moment présent.

        Cette méthode doit être appelée à chaque battement (par exemple,
        lorsque l'utilisateur appuie sur une touche).
        """
        self._timestamps.append(time.monotonic())

    @property
    def bpm(self) -> float:
        """
        Calcule et retourne le BPM actuel.

        Retourne 0.0 s'il n'y a pas assez de taps (moins de 2) pour calculer
        un intervalle. Le calcul est basé sur l'intervalle moyen des taps stockés.

        :return: Le BPM calculé, ou 0.0 si les données sont insuffisantes.
        """
        if len(self._timestamps) < 2:
            return 0.0

        intervals = [
            self._timestamps[i] - self._timestamps[i - 1]
            for i in range(1, len(self._timestamps))
        ]
        avg_interval = sum(intervals) / len(intervals)

        if avg_interval == 0:
            return 0.0

        return 60.0 / avg_interval


def main() -> None:
    """
    Une démonstration interactive de la classe TapTempo.
    """
    tap_tempo = TapTempo()
    print("Appuyez sur Entrée pour taper le tempo. Appuyez sur Ctrl+C pour quitter.")

    try:
        while True:
            input()  # Attend que l'utilisateur appuie sur Entrée
            tap_tempo.tap()
            bpm = tap_tempo.bpm
            if bpm > 0:
                print(f"BPM: {bpm:.2f}")
            else:
                print("Tapez encore pour calculer le BPM...")
    except KeyboardInterrupt:
        print("\nSortie.")


if __name__ == "__main__":
    main()
