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
import threading


class Trigger(threading.Thread):
    """Threaded Trigger base class. A trigger will :meth:`raise <raise_event>` a :class:`~dobby.triggers.RecognitionEvent` or an :class:`~dobby.triggers.ActionEvent`
    when the detection is successful

    :param Queue.Queue event_queue: queue where to put the events
    
    """
    def __init__(self, event_queue):
        super(Trigger, self).__init__()
        self._stop = False
        self.event_queue = event_queue

    def stop(self):
        """Stop the thread"""
        self._stop = True

    def raise_event(self, event):
        """Raise an event in the :attr:`event_queue`"""
        self.queue.put(event)


class RecognitionEvent(object):
    """A RecognitionEvent indicates that the recognition can be launched to
    analyze the next sentence

    """
    pass


class ActionEvent(object):
    """An ActionEvent indicates that this is not necessary to launch the recognition
    and provides the recognized sentence

    :param string sentence: the recognized sentence

    """
    def __init__(self, sentence):
        self.sentence = sentence
