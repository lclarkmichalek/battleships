SHELL=/bin/bash

PREFIX=/usr/local
PYTHONVERSION=2.6
PYTHONLIBDIR=$(PREFIX)/lib/python$(PYTHONVERSION)
BINDIR="$(PREFIX)/bin"
CXARGS=-c -O --no-copy-deps

install:
	mkdir -p $(PYTHONLIBDIR) $(BINDIR)
	cp ./battleshipslib.py $(PYTHONLIBDIR)
	cxfreeze ./xbattleships.py $(CXARGS) --target-dir $(BINDIR)
	cxfreeze ./battleships.py $(CXARGS) --target-dir $(BINDIR)
