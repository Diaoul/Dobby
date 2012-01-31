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
from . import ActionForm
from ..ui.action_feed_ui import Ui_ActionFeedForm
from PySide.QtCore import *
from PySide.QtGui import *
from dobby.models.actions.feed import Feed


class ActionFeedWidget(QWidget, Ui_ActionFeedForm):
    def __init__(self, parent=None):
        super(ActionFeedWidget, self).__init__(parent)
        self.setupUi(self)


class ActionFeedForm(ActionForm):
    def __init__(self, parent=None):
        super(ActionFeedForm, self).__init__(parent)
        self.setActionForm(ActionFeedWidget())

    def getAction(self):
        if not self.action:
            self.action = Feed()
        super(ActionFeedForm, self).fillAction(self.action)
        self.action.url = self.qwAction.qleURL.text()
        return self.action

    def fromAction(self, action):
        super(ActionFeedForm, self).fromAction(action)
        self.qwAction.qleURL.setText(action.url)
