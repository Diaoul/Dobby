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
from models.actions import Action
from models.sentence import Sentence
from triggers.clapper import Pattern, QuietPattern, NoisyPattern, Clapper
import threading


def initTriggers(queue, config):
    triggers = []
    for trigger_name in config['triggers']:
        if trigger_name == 'clapper':
            p = Pattern([QuietPattern(1), NoisyPattern(1, 4), QuietPattern(1, 6), NoisyPattern(1, 4), QuietPattern(1)])
            t = Clapper(event_queue=queue, pattern=p, device_index=config['Clapper']['device_index'], block_time=config['Clapper']['block_time'])
            t.start()
            triggers.append(t)


class Dobby(threading.Thread):
    def __init__(self, event_queue, session):
        super(Dobby, self).__init__()
        self.event_queue = event_queue
        self.session = session
        
    def run(self):
        while 1:
            event = self.event_queue.get()
            #TODO: Sentence <-> Actions relation
            actions = self.session.query(Action).with_polymorphic('*').filter(Sentence.id == 1)