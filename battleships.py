#!/bin/python
import socket
import sys
import select
import time

global states
states = {"EMPTY": True, "SHIP": True, "MISS": False, "HIT": False}

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('google.com',0))

global ip
ip = s.getsockname()[0]

del s

global port
port = 1768

def log(*args):
    for arg in args:
        sys.stderr.write(str(arg))
    sys.stderr.write('\n')

class board():
    def __init__(self):
        
        self.values = []
        for x in range(0,12):
            values = []
            for x in range(0,12):
                values.append("EMPTY")
            self.values.append(values)
        
        self.shots = []
        for list in self.values:
            #Can't just copy list, as each contained list is another object
            self.shots.append(list[:])
        
        self.ships = [2, 2, 3, 4, 5]
        
        self.shipcoords = []
        self.game = 'PLAYING'
        
        self.connection = connection()
    
    
    def placeShip(self, start, end):
        '''self and start = tuple with int cords'''
        if start[0] != end[0] and start[1] != end[1]:
            return False
        if start[0] == end[0]:
            cells = range(start[1],end[1]+1)
            if not len(cells) in self.ships:
                return False
            else:
                self.ships.remove(len(cells))
            for x in cells:
                if self.values[start[0]][x] != "EMPTY":
                    return False
            for x in cells:
                self.values[start[0]][x] = "SHIP"
                self.shipcoords.append((start[0], x))
        elif start[1] == end[1]:
            cells = range(start[0],end[0]+1)
            if not len(cells) in self.ships:
                return False
            else:
                self.ships.remove(len(cells))
            for x in cells:
                if self.values[x][start[1]] != "EMPTY":
                    return False
            for x in cells:
                self.values[x][start[1]] = "SHIP"
                self.shipcoords.append((x, start[1]))
        
        return True
    
    def reciveShot(self, type = 'Blocking'):
        '''True if hit, False if not
        raises InvalidLine if not vert or horis line'''
        if type == 'Blocking':
            coord = self.connection.recive()
        elif type == 'NonBlocking':
            coord = self.connection.reciveone()
            if not coord:
                return
        if coord[:7] != '<coord>':
            self.connection.close()
            raise RuntimeError
        else:
            coord = [int(x) for x in coord[7:].replace('(','').replace(')','').split(',')]
        state = self.values[coord[0]][coord[1]]
        if state == "SHIP":
            self.values[coord[0]][coord[1]] = "HIT"
            if self.checkLost():
                self.connection.send('<youwin>')
                self.game = "LOST"
            else:
                self.connection.send('<coordrtn>True')
            return True
        elif state == "EMPTY":
            self.values[coord[0]][coord[1]] = "MISS"
            self.connection.send('<coordrtn>False')
            self.checkLost()
            return False
    
    def sendShot(self, coord):
        self.connection.send('<coord>' + str(coord))
        
        recived = self.connection.recive()
        
        log('Recived: '+recived)
        
        if recived[:10] == '<coordrtn>':
            result = recived[10:]
        elif recived[:8] == '<youwin>':
            self.shots[coord[0]][coord[1]] = "HIT"
            self.game = 'WON'
            return True
        else:
            self.connection.close()
            raise RuntimeError
        
        if result == 'True':
            self.shots[coord[0]][coord[1]] = "HIT"
            return True
        elif result == 'False':
            self.shots[coord[0]][coord[1]] = "MISS"
            return False
    
    def checkLost(self):
        '''Return True if lost, else False'''
        for cell in self.shipcoords:
            if self.values[cell[0]][cell[1]] != "HIT":
                return False
        self.game = 'LOST'
        return True
    

