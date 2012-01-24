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
from ..ui.action_weather_ui import Ui_ActionWeatherDialog
from PySide.QtCore import *
from PySide.QtGui import *
from dobby.models.actions.weather import Weather
import pywunderground


class ActionWeatherForm(QDialog, Ui_ActionWeatherDialog):
    def __init__(self, parent=None):
        super(ActionWeatherForm, self).__init__(parent)
        self.setModal(True)
        self.setupUi(self)
        
        # City Completer
        self.completer = WeatherCityCompleter(self.qleCity)
        self.qleCity.setCompleter(self.completer)
        
        # Signals
        self.delay = DelayedExecutionTimer()
        self.qleCity.textEdited.connect(self.delay.trigger)
        self.delay.delayed.connect(self.completer.update)

    def setupCompleter(self):
        completer = QCompleter(self)
        self.qleCity.setCompleter(completer)

    def getAction(self):
        cities = [city for city in self.completer.cities if city['name'] == self.qleCity.text()]
        print repr(self.completer.cities)
        print repr(cities)
        return Weather(name=self.qleName.text(), tts=self.qpteTTS.toPlainText(), query=cities[0]['l'].replace('/q/', ''))

    def accept(self):
        if self.qleCity.text() not in [city['name'] for city in self.completer.cities]:
            QMessageBox.information(self, 'Invalid city', 'The city you entered is invalid, please correct it or cancel', QMessageBox.Ok)
            return
        super(ActionWeatherForm, self).accept()


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
