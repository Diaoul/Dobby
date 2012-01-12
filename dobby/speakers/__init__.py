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


class Speaker(threading.Thread):
    """Threaded Speaker base. Its task is to speak each actions it gets in a row"""
    def __init__(self, action_queue):
        super(Speaker, self).__init__()
        self.state = IDLE
        self.action_queue = action_queue
        self._stop = False

    def stop(self):
        """Stop the thread"""
        self._stop = True

    def speak(self, text):
        """Speak the text and block until it's said

        :param string text: text to speech

        """
        pass

    def wait(self, timeout=10, poll=0.1):
        
        pass

    def terminate(self):
        pass

    def run(self):
        while not self._stop:
            try:
                action_message = self.action_queue.get(1)
            except Queue.Empty:
                continue
            self.speak(action_message)
            self.wait(60, 1)
            self.action_queue.task_done()
        self.terminate()
