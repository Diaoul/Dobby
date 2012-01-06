# Copyright 2011 Antoine Bertin <diaoulael@gmail.com>
#
# This file is part of Dobby.
#
# Dobby is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dobby is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dobby.  If not, see <http://www.gnu.org/licenses/>.
import Queue
import speechd
import threading
import time


IDLE, SPEAKING = range(2)


class TTS(threading.Thread):
    """TTS using speechd. The thread's task is to speak each actions it gets in a row"""
    def __init__(self, name, action_queue, engine, voice, language, volume, rate, pitch):
        super(TTS, self).__init__()
        self.state = IDLE
        self.action_queue = action_queue
        self.client = speechd.SSIPClient(name)
        self.client.set_output_module(engine)
        self.client.set_voice(voice)
        self.client.set_language(language)
        self.client.set_volume(volume)
        self.client.set_rate(rate)
        self.client.set_pitch(pitch)
        self.client.set_punctuation(speechd.PunctuationMode.SOME)
        self._stop = False

    def stop(self):
        self._stop = True

    def speak(self, text):
        self.client.speak(text, callback=self._callback, event_types=(speechd.CallbackType.END))
        self.state = SPEAKING

    def wait(self, timeout=10, poll=0.1):
        i = 0
        while self.state == SPEAKING and i <= timeout / poll:
            time.sleep(poll)
            i += 1

    def _callback(self, event_type):
        if event_type == speechd.CallbackType.END:
            self.state = IDLE

    def run(self):
        while not self._stop:
            try:
                action_message = self.action_queue.get(1)
            except Queue.Empty:
                continue
            self.speak(action_message)
            self.wait(60, 1)
            self.action_queue.task_done()
        self.client.close()
