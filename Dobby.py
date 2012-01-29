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
from dobby import infos
from dobby.app import Application
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description=infos.__description__)
    parser.add_argument('-d', '--daemon', action='store_true', help='run as daemon', default=False)
    parser.add_argument('-p', '--pid-file', action='store', dest='pidfile', help='create pid file')
    parser.add_argument('-c', '--config-file', action='store', dest='configfile', help='config file to use')
    parser.add_argument('--list-devices', action='store_true', dest='list_devices', help='list available devices and exit')
    parser.add_argument('--data-dir', action='store', dest='data_dir', help='data directory to store cache, config, logs and database', default='data')
    group_verbosity = parser.add_mutually_exclusive_group()
    group_verbosity.add_argument('-q', '--quiet', action='store_true', help='disable console output')
    group_verbosity.add_argument('-v', '--verbose', action='store_true', help='verbose console output')
    parser.add_argument('--version', action='version', version=infos.__version__)
    args = parser.parse_args()

    # List devices
    if args.list_devices:
        import pyaudio
        pa = pyaudio.PyAudio()
        for i in range(pa.get_device_count()):
            device_infos = pa.get_device_info_by_index(i)
            print device_infos['name'] + '\t' + str(device_infos['index'])
        sys.exit(0)

    # Init the app
    app = Application(os.path.abspath(args.data_dir), configfile=args.configfile, pidfile=args.pidfile, quiet=args.quiet, verbose=args.verbose, daemon=args.daemon)

    # Write default configuration
    if not os.path.exists(app.configfile):
        app.write_default_config()

    # Validate configuration
    results = app.validate_config()
    if results != True:
        for (section_list, key, _) in results:
            if key is not None:
                sys.stderr.write('The "%s" key in the section "%s" failed validation\n' % (key, ', '.join(section_list)))
            else:
                sys.stderr.write('The following section was missing: %s\n' % ', '.join(section_list))
        sys.exit(1)

    # Start the app
    app.start()


if __name__ == '__main__':
    main()
