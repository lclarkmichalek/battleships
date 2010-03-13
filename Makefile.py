#!/bin/env python
import os
import sys
import shutils

PREFIX = '/usr/local/'
DATADIR = PREFIX + 'share/Battleships/'
GRAPHICSDIR = DATADIR + 'Graphics/'
BINDIR = PREFIX + 'bin/'

def install():
	os.mkdirs(GRAPHICSDIR)
	shutils

if __name__ == "__main__":
	if os.getuid() != 0:
		sys.exit('Must be run as root')
	try:
		eval(sys.argv[1])()
	except NameError:
		sys.exit('%s is not a valid function' % sys.argv[1])
