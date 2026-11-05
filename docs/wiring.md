# Wiring

## Components
- ESP32 (CH9102)
- MPU-6050
- 2x SG90 servos (pan & tilt)
- KY-008 650 nm laser module (5V rated, run at 3.3V)
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

Laser (switched by NPN transistor, powered from 3.3V):
- GPIO 27 -> 1k ohm resistor -> transistor base
- 10k ohm resistor between transistor base and GND (pull-down)
- Laser (+) -> 3.3V
- Laser (-) -> transistor collector
- Transistor emitter -> GND

Power filtering:
- 100nF capacitor connected between 5V and GND

## Notes
- Connect the ESP32 to a USB 3.0 port on the motherboard to avoid 5V brownouts when servos move.
- Move one axis at a time in software to keep current draw low.
- Leave slack on the MPU-6050 and laser wires so they don't pull on the tilt axis.
- The laser runs at 3.3V instead of its rated 5V, so the spot is dimmer. This is enough for the camera to detect it, but a brighter spot would make detection more reliable in a lit room.