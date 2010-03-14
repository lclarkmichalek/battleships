SHELL=/bin/sh

PREFIX=/usr/local
PYTHONVERSION=2.6
PYTHONLIBDIR=$(PREFIX)/lib/python$(PYTHONVERSION)
BINDDIR=$(PREFIX)/bin
CXARGS="-c -O --no-copy-deps"

install:
	install -D 644 ./battleshipslib.py $(PYTHONLIBDIR)/battleshipslib.py
	cxfreeze ./xbattleships.py $(CXARGS) --target-dir $(BINDIR)
	cxfreeze ./battleships.py $(CXARGS) --target-dir $(BINDIR)
