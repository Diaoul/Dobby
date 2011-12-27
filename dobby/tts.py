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

import config
import speechd

client = None

def initTTS():
    global client
    client = speechd.SSIPClient('Dobby')
    client.set_output_module(config['TTS']['engine'])
    client.set_voice(config['TTS']['voice'])
    client.set_language(config['TTS']['language'])
    client.set_volume(config['TTS']['volume'])
    client.set_rate(config['TTS']['rate'])
    client.set_pitch(config['TTS']['pitch'])
    client.set_punctuation(speechd.PunctuationMode.SOME)

def closeTTS():
    client.close()