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
from ..ui.action_ui import Ui_ActionDialog


class ActionForm(QDialog, Ui_ActionDialog):
    def __init__(self, parent=None):
        super(ActionForm, self).__init__(parent)
        self.setupUi(self)
        self.qpbTest = self.buttonBox.addButton('&Test', QDialogButtonBox.ActionRole)
        self.qpbTest.clicked.connect(self.test)
        self.action = None

    def setActionForm(self, widget):
        self.qwAction = widget
        self.verticalLayout.insertWidget(1, self.qwAction)

    def fillAction(self, action):
        action.name = self.qleName.text()
        action.tts = self.qpteTTS.toPlainText()

    def fromAction(self, action):
        self.action = action
        self.qleName.setText(action.name)
        self.qpteTTS.setPlainText(action.tts)

    @Slot()
    def test(self):
        action = self.getAction()
        try:
            QMessageBox.information(self, 'Test successful', action.format_tts())
        except Exception as e:
            QMessageBox.warning(self, 'Test failed', 'Error message: %s' % e)