class connection():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def setServer(self):
        self.type = 'Server'
        self.sock.bind((ip, port))
        self.sock.listen(1)
        (self.socket, self.address) = self.sock.accept()
        self.socket.setblocking(0)
    
    def setClient(self, address):
        self.type = 'Client'
        self.sock.connect((address, port))
        self.socket = self.sock
        self.socket.setblocking(0)
    
    def check(self, timeout = 60):
        readable, writeable, errorable = select.select([self.socket],
                                                       [self.socket], 
                                                       [self.socket], 
                                                       timeout)
        return (bool(readable), bool(writeable), bool(errorable))
    
    def send(self, content):
        if self.check()[2]:
            self.socket.close()
            raise RuntimeError
        class ToLong(Exception): pass
        length = len(content)
        if length > 100:
            raise ToLong
        if length < 10:
            length = '0' + str(length)
        else:
            length = str(length)
        self.socket.send(str(length) + content)
        log('Sent: '+length + content)
    
    def recive(self):
        if self.check()[2]:
            self.socket.close()
            raise RuntimeError
        while not self.check()[0]:
            time.sleep(0.1)
            if self.check()[2]:
                self.socket.close()
                raise RuntimeError
        length = self.socket.recv(2)
        length = int(length)
        content = self.socket.recv(length)
        log('Recived: ' + str(length) + content)
        return content
    
    def reciveone(self):
        if self.check()[2]:
            self.socket.close()
            raise RuntimeError
        elif not self.check()[0]:
            return False
        length = self.socket.recv(2)
        if length == '':
            return False
        length = int(length)
        content = self.socket.recv(length)
        log('Recived: ' + str(length) + content)
        return content
    
    def close(self):
        self.socket.close()


if __name__ == "__main__":
    def printBoard(board):
        print 'SHOTS'
        print '   A B C D E F G H I J K L'
        for i in range(0,len(board.shots)):
            if i+1 < 10:
                print ' %s' % (i+1),
            else:
                print i+1,
            for item in board.shots[i]:
                print item[0],
            print ''
        print 'SHIPS'
        print '   A B C D E F G H I J K L'
        for i in range(0,len(board.values)):
            if i+1 < 10:
                print ' %s' % (i+1),
            else:
                print i+1,
            for item in board.values[i]:
                print item[0],
            print ''
        return
    
    Board = board()
    
    r = raw_input('Server or client? ')
    if r == 'Client':
        address = raw_input('Server ip address: ')
        Board.connection.setClient(address)
    elif r == 'Server':
        print 'Waiting for connection. Your ip adress is %s' % ip
        Board.connection.setServer()
    
    print 'CONNECTED\n'
    printBoard(Board)
    print 'PLACE SHIPS'
    start = raw_input('Coordinates of one end of the ship: ')
    end = raw_input('Coordinates of other end of the ship: ')
    start = (int(start[1])-1,'ABCDEFGHIJKL'.index(start[0]))
    end = (int(end[1])-1,'ABCDEFGHIJKL'.index(end[0]))

    
    if not Board.placeShip(start, end):
        raise RuntimeError
    printBoard(Board)
    
    if Board.connection.type == 'Server':
        #TODO: Random first go selection. Problems: involes communication, complicates game initilisation.
        coord = raw_input('Please place your shot. Enter shot coordinates: ')
        coord = (int(coord[1])-1,'ABCDEFGHIJKL'.index(coord[0]))
        print coord
        if Board.sendShot(coord):
            print 'HIT!'
        else:
            print 'MISS!'
    while Board.game == 'PLAYING':
        print 'Waiting for shot'
        if Board.reciveShot():
            print 'HIT!'
        else:
            print 'MISS!'
        while Board.game == 'PLAYING':
            choice = raw_input('(s)how board, (P)lace shot, (e)xit: ')
            if choice == 's':
                printBoard(Board)
            elif choice == 'e':
                Board.connection.close()
                sys.exit()
            else:
                coord = raw_input('Enter shot coordinates: ')
                coord = (int(coord[1])-1,'ABCDEFGHIJKL'.index(coord[0]))
                if Board.sendShot(coord):
                    print 'HIT!'
                else:
                    print 'MISS'
                break
        
        if Board.game == 'LOST':
            print 'Sorry, you lost. Ending boards:'
            printBoard(Board)
        elif Board.game == 'WON':
            print 'YOU WON! Ending boards:'
            printBoard(Board)
        
    
    Board.connection.close()
    
