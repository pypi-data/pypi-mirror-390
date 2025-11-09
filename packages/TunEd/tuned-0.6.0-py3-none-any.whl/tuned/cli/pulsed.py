"""
Copyright (C) 2025 drd <drd.ltt000@gmail.com>

This file is part of TunEd.

TunEd is free software: you can redistribute and/or modify
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
from queue import Empty

from tuned.sound_analysis.process import (
    AnalysisProcess,
    SAMPLING_RATE,
    CHUNK_SIZE,
    ATTACK_BUFFER_TIMES
)
from tuned.sound_analysis.strategies import AubioAttackStrategy
from tuned.metronome.clock import ClockGenerator
from tuned.cli.display.terminal import TerminalDisplay

def run(args):
    """Lance l'application en mode d'entraînement rythmique (pulsed)."""
    
    display = TerminalDisplay([], 'pulsed', args.beats, args.flow_rate)
    analysis_queue = multiprocessing.Queue()
    clock_queue = multiprocessing.Queue()
    shutdown_event = multiprocessing.Event()
    
    analysis_proc = None
    clock_proc = None

    try:
        # --- Définition de la configuration d'analyse (on n'a besoin que des attaques) ---
        analyzer_configs = [
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

        # --- Démarrage des processus d'analyse et de métronome ---
        analysis_proc = AnalysisProcess(
            results_queue=analysis_queue,
            shutdown_event=shutdown_event,
            analyzer_configs=analyzer_configs,
            monitoring=args.monitoring,
            latency=args.latency
        )
        
        clock_proc = ClockGenerator(
            queue=clock_queue, 
            bpm=args.bpm, 
            beats_per_bar=args.beats, 
            flow_rate=args.flow_rate
        )

        analysis_proc.start()
        clock_proc.start()
        display.print_startup_message(ref_freq=args.frequency, bpm=args.bpm)

        # --- Boucle principale (UI) ---
        from collections import deque
        
        ticks_history = deque(maxlen=100)
        last_attack_time = 0
        last_offset_ms = None # Mémorise le dernier offset calculé

        while not shutdown_event.is_set():
            execution_start_time = time.perf_counter()
            display_data = {}

            # --- Récupère le dernier tick disponible ---
            latest_tick = None
            while not clock_queue.empty():
                tick_result = clock_queue.get_nowait()
                if 'tick' in tick_result:
                    latest_tick = tick_result['tick']
                    ticks_history.append(latest_tick)
            
            # --- Récupère et traite la dernière attaque ---
            latest_attack = None
            while not analysis_queue.empty():
                analysis_result = analysis_queue.get_nowait()

                # Gère les messages de débogage de l'analyseur
                if 'debug' in analysis_result and analysis_result['debug'] == 'latency_info':
                    info_str = (
                        f"~ [INFO] Monitoring: {analysis_result['monitoring']}, "
                        f"Latence Demandée: '{analysis_result['latency_requested']}', "
                        f"Latence Obtenue: ({analysis_result['latency_obtained'][0]:.4f}s, {analysis_result['latency_obtained'][1]:.4f}s)"
                    )
                    display.print_line(info_str)
                    continue

                attack = analysis_result.get('attack')
                if attack and attack.detected and attack.timestamp != last_attack_time:
                    last_attack_time = attack.timestamp
                    latest_attack = attack

            if latest_attack and ticks_history:
                closest_tick = min(ticks_history, key=lambda t: abs(t.process_monotonic_time - latest_attack.timestamp))
                last_offset_ms = (latest_attack.timestamp - closest_tick.process_monotonic_time) * 1000
                display_data['attack'] = latest_attack

            # --- Préparation des données pour l'affichage ---
            if latest_tick:
                display_data['tick'] = latest_tick
                display_data['offset_ms'] = last_offset_ms # Utilise le dernier offset connu
                
                execution_time = time.perf_counter() - execution_start_time
                output_string = display.format_output(display_data, execution_time)
                display.print_line(output_string)

                # On réinitialise l'offset pour qu'il ne soit utilisé qu'une seule fois.
                last_offset_ms = None

            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\nUne erreur est survenue: {e}")
    finally:
        print("\nArrêt en cours...")
        shutdown_event.set()
        if analysis_proc:
            analysis_proc.join()
        if clock_proc:
            clock_proc.stop()
            clock_proc.join()
        sys.exit()
