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
from controller import Controller
from db import Session
from recognizers.julius import Julius as JuliusRecognizer
from triggers.clapper import Pattern, QuietPattern, NoisyPattern, Clapper
from triggers.julius import Julius as JuliusTrigger
from tts import TTS
import logging
import pyjulius


logger = logging.getLogger(__name__)


def initTriggers(event_queue, recognizer, config):
    logger.debug(u'Initializing triggers')
    triggers = []
    for trigger_name in config['triggers']:
        if trigger_name == 'clapper':
            pattern = Pattern([QuietPattern(1), NoisyPattern(1, 4), QuietPattern(1, 6), NoisyPattern(1, 4), QuietPattern(1)])
            trigger = Clapper(event_queue, config['Clapper']['device_index'], pattern, config['Clapper']['threshold'],
                        config['Clapper']['channels'], config['Clapper']['rate'], config['Clapper']['block_time'])
            trigger.start()
            triggers.append(trigger)
            logger.debug(u'Trigger clapper initialized')
        elif trigger_name == 'julius':
            trigger = JuliusTrigger(event_queue, config['Julius']['sentence'], recognizer, config['Julius']['action'])
            trigger.start()
            triggers.append(trigger)
            logger.debug(u'Trigger julius initialized')
    return triggers

def initRecognizer(config):
    if config['recognizer'] == 'julius':
        client = pyjulius.Client(config['Julius']['host'], config['Julius']['port'], config['Julius']['encoding'])
        recognizer = JuliusRecognizer(client, config['Julius']['min_score'])
        recognizer.start()
    return recognizer

def initTTS(action_queue, config):
    tts = TTS('Dobby', action_queue, str(config['engine']), str(config['voice']), str(config['language']),
              config['volume'], config['rate'], config['pitch'])
    tts.start()
    return tts

def initController(event_queue, action_queue, recognizer, config):
    controller = Controller(event_queue, action_queue, Session(), recognizer, config['failed_message'], config['recognition_timeout'])
    controller.start()
    return controller
    