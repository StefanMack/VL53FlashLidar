#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Programm zur Darstellung der Scandaten des VL53L1X Flash Lidar von STMicrosystems
# Der Sensor wird an einem Arduino betrieben über dessen serielle Schnittstelle eine
# Messung getriggert und anschließend ausgelesen wird.
# Die Rückgabedaten enthalten für die gemessenen 13 Winkel jeweils eine Reichweite,
# eine Standardabweichung sowie den Umgebungslichtpegel.
# Zugehöriges Arduinoprogramm: roi_scan_VL53L1X
#
# Maximale Scanrate ca. 3-4 FPS. Erhöhung Baudrate auf 1000000 oder Verwendung
# Arduino Due statt Uno erhöht Scanrate nicht signifikant.
#
# Zum Aufzeichnen des Scanbildes siehe animML53L1XScan_record.py
#
# Es gibt immer wieder Probleme mit der Seriellen Schnittstelle, die nicht auftauchen
# wenn die einzelnen entsprechenden Befehle als Root über die Konsole ausgeführt
# werden. Vermutlich hat das etwas mit den unterschiedlichen Berechtigungen von Root
# bzw. Spyder bezüglich Zugriff auf die serielle Schnittstelle zu tun.
# S. Mack, 18.2.22

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from time import sleep
from serial import Serial
from os import _exit
import logging
# Logging Meldungen von matplotlib nur fuer Level WARNING
logging.getLogger('matplotlib').setLevel(logging.WARNING)

# Nachfolgende Zeile für Debugmeldungen ausschalten (level=0 bedeutet alle Meldungen)
# DEBUG 10, INFO 20, WARNING 30
#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.WARNING)
#logging.basicConfig(filename='logDatei.log', level=logging.WARNING)

# Messzeit Sensor: SCAN_PTS * MeasurementTimingBudget (12 ms min)
SCAN_PERIOD=50 # + Messzeit Sensor  = Dauer 1 Scan (Wartezeit nach jeder Messung)
SCAN_PTS=13 # Messwerte / Winkel pro Scan
SCAN_RES=1.8 # Winkelaufloesung in Grad
#RANGE_CALIB=[9,4,2,-3,-10,-11,-11,-8,-3,-2,6,11,17] # Siehe ScanView.init()
CALIBRATE= False

PORT='/dev/ttyACM0' # Hier richtige Schnittstelle angeben

class ScanView(object):
    def __init__(self, ax, scanpts=20, scanres=1, maxrange=1000):
        logging.debug('Scanner init')
        self.ax = ax
        self.scanpts=scanpts
        self.scanres=scanres
        self.scanangle = scanres*(scanpts-1)/2 # 1/2 Winkel Scanbereich
        self.maxrange = maxrange # initiale Länge y-Achse, wird später an max. Reichweite angepasst
        self.rangecalib=np.array([9,4,2,-3,-10,-11,-11,-8,-3,-2,6,11,17])
        self.angledata = np.arange(0,13)*scanres - self.scanangle # Array mit Winkelwerten ( 0° = Mitte)
        logging.debug('Scanner init')
        self.rangedata = [0]*scanpts # Liste mit Nullen
        self.line,  = self.ax.plot(self.angledata, self.rangedata,':o')
        self.ax.set_ylim(0, self.maxrange)
        self.ax.set_xlim(-self.scanangle-1, self.scanangle+1)
        self.ax.set_title('VL53L1X Scan')
        self.ax.set_xlabel('Winkel (°)')
        self.ax.set_ylabel('Reichweiten senkrecht (mm)')
        logging.debug('Scanner init end')
        
    def update(self, ranges):
        # Umrechnung radiale Reichweiten in senkrechte Abstaende
        self.rangedata = ranges*np.cos(self.angledata/180*np.pi)-self.rangecalib
        self.ax.set_ylim(min(self.rangedata)*0.9, max(self.rangedata)*1.1) # Anpassung y-Achse
        self.line.set_data(self.angledata, self.rangedata) # Plotdaten aktualisieren
        return self.line,
    
def calibrate(nave):
    calib_ranges=np.zeros(13)
    print('Offestkalibrierung.....')
    print('Scanner auf ebene Fläche ausrichten. Weter mit <Return> Abbruch mit <x> + <Return> ')
    choice = input()
    if choice == 'x':
        return
    else:
        for i in range(nave):
            print('.', end='',flush=True)
            calib_ranges += getRanges()
            sleep (SCAN_PERIOD/1000)      
    print('')
    calib_ranges = np.round((calib_ranges - np.average(calib_ranges)) / nave, 0)
    print('Ergebnis Offsetkalibrierung: {}'.format(calib_ranges))
            

def getRanges(): # neuen Datenpunkt von serieller Schnittstelle lesen
    logging.debug('getRanges()')
    port.flushInput() # seriellen Puffer leeren
    port.write(b'\n') # Sensormessung via Arduino anfordern
    #sleep(0.01) # noetig sonst manchmal Fehler bei port.readline()
    logging.debug('getRanges() Bytes nach port.write(): {}'.format(port.in_waiting))
    # von Schnittstelle Byte Array bis \n lesen und in String konvertieren
    buff_bytearray = port.readline()
    logging.debug('Ranges Bytearray: {}'.format(buff_bytearray))
    buff_string = buff_bytearray.decode()[:-3] 
    buff_list = buff_string.split(",")
    logging.debug('buff_list: {}'.format(buff_list))
    ranges = np.array(list(map(int,buff_list[::3])))
    return(ranges)

def data_gen(): # muss Iterator sein, daher yield und die While-Schleife. Wird wegen 
    while True: # repeat=False nur einmal aufgerufen, daher While-Endlosschleife
        ranges = getRanges()
        yield ranges    
      
try:
    logging.debug('Programmstart')
    port = Serial(port=PORT, baudrate=115200) # Hier richtige Baudrate angeben
    port.readline() # '0/r/n' auslesen damit bei erstem getRange() kein Fehler
    logging.debug('Serielle Schnittstelle geoeffnet...')
    if CALIBRATE:
        calibrate(10)
        logging.debug('Offsetkalibrierung fertig')
    fig, ax = plt.subplots() # Plot und Achse erstellen
    logging.debug('Animationsplot erstellt')
    scanner = ScanView(ax=ax,scanpts=SCAN_PTS,scanres=SCAN_RES)
    logging.debug('ScanView Object erzeugt')
    # Animation instanzieren, intervall in ms!, blit=False zum Nachskalieren Achsen nötig 
    ani = animation.FuncAnimation(fig, scanner.update, frames=data_gen, interval=SCAN_PERIOD, blit=False, repeat=False)
    logging.debug('Animation gestartet')
    plt.show() # Plot starten (Programm bleibt ab jetzt in dieser Schleife bis Plotfenster geschlossen)     
except KeyboardInterrupt:
    print()
    print('Strg + C erkannt...')
    sleep(2)      
finally: # wird ausgeführt nach Schließen des Plotfensters
    print('...COM-Verbindung wird beendet.')
    port.close() # COM-Verbindung beenden
    sleep(1)
    _exit(1) # Konsolenfenster schließen

