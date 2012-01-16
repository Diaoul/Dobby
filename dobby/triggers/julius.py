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
from . import Trigger, RecognitionEvent, VoiceCommandEvent
import Queue
import logging


logger = logging.getLogger(__name__)


class Julius(Trigger):
    """Analyze an audio source and put an event in the queue if voice command is spoken

    :param string voice_command: voice command to match
    :param Recognizer recognizer: :class:`Julius Recognizer <dobby.recognizers.julius.Julius>` instance 
    :param boolean action: whether to fire :class:`VoiceCommandEvents <dobby.triggers.VoiceCommandEvent>` or not

    """
    def __init__(self, event_queue, voice_command, recognizer, action):
        super(Julius, self).__init__(event_queue)
        self.voice_command = voice_command
        self.recognizer = recognizer
        self.action = action

    def run(self):
        recognition_queue = Queue.Queue()
        self.recognizer.subscribe(recognition_queue)
        while not self._stop:
            try:
                recognition = recognition_queue.get(timeout=1)
            except Queue.Empty:
                continue
            recognized_voice_command = unicode(recognition)
            if recognized_voice_command == self.voice_command:
                logger.debug(u'Firing RecognitionEvent')
                self.event_queue.put(RecognitionEvent())
                continue
            if self.action and recognized_voice_command.startswith(self.voice_command):
                voice_command = recognized_voice_command[len(self.voice_command) + 1:]
                logger.debug(u'Firing VoiceCommandEvent("%s")' % voice_command)
                self.event_queue.put(VoiceCommandEvent(voice_command))
                continue
            logger.debug(u'Reject recognition "%s"' % (recognized_voice_command))
        self.recognizer.unsubscribe(recognition_queue)
        logger.info(u'Terminating...')
