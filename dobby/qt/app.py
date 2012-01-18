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
from ..app import Application as Dobby
from PySide import QtGui, QtCore
from ui.mainui import Ui_MainWindow
import locale
import logging
import os.path
import time


logger = logging.getLogger(__name__)


class Application(QtGui.QApplication):
    def initTranslators(self):
        loc = locale.getdefaultlocale()[0]
        translator = QtCore.QTranslator()
        print translator.load(os.path.join('ts', loc))
        print translator.load('qt_' + loc, QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
        self.installTranslator(translator)


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.dobby = DobbyApplication()
        self.connectActions()
 
    def connectActions(self):
        self.actionStart.triggered.connect(self.dobby.start)
        self.actionStop.triggered.connect(self.dobby.stop)
        self.actionQuit.triggered.connect(self.quit)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?",
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.hide()
            self.quit()
            event.accept()
        else:
            event.ignore()

    def quit(self):
        self.dobby.stop()
        QtGui.qApp.quit

class DobbyApplication(QtCore.QThread):
    def __init__(self, parent=None):
        super(DobbyApplication, self).__init__(parent)
        self.dobby = Dobby(os.path.abspath('data'), quiet=True, verbose=False, use_signal=False)
        self._stop = False

    def stop(self):
        self.dobby.stop()
        self._stop = True

    def run(self):
        self.dobby.start()
        while not self._stop:
            time.sleep(1)
