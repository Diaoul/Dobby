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
import abc
import threading


class Recognizer(threading.Thread):
    def __init__(self):
        super(Recognizer, self).__init__()
        self.queues = []
        self._stop = False

    def stop(self):
        self._stop = True

    def subscribe(self, queue):
        self.queues.append(queue)

    def unsubscribe(self, queue):
        self.queues.remove(queue)