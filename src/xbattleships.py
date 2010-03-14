#!/bin/python
# -*- coding: utf-8 -*-
#    Copyright 2010 Laurie Clark-Michalek (Blue Peppers) <bluepeppers@archlinux.us>
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from time import sleep
import battleshipslib
import battleshipsimages
import sys

log = battleshipslib.log



app = QApplication(sys.argv)
app.setWindowIcon(QIcon(':/LOGO.png'))
size = 30
EMPTY = QPixmap(':/EMPTY.png').scaled(size,size)
HIT = QPixmap(':/HIT.png').scaled(size,size)
MISS = QPixmap(':/MISS.png').scaled(size,size)
SHIP = QPixmap(':/SHIP.png').scaled(size,size)

def encode(input):
    output = input
    return output

def decode(input):
    output = input
    return output

class square(QLabel):
    def __init__(self, row, column, parent=None, value="EMPTY"):
        super(square, self).__init__(parent)
        
        self.value = value
        
        self.setPixmap(eval(value))
        
        self.row = row
        
        self.column = column
    
    def changeType(self, value):
        self.value = value
        
        self.setPixmap(eval(value))

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super(ConnectionDialog, self).__init__(parent)
        
        clientlayout = QVBoxLayout()
        clientlayout.addWidget(QLabel('<center><h4>If you have a connection code'))
        clientlayout.addWidget(QLabel('<center>Enter your connection code below'))
        self.Input = QLineEdit()
        clientlayout.addWidget(self.Input)
        
        serverlayout = QVBoxLayout()
        serverlayout.addWidget(QLabel('<center><h4>If you require a connection code'))
        serverlayout.addWidget(QLabel('<center>Your connection code is:\n\n'))
        serverlayout.addWidget(QLineEdit('%s' % encode(battleshipslib.ip)))
        
        seperator = QFrame()
        seperator.setFrameShape(QFrame.VLine)
        
        mainsplitter = QHBoxLayout()
        mainsplitter.addLayout(clientlayout)
        mainsplitter.addWidget(seperator)
        mainsplitter.addLayout(serverlayout)
        
        layout = QVBoxLayout()
        layout.addLayout(mainsplitter)
        buttonbox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        layout.addWidget(buttonbox)
        self.setLayout(layout)
        self.connect(buttonbox, SIGNAL('accepted ()'),
                     self.accept)
        self.connect(buttonbox, SIGNAL('rejected ()'),
                     self.reject)

class ReciveThread(QThread):
    
    over = pyqtSignal()
    
    def shot(self, parent):
        returncode = parent.game.reciveShot(type='NonBlocking')
        if returncode:
            parent.Output.append('\n\nOne of your ships was hit.')
            return True
        elif returncode == None:
            return None
        else:
            parent.Output.append('\n\nThe enemy missed.')
            return False
        
        parent.Output.append('\n\nPlease enter the coordinates you would like us to target')
    
    def run(self):
        self.parent.Output.append('\n\nWaiting for a shot.')
        shot = self.shot(self.parent)
        while shot == None:
            sleep(0.2)
            shot = self.shot(self.parent)
        
        self.over.emit()
        
        self.connect(self.parent.Input, SIGNAL("editingFinished ()"),
                                        self.parent.sendShot)  

class ServerThread(QThread):
    over = pyqtSignal()
    
    def run(self):
        self.parent.game.connection.setServer()
        
        self.over.emit()
        

