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
from Queue import Queue
from configobj import flatten_errors
from dobby.config import initConfig, validator
from dobby.controller import Controller
from dobby.db import initDb
from dobby.recognizers.julius import Julius as JuliusRecognizer
from dobby.speakers.speechdispatcher import SpeechDispatcher
from dobby.triggers.clapper import Pattern, QuietPattern, NoisyPattern, Clapper
from dobby.triggers.julius import Julius as JuliusTrigger
from sqlalchemy.orm import scoped_session
import atexit
import logging.handlers
import os
import signal
import sys
import time


logger = logging.getLogger()
appdir = os.path.abspath(os.path.dirname(__file__))


class Application(object):
    def __init__(self, datadir, configfile=None, pidfile=None, quiet=False, verbose=False, daemon=False, use_signal=True):
        self.datadir = os.path.abspath(datadir)
        if not os.path.exists(self.datadir):
            os.makedirs(self.datadir)
        self.pidfile = pidfile or os.path.join(self.datadir, 'dobby.pid')
        self.configfile = configfile or os.path.join(self.datadir, 'config.ini')
        self.quiet = quiet
        self.verbose = verbose
        self.daemon = daemon
        self.use_signal = use_signal
        self.event_queue = Queue()
        self.tts_queue = Queue()
        self.config = initConfig(self.configfile)
        initLogging(self.quiet or self.daemon, self.verbose, os.path.join(self.datadir, 'logs'))
        self.Session = scoped_session(initDb(os.path.join(self.datadir, 'dobby.db')))
        self.running = False

    def daemonize(self):
        """Do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16

        """
        try:
            pid = os.fork()
            if pid > 0:  # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write('Fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:  # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write('Fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        # write pidfile
        atexit.register(self.delpid)
        file(self.pidfile, 'w+').write('%s\n' % str(os.getpid()))

    def delpid(self):
        os.remove(self.pidfile)
    
    def start(self):
        """Start the application (and daemonize if necessary)"""
        file(self.pidfile, 'w+').write('%s\n' % str(os.getpid()))
        if self.daemon:
            self.daemonize()
        self.run()

    def stop(self):
        """Stop the application"""
        if not self.running:
            return
        if self.config['General']['bye_message']:
            self.tts_queue.put(self.config['General']['bye_message'])
        self.controller.stop()
        self.controller.join()
        for trigger in self.triggers:
            trigger.stop()
            trigger.join()
        self.recognizer.stop()
        self.recognizer.join()
        self.speaker.stop()
        self.speaker.join()
        self.config.write()
        self.running = False

    def run(self):
        self.running = True
        self.recognizer = initRecognizer(self.config['Recognizer'])
        self.recognizer.start()
        self.triggers = initTriggers(self.event_queue, self.recognizer, self.config['Trigger'])
        for trigger in self.triggers:
            trigger.start()
        self.speaker = initSpeaker(self.tts_queue, self.config['Speaker'])
        self.speaker.start()
        self.controller = initController(self.event_queue, self.tts_queue, self.Session(), self.recognizer, self.config['General'])
        self.controller.start()

        # Welcome message
        if self.config['General']['welcome_message']:
            self.tts_queue.put(self.config['General']['welcome_message'])

        # Plug signals
        if self.use_signal:
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Wait until it's time to exit
        while self.running:
            time.sleep(1)
        #TODO: Error handling of prematurate child death

    def signal_handler(self, *args):
        logger.info(u'Stop signal caught')
        self.stop()
        exit(0)

    def write_default_config(self):
        self.config.validate(validator, copy=True)
        self.config.write()

    def validate_config(self):
        results = self.config.validate(validator, copy=True)
        if results != True:
            return flatten_errors(self.config, results)
        return True


def initTriggers(event_queue, recognizer, config):
    """Initialize all triggers as defined in the config

    :param Queue.Queue event_queue: where event will be raised into
    :param Recognizer recognizer: recognizer instance (only :class:`~dobby.recognizers.julius.Julius` is supported now)
    :param dict config: triggers-related settings
    :return: started triggers
    :rtype: list of Trigger

    """
    logger.debug(u'Initializing triggers')
    triggers = []
    for trigger_name in config['triggers']:
        if trigger_name == 'clapper':
            pattern = Pattern([QuietPattern(1), NoisyPattern(1, 4), QuietPattern(1, 6), NoisyPattern(1, 4), QuietPattern(1)])
            trigger = Clapper(event_queue, config['Clapper']['device_index'], pattern, config['Clapper']['threshold'],
                        config['Clapper']['channels'], config['Clapper']['rate'], config['Clapper']['block_time'])
            triggers.append(trigger)
            logger.debug(u'Trigger clapper initialized')
        elif trigger_name == 'julius':
            trigger = JuliusTrigger(event_queue, config['Julius']['sentence'], recognizer, config['Julius']['action'])
            triggers.append(trigger)
            logger.debug(u'Trigger julius initialized')
    return triggers

def initRecognizer(config):
    """Initialize the recognizer as defined in the config

    :param dict config: recognizer-related settings
    :return: started recognizer
    :rtype: Recognizer

    """
    if config['recognizer'] == 'julius':
        recognizer = JuliusRecognizer(config['Julius']['host'], config['Julius']['port'], config['Julius']['encoding'], config['Julius']['min_score'])
    return recognizer

def initSpeaker(tts_queue, config):
    """Initialize the Speaker as defined in the config

    :param Queue.Queue tts_queue: where actions are taken from
    :param dict config: Speaker-related settings
    :return: started Speaker
    :rtype: Speaker

    """
    if config['speaker'] == 'speechdispatcher':
        speaker = SpeechDispatcher(tts_queue, 'Dobby', str(config['SpeechDispatcher']['engine']), str(config['SpeechDispatcher']['voice']),
                          str(config['SpeechDispatcher']['language']), config['SpeechDispatcher']['volume'],
                          config['SpeechDispatcher']['rate'], config['SpeechDispatcher']['pitch'])
    return speaker

def initController(event_queue, tts_queue, session, recognizer, config):
    """Initialize the Controller as defined in the config

    :param Queue.Queue event_queue: where events are taken from
    :param Queue.Queue tts_queue: where actions are put into
    :param Session session: a SQLAlchemy database session
    :param Recognizer recognizer: the recognizer instance
    :param dict config: general settings
    :return: controller
    :rtype: Controller

    """
    controller = Controller(event_queue, tts_queue, session, recognizer, config['recognition_timeout'], config['failed_message'], config['confirmation_messages'])
    return controller

def initLogging(quiet, verbose, log_dir):
    """Initialize logging

    :param boolean quiet: whether to log in console or not
    :param boolean verbose: use DEBUG level for console logging
    :param string log_dir: directory for log files

    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handlers = []
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    handler = logging.handlers.RotatingFileHandler(os.path.join(log_dir, 'dobby.log'), maxBytes=2097152, backupCount=3, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s', datefmt='%m/%d/%Y %H:%M:%S'))
    handlers.append(handler)
    if not quiet:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(levelname)-8s:%(name)-32s:%(message)s'))
        if verbose:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.INFO)
        handlers.append(handler)
    root.handlers = handlers
