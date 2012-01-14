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
import random
import threading


logger = logging.getLogger(__name__)


class Controller(threading.Thread):
    """Threaded controller that holds the main logic of Dobby. It grabs events as they come and put corresponding
    (according to the database) processed actions in the queue.
    Error message and confirmation messages are customizable

    :param Queue.Queue event_queue: where to listen for events
    :param Queue.Queue tts_queue: where to put the tts from processed actions
    :param Session session: Dobby database session
    :param integer recognition_timeout: time to wait for a sentence to be recognized once a :class:`RecognitionEvent` is received
    :param string failed_message: error message to say when the recognized sentence does not match anything in the database
    :param list confirmation_messages: a random message to say is picked and sent to the action queue whenever a :class:`RecognitionEvent` is caught

    """
    def __init__(self, event_queue, tts_queue, session, recognizer, recognition_timeout, failed_message, confirmation_messages):
        super(Controller, self).__init__()
        self.event_queue = event_queue
        self.tts_queue = tts_queue
        self.session = session
        self.recognizer = recognizer
        self.recognition_timeout = recognition_timeout
        self.failed_action = Action(tts=failed_message)
        self.confirmation_messages = confirmation_messages
        self._stop = False

    def stop(self):
        """Stop the thread"""
        self._stop = True

    def run(self):
        while not self._stop:
            # Get the event from the queue
            try:
                event = self.event_queue.get(timeout=1)
            except Queue.Empty:
                continue
            
            # Fire an Action directly if the event is an ActionEvent
            if isinstance(event, ActionEvent):
                logger.debug(u'ActionEvent catched with sentence "%s"' % event.sentence)
                sentence = self.session.query(Sentence).filter(Sentence.text == event.sentence).first()

            # Launch recognition and analyze the first sentence
            elif isinstance(event, RecognitionEvent):
                # Send a random confirmation message
                if self.confirmation_messages:
                    self.tts_queue.put(random.sample(self.confirmation_messages, 1)[0])
                # Monitor the recognized sentences and catch the first one
                recognition_queue = Queue.Queue()
                self.recognizer.subscribe(recognition_queue)
                try:
                    recognition = recognition_queue.get(timeout=self.recognition_timeout)
                    recognized_sentence = unicode(recognition)
                    logger.debug(u'RecognitionEvent catched with sentence "%s"' % recognized_sentence)
                    sentence = self.session.query(Sentence).filter(Sentence.text == recognized_sentence).first()
                except Queue.Empty:
                    sentence = None
                    pass
                self.recognizer.unsubscribe(recognition_queue)

            # Failed message if no sentence
            if not sentence:
                logger.debug(u'Could not find the sentence in database')
                if self.failed_action.tts:
                    self.tts_queue.put(self.failed_action.format_tts())
                continue

            # Loop over the sentence's actions in the correct order and execute them
            for action_number in sorted(sentence.actions.keys()):
                self.tts_queue.put(sentence.actions[action_number].format_tts())

            # Mark the task as done
            self.event_queue.task_done()
        logger.info(u'Terminating...')
