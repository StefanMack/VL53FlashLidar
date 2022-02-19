# Low Cost Flash Lidar mit VL53L1X
Der TOF-Sensor VL53L1X von ST Micro (https://www.st.com) misst Abstände mit dem Lichtlaufzeitverfahren. Dabei wird ähnlich wie beim Ultraschallverfahren über die Echolaufzeit („Time Of Flight“ = TOF) der Abstand eines Objekts bestimmt, welches das Echo erzeugt hat.
![Sensor](/sensorBreakout_klein.JPG)

Der Sensor VL53L1X ist von verschiedenen Herstellern wie Adafruit oder Pololu auf einem Breakout-Board verfügbar. Ein solches Board kostet ca. 15 €.

Genau genommen handelt es sich hierbei nicht nur um einen einstrahligen TOF-Sensor sondern um einen Flash Lidar:
Der VL53L1X beleuchtet die Szene global, kann aber aufgrund seiner 16x16 getrennten Empfänger (SPADs) Echos aus unterschiedlichen Richtungen unterscheiden. Somit kann man ihn auch als „Pulslaufzeitkamera mit 16x16 Pixeln“ bezeichnen.
![Messaufbau](/setupFussboden_klein.JPG)

Anders als bei einer echten Pulslaufzeitkamera kann der  VL53L1X pro Messung immer nur einen vorher festgelegten Pixelbereich auslesen. Diese Pixelbereich muss zudem mindestens 4x4 Pixel groß sein.

In einem Applikationsvideo (https://www.youtube.com/watch?v=J_4giQJt7WI) von ST Micro wird ein Flash Lidar vorgestellt, der aus 9 VL53L1X Sensoren aufgebaut ist und damit einen Scanfeld von etwa 180° überwacht. Jeder Einzelsensor davon überwacht ein Winkelsegment von ca. 20°.
Dieses Applikationsvideo war die Inspiration für die hier vorgestellte Arbeit: Statt 9 Sensoren wird hier nur ein Sensor verwendet.

Im 16x16 Empfängerarray des VL53L1X wird ein 4 Pixel breiter und 16 Pixel hoher ROI („Region Of Interest“=ROI) definiert. Dabei handelt es sich um den Pixelbereich, welcher für die TOF-Messung verwendet wird. Da sich vor dem Empfängerarray eine Linse befindet, bewirkt ein Verschieben dieses ROI eine Änderung der „Blickrichtung“ des Empfängers – so als würde man eine Kameraobjektiv schwenken.

Innerhalb der Breite des 16x16 Empfängerarrays wird dieser 4x4 ROI nun schrittweise jeweils um 1 Pixel horizontal verschoben. Dies entspricht einer Winkeländerung von jeweils 1,8° bzw. bei 13 möglichen Positionen des ROI einem Scanfeld von 21,6°.
Nähere Informationen finden sich z.B. in den Application Notes UM2510 oder AN5191 von ST Micro.

Der VL53L1X  wird von einem Arduino Uno wie oben beschrieben gesteuert. Der Arduino Uno gibt jeweils nach einem kompletten Scan die 13 Messwerte für den gemessenen Abstand, die Standardabweichung der Abstandsmessung sowie den Fremdlichtpegel über die serielle Schnittstelle aus. Dazu muss auf dem Arduino Uno die Firmware `roi_scan_VL53L1X.ino` aufgespielt sein.
Dieses Arduino-Programm verwendet die  VL53L1X-Bibliothek von Pololu (https://www.github.com/pololu/vl53l1x-arduino) welche auf der von ST Micro bereitgestellten C-Bibliothek basiert. Damit die Standardabweichungen ausgegeben werden, muss die Pololu-Bibliothek noch entsprechend modifiziert werden, da diese Funktion darin nicht implementiert ist.  

![VideoMessung](/animationVL53L1XScanner.gif)  

Das Python-Programm `animVL53L1X.py` triggert diese Scans am Arduino, liest die Messwerte aus und stellt sie grafisch animiert dar.
