#!/bin/python
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from time import sleep
import battleships
import images
import sys

log = battleships.log

size = 30

app = QApplication(sys.argv)

EMPTY = QPixmap(':/EMPTY.png').scaled(size,size)
HIT = QPixmap(':/HIT.png').scaled(size,size)
MISS = QPixmap(':/MISS.png').scaled(size,size)
SHIP = QPixmap(':/SHIP.png').scaled(size,size)

class square(QLabel):
    def __init__(self, row, column, parent=None, value="EMPTY"):
        super(square, self).__init__(parent)
        
        self.value = value
        
        pixmap = QPixmap(':/%s.png' % value)
        pixmap = pixmap.scaled(30, 30)
        
        self.setPixmap(eval(value))
        
        self.row = row
        
        self.column = column
    
    def changeType(self, value):
        self.value = value
        
        self.setPixmap(eval(value))

class ConnectionWindow(QDialog):
    def __init__(self, parent=None):
        super(ConnectionWindow, self).__init__(parent)
        
        clientlayout = QHBoxLayout()
        clientlayout.addWidget(QLabel('<center><h4>Client Infomation'))
        clientlayout.addWidget(QLabel('<center>Enter your invite code below'))
        self.Input = QLineEdit()
        clientlayout.addWidget(self.Input)
        
        serverlayout = QHBoxLayout()
        serverlayout.addWidget(QLabel('<center><h4>Server Infomation'))
        serverlayout.addWidget(QLabel('<center>Send this invitation code to your partner:'))
        serverlayout.addWidget(QLabel('%s' % battleships.ip))
        
        seperator = QFrame()
        seperator.setFrameShape(QFrame.VLine)
        
        mainsplitter = QVBoxLayout()
        mainsplitter.addLayout(clientlayout)
        mainsplitter.addWidget(seperator)
        mainsplitter.addLayout(serverlayout)
        
        layout = QVBoxLayout()
        layout.addLayout(mainsplitter)
        buttonbox = QDialogButtonBox(QDialogButtonBox.Ok)
        layout.addWidget(buttonbox)
        self.setLayout(layout)
        self.connect(buttonbox, SIGNAL('accepted ()'),
                     self.accept)

class GameWindow(QMainWindow):
    def __init__(self, parent=None):
        super(GameWindow, self).__init__(parent)
        
        #GAME
        self.game = battleships.board()
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
        self.Output.setText('Welcome! Commander!')
        self.Input = QLineEdit()
        
        self.createsetLayout()
        
        
        
        #Set connection type and ip and so forth
        dialog = ConnectionWindow(self)
        if dialog.exec_():
            log('Dialog shown')
            if unicode(dialog.Input.text()) == '':
                log('server')
                self.game.connection.setServer()
                log('Connected')
            else:
                log('Client')
                self.game.connection.setClient(unicode(dialog.Input.text()))
                log('Connected')
        
        content = ['This isn\'t a war. It never was a war, any more than there\'s ',
        'war between man and ants. There\'s the ants builds their cities, live their ',
        'lives, have wars, revolutions, until the men want them out of the way, and ',
        'then they go out of the way. That\'s what we are now--just ants.\n \n',
        'And so we end up with you, private parts.\n\n\n\n',
        'Situation: The enemy have 5 ships in an area of 1200x1200m. We can shell',
        ' any point in that square, and destroy anything within 100m of the shell impact. ',
        'However, we are in an identical situation to the enemy. This is a problem.\n\n',
        'Mission: Destroy all enemy ships before they destroy yours\n\n',
        'Execution: Bomb \'em to hell!\n\n',
        'Assesment: Are they dead? No? Bomb \'em to hell!\n\n\n\n',
        'ALERT!! Before the enemy starts shelling, we have one last chance to move our ships.',
        ' Move the ships by entering the coordinates of the bow of the ship, followed by the ',
        'coordinates of the stern.\n\n',
        'i.e. D3,D5\n\n',
        'Ships avalible, listed by length:\n',
        'Carrier. Length 5. Quantity 1.\n',
        'Battleship. Length 4. Quantity 1.\n',
        'Cruiser. Length 3. Quantity 1.\n',
        'Tug. Length 2. Quantity 2.\n']
        
        
        self.Output.setText(''.join(content))
        
        self.connect(self.Input, SIGNAL("editingFinished ()"),
                                        self.placeShip)
    
    
    def placeShip(self):
        log('Placing ship')
        log(self.game.ships)
        input = self.Input.text().split(',')
        self.Input.setText('')
        if len(input) != 2:
            return
        start = input[0]
        start = (int(start[1:])-1,'ABCDEFGHIJKL'.index(unicode(start[0]).capitalize()))
        end = input[1]
        end = (int(end[1:])-1,'ABCDEFGHIJKL'.index(unicode(end[0]).capitalize()))
        returncode = self.game.placeShip(start, end)
        log(returncode)
        if returncode:
            self.syncLists()
            if self.game.ships == []:
                self.disconnect(self.Input, SIGNAL("editingFinished ()"),
                                            self.placeShip)
                self.Output.append('\n\nShips have been moved. Hopefully not for the last time.')
                
            else:
                self.Output.append('\nYou have %i ships left to place %s' % (len(self.game.ships), str(tuple(self.game.ships))))
                return
        else:
            self.Output.append('THIS IS WAR SOLDIER! WE DON\'T HAVE TIME FOR MUCKING AROUND!')
            return
        self.Input.setText('')
        self.syncLists()
        if self.game.connection.type == "Server":
            self.connect(self.Input, SIGNAL("editingFinished ()"),
                                    self.sendShot)
        else:
            self.Output.append('We\re  preparing to recive shots. Ok?')
            self.connect(self.Input, SIGNAL("editingFinished ()"),
                                                    self.reciveShot)
    
    def reciveShot(self):
        self.disconnect(self.Input, SIGNAL("editingFinished ()"),
                                                    self.reciveShot)
        log('reciving shot')
        self.Output.append('\n\nWe can only wait now...')
        returncode = self.game.reciveShot()
        self.syncLists()
        if returncode:
            self.Output.append('\n\nIt appears a ship has been hit. May their soles rest in peace.')
            if self.game.game == "LOST":
                self.LostGame()
        else:
            self.Output.append('\n\nWe were lucky. They missed...')
        
        self.Output.append('\n\nPlease enter the coordinates you would like us to target')
        
        self.connect(self.Input, SIGNAL("editingFinished ()"),
                                        self.sendShot)
    
    def sendShot(self):
        log('sending shot')
        self.disconnect(self.Input, SIGNAL("editingFinished ()"),
                                self.sendShot)
        coord = self.Input.text()
        coord = (int(coord[1])-1,'ABCDEFGHIJKL'.index(coord[0]))
        log (coord)
        returncode = self.game.sendShot(coord)
        if returncode:
            self.Output.append('\n\nWe have hit the enemy. Today is a glorious day.')
            if self.game.game == "WON":
                self.WonGame()
        else:
            self.Output.append('\n\nI must regretfully inform you that we have missed the enemy on this occasion.' )
        
        self.Output.append('We\re  preparing to recive shots. Ok?')
        self.connect(self.Input, SIGNAL("editingFinished ()"),
                                                    self.reciveShot)
        
    
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
