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
from models.actions import Action
from models.sentence import Sentence
from triggers import ActionEvent, RecognitionEvent
import Queue
import logging
import threading


logger = logging.getLogger(__name__)


class Controller(threading.Thread):
    def __init__(self, event_queue, action_queue, session, recognizer, failed_message, recognition_timeout):
        super(Controller, self).__init__()
        self.event_queue = event_queue
        self.action_queue = action_queue
        self.session = session
        self.recognizer = recognizer
        self.failed_action = Action(tts=failed_message)
        self.recognition_timeout = recognition_timeout
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        while not self._stop:
            # Get the event from the queue
            event = self.event_queue.get()
            
            # Fire an Action directly if the event is an ActionEvent
            if isinstance(event, ActionEvent):
                logger.debug(u'ActionEvent catched with sentence "%s"' % event.sentence)
                sentence = self.session.query(Sentence).filter(Sentence.text == event.sentence).first()

            # Launch recognition and analyze the first sentence
            elif isinstance(event, RecognitionEvent):
                recognition_queue = Queue.Queue()
                self.recognizer.subscribe(recognition_queue)
                try:
                    recognition = recognition_queue.get(timeout=self.recognition_timeout)
                    recognized_sentence = unicode(recognition)
                    logger.debug(u'RecognitionEvent catched with sentence "%s"' % recognized_sentence)
                    sentence = self.session.query(Sentence).filter(Sentence.text == recognized_sentence).first()
                except Queue.Empty:
                    pass
                self.recognizer.unsubscribe(recognition_queue)

            # Failed message if no sentence
            if not sentence:
                logger.debug(u'Could not find the sentence in database')
                if self.failed_action.tts:
                    self.action_queue.put(self.failed_action.formated_tts)
                continue

            # Loop over the sentence's actions in the correct order and execute them
            for action_number in sorted(sentence.actions.keys()):
                self.action_queue.put(sentence.actions[action_number].formated_tts)

            # Mark the task as done
            self.event_queue.task_done()
