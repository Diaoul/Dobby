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
from ..timers import DelayedExecutionTimer
from ..ui.action_weather_ui import Ui_ActionWeatherForm
from . import ActionForm
from dobby.models.actions.weather import Weather
from PySide.QtCore import *
from PySide.QtGui import *
import pywunderground


class ActionWeatherWidget(QWidget, Ui_ActionWeatherForm):
    def __init__(self, parent=None):
        super(ActionWeatherWidget, self).__init__(parent)
        self.setupUi(self)
        
        # City Completer
        self.completer = WeatherCityCompleter(self.qleCity)
        self.qleCity.setCompleter(self.completer)
        
        # Signals
        self.delay = DelayedExecutionTimer()
        self.qleCity.textEdited.connect(self.delay.trigger)
        self.delay.delayed.connect(self.completer.update)


class ActionWeatherForm(ActionForm):
    def __init__(self, parent=None):
        super(ActionWeatherForm, self).__init__(parent)
        self.setActionForm(ActionWeatherWidget())

    def getAction(self):
        if not self.action:
            self.action = Weather()
        super(ActionWeatherForm, self).fillAction(self.action)
        cities = [city for city in self.qwAction.completer.cities if city['name'] == self.qwAction.qleCity.text()]
        if cities:
            self.action.city_name = cities[0]['name']
            self.action.query = cities[0]['l'].replace('/q/', '')
        return self.action

    def fromAction(self, action):
        super(ActionWeatherForm, self).fromAction(action)
        self.qwAction.qleCity.setText(action.city_name)


class WeatherCityCompleter(QCompleter):
    def __init__(self, parent=None):
        super(WeatherCityCompleter, self).__init__(parent)
        self.cities = []
        self.setModel(QStringListModel())
        self.setCaseSensitivity(Qt.CaseInsensitive)

    @Slot(str)
    def update(self, query):
        if len(query) < 3:
            return
        self.cities = pywunderground.autocomplete(query)
        self.model().setStringList([city['name'] for city in self.cities])
        self.complete()
