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
import logging
import threading
import time


IDLE, SPEAKING = range(2)


class Speaker(threading.Thread):
    """Threaded Speaker base. Its task is to speak each actions it gets in a row

    :param Queue.Queue tts_queue: where to pick text-to-speech

    """
    def __init__(self, tts_queue):
        super(Speaker, self).__init__()
        self.state = IDLE
        self.tts_queue = tts_queue
        self._stop = False

    def stop(self):
        """Stop the thread"""
        self._stop = True

    def speak(self, text):
        """Speak the text and block until it's said

        :param string text: text to speech

        """

    def terminate(self):
        """Terminate the thread"""

    def run(self):
        """Wait for events in the :attr:`tts_queue` and speak the received TTS. Once
        the thread is told to stop, :meth:`terminate` is called

        """
        while not self._stop:
            try:
                action_message = self.tts_queue.get(timeout=1)
            except Queue.Empty:
                continue
            self.speak(action_message)
            self.tts_queue.task_done()
        self.terminate()
