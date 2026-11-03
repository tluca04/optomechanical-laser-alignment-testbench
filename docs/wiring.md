# Wiring

## Components
- ESP32 (CH9102)
- MPU-6050
- 2x SG90 servos (pan & tilt)
- 5V laser module
- 100nF (104) ceramic capacitor
- 1k ohm and 10k ohm resistors

## Connections

MPU-6050:
- VCC -> 3.3V
- GND -> GND
- SDA -> GPIO 21
- SCL -> GPIO 22

Servo Pan:
- Signal (Orange) -> GPIO 25
- VCC (Red) -> 5V
- GND (Brown) -> GND

Servo Tilt:
- Signal (Orange) -> GPIO 26
- VCC (Red) -> 5V
- GND (Brown) -> GND

Laser:
- (+) -> GPIO 27 (with 1k series resistor and 10k pull-down resistor to GND)
- (-) -> GND

Power filtering:
- 100nF capacitor connected between 5V and GND

## Notes
- Connect the ESP32 to a USB 3.0 port on the motherboard to avoid 5V brownouts when servos move.
- Move one axis at a time in software to keep current draw low.
- Leave slack on the MPU-6050 and laser wires so they don't pull on the tilt axis.