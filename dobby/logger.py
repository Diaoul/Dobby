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
import logging.handlers
import sys


def initLogging(quiet, verbose, config):
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

def getLogger(name=None):
    logger = logging.getLogger(name)
    return logger 
