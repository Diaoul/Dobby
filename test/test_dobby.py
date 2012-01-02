# Copyright 2011 Antoine Bertin <diaoulael@gmail.com>
#
# This file is part of Dobby.

# Dobby is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Dobby is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Dobby.  If not, see <http://www.gnu.org/licenses/>.
from dobby.triggers.clapper import Pattern, QuietPattern, NoisyPattern, Clapper
from dobby.models.actions import wunderground
import Queue
import dobby.tts
import logging
import time
import unittest


logging.getLogger().setLevel(logging.DEBUG)


class TTSClientTestCase(unittest.TestCase):
    def setUp(self):
        self.config = {'engine': 'espeak', 'voice': 'MALE1', 'language': 'en', 'volume': 100, 'rate': 0, 'pitch': 0}
        self.tts_client = dobby.tts.TTSClient('test_dobby', self.config)

    def tearDown(self):
        self.tts_client.terminate()

    def test_state(self):
        self.tts_client.speak('This is a rather long test to be able to identify states')
        self.assertTrue(self.tts_client.state == dobby.tts.SPEAKING)
        self.tts_client.wait()
        self.assertTrue(self.tts_client.state == dobby.tts.IDLE)

    def test_espeak(self):
        self.tts_client.set_engine('espeak')
        self.tts_client.speak('This is a special test case. Please assert true if you hear this.')
        self.tts_client.wait()

    def test_flite(self):
        self.tts_client.set_engine('flite')
        self.tts_client.speak('This is a special test case. Please assert true if you hear this.')
        self.tts_client.wait()


class ClapperTestCase(unittest.TestCase):
    def setUp(self):
        # This patterns defines a QuietBlock of 1*0.25s min (no max) followed by a NoisyBlock of 1*0.25s min and 3*0.25s max, etc.
        # Clap 2 times for it to work
        p = Pattern([QuietPattern(1), NoisyPattern(1, 3), QuietPattern(1, 2), NoisyPattern(1, 3), QuietPattern(1)])
        self.clapper = Clapper(event_queue=Queue.Queue(), device_index=8, pattern=p, block_time=0.25)

    def test_main(self):
        self.clapper.start()
        time.sleep(4)  # let it live for a few seconds only :evil:
        self.clapper.stop()
        self.clapper.join()

class WeatherUndergroundTestCase(unittest.TestCase):
    def test_request(self):
        results = wunderground.request('01b1334435fa449f', ['conditions', 'forecast'], 'France/Cergy-Pontoise')
        self.assertTrue(len(results) > 0)