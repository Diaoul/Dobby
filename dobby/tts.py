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
import speechd
import time


IDLE, SPEAKING = range(2)


class TTSClient(object):
    """Client for the TTS using speechd"""
    def __init__(self, name, config):
        self.state = IDLE
        self.client = speechd.SSIPClient(name)
        self.client.set_output_module(config['engine'])
        self.client.set_voice(config['voice'])
        self.client.set_language(config['language'])
        self.client.set_volume(config['volume'])
        self.client.set_rate(config['rate'])
        self.client.set_pitch(config['pitch'])
        self.client.set_punctuation(speechd.PunctuationMode.SOME)

    def terminate(self):
        self.client.close()

    def set_engine(self, engine):
        self.client.set_output_module(engine)

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
