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
#from . import Recognizer
import select
import socket
import sys

def get_sentence(reco_out):
    words_scores = []
    words = []
    scores = []
    
    index_start = reco_out.find("<RECOGOUT>")
    index_end = reco_out.find("</RECOGOUT>") + 11
    
    reco_lines = reco_out[index_start:index_end].splitlines()
    
    for i in range(3, len(reco_lines) - 3):
        index_word = reco_lines[i].find("WORD=")
        index_class = reco_lines[i].find("CLASSID=")
        index_cm = reco_lines[i].find("CM=")
        
        word = reco_lines[i][index_word + 6:index_class - 2]
        score = reco_lines[i][index_cm + 4:index_cm + 9]
    words.append(word)
    scores.append(score)
    
    for i in range(len(words)):
        s = []
        s.append(words[i])
        s.append(scores[i])
    words_scores.append(s)

    return words_scores

class JuliusRecognizer(object):
    def __init__(self, host, port, max_sentences, timeout):
        #super(JuliusRecognizer, self).__init__(max_sentences, timeout)
        self.host = host
        self.port = port

    def recognize(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))
        inputready, _, __ = select.select([client_socket], [], [])
        keep = True
        reco_out = ""
        while 1:
            for i in inputready:
                if i == sys.stdin:
                    data = sys.stdin.readline()
                    if data:
                        client_socket.send(data.upper())
                elif i == client_socket:
                    data = client_socket.recv(256)
                    print repr(data)
                    if not data:
                        print 'Shutting down.'
                        flag = False
                        break
                    else:
                        if "<RECOGOUT>" in data:                # found the start of a reco block
                            reco_out = data                       # start a new reco_out block
                            keep = True                           # keep all the following data
                        elif "</RECOGOUT>" in data:             # found the end of a reco block
                            reco_out = reco_out + data            #
                            print get_sentence(reco_out)          # get the words and scores from the reco block
                            sys.stdout.flush()
                        elif keep:                              # not yet the end of the block, keep data and continue
                            reco_out = reco_out + data
                        else:                                   # no reco block found yet discard the data
                            keep = False
                            reco_out = ""

if __name__ == '__main__':
    jr = JuliusRecognizer('localhost', 10500, 5, 5)
    jr.recognize()