#!/usr/bin/env python
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

from battleshipslib import *

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
    while Board.ships != []:
        start = raw_input('Coordinates of one end of the ship: ')
        end = raw_input('Coordinates of other end of the ship: ')
        start = (int(start[1])-1,'ABCDEFGHIJKL'.index(start[0]))
        end = (int(end[1])-1,'ABCDEFGHIJKL'.index(end[0]))

    
        if not Board.placeShip(start, end):
            raise RuntimeError
        printBoard(Board)
        print 'SHIPS LEFT: %s' % Board.ships
    
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
