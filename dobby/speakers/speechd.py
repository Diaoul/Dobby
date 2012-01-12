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
from . import Speaker, IDLE, SPEAKING
import speechd
import time


class Speechd(Speaker):
    """Speaker using speechd

    :param string name: speechd's name of the SSIPClient
    :param string engine: speechd's output module
    :param string voice: speechd's voice
    :param string language: speechd's language
    :param integer rate: speechd's rate
    :param integer pitch: speechd's pitch

    """
    def __init__(self, action_queue, name, engine, voice, language, volume, rate, pitch):
        super(Speechd, self).__init__(action_queue)
        self.client = speechd.SSIPClient(name)
        self.client.set_output_module(engine)
        self.client.set_voice(voice)
        self.client.set_language(language)
        self.client.set_volume(volume)
        self.client.set_rate(rate)
        self.client.set_pitch(pitch)
        self.client.set_punctuation(speechd.PunctuationMode.SOME)

    def speak(self, text, blocking=True):
        self.client.speak(text, callback=self._callback, event_types=(speechd.CallbackType.END))
        self.state = SPEAKING
        self._wait()

    def _callback(self, event_type):
        """Callback for speechd end of speech"""
        if event_type == speechd.CallbackType.END:
            self.state = IDLE

    def _wait(self, timeout=60, poll=0.1):
        """Block until :attr:`state` changes back to :data:`IDLE`"""
        i = 0
        while self.state == SPEAKING and i <= timeout / poll:
            time.sleep(poll)
            i += 1

    def terminate(self):
        self.client.close()
