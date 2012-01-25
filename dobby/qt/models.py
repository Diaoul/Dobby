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
from dobby.models.actions import Action
from dobby.models.command import Command
from dobby.models.scenario import Scenario
from sqlalchemy.orm import joinedload
import pickle


class ScenarioModel(QAbstractListModel):
    def __init__(self, session, parent=None):
        super(ScenarioModel, self).__init__(parent)
        self.session = session
        self.scenarios = session.query(Scenario).options(joinedload('associations.action'), joinedload('commands')).all()

    def rowCount(self, parent=QModelIndex()):
        return len(self.scenarios)

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        scenario = self.scenarios[index.row()]
        if not scenario:
            return None
        if role == Qt.DisplayRole:
            return scenario.name
        return None

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole or not value:
            return False
        scenario = self.scenarios[index.row()]
        scenario.name = value
        self.session.commit()
        self.dataChanged.emit(index, index)
        return True

    def addScenario(self, name):
        self.beginInsertRows(QModelIndex(), len(self.scenarios), len(self.scenarios))
        scenario = Scenario(name=name)
        self.session.add(scenario)
        self.session.commit()
        self.scenarios.append(scenario)
        self.endInsertRows()

    def removeScenario(self, index):
        self.beginRemoveRows(QModelIndex(), index, index)
        scenario = self.scenarios.pop(index)
        self.session.delete(scenario)
        self.session.commit()
        self.endRemoveRows()


class ScenarioCommandModel(QAbstractListModel):
    def __init__(self, session, parent=None):
        super(ScenarioCommandModel, self).__init__(parent)
        self.session = session
        self.commands = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.commands)

    def data(self, index, role=Qt.DisplayRole):
        command = self.commands[index.row()]
        if not command:
            return None
        if role == Qt.DisplayRole:
            return command.text
        return None

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole or not value:
            return False
        command = self.commands[index.row()]
        command.text = value
        self.session.commit()
        self.dataChanged.emit(index, index)
        return True

    def addCommand(self, text):
        self.beginInsertRows(QModelIndex(), len(self.commands), len(self.commands))
        self.commands.append(Command(text=text))
        self.session.commit()
        self.endInsertRows()

    def removeCommand(self, index):
        self.beginRemoveRows(QModelIndex(), index, index)
        command = self.commands.pop(index)
        self.session.delete(command)
        self.session.commit()
        self.endRemoveRows()

    def setCommands(self, commands):
        self.beginResetModel()
        self.commands = commands
        self.endResetModel()


class ScenarioActionModel(QAbstractListModel):
    def __init__(self, session, parent=None):
        super(ScenarioActionModel, self).__init__(parent)
        self.session = session
        self.actions = {}

    def rowCount(self, parent=QModelIndex()):
        return len(self.actions)

    def dropMimeData(self, data, action, row, column, parent):
        action_ids = pickle.loads(data.data('application/x-action-id'))
        for action_id in action_ids:
            self.addAction(self.session.query(Action).get(action_id))
        return True

    def mimeTypes(self):
        return ['application/x-action-id']

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled

    def data(self, index, role=Qt.DisplayRole):
        action = self.actions[sorted(self.actions.keys())[index.row()]]
        if not action:
            return None
        if role == Qt.DisplayRole:
            return action.name
        if role == Qt.DecorationRole:
            return QIcon(':/actions/%s' % action.discriminator)
        return None

    def setActions(self, actions):
        self.beginResetModel()
        self.actions = actions
        self.endResetModel()

    def addAction(self, action):
        self.beginInsertRows(QModelIndex(), len(self.actions), len(self.actions))
        if self.actions:
            order = max(self.actions.keys()) + 1
        else:
            order = 1
        self.actions[order] = action
        self.session.commit()
        self.endInsertRows()

    def removeAction(self, index):
        self.beginRemoveRows(QModelIndex(), index, index)
        del self.actions[sorted(self.actions.keys())[index]]
        self.session.commit()
        self.endRemoveRows()


class ActionModel(QAbstractListModel):
    def __init__(self, session, parent=None):
        super(ActionModel, self).__init__(parent)
        self.session = session
        self.actions = self.session.query(Action).all()

    def rowCount(self, parent=QModelIndex()):
        return len(self.actions)

    def data(self, index, role=Qt.DisplayRole):
        action = self.actions[index.row()]
        if not action:
            return None
        if role == Qt.DisplayRole:
            return action.name
        if role == Qt.DecorationRole:
            return QIcon(':/actions/%s' % action.discriminator)
        return None

    def mimeData(self, indexes):
        mimedata = QMimeData()
        mimedata.setData('application/x-action-id', pickle.dumps([self.actions[index.row()].id for index in indexes]))
        return mimedata

    def mimeTypes(self):
        return ['application/x-action-id']

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled

    def addAction(self, action):
        self.beginInsertRows(QModelIndex(), len(self.actions), len(self.actions))
        self.session.add(action)
        self.session.commit()
        self.actions.append(action)
        self.endInsertRows()

    def removeAction(self, index):
        self.beginRemoveRows(QModelIndex(), index, index)
        action = self.actions.pop(index)
        self.session.delete(action)
        self.session.commit()
        self.endRemoveRows()
