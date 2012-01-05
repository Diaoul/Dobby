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
from models.sentence import Sentence
from sqlalchemy.orm import joinedload
from triggers import ActionEvent, RecognitionEvent
from triggers.clapper import Pattern, QuietPattern, NoisyPattern, Clapper
from triggers.julius import Julius
import logging
import threading

logger = logging.getLogger(__name__)


def initTriggers(queue, config):
    triggers = []
    logger.debug(u'Initializing triggers')
    for trigger_name in config['triggers']:
        if trigger_name == 'clapper':
            p = Pattern([QuietPattern(1), NoisyPattern(1, 4), QuietPattern(1, 6), NoisyPattern(1, 4), QuietPattern(1)])
            t = Clapper(event_queue=queue, pattern=p, device_index=config['Clapper']['device_index'], block_time=config['Clapper']['block_time'])
            t.start()
            triggers.append(t)
            logger.debug(u'Trigger clapper initialized')
        elif trigger_name == 'julius':
            t = Julius(event_queue=queue, sentence=config['Julius']['sentence'], min_score=config['Julius']['min_score'], host=config['Julius']['host'], port=config['Julius']['port'], encoding=config['Julius']['encoding'], action=config['Julius']['action'])
            t.start()
            triggers.append(t)
            logger.debug(u'Trigger julius initialized')


class Dobby(threading.Thread):
    def __init__(self, event_queue, session, tts_client, recognizer):
        super(Dobby, self).__init__()
        self.event_queue = event_queue
        self.session = session
        self.tts_client = tts_client
        self.recognizer = recognizer
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
            
            # Launch recognition and analyze the first sentences (max_sentences)
            elif isinstance(event, RecognitionEvent):
                logger.debug(u'RecognizeEvent catched')
                for _ in range(self.max_sentences):
                    sentence_text = self.recognizer.recognize()
                    sentence = self.session.query(Sentence).filter(Sentence.text == sentence_text).first()
                    if sentence:
                        break

            #sentence = self.session.query(Sentence).options(joinedload(Sentence.actions)).with_polymorphic('*').filter(Sentence.text == recognized_sentence).first()
            # Loop over the sentence's actions in the correct order and execute them
            for action_number in sorted(sentence.actions.keys()):
                #TODO: Make a configurable error TTS to say
                self.tts_client.speak(sentence.actions[action_number].formated_tts)
            self.event_queue.task_done()