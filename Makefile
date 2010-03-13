SHELL = /bin/sh

PREFIX = /usr/local
DATADIR = $(PREFIX)/share/Battleships
GRAPHICSDIR = $(DATADIR)/Graphics
BINDIR = $(PREFIX)/bin


all: graphics
	install	


graphics:
	sed -i "s/Graphics/$(GRAPHICSDIR)" ./images.qrc
	pyrcc4 ./images.qrc -o ./images.py

install:
	mkdir -p $(GRAPHICSDIR)
	cp Graphics/* $(GRAPHICSDIR)
	install 755 -D ./battleships.pyw $(BINDIR)/battleships.X11
	install 755 -D ./battleships.py $(BINDIR)/battleships
