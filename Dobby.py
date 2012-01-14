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
from dobby import infos
from dobby.app import initRecognizer, initTriggers, initSpeaker, initController, initLogging
from dobby.config import initConfig
from dobby.db import initDb
import argparse
import logging


logger = logging.getLogger()


def main():
    parser = argparse.ArgumentParser(description=infos.__description__)
    parser.add_argument('-d', '--daemon', action='store_true', help='run as daemon', default=False)
    parser.add_argument('-p', '--pid-file', action='store', dest='pid_file', help='create pid file')
    parser.add_argument('-c', '--config-file', action='store', dest='config_file', help='config file to use', default='config.ini')
    group_verbosity = parser.add_mutually_exclusive_group()
    group_verbosity.add_argument('-q', '--quiet', action='store_true', help='disable console output')
    group_verbosity.add_argument('-v', '--verbose', action='store_true', help='verbose console output')
    parser.add_argument('--version', action='version', version=infos.__version__)
    args = parser.parse_args()
    
    # Init config
    config = initConfig(args.config_file)
    
    # Init logging
    #FIXME: args.verbose instead of True
    initLogging(args.quiet, True, config['Logging'])
    
    # Init db
    initDb()
    
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
    
    config.write()

if __name__ == '__main__':
#    import pyaudio
#    pa = pyaudio.PyAudio()
#    for i in range(pa.get_device_count()):
#        infos = pa.get_device_info_by_index(i)
#        print infos['name'] + "\t" + str(infos['index'])
    main()
