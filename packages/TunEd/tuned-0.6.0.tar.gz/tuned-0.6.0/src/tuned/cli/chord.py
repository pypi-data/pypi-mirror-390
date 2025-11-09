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
import multiprocessing
import sys
import time
import datetime
from datetime import timedelta
from queue import Empty

from tuned.sound_analysis.process import (
    AnalysisProcess,
    SAMPLING_RATE,
    CHUNK_SIZE,
    SPECTRAL_BUFFER_TIMES,
    ATTACK_BUFFER_TIMES
)
from tuned.sound_analysis.strategies import ChordDetectionStrategy, AubioAttackStrategy
from tuned.cli.display.terminal import TerminalDisplay

def run(args):
    """L_ance l'application en mode accordeur d'accords."""
    start_datetime = datetime.datetime.now()
    start_perf_counter_time = time.perf_counter()

    # --- Configuration de l'affichage ---
    default_display = ['chord', 'notes']
    verbosity_display = {
        0: [],
        1: ['precision'],
        2: ['precision', 'frequency'],
        3: ['precision', 'frequency', 'signal_level', 'attack'],
        4: ['precision', 'frequency', 'signal_level', 'attack', 'execution_time'],
        6: ['precision', 'frequency', 'signal_level', 'attack', 'execution_time', 'egg']
    }
    to_display = [*default_display, *verbosity_display[args.verbose]]
    
    display = TerminalDisplay(to_display, 'chord', args.beats, args.flow_rate)
    results_queue = multiprocessing.Queue()
    shutdown_event = multiprocessing.Event()
    analysis_proc = None

    try:
        # --- Définition de la configuration d'analyse ---
        analyzer_configs = [
            {
                'strategy_class': ChordDetectionStrategy,
                'strategy_params': {
                    'ref_freq': args.frequency,
                    'identify_harmonics': args.identify_harmonics
                },
                'buffer_times': SPECTRAL_BUFFER_TIMES
            },
            {
                'strategy_class': AubioAttackStrategy,
                'strategy_params': {
                    'sampling_rate': SAMPLING_RATE,
                    'win_s': CHUNK_SIZE,
                    'hop_s': CHUNK_SIZE,
                    'method': "specdiff"
                },
                'buffer_times': ATTACK_BUFFER_TIMES
            }
        ]

        # --- Démarrage du processus d'analyse ---
        analysis_proc = AnalysisProcess(
            results_queue=results_queue,
            shutdown_event=shutdown_event,
            analyzer_configs=analyzer_configs,
            monitoring=args.monitoring,
            latency=args.latency
        )
        analysis_proc.start()
        display.print_startup_message(ref_freq=args.frequency, bpm=args.bpm)

        # --- Boucle principale (UI) ---
        while not shutdown_event.is_set():
            execution_start_time = time.perf_counter()
            try:
                result = results_queue.get(timeout=0.1)

                # INTERCEPTER ET AFFICHER LE MESSAGE DE DÉBOGAGE
                if 'debug' in result and result['debug'] == 'latency_info':
                    info_str = (
                        f"~ [INFO] Monitoring: {result['monitoring']}, "
                        f"Latence Demandée: '{result['latency_requested']}', "
                        f"Latence Obtenue: ({result['latency_obtained'][0]:.4f}s, {result['latency_obtained'][1]:.4f}s)"
                    )
                    display.print_line(info_str)
                    continue

                if 'error' in result:
                    print(f"\nErreur dans le processus d'analyse: {result['error']}")
                    break

                execution_time = timedelta(seconds=time.perf_counter() - execution_start_time).total_seconds()
                output_string = display.format_output(result, execution_time)
                display.print_line(output_string)

            except Empty:
                continue

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\nUne erreur est survenue: {e}")
    finally:
        # --- Message de fin ---
        start_hour_str = start_datetime.strftime("%H:%M:%S")
        wall_time = time.perf_counter() - start_perf_counter_time
        s = int(wall_time)
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        display.end_current_line()
        print(f"\n TunEd started at: {start_hour_str}")
        print(f" Total session time: {duration_str}\n")
        print(" Bye!")

        # --- Arrêt propre ---
        shutdown_event.set()
        if analysis_proc:
            analysis_proc.join()
        sys.exit()
