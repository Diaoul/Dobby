#!/usr/bin/env python
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
from configobj import ConfigObj, flatten_errors
from dobby import infos
from dobby.controller import Controller
from dobby.db import initDb, Session
from dobby.recognizers.julius import Julius as JuliusRecognizer
from dobby.speakers.speechdispatcher import SpeechDispatcher
from dobby.triggers.clapper import Pattern, QuietPattern, NoisyPattern, Clapper
from dobby.triggers.julius import Julius as JuliusTrigger
from validate import Validator, VdtValueError, VdtTypeError
import argparse
import logging.handlers
import os
import signal
import sys


logger = logging.getLogger()


def main():
    parser = argparse.ArgumentParser(description=infos.__description__)
    parser.add_argument('-d', '--daemon', action='store_true', help='run as daemon', default=False)
    parser.add_argument('-p', '--pid-file', action='store', dest='pid_file', help='create pid file')
    parser.add_argument('-c', '--config-file', action='store', dest='config_file', help='config file to use')
    parser.add_argument('--list-devices', action='store_true', dest='list_devices', help='list available devices and exit')
    parser.add_argument('--data-dir', action='store', dest='data_dir', help='data directory to store cache, config, logs and database', default='data')
    group_verbosity = parser.add_mutually_exclusive_group()
    group_verbosity.add_argument('-q', '--quiet', action='store_true', help='disable console output')
    group_verbosity.add_argument('-v', '--verbose', action='store_true', help='verbose console output')
    parser.add_argument('--version', action='version', version=infos.__version__)
    args = parser.parse_args()
    
    if args.list_devices:
        import pyaudio
        pa = pyaudio.PyAudio()
        for i in range(pa.get_device_count()):
            device_infos = pa.get_device_info_by_index(i)
            print device_infos['name'] + "\t" + str(device_infos['index'])
        sys.exit(0)

    # Init paths
    data_dir = os.path.abspath(args.data_dir)
    config_file = args.config_file or os.path.join(data_dir, 'config.ini')
    
    # Create the data directory
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Init config
    config = initConfig(config_file)
    
    # Init logging
    initLogging(args.quiet or args.daemon, args.verbose, os.path.join(data_dir, 'logs'))
    
    # Init db
    initDb(os.path.join(data_dir, 'dobby.db'))

    # Daemonize
    if args.daemon:
        daemonize()

    # Write pid
    pid_file = None
    if args.pid_file:
        pid_file = args.pid_file
    elif args.daemon:
        pid_file = os.path.join(data_dir, 'dobby.pid')
    if pid_file:
        file(pid_file, 'w+').write('%s\n' % str(os.getpid()))
    
    # Init recognizer
    recognizer = initRecognizer(config['Recognizer'])

    # Init triggers
    event_queue = Queue()
    triggers = initTriggers(event_queue, recognizer, config['Trigger'])

    # Init speaker
    tts_queue = Queue()
    speaker = initSpeaker(tts_queue, config['Speaker'])

    # Start controller
    controller = initController(event_queue, tts_queue, recognizer, config['General'])
    
    # Welcome message
    if config['General']['welcome_message']:
        tts_queue.put(config['General']['welcome_message'])

    # Handle termination
    def handler(*args):
        logger.info(u'Stop signal caught')
        if config['General']['bye_message']:
            tts_queue.put(config['General']['bye_message'])
        controller.stop()
        controller.join()
        for trigger in triggers:
            trigger.stop()
            trigger.join()
        recognizer.stop()
        recognizer.join()
        speaker.stop()
        speaker.join()
        config.write()
        exit(0)

    # Plug signals
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    
    # Wait until it's time to exit
    signal.pause()

def daemonize():
    """Daemonize"""
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
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
        if pid > 0:
            # exit from second parent
            sys.exit(0)
    except OSError, e:
        sys.stderr.write('Fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
        sys.exit(1)

    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = file('/dev/null', 'r')
    so = file('/dev/null', 'a+')
    se = file('/dev/null', 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

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
    :return: started recognizer
    :rtype: Recognizer

    """
    if config['recognizer'] == 'julius':
        recognizer = JuliusRecognizer(config['Julius']['host'], config['Julius']['port'], config['Julius']['encoding'], config['Julius']['min_score'])
        recognizer.start()
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
    speaker.start()
    return speaker

def initController(event_queue, tts_queue, recognizer, config):
    """Initialize the Controller as defined in the config

    :param Queue.Queue event_queue: where events are taken from
    :param Queue.Queue tts_queue: where actions are put into
    :param Recognizer recognizer: the recognizer instance
    :param dict config: general settings
    :return: controller
    :rtype: Controller

    """
    controller = Controller(event_queue, tts_queue, Session(), recognizer, config['recognition_timeout'], config['failed_message'], config['confirmation_messages'])
    controller.start()
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

def initConfig(path='config.ini'):
    """Initialize and validate the configuration file. If the validation test fails,
    error messages are written to sys.stderr and we exit with status 1

    :param string path: path to the configuration file
    :return: the read configuration
    :rtype: ConfigObj

    """
    def is_option_list(value, *args):
        """Validator for a list of options"""
        if not isinstance(value, list):
            raise VdtTypeError(value)
        for v in value:
            if v not in args:
                raise VdtValueError(v)
        return value

    config = ConfigObj(path, configspec='config.spec', encoding='utf-8')
    vtor = Validator({'option_list': is_option_list})
    results = config.validate(vtor, copy=True)
    if results != True:
        for (section_list, key, _) in flatten_errors(config, results):
            if key is not None:
                sys.stderr.write('The "%s" key in the section "%s" failed validation\n' % (key, ', '.join(section_list)))
            else:
                sys.stderr.write('The following section was missing: %s\n' % ', '.join(section_list))
        sys.exit(1)
    return config


if __name__ == '__main__':
    main()