class GameWindow(QMainWindow):
    def __init__(self, parent=None):
        super(GameWindow, self).__init__(parent)
        
        #GAME
        self.game = battleshipslib.board()
        self.game.ships = [2]
        
        self.VALUES = []
        self.SHOTS = []
        
        for row in range(0, len(self.game.values)):
            shots = []
            values = []
            for column in range(0, len(self.game.values[row])):
                shots.append(square(row, column))
                values.append(square(row, column))
            self.SHOTS.append(shots)
            self.VALUES.append(values)
        
        self.Output = QTextBrowser()
        Font = QFont()
        Font.setStyleHint(QFont.TypeWriter)
        #Font.setCapitalization(QFont.AllUppercase)
        Font.setFamily('Monospace')
        self.Output.setCurrentFont(Font)
        self.Output.setText('Welcome to BattLeships')
        self.Input = QLineEdit()
        
        self.createsetLayout()
        
        self.setWindowTitle('Battleships')
        
        
        menu = self.menuBar()
        file = menu.addMenu('&File')
        
        connect = self.createAction('Connect', shortcut='Ctrl+N', slot=self.createConnection, icon=QIcon(':/CONNECT.png'))
        file.addAction(connect)
        
        content = ['Place ships please. Lengths are: 5, 4, 3, 2, 2',
                   '\n\nEnter coordinates in the form \'A1,B3\', with A1 being the start of the ship, and B3 being the end',
                   '\n\n']
        
        
        self.Output.setText(''.join(content))
        
        self.connect(self.Input, SIGNAL("editingFinished ()"),
                                        self.placeShip)
    def createConnection(self):
        dialog = ConnectionDialog()
        if dialog.exec_():
            self.connecting = QMessageBox.information(self, 'Connecting', 'Connecting...')
            text = decode(dialog.Input.text())
            if len(text.split('.')) == 3:
                self.game.connection.setClient(text)
                self.finishedConnecting()
            elif text == '':
                self.thread = ServerThread()
                self.thread.parent = self
                self.thread.over.connect(self.finishedConnecting)
                self.thread.run()
            else:
                self.connecting.close()
                QMessageBox.critical(self, 'End', 'Invalid invitation code')
        

        
    def finishedConnecting(self):
        self.connecting.close()
        if self.game.ships == []:
            if self.game.connection.type == "Server":
                self.connect(self.Input, SIGNAL("editingFinished ()"),
                                self.sendShot)
            else:
                self.reciveShot()
                self.syncLists()
        
    
    def placeShip(self):
        input = self.Input.text().split(',')
        self.Input.setText('')
        if len(input) != 2:
            return
        start = input[0]
        start = (int(start[1:])-1,'ABCDEFGHIJKL'.index(unicode(start[0]).capitalize()))
        end = input[1]
        end = (int(end[1:])-1,'ABCDEFGHIJKL'.index(unicode(end[0]).capitalize()))
        returncode = self.game.placeShip(start, end)
        if returncode:
            self.syncLists()
            if self.game.ships == []:
                self.disconnect(self.Input, SIGNAL("editingFinished ()"),
                                            self.placeShip)
                self.Output.append('\n\nFinished placing ships')
                
            else:
                self.Output.append('\nYou have %i ships left to place %s' % (len(self.game.ships), str(tuple(self.game.ships))))
                return
        else:
            self.Output.append('\nInvalid coordinates')
            return
        self.Input.setText('')
        self.syncLists()
        try:
            self.game.connection.type
        except AttributeError:
            self.Output.append('\nShips placed, please now connect to your opponent')
            return
        
        
        if self.game.connection.type == "Server":
            self.connect(self.Input, SIGNAL("editingFinished ()"),
                                    self.sendShot)
        else:
            self.reciveShot()
            self.syncLists()
    
    def reciveShot(self):
        
        self.thread = ReciveThread()
        self.thread.parent = self
        self.thread.start()
        self.thread.over.connect(self.syncLists)
    
    def sendShot(self):
        self.Output.append('\nEnter the coordinates for us to target')
        
        coord = self.Input.text()
        if len(coord) != 2:
            return
        self.disconnect(self.Input, SIGNAL("editingFinished ()"),
                                self.sendShot)
        coord = (int(coord[1])-1,'ABCDEFGHIJKL'.index(coord[0]))
        returncode = self.game.sendShot(coord)
        if returncode:
            self.Output.append('\n\nYou hit the enemy.')
            if self.game.game == "WON":
                self.WonGame()
            elif self.game.game == "LOST":
                self.LostGame()
        else:
            self.Output.append('\n\nYou missed the enemy.' )
        
        self.Input.setText('')
        
        self.reciveShot()
        self.syncLists()
        
    def WonGame(self):
        dialog = QMessageBox('You won the game. Well done')
        dialog.exec_()
        self.close()
    
    def LostGame(self):
        dialog = QMessageBox('You lost the game. Better luck next time')
        dialog.exec_()
        self.close()
    
    def createsetLayout(self):
        Layout = QGridLayout()
        Layout.addLayout(self.createBoard(),0,0,2,1)
        Layout.addWidget(self.Output,0,1)
        Layout.addWidget(self.Input,1,1)
        Widget = QWidget()
        Widget.setLayout(Layout)
        self.setCentralWidget(Widget)
        
    def syncLists(self):
        for row in range(0, len(self.game.values)):
            for column in range(0, len(self.game.values[row])):
                self.VALUES[row][column].changeType(self.game.values[row][column])
                self.SHOTS[row][column].changeType(self.game.shots[row][column])        
    
    def createBoard(self):
        FullLayout = QGridLayout()
        
        ShotsFrame = QFrame()
        ShotsFrame.setFrameShape(QFrame.StyledPanel)
        ShotsFrame.setFrameShadow(QFrame.Sunken)
        ShotsLayout = QGridLayout()
        ShotsLayout.addWidget(QLabel("<h3><center><u>Shots"),0,0,1,len(self.game.values))
        
        ValuesFrame = QFrame()
        ValuesFrame.setFrameShape(QFrame.StyledPanel)
        ValuesFrame.setFrameShadow(QFrame.Sunken)
        ValuesLayout = QGridLayout()
        ValuesLayout.addWidget(QLabel("<h3><center><u>Ships"),0,0,1,len(self.game.values))
        
        for index, character in enumerate(' ABCDEFGHIJKL'):
            ShotsLayout.addWidget(QLabel('<center>' + character), 1, index)
            ValuesLayout.addWidget(QLabel('<center>' + character), 1, index)
        
        for row in range(0, len(self.game.values)):
            ShotsLayout.addWidget(QLabel('<center>' + str(row + 1)), row + 2, 0)
            ValuesLayout.addWidget(QLabel('<center>' + str(row + 1)), row + 2, 0)
            for column in range(0, len(self.game.values[row])):
                ShotsLayout.addWidget(self.SHOTS[row][column], row + 2, column + 1)
                ValuesLayout.addWidget(self.VALUES[row][column], row + 2, column + 1)
        
        ShotsFrame.setLayout(ShotsLayout)
        ValuesFrame.setLayout(ValuesLayout)
        
        FullLayout.addWidget(ShotsFrame, 0, 0)
        FullLayout.addWidget(ValuesFrame, 1, 0)
        
        
        return FullLayout
    
    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
    
        

game = GameWindow()
game.show()
app.exec_()
