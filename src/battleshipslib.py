#!/bin/env python
# -*- coding: utf-8 -*-
#    Copyright 2010 Laurie Clark-Michalek (Blue Peppers) <bluepeppers@archlinux.us>
#
#    This program (Battleships) is free software: you can redistribute it and/or modify
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
port = 1771

def log(*args):
    for arg in args:
        sys.stderr.write(str(arg))
    sys.stderr.write('\n')

class NetworkError(Exception): pass

class Shutdown(Exception): pass

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
    
    def close(self):
        if self.connection.__dict__.has_key('socket'):
            self.connection.close()
    

class connection():
    def __init__(self, timeout = 5):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.timeout = timeout
        self.moving = 0
    
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
    
    def check(self, timeout = 0):
        readable, null, null = select.select([self.socket], [], [], timeout)
        null, writeable, null = select.select([], [self.socket], [], timeout)
        null, null, errorable = select.select([], [], [self.socket], timeout)
        del null
        
        if bool(errorable): raise NetworkError
        
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
        log(content)
        self.socket.send(str(length) + content)
    
    def recive(self):
        if self.check()[2]:
            self.socket.close()
            raise RuntimeError
        if self.check()[0]:
            self.moving += 1
            log(self.moving)
            if self.moving >= self.timeout:
                raise Shutdown
        else:
            self.moving = 0
        while not self.check()[0]:
            time.sleep(0.1)
            if self.check()[2]:
                self.socket.close()
                raise RuntimeError
        length = self.socket.recv(2)
        try:
            length = int(length)
        except ValueError:
            raise Shutdown
        content = self.socket.recv(length)
        log (content)
        return content
    
    def reciveone(self):
        if self.check()[2]:
            self.socket.close()
            raise RuntimeError
        if self.check()[0]:
            self.moving += 1
            log(self.moving)
            if self.moving >= self.timeout:
                raise Shutdown
        else:
            self.moving = 0
            return False
        length = self.socket.recv(2)
        if length == '':
            return False
        length = int(length)
        content = self.socket.recv(length)
        log (content)
        return content
    
    def close(self):
        self.socket.close()



    
