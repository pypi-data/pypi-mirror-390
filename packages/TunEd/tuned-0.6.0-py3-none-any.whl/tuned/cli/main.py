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
import argparse

from . import tuner, chord, metronome, pulsed

def time_signature_type(value: str) -> tuple[int, int]:
    """
    Type personnalisé pour argparse. Valide le format de la signature rythmique (ex: "4/4")
    et s'assure que les valeurs sont dans les plages autorisées.
    """
    try:
        numerator, denominator = map(int, value.split('/'))
        if not (1 <= numerator <= 5):
            raise ValueError("Le numérateur (temps par mesure) doit être compris entre 1 et 5.")
        if denominator not in [1, 2, 4, 8, 16, 32, 64]:
            raise ValueError("Le dénominateur (unité de temps) doit être l'un des suivants : 1, 2, 4, 8, 16, 32, 64.")
        return numerator, denominator
    except Exception as e:
        raise argparse.ArgumentTypeError(f"Format de signature invalide '{value}'. {e}. Utilisez un format comme '4/4'.")

def tuned():
    """Point d'entrée principal qui aiguille vers le bon mode."""
    parser = argparse.ArgumentParser(prog='TunEd', description='Accordeur en ligne de commande', epilog='')
    parser.add_argument('--version', action='version', version='%(prog)s 0.6.0')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Niveau de verbosité.')
    parser.add_argument('--mod', '-m', action='store', default='note', choices=['note', 'chord', 'metronome', 'pulsed'],
                        help='Mode de détection (note, accord ou métronome).')

    parser.add_argument('--frequency', '-f', action='store', default=440, type=int, help='Fréquence de référence (La).')

    parser.add_argument('--monitoring', action='store_true', help="Active le monitoring audio (le son de l'entrée est renvoyé à la sortie).")
    # parser.add_argument('--latency', action='store', default=None,
    #                     help="Suggère une latence pour le flux audio (ex: 'low', 'high', ou une valeur en secondes comme 0.02).")

    # Arguments pour le métronome
    parser.add_argument('--bpm', action='store', default=60, type=int, help='Battements par minute pour le mode métronome.')
    parser.add_argument('--time-signature', '-ts', type=time_signature_type, default=(4, 4),
                        help="Signature rythmique (ex: '4/4', '3/8'). Remplace --beats et --flow-rate.")

    # Argument pour l'analyse d'accord
    parser.add_argument('--no-harmonics-identification', '-nohi', action='store_false', dest='identify_harmonics',
                        help="Désactive l'identification des harmoniques pour les accords.")

    args = parser.parse_args()
    
    # Correction pour que --verbose 5 et plus soient ramenés à 4
    if args.verbose not in [0, 1, 2, 3, 4, 6]:
        args.verbose = 4
        
    # gestion de la latence
    args.latency = 'low' if args.monitoring else 0.25

    # Crée les attributs 'beats' et 'flow_rate' à partir de la signature rythmique
    # pour assurer la compatibilité avec les modules de mode.
    args.beats = args.time_signature[0]
    args.flow_rate = args.time_signature[1]

    if args.mod == 'chord':
        chord.run(args)
    elif args.mod == 'metronome':
        metronome.run(args)
    elif args.mod == 'pulsed':
        pulsed.run(args)
    else: # 'note' est le mode par défaut
        tuner.run(args)

if __name__ == '__main__':
    tuned()