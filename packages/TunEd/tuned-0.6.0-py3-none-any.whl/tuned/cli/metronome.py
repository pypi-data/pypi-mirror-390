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

import numpy as np
import sounddevice as sd

from tuned.metronome.clock import ClockGenerator
from tuned.midi.controller import MidiController
from tuned.cli.display.terminal import TerminalDisplay

def generate_tick_sound(frequency=1000, duration=0.05, samplerate=44100):
    """Génère les données d'un simple son de tick."""
    t = np.linspace(0., duration, int(samplerate * duration), endpoint=False)
    amplitude = np.iinfo(np.int16).max * 0.1
    data = amplitude * np.sin(2. * np.pi * frequency * t)
    return data.astype(np.int16)

def run(args):
    """L_ance l'application en mode métronome."""
    start_datetime = datetime.datetime.now()
    start_perf_counter_time = time.perf_counter()

    # --- Configuration de l'affichage ---
    default_display = ['pulse']
    verbosity_display = {
        0: [],
        1: ['heart_beat'],
        2: ['heart_beat', 'midi_message'],
        3: ['heart_beat', 'midi_message', 'real_bpm'],
        4: ['heart_beat', 'midi_message', 'real_bpm', 'execution_time'],
        6: ['heart_beat', 'midi_message', 'real_bpm', 'execution_time', 'egg']  # Pas d'infos verbose pour le métronome pour l'instant
    }
    to_display = [*default_display, *verbosity_display[args.verbose]]

    display = TerminalDisplay(to_display, 'metronome', args.beats, args.flow_rate)
    results_queue = multiprocessing.Queue()
    midi_ui_queue = multiprocessing.Queue()
    clock_proc = None
    midi_proc = None
    stream = None

    try:
        # --- Démarrage du flux audio ---
        tick_sound_data_1 = generate_tick_sound()
        tick_sound_data_2 = generate_tick_sound(frequency=2000)
        stream = sd.OutputStream(samplerate=44100, channels=1, dtype='int16')
        stream.start()

        # --- Configuration du Pipe pour la communication MIDI -> Clock ---
        midi_to_clock_parent, midi_to_clock_child = multiprocessing.Pipe()

        # --- Démarrage du contrôleur MIDI (tentative) ---
        midi_proc = MidiController(
            pipe=midi_to_clock_parent,
            ui_queue=midi_ui_queue
        )
        midi_proc.start()

        # --- Démarrage du métronome (toujours en autostart) ---
        clock_proc = ClockGenerator(
            pipe=midi_to_clock_child,
            queue=results_queue,
            bpm=args.bpm,
            beats_per_bar=args.beats,
            flow_rate=args.flow_rate,
            autostart=True
        )
        clock_proc.start()
        display.print_startup_message(ref_freq=args.frequency, bpm=args.bpm)

        # --- Boucle principale (UI) ---
        last_midi_message = None
        last_tick_result = None
        needs_redraw = True  # Pour forcer le premier affichage

        while True:
            execution_start_time = time.perf_counter()

            # --- Récupère le dernier message MIDI (non-bloquant) ---
            try:
                while not midi_ui_queue.empty():
                    last_midi_message = midi_ui_queue.get_nowait()
                    needs_redraw = True
            except Empty:
                pass

            # --- Récupère le dernier tick du métronome (non-bloquant) ---
            try:
                last_tick_result = results_queue.get_nowait()
                needs_redraw = True
            except Empty:
                pass

            # --- Redessine l'affichage si nécessaire ---
            if needs_redraw:
                result_for_display = last_tick_result if last_tick_result else {}
                result_for_display['midi_message'] = last_midi_message

                # --- Génération du son (uniquement si on a un nouveau tick) ---
                if last_tick_result:
                    tick = last_tick_result.get('tick')
                    if tick:
                        ticks_per_beat = args.flow_rate / args.beats
                        if (tick.pulse - 1) % ticks_per_beat == 0:
                            if tick.beat == 1:
                                stream.write(tick_sound_data_2)
                            else:
                                stream.write(tick_sound_data_1)

                execution_time = timedelta(seconds=time.perf_counter() - execution_start_time).total_seconds()
                output_string = display.format_output(result_for_display, execution_time)
                display.print_line(output_string)
                
                needs_redraw = False
                last_tick_result = None # On a traité ce tick

            time.sleep(0.01) # Empêche la boucle de consommer 100% du CPU


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
        if midi_proc:
            midi_proc.stop()
            midi_proc.join()
        if clock_proc:
            clock_proc.shutdown()
            clock_proc.join()
        if stream:
            stream.stop()
            stream.close()
        sys.exit()
