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

    def addNewScenario(self, name):
        """Add a new scenario

        :param string name: name of the scenario

        """
        self.beginInsertRows(QModelIndex(), len(self.scenarios), len(self.scenarios))
        scenario = Scenario(name=name)
        self.session.add(scenario)
        self.session.commit()
        self.scenarios.append(scenario)
        self.endInsertRows()

    def removeScenarios(self, row, count=1):
        """Remove scenarios

        :param int row: first row to remove
        :param int count: number of rows to remove

        """
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        for i in range(row + count - 1, row - 1, -1):
            self.session.delete(self.scenarios.pop(i))
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

    def addNewCommand(self, text):
        """Add a new command to the scenario

        :param string text: text of the command

        """
        self.beginInsertRows(QModelIndex(), len(self.commands), len(self.commands))
        self.commands.append(Command(text=text))
        self.session.commit()
        self.endInsertRows()

    def removeCommands(self, row, count=1):
        """Remove scenario's commands

        :param int row: first row to remove
        :param int count: number of rows to remove

        """
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        for i in range(row + count - 1, row - 1, -1):
            self.commands.pop(i)
        self.session.commit()
        self.endRemoveRows()

    def setCommands(self, commands):
        """Resets the model with new commands"""
        self.beginResetModel()
        self.commands = commands
        self.endResetModel()


class ScenarioActionModel(QAbstractListModel):
    def __init__(self, session, parent=None):
        super(ScenarioActionModel, self).__init__(parent)
        self.session = session
        self.actions = {}

    def rowCount(self, parent=QModelIndex()):
        """Number of actions associated with a scenario"""
        return len(self.actions)

    def dropMimeData(self, data, action, row, column, parent):
        """Copy an action from the ActionModel or move an action from itself to another index"""
        if action == Qt.DropAction.CopyAction:
            action_ids = pickle.loads(data.data('application/x-action-id'))
            for action_id in action_ids:
                self.insertAction(self.session.query(Action).get(action_id), row if row != -1 else len(self.actions))
        elif action == Qt.DropAction.MoveAction:
            if row == -1:
                return False
            rows = pickle.loads(data.data('application/x-scenarioaction-rows'))
            self.moveActions(min(rows), max(rows), row)
        return True

    def supportedDropActions(self):
        """Allow Copy and Move drop actions"""
        return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

    def mimeTypes(self):
        return ['application/x-action-id', 'application/x-scenarioaction-rows']

    def mimeData(self, indexes):
        """Serialize the indexes to move in a special mimetype that is used when dragging occurs"""
        mimedata = QMimeData()
        mimedata.setData('application/x-scenarioaction-rows', pickle.dumps([index.row() for index in indexes]))
        return mimedata

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

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
        """Resets the model with new actions"""
        self.beginResetModel()
        self.actions = actions
        self.endResetModel()

    def insertAction(self, action, index):
        """Insert an action to the specified index"""
        self.beginInsertRows(QModelIndex(), index, index)
        orders = self.actions.keys()
        actions = self.actions.values()
        orders.insert(index, None)
        actions.insert(index, action)
        for i in range(len(orders)):
            self.actions[i] = actions[i]
        self.session.commit()
        self.endInsertRows()

    def moveActions(self, sourceFirst, sourceLast, destinationRow):
        """Move actions

        :param int sourceFirst: first row to move
        :param int sourceLast: last row to move
        :param int destinationRow: destination row

        """
        self.beginMoveRows(QModelIndex(), sourceFirst, sourceLast, QModelIndex(), destinationRow)
        actions = self.actions.values()
        for i in range(sourceLast, sourceFirst - 1, -1):
            actions.insert(destinationRow - (1 if i < destinationRow else 0), actions.pop(i))
        self.actions.clear()
        for i in range(len(actions)):
            self.actions[i] = actions[i]
        self.session.commit()
        self.endMoveRows()

    def removeActions(self, row, count=1):
        """Remove scenario's actions

        :param int row: first row to remove
        :param int count: number of rows to remove

        """
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        for i in range(row, row + count):
            del self.actions[self.actions.keys()[i]]
        self.session.commit()
        self.endRemoveRows()


class ActionModel(QAbstractListModel):
    """Action model that supports dragging. This is a proxy to the Action model"""

    def __init__(self, session, parent=None):
        super(ActionModel, self).__init__(parent)
        self.session = session
        self.actions = self.session.query(Action).all()

    def rowCount(self, parent=QModelIndex()):
        return len(self.actions)

    def data(self, index, role=Qt.DisplayRole):
        action = self.actions[index.row()]
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

    def appendAction(self, action):
        """Append an action

        :param Action action: action to append

        """
        self.insertActions([action], self.rowCount())

    def insertActions(self, actions, row=0):
        """Insert actions
        
        :param list actions: actions to insert
        :param int row: row before which actions will be inserted

        """
        self.beginInsertRows(QModelIndex(), row, row + len(actions) - 1)
        for action in reversed(actions):
            self.actions.insert(row, action)
            self.session.add(action)
        self.session.commit()
        self.endInsertRows()

    def removeActions(self, row, count=1):
        """Remove actions

        :param int row: first row to remove
        :param int count: number of rows to remove

        """
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        for i in range(row + count - 1, row - 1, -1):
            self.session.delete(self.actions.pop(i))
        self.session.commit()
        self.endRemoveRows()
