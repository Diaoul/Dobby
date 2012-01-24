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
from PySide.QtCore import *
from PySide.QtGui import *


class DelayedExecutionTimer(QObject):
    delayed = Signal(str)

    def __init__(self, min_delay=250, max_delay=1000, parent=None):
        super(DelayedExecutionTimer, self).__init__(parent)
        self.minTimer = QTimer(self)
        self.minTimer.setInterval(min_delay)
        self.minTimer.timeout.connect(self.delay)
        self.maxTimer = QTimer(self)
        self.maxTimer.setInterval(max_delay)
        self.maxTimer.timeout.connect(self.delay)
        self.lastString = ''

    @Slot(str)
    def trigger(self, string):
        self.lastString = string
        if not self.maxTimer.isActive():
            self.maxTimer.start()
        self.minTimer.stop()
        self.minTimer.start()

    @Slot()
    def delay(self):
        self.minTimer.stop()
        self.maxTimer.stop()
        self.delayed.emit(self.lastString)
