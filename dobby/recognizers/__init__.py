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


class Recognizer(threading.Thread):
    """Threaded Recognizer base class. A queue can be subscribed to the Recognizer and
    hence, receive recognized :class:`pyjulius.Sentence` objects

    .. attribute:: subscribers

        List of subscribers

    """
    def __init__(self):
        super(Recognizer, self).__init__()
        self.subscribers = []
        self._stop = False

    def stop(self):
        """Stop the thread"""
        self._stop = True

    def subscribe(self, subscriber):
        """Add a queue to the Recognizer's subscribers list. A subscriber will receive
        :meth:`published <dobby.recognizers.Recognizer.publish>` :class:`pyjulius.Sentence` objects

        :param Queue.Queue subscriber: subscriber to append

        """
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        """Remove a queue from the subscribers list

        :param Queue.Queue subscriber: subscriber to remove

        """
        self.subscribers.remove(subscriber)

    def publish(self, sentence):
        """Publish a recognized sentence to all subscribers

        :param pyjulius.Sentence sentence: the recognized sentence
        
        .. note::
        
            The type of the `sentence` parameter may change in the near future when a new :class:`Recognizer` will be added

        """
        for subscriber in self.subscribers:
            subscriber.put(sentence)
