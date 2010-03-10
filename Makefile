all: graphics

graphics: 
	pyrcc4 ./images.qrc -o ./images.py
