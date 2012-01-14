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
from . import Speaker, SPEAKING, IDLE
import logging
import speechd
import time


logger = logging.getLogger(__name__)


class SpeechDispatcher(Speaker):
    """Speaker using speech-dispatcher (speechd)

    :param string name: speechd's name of the SSIPClient
    :param string engine: speechd's output module
    :param string voice: speechd's voice
    :param string language: speechd's language
    :param integer rate: speechd's rate
    :param integer pitch: speechd's pitch

    """
    def __init__(self, tts_queue, name, engine, voice, language, volume, rate, pitch):
        super(SpeechDispatcher, self).__init__(tts_queue)
        self.client = speechd.SSIPClient(name)
        self.client.set_output_module(engine)
        self.client.set_voice(voice)
        self.client.set_language(language)
        self.client.set_volume(volume)
        self.client.set_rate(rate)
        self.client.set_pitch(pitch)
        self.client.set_punctuation(speechd.PunctuationMode.SOME)

    def speak(self, text):
        logger.debug(u'Speaking "%s"' % text)
        self.client.speak(text, callback=self._callback, event_types=(speechd.CallbackType.END))
        self.state = SPEAKING
        self._wait()

    def _callback(self, event_type):
        """Callback for speechd end of speech

        :param speechd.CallbackType event_type: type of the event raised by speechd

        """
        if event_type == speechd.CallbackType.END:
            self.state = IDLE

    def _wait(self, timeout=60, poll=0.1):
        """Block until :attr:`state` changes back to :data:`IDLE`

        :param integer timeout: maximum time to wait
        :param double poll: polling interval for checking :attr:`state`

        """
        i = 0
        while self.state == SPEAKING and i <= timeout / poll:
            time.sleep(poll)
            i += 1

    def terminate(self):
        logger.debug(u'Terminating...')
        self.client.close()
