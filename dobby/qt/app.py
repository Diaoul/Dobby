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
from PySide.QtCore import *
from PySide.QtGui import *
from dobby.models.actions.datetime import Datetime
from dobby.models.actions.feed import Feed
from dobby.models.actions.weather import Weather
from dobby.qt.dialogs.configure import ConfigForm
from dobby.qt.dialogs.datetime import ActionDatetimeForm
from dobby.qt.dialogs.feed import ActionFeedForm
from dobby.qt.dialogs.weather import ActionWeatherForm
from dobby.qt.models import ScenarioModel, ScenarioCommandModel, \
    ScenarioActionModel, ActionModel
from ui.main_ui import Ui_MainWindow
import dobby.infos
import os.path
import pyjulius.exceptions
import time


class Application(QApplication):
    def __init__(self, args):
        super(Application, self).__init__(args)
        locale = QLocale.system().name()
        translator = QTranslator()
        translator.load(os.path.join('ts', locale))
        translator.load('qt_' + locale, QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        self.installTranslator(translator)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.dobby = DobbyApplication()
        self.session = self.dobby.dobby.Session()
        self.qaStop.setVisible(False)

        # Scenario Models
        self.scenarioModel = ScenarioModel(self.session)
        self.qlvScenarios.setModel(self.scenarioModel)
        self.scenarioCommandModel = ScenarioCommandModel(self.session)
        self.qlvScenarioCommands.setModel(self.scenarioCommandModel)
        self.scenarioActionModel = ScenarioActionModel(self.session)
        self.qlvScenarioActions.setModel(self.scenarioActionModel)

        # Action Model
        self.actionModel = ActionModel(self.session)
        self.qlvActions.setModel(self.actionModel)

        # Scenario Signals
        self.qpbScenarioAdd.clicked.connect(self.addScenario)
        self.qpbScenarioRemove.clicked.connect(self.removeScenario)
        self.qpbScenarioCommandAdd.clicked.connect(self.addScenarioCommand)
        self.qpbScenarioCommandRemove.clicked.connect(self.removeScenarioCommand)
        self.qlvScenarios.selectionModel().selectionChanged.connect(self.changeScenario)
        self.qlvScenarioActions.doubleClicked.connect(self.removeScenarioAction)

        # Action Signals
        self.qpbActionAdd.clicked.connect(self.addAction)
        self.qpbActionRemove.clicked.connect(self.removeAction)
        self.qlvActions.doubleClicked.connect(self.editAction)

        # Dobby Signals
        self.qaStart.triggered.connect(self.startDobby)
        self.qaStop.triggered.connect(self.stopDobby)
        
        # Config Signals
        self.qaConfigure.triggered.connect(self.configure)
        
        # Others
        self.qaAbout.triggered.connect(self.about)

    @Slot()
    def about(self):
        QMessageBox.about(self, 'About Dobby', 'Dobby v' + dobby.infos.__version__ + '\n\n' + 'Dobby is free! (GPLv3 licensed software)')

    @Slot(QModelIndex, QModelIndex)
    def changeScenario(self, selected, deselected):
        self.scenarioCommandModel.setCommands(self.scenarioModel.scenarios[selected.indexes()[0].row()].commands)
        self.scenarioActionModel.setActions(self.scenarioModel.scenarios[selected.indexes()[0].row()].actions)

    @Slot()
    def addScenario(self):
        text = self.qleScenario.text()
        if not text:
            return 
        self.scenarioModel.addScenario(text)
        self.qleScenario.clear()

    @Slot()
    def removeScenario(self):
        self.scenarioModel.removeScenarios(self.qlvScenarios.currentIndex().row())

    @Slot()
    def addScenarioCommand(self):
        text = self.qleScenarioCommand.text()
        if not text:
            return
        self.scenarioCommandModel.addNewCommand(text)
        self.qleScenarioCommand.clear()

    @Slot()
    def removeScenarioCommand(self):
        self.scenarioCommandModel.removeCommands(self.qlvScenarioCommands.currentIndex().row())

    @Slot()
    def removeScenarioAction(self):
        self.scenarioActionModel.removeActions(self.qlvScenarioActions.currentIndex().row())

    @Slot()
    def addAction(self):
        if self.qcbActionType.currentText() == 'Weather':
            dialog = ActionWeatherForm(self)
        elif self.qcbActionType.currentText() == 'Datetime':
            dialog = ActionDatetimeForm(self)
        elif self.qcbActionType.currentText() == 'Feed':
            dialog = ActionFeedForm(self)
        result = dialog.exec_()
        if result != QDialog.Accepted:
            return
        self.actionModel.appendAction(dialog.getAction())

    @Slot()
    def removeAction(self):
        self.actionModel.removeActions(self.qlvActions.currentIndex().row())

    @Slot(QModelIndex)
    def editAction(self, index):
        action = self.actionModel.actions[index.row()]
        if isinstance(action, Weather):
            dialog = ActionWeatherForm(self)
        elif isinstance(action, Datetime):
            dialog = ActionDatetimeForm(self)
        elif isinstance(action, Feed):
            dialog = ActionFeedForm(self)
        dialog.fromAction(self.actionModel.actions[index.row()])
        result = dialog.exec_()
        if result != QDialog.Accepted:
            return
        self.session.add(dialog.getAction())
        self.session.commit()

    @Slot()
    def configure(self):
        dialog = ConfigForm(self.dobby.dobby.config, self)
        result = dialog.exec_()
        if result != QDialog.Accepted:
            return

    def startDobby(self):
        try:
            self.dobby.start()
        #TODO: Check for the recognizer in dobby before 'run'
        except pyjulius.exceptions.ConnectionError:
            QMessageBox.question(self, 'Error', 'Did you start the recognizer?', QMessageBox.Ok)
        except:
            raise
        self.qaStart.setVisible(False)
        self.qaStop.setVisible(True)
 
    def stopDobby(self):
        self.dobby.stop()
        self.qaStop.setVisible(False)
        self.qaStart.setVisible(True)

    def closeEvent(self, event):
        #FIXME
        self.hide()
        self.quit()
        event.accept()
        return
        reply = QMessageBox.question(self, 'Message', 'Are you sure to quit?',
                                           QMessageBox.Yes | QMessageBox.No,
                                           QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.hide()
            self.quit()
            event.accept()
        else:
            event.ignore()

    def quit(self):
        self.stopDobby()
        qApp.quit


class DobbyApplication(QThread):
    #TODO: Make a real application instead of using Dobby like this... /!\ http://labs.qt.nokia.com/2010/06/17/youre-doing-it-wrong/
    #TODO: Inherit Dobby as well as QThread instead of encapsulate the Dobby (poor Dobby...)
    #TODO: Choose between the two options above.
    def __init__(self, parent=None):
        super(DobbyApplication, self).__init__(parent)
        self.dobby = Dobby(os.path.abspath('data'), quiet=False, verbose=False, use_signal=False)
        self.dobby.validate_config()
        self.running = False

    def stop(self):
        if not self.running:
            return
        self.dobby.stop()
        self.running = False
        self.wait()

    def run(self):
        self.running = True
        self.dobby.start()
        while self.running:
            time.sleep(1)
