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
from xml.etree.ElementTree import XML
import re
import socket


CONNECTED, DISCONNECTED = range(2)


class Client(object):
    def __init__(self, host='localhost', port=10500, encoding='utf-8'):
        self.host = host
        self.port = port
        self.encoding = encoding
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.state = DISCONNECTED
    
    def connect(self):
        self.sock.connect((self.host, self.port))
        self.state = CONNECTED

    def disconnect(self):
        self.sock.shutdown()
        self.sock.close()
        self.state = DISCONNECTED

    def send(self, data):
        self.sock.send(data)

    def _readline(self):
        line = ''
        data = self.sock.recv(1)
        while data != '\n':
            line += unicode(data, self.encoding)
            data = self.sock.recv(1)
        return line

    def _readblock(self):
        block = ''
        line = self._readline()
        while line != '.':
            block += line
            line = self._readline()
        return block

    def _readxml(self):
        block = re.sub(r'<(/?)s>', r'&lt;\1s&gt;', self._readblock())
        return XML(block)

    def empty(self):
        self.sock.setblocking(False)
        while 1:
            try:
                self.sock.recv(4096)
            except socket.error:
                break
        self.sock.setblocking(True)

    def etree(self, tag):
        xml = self._readxml()
        while xml.tag != tag:
            xml = self._readxml()
        return xml

    def recognize(self):
        xml = self.etree('RECOGOUT')
        shypo = xml.find('SHYPO')
        return Sentence.from_shypo(shypo, self.encoding)


class Sentence(object):
    def __init__(self, words, score=None):
        self.words = words
        self.score = score or 0

    @classmethod
    def from_shypo(cls, xml, encoding='utf-8'):
        score = float(xml.get('SCORE'))
        words = [Word.from_whypo(w_xml, encoding) for w_xml in xml.findall('WHYPO') if w_xml.get('WORD') not in ['<s>', '</s>']]
        return cls(words, score)

    def __repr__(self):
        return "<Sentence('%f', '%r')>" % (self.score, self.words)

    def __unicode__(self):
        return u' '.join([unicode(w) for w in self.words])


class Word(object):
    def __init__(self, word, confidence=None):
        self.word = word
        self.confidence = confidence or 0.0

    @classmethod
    def from_whypo(cls, xml, encoding='utf-8'):
        word = unicode(xml.get('WORD'), encoding)
        confidence = float(xml.get('CM'))
        return cls(word, confidence)

    def __repr__(self):
        return "<Word('%f','%s')>" % (self.confidence, self.word)

    def __unicode__(self):
        return self.word.lower()
        

if __name__ == '__main__':
    c = Client()
    c.connect()
    while 1:
        print str(c.recognize())
