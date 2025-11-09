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
import time
from multiprocessing import Process

from .tick import Tick


class ClockGenerator(Process):

    def __init__(self,
                 pipe=None,
                 queue=None,
                 bpm=60,
                 beats_per_bar=4,
                 flow_rate=4,
                 autostart=True,
                 *args,
                 **kwargs):
        """
        Initialise le processus ClockGenerator.

        Args:
            pipe: Un Pipe multiprocessing pour la communication entrante (commandes).
            queue: Une Queue multiprocessing pour la communication sortante (ticks).
            bpm (int): Battements par minute.
            beats_per_bar (int): Le nombre de temps par mesure.
            flow_rate (int): Le nombre de ticks par mesure (ex: 4=noire, 8=croche).
            autostart (bool): Si True, le métronome commence à générer des ticks immédiatement.
                              Si False, il attend une commande 'start'.
        """
        Process.__init__(self, *args, **kwargs)

        self.pipe = pipe
        self.queue = queue
        self.bpm = bpm
        self.beats_per_bar = beats_per_bar
        self.flow_rate = max(1, flow_rate)

        self.pulse = 0
        self.bar = 1
        self.beat_index = 0
        self.tick_in_beat = 0
        self.ticks_in_beats = []
        self._recalculate_ticks_distribution()

        self.start_time = time.monotonic()
        self.running = autostart
        self._shutdown = False

        # Dictionnaire des gestionnaires de commandes
        self._command_handlers = {
            'set_bpm': self._handle_set_bpm,
            'set_time_signature': self._handle_set_time_signature,
            'start': self._handle_start,
            'stop': self._handle_stop,
            'shutdown': self._handle_shutdown,
        }

    def _recalculate_ticks_distribution(self):
        """Recalcule la répartition des ticks par temps en fonction de la signature rythmique."""
        ticks_per_quarter_note = self.flow_rate / 4
        effective_flow_rate = int(ticks_per_quarter_note * self.beats_per_bar)

        if effective_flow_rate > 0 and self.beats_per_bar > 0:
            base_ticks = effective_flow_rate // self.beats_per_bar
            extra_ticks = effective_flow_rate % self.beats_per_bar
            self.ticks_in_beats = [base_ticks + (1 if i < extra_ticks else 0) for i in range(self.beats_per_bar)]
        else:
            self.ticks_in_beats = [0] * self.beats_per_bar

    def _handle_set_bpm(self, value):
        """Gère la commande 'set_bpm'."""
        if isinstance(value, (int, float)) and value > 0:
            self.bpm = float(value)
        return self.bpm_to_sleep_time()

    def _handle_set_time_signature(self, value):
        """Gère la commande 'set_time_signature'."""
        if isinstance(value, (list, tuple)) and len(value) == 2:
            self.beats_per_bar = int(value[0])
            self.flow_rate = int(value[1])
            self._recalculate_ticks_distribution()
        # Le changement de flow_rate affecte l'intervalle, on le recalcule et le retourne.
        return self.bpm_to_sleep_time()

    def _handle_start(self, _value=None):
        """Démarre ou reprend la génération de ticks."""
        if not self.running:
            # Recalcule le start_time pour une reprise fluide
            tick_interval = self.bpm_to_sleep_time()
            self.start_time = time.monotonic() - (self.pulse * tick_interval)
            self.running = True
        return None

    def _handle_stop(self, _value=None):
        """Met en pause la génération de ticks."""
        self.running = False
        return None

    def _handle_shutdown(self, _value=None):
        """Prépare l'arrêt du processus."""
        self.running = False
        self._shutdown = True
        return None

    def bpm_to_sleep_time(self):
        """ Calcule l'intervalle de temps entre chaque tick. """
        ticks_per_minute = self.bpm * (self.flow_rate / 4)
        return 60 / ticks_per_minute if ticks_per_minute > 0 else float('inf')

    def now_pulse(self):
        self.pulse += 1
        return self.pulse

    def run(self):
        try:
            tick_interval = self.bpm_to_sleep_time()
            last_tick_time = self.start_time

            while not self._shutdown:
                # --- Vérifie et traite les commandes entrantes (non-bloquant) ---
                if self.pipe and self.pipe.poll():
                    message = self.pipe.recv()
                    if isinstance(message, dict):
                        command = message.get('command')
                        handler = self._command_handlers.get(command)
                        if handler:
                            old_tick_interval = tick_interval
                            new_interval = handler(message.get('value'))
                            if new_interval is not None and new_interval != old_tick_interval:
                                # Ajuste le start_time pour une transition de tempo fluide,
                                # en compensant le changement d'intervalle.
                                self.start_time += self.pulse * (old_tick_interval - new_interval)
                                tick_interval = new_interval

                if not self.running:
                    time.sleep(0.01)  # Pause active pour ne pas surcharger le CPU
                    continue

                # --- Génération du tick (uniquement si self.running est True) ---
                try:
                    # Calcule le moment où le prochain tick DEVRAIT se produire.
                    next_tick_target = self.start_time + (self.pulse + 1) * tick_interval

                    # Calcule le temps à attendre à partir de maintenant.
                    current_time = time.monotonic()
                    sleep_duration = next_tick_target - current_time

                    if sleep_duration > 0:
                        time.sleep(sleep_duration)

                    tick_time = time.monotonic()
                    actual_interval = tick_time - last_tick_time
                    last_tick_time = tick_time

                    pulse = self.now_pulse()

                    # --- Calcul de la position musicale ---
                    beat = self.beat_index + 1
                    ticks_for_current_beat = self.ticks_in_beats[self.beat_index]
                    beat_progress = self.tick_in_beat / ticks_for_current_beat if ticks_for_current_beat > 0 else 0
                    real_bpm = 60 / actual_interval if actual_interval > 0 else 0

                    tick = Tick(
                        pulse=pulse, beat=beat, bar=self.bar, bpm=self.bpm,
                        beat_progress=beat_progress, beat_interval=actual_interval,
                        total_time=tick_time - self.start_time,
                        process_monotonic_time=tick_time, real_bpm=real_bpm
                    )

                    # --- Mise à jour de l'état pour le prochain tick ---
                    self.tick_in_beat += 1
                    if self.tick_in_beat >= self.ticks_in_beats[self.beat_index]:
                        self.tick_in_beat = 0
                        self.beat_index += 1
                        if self.beat_index >= self.beats_per_bar:
                            self.beat_index = 0
                            self.bar += 1
                    
                    # --- Envoi du tick ---
                    tick_dict = {'tick': tick}
                    if self.queue:
                        self.queue.put_nowait(tick_dict)
                    elif self.pipe: # Fallback si seule la pipe est fournie
                        self.pipe.send(tick_dict)
                    else:
                        print(f"print {tick_dict}")

                except Exception:
                    break
        except KeyboardInterrupt:
            pass

    def shutdown(self):
        """Demande l'arrêt propre du processus depuis l'extérieur."""
        if self.pipe:
            self.pipe.send({'command': 'shutdown'})
        else:
            self._shutdown = True
