SHELL=/bin/bash

PREFIX=/usr/local
PYTHONVERSION=2.6
PYTHONLIBDIR=$(PREFIX)/lib/python$(PYTHONVERSION)
BINDIR="$(PREFIX)/bin"
CXARGS=-c -O --no-copy-deps

install:
	mkdir -p $(PYTHONLIBDIR) $(BINDIR)
	cp ./src/battleshipslib.py $(PYTHONLIBDIR)
	cxfreeze ./src/xbattleships.py $(CXARGS) --target-dir $(BINDIR)
	cxfreeze ./src/battleships.py $(CXARGS) --target-dir $(BINDIR)
