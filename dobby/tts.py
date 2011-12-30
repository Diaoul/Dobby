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

import speechd

# States
IDLE, SPEAKING = range(2)

class TTSClient(object):
    """Client for the TTS using speechd"""
    def __init__(self, name, config):
        self.state = IDLE
        self.client = speechd.SSIPClient(name)
        self.client.set_output_module(config['engine'])
        self.client.set_voice(config['voice'])
        self.client.set_language(config['language'])
        self.client.set_volume(config['volume'])
        self.client.set_rate(config['rate'])
        self.client.set_pitch(config['pitch'])
        self.client.set_punctuation(speechd.PunctuationMode.SOME)
        
    def speak(self, text):
        #TODO callbacks for BEGIN and END that sets the TTSClient state
        self.client.speak(text, callback=None, event_types=None)
        self.state = SPEAKING
