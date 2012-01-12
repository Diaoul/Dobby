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
import logging.handlers
import pyjulius
import sys


logger = logging.getLogger(__name__)


def initTriggers(event_queue, recognizer, config):
    """Initialize all triggers as defined in the config

    :param Queue.Queue event_queue: where event will be raised into
    :param Recognizer recognizer: recognizer instance (only :class:`~dobby.recognizers.julius.Julius` is supported now)
    :param dict config: triggers-related settings
    :returns: started triggers
    :rtype: list of Trigger

    """
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
    """Initialize the recognizer as defined in the config

    :param dict config: recognizer-related settings
    :returns: started recognizer
    :rtype: Recognizer

    """
    if config['recognizer'] == 'julius':
        client = pyjulius.Client(config['Julius']['host'], config['Julius']['port'], config['Julius']['encoding'])
        recognizer = JuliusRecognizer(client, config['Julius']['min_score'])
        recognizer.start()
    return recognizer

def initTTS(action_queue, config):
    """Initialize the TTS as defined in the config

    :param Queue.Queue action_queue: where actions are taken from
    :param dict config: TTS-related settings
    :returns: started TTS
    :rtype: TTS

    """
    tts = TTS('Dobby', action_queue, str(config['engine']), str(config['voice']), str(config['language']),
              config['volume'], config['rate'], config['pitch'])
    tts.start()
    return tts

def initController(event_queue, action_queue, recognizer, config):
    """Initialize the Controller as defined in the config

    :param Queue.Queue event_queue: where events are taken from
    :param Queue.Queue action_queue: where actions are put into
    :param Recognizer recognizer: the recognizer instance
    :param dict config: general settings
    :returns: controller
    :rtype: Controller

    """
    controller = Controller(event_queue, action_queue, Session(), recognizer, config['recognition_timeout'], config['failed_message'], config['confirmation_messages'])
    controller.start()
    return controller

def initLogging(quiet, verbose, config):
    """Initialize logging

    :param boolean quiet: whether to log in console or not
    :param boolean verbose: use DEBUG level for console logging
    :param dict config: logging-related settings

    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handlers = []
    if config['file']:
        handlers.append(logging.handlers.RotatingFileHandler(config['file'], config['max_bytes'], config['backup_count'], encoding='utf-8'))
    if not quiet:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter('%(name)s : %(levelname)-8s : %(message)s'))
        if verbose:
            stream_handler.setLevel(logging.DEBUG)
        else:
            stream_handler.setLevel(logging.INFO)
        handlers.append(stream_handler)
    root.handlers = handlers
    