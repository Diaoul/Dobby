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
from ..ui.action_feed_ui import Ui_ActionFeedDialog
from PySide.QtCore import *
from PySide.QtGui import *
from dobby.models.actions.feed import Feed
import feedparser


class ActionFeedForm(QDialog, Ui_ActionFeedDialog):
    def __init__(self, parent=None):
        super(ActionFeedForm, self).__init__(parent)
        self.setModal(True)
        self.setupUi(self)
        self.action = None

    def getAction(self):
        if not self.action:
            self.action = Feed()
        self.action.name = self.qleName.text()
        self.action.tts = self.qpteTTS.toPlainText()
        self.action.url = self.qleURL.text()
        return self.action

    def fromAction(self, action):
        self.action = action
        self.qleName.setText(action.name)
        self.qpteTTS.setPlainText(action.tts)
        self.qleURL.setText(action.url)

    def accept(self):
        feed = feedparser.parse(self.qleURL.text())
        if not feed['entries']:
            QMessageBox.information(self, 'Invalid feed', 'The feed entered is invalid, please correct it or cancel', QMessageBox.Ok)
            return
        super(ActionFeedForm, self).accept()
