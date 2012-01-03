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
from dobby.config import initConfig
from dobby.core import initTriggers, Dobby
from dobby.db import initDb, Session
from dobby.logger import initLogging, getLogger
from dobby.tts import TTSClient
import argparse


logger = getLogger()


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
    initLogging(args.quiet, args.verbose, config['Logging'])
    
    # Init db
    initDb()

    # Start triggers
    queue = Queue()
    triggers = initTriggers(queue, config['Trigger'])
    
    # Start Dobby
    dobby = Dobby(queue, Session(), TTSClient('Dobby', config['TTS']))
    dobby.start()
    
    config.write()

if __name__ == '__main__':
    main()
