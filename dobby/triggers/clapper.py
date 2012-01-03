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
from . import Trigger, TriggerEvent
from collections import deque
import logging
import math
import pyaudio
import struct


logger = logging.getLogger(__name__)


class Block(object):
    """A block of audio data to insert in a Sequence"""
    def __init__(self, length=1):
        self.length = length

    def increase(self, amount=1):
        self.length += amount

    def __repr__(self):
        return '<' + self.__class__.__name__ + ' "%d">' % self.length


class QuietBlock(Block):
    """Represent a quiet block of audio data"""
    pass


class NoisyBlock(Block):
    """Represent a noisy block of audio data"""
    pass


class Sequence(deque):
    """The latest sequence of blocks read from an audio source
    Adding a Block of the same type of the previous one will increase its length
    """
    def append(self, x):
        if len(self) == 0:
            super(Sequence, self).append(x)
            return
        last = self.pop()
        if type(x) == type(last):
            last.increase(x.length)
            super(Sequence, self).append(last)
            return
        super(Sequence, self).append(last)
        super(Sequence, self).append(x)


class PatternItem(object):
    """A PatternItem is linked to a Block add will be used to validate it"""
    validate = None

    def __init__(self, min_count=None, max_count=None):
        self.min = min_count
        self.max = max_count
    
    def match(self, block):
        if self.min is not None and block.length < self.min:
            return False
        if self.max is not None and block.length > self.max:
            return False
        if self.validate is not None and not isinstance(block, self.validate):
            return False
        return True


class QuietPattern(PatternItem):
    """A QuietPattern validates a QuietBlock"""
    validate = QuietBlock


class NoisyPattern(PatternItem):
    """A NoisyPattern validates a NoisyBlock"""
    validate = NoisyBlock


class Pattern(list):
    """Enhanced list that is used to match a Sequence"""
    def match(self, sequence):
        if len(sequence) != len(self):
            return False
        for i in range(len(sequence)):
            if not self[i].match(sequence[i]):
                return False
        return True


class ClapperEvent(TriggerEvent):
    """Event put in the event_queue of the Clapper"""
    pass


class Clapper(Trigger):
    """Analyze an audio source and put an event in the queue if the resulting Sequence of Block matches the Pattern"""
    def __init__(self, event_queue, device_index, pattern, threshold=0.020, channels=1, rate=44100, block_time=0.05):
        super(Clapper, self).__init__(event_queue)
        self.device_index = device_index
        self.pattern = pattern
        self.threshold = threshold
        self.channels = channels
        self.rate = rate
        self.block_time = block_time

    def run(self):
        # Init the stream
        pa = pyaudio.PyAudio()
        chunk = int(self.rate * self.block_time)
        stream = pa.open(format=pyaudio.paInt16, channels=self.channels, rate=self.rate,
                         input=True, input_device_index=self.device_index, frames_per_buffer=chunk)
        threshold = self.threshold
        sequence = Sequence(maxlen=len(self.pattern))
        # Main loop
        while not self._stop:
            data_block = stream.read(chunk)
            rms = self.get_rms(data_block)
            # Detect the type of block
            if rms > threshold:
                sequence.append(NoisyBlock())
            else:            
                sequence.append(QuietBlock())
            # Trigger an event and reset if the sequence matches the pattern
            if self.pattern.match(sequence):
                logger.debug(u'Pattern matched the sequence %r' % sequence)
                self.event_queue.put(ClapperEvent())
                sequence.clear()
        # Close
        stream.close()
        pa.terminate()


    def get_rms(self, data_block):
        """Get the Root Mean Square of the block"""
        count = len(data_block) / 2
        shorts = struct.unpack('%dh' % count, data_block)
        # iterate over the block to compute the sum of squares
        sum_squares = 0.0
        for sample in shorts:
            # sample is a signed short in +/- 32768, normalize it to +/- 1.0
            n = float(sample) / 32768
            sum_squares += n * n
        return math.sqrt(sum_squares / count)
