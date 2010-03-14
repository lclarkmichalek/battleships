SHELL=/bin/bash

PREFIX=/usr/local
PYTHONVERSION=2.6
PYTHONLIBDIR=$(PREFIX)/lib/python$(PYTHONVERSION)
BINDIR=$(PREFIX)/bin
CXARGS=-c -O --no-copy-deps
DESTDIR=./dest

install:
	mkdir -p $(PYTHONLIBDIR) $(BINDIR)
	install -m 644 $(DESTDIR)$(PYTHONLIBDIR)/battleshipslib.py $(PYTHONLIBDIR)
	install -m 755 $(DESTDIR)$(BINDIR)/xbattleships.py $(BINDIR)
	install -m 755 $(DESTDIR)$(BINDIR)/battleships.py $(BINDIR)

make:
	mkdir -p $(DESTDIR)$(PYTHONLIBDIR) $(DESTDIR)$(BINDIR)
	install -m 644 ./src/battleshipslib.py $(DESTDIR)$(PYTHONLIBDIR)
	cxfreeze ./src/xbattleships.py $(CXARGS) --target-dir $(DESTDIR)$(BINDIR)
	cxfreeze ./src/battleships.py $(CXARGS) --target-dir $(DESTDIR)$(BINDIR)
