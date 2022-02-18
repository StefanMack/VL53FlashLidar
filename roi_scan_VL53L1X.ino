/*
Arduino-Firmware zum Auslesen des Lidar-Sensors VL53L1X im Flash Lidar Modus.
Der ROI (4x16 SPADS (minimal 4x4 SPADs)) wird bei jeder Einzelmessung um eine
SPAD-Position horizontal verschoben. Bei einem 4 SPADs breiten ROI sind über
die Gesamtbreite von 16 SPADs somit 13 ROI-Positionen möglich.
Diese 13 ROI-Positionen werden sequentiell gemessen, was einen horizontalen
(ROPI-)Scan entspricht.
Wegen der höheren Fremdlichtfestigkeit wird der Short Distance Mode mit einer
maximalen Reichweite von 1,3 m verwendet.
16 horizontale SPADS entsprechen einem horizontalem Sichtfeld von 27°.
!!!
Die verwendete Bibliothek VL53L1X aus github.com/pololu/vl53l1x-arduino
muss modifiziert werden, damit auch die Sigma-Werte ausgegeben werden:

S. Mack, 18.2.22
*/

#include <Wire.h>
#include <VL53L1X.h>

#define ROI_W 4   // Breite ROI
#define ROI_H 16  // Hoehe ROI

VL53L1X sensor;

uint8_t angle; // Indizes Winkelpositionen
uint8_t roi_h, roi_w, roi_center; // ROI Hoehe, Breite und Zentrum
uint16_t scan_ranges[13],scan_sigmas[13],scan_ambients[13]; // Listen fuer Messwerte

String serial_string;
 

void setup()
{
  Serial.begin(115200);
  //Serial.begin(1000000);
  Serial.println(0); // Noetig fuer Python-Programm?
  Wire.begin();
  Wire.setClock(400000); // 400 kHz I2C

  sensor.setTimeout(100); // >= 100 ms sonst Fehlfunktion
  if (!sensor.init())
  {
    Serial.println("Failed to detect and initialize sensor!");
    while (1);
  }
  
  sensor.setDistanceMode(VL53L1X::Short); // Short = max. 1,3 m Reichweite
  sensor.setMeasurementTimingBudget(12000); // Messdauer in µs (12000 minimal)
  sensor.setROISize(ROI_W,ROI_H); // Groeße ROI
}

void loop()
{
  // Python-Skript als Client initiiert mit /n Messung
  if (Serial.available()>0){
    uint8_t inByte = Serial.read();
    serial_string=String("");
    for(angle=0; angle<=12; angle++){
      roi_center = 8*angle + 151;
      sensor.setROICenter(roi_center);
      sensor.readSingle(true); // Blocking Read: Funktion blockiert bis Messwert verfuegbar
      serial_string += sensor.ranging_data.range_mm; // Reichweite in mm
      serial_string += ",";
      serial_string += sensor.ranging_data.sigma_mm; // Sigma Reichweite in mm
      serial_string += ",";
      serial_string += sensor.ranging_data.ambient_count_rate_MCPS; // Fremdlicht in Megacounts Per Second
      serial_string += ",";
    }
    Serial.println(serial_string);
  }
}
