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
from ..ui.config_ui import Ui_ConfigDialog
from PySide.QtCore import *
from PySide.QtGui import *
from dobby.config import validator


class ConfigForm(QDialog, Ui_ConfigDialog):
    def __init__(self, config, parent=None):
        super(ConfigForm, self).__init__(parent)
        self.setModal(True)
        self.setupUi(self)
        self.config = config
        self.load()

    def load(self):
        # General
        self.qleGeneralWelcomeMessage.setText(self.config['General']['welcome_message'])
        self.qleGeneralByeMessage.setText(self.config['General']['bye_message'])
        self.qleGeneralFailedMessage.setText(self.config['General']['failed_message'])
        self.qleGeneralConfirmationMessage.setText(self.config['General']['confirmation_message'])
        self.qsbGeneralRecognitionTimeout.setValue(self.config['General']['recognition_timeout'])
        
        # Speakers
        speakers = ['speechdispatcher']
        self.qcbSpeaker.setCurrentIndex(speakers.index(self.config['Speaker']['speaker']))
        self.qleSpeakerSpeechDispatcherEngine.setText(self.config['Speaker']['SpeechDispatcher']['engine'])
        self.qleSpeakerSpeechDispatcherVoice.setText(self.config['Speaker']['SpeechDispatcher']['voice'])
        self.qleSpeakerSpeechDispatcherLanguage.setText(self.config['Speaker']['SpeechDispatcher']['language'])
        self.qsbSpeakerSpeechDispatcherVolume.setValue(self.config['Speaker']['SpeechDispatcher']['volume'])
        self.qsbSpeakerSpeechDispatcherRate.setValue(self.config['Speaker']['SpeechDispatcher']['rate'])
        self.qsbSpeakerSpeechDispatcherPitch.setValue(self.config['Speaker']['SpeechDispatcher']['pitch'])
        
        # Recognizers
        recognizers = ['julius']
        self.qcbRecognizer.setCurrentIndex(recognizers.index(self.config['Recognizer']['recognizer']))
        self.qleRecognizerJuliusHost.setText(self.config['Recognizer']['Julius']['host'])
        self.qleRecognizerJuliusPort.setText(unicode(self.config['Recognizer']['Julius']['port']))
        self.qleRecognizerJuliusEncoding.setText(self.config['Recognizer']['Julius']['encoding'])
        self.qsbRecognizerJuliusMinimumScore.setValue(self.config['Recognizer']['Julius']['min_score'])
        
        # Triggers
        if 'clapper' in self.config['Trigger']['triggers']:
            self.qcbTriggerClapperEnabled.setChecked(True)
        
        if 'julius' in self.config['Trigger']['triggers']:
            self.qcbTriggerJuliusEnabled.setChecked(True)
        self.qleTriggerClapperDeviceIndex.setText(unicode(self.config['Trigger']['Clapper']['device_index']))
        self.qdsbTriggerClapperBlockTime.setValue(self.config['Trigger']['Clapper']['block_time'])
        self.qleTriggerJuliusSentence.setText(self.config['Trigger']['Julius']['sentence'])
        self.qcbTriggerJuliusAction.setChecked(self.config['Trigger']['Julius']['action'])

    def save(self):
        # General
        self.config['General']['welcome_message'] = self.qleGeneralWelcomeMessage.text()
        self.config['General']['bye_message'] = self.qleGeneralByeMessage.text()
        self.config['General']['failed_message'] = self.qleGeneralFailedMessage.text()
        self.config['General']['confirmation_message'] = self.qleGeneralConfirmationMessage.text()
        self.config['General']['recognition_timeout'] = self.qsbGeneralRecognitionTimeout.value()
        
        # Speakers
        speakers = ['speechdispatcher']
        self.config['Speaker']['speaker'] = speakers[self.qcbSpeaker.currentIndex()]
        self.config['Speaker']['SpeechDispatcher']['engine'] = self.qleSpeakerSpeechDispatcherEngine.text()
        self.config['Speaker']['SpeechDispatcher']['voice'] = self.qleSpeakerSpeechDispatcherVoice.text()
        self.config['Speaker']['SpeechDispatcher']['language'] = self.qleSpeakerSpeechDispatcherLanguage.text()
        self.config['Speaker']['SpeechDispatcher']['volume'] = self.qsbSpeakerSpeechDispatcherVolume.value()
        self.config['Speaker']['SpeechDispatcher']['rate'] = self.qsbSpeakerSpeechDispatcherRate.value()
        self.config['Speaker']['SpeechDispatcher']['pitch'] = self.qsbSpeakerSpeechDispatcherPitch.value()
        
        # Recognizers
        recognizers = ['julius']
        self.config['Recognizer']['recognizer'] = recognizers[self.qcbRecognizer.currentIndex()]
        self.config['Recognizer']['Julius']['host'] = self.qleRecognizerJuliusHost.text()
        self.config['Recognizer']['Julius']['port'] = self.qleRecognizerJuliusPort.text()
        self.config['Recognizer']['Julius']['encoding'] = self.qleRecognizerJuliusEncoding.text()
        self.config['Recognizer']['Julius']['min_score'] = self.qsbRecognizerJuliusMinimumScore.value()
        
        # Triggers
        self.config['Trigger']['triggers'] = []
        if self.qcbTriggerClapperEnabled.isChecked():
            self.config['Trigger']['triggers'].append('clapper')
        if self.qcbTriggerJuliusEnabled.isChecked():
            self.config['Trigger']['triggers'].append('julius')
        self.config['Trigger']['Clapper']['device_index'] = self.qleTriggerClapperDeviceIndex.text()
        self.config['Trigger']['Clapper']['block_time'] = self.qdsbTriggerClapperBlockTime.value()
        self.config['Trigger']['Julius']['sentence'] = self.qleTriggerJuliusSentence.text()
        self.config['Trigger']['Julius']['action'] = self.qcbTriggerJuliusAction.isChecked()
        
        
    def accept(self):
        self.save()
        if not self.config.validate(validator):
            QMessageBox.warning(self, 'Validation failed', 'The configuration entered is not valid, please check values and retry', QMessageBox.Ok, QMessageBox.Ok)
            return
        self.config.write()
        super(ConfigForm, self).accept()
