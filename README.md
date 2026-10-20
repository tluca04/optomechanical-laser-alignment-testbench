# Optomechanical Laser Alignment Testbench

Testbench built to see how well sensor feedback and mechanical spring preloading can fix the backlash and vibration issues of cheap SG90 micro-servos when steering a laser beam.

An ESP32 controls a 2-axis pan-tilt mount carrying a 650 nm laser diode (KY-008), while reading angle encoders, an IMU, and environmental sensors. A webcam on the PC tracks the laser spot on a target to close the control loop.

## Hardware notes

The pan-tilt bracket is 3D-printed and uses springs to preload the servo gears. Since SG90 servos draw current spikes that can reset or add noise to the ESP32, the servos and laser run on a separate 5V rail from an LM2596 buck converter. The laser is switched through an NPN transistor.

Sensors on the rig:
- 2x AS5600 magnetic encoders (12-bit) on the pan and tilt shafts to measure the real angle vs. commanded PWM.
- MPU-6050 IMU on the laser bracket to measure vibrations and impacts.
- BH1750 light sensor behind a pinhole on the target, plus a USB webcam running OpenCV to track the (X, Y) center of the laser dot.
- BMP280, AHT20, and INA219 to check if room temperature or laser current drift over time.
- SSD1306 OLED screen and a MicroSD SPI module for local display and logging.

## Todo / Progress

- [x] ESP-IDF I2C master driver (GPIO 21/22)
- [x] MPU-6050 communication check (WHO_AM_I returns 0x72 instead of 0x68, since the GY-521 board has a clone chip)
- [x] Python serial reader and CSV logger (host/reader.py)
- [x] 14-byte burst read for accel, temp and gyro
- [x] 100 Hz sampling loop + 44 Hz hardware low-pass filter (DLPF = 0x03)
- [x] Python script to plot accel and gyro data (host/plot.py)
- [x] PWM control for the SG90 servos (LEDC driver)
- [x] Staggered servo movement, so the USB port doesn't brown out
- [x] Two-way UART: the ESP32 reads commands (CMD,pan,tilt) without blocking the main loop
- [ ] GPIO switching for the laser transistor
- [ ] Read both AS5600 encoders
- [ ] Add BMP280, AHT20, INA219 and BH1750 drivers
- [ ] SSD1306 OLED and MicroSD SPI logging
- [ ] OpenCV script to find the laser spot (X, Y) coordinates
- [ ] Closed-loop serial tracking

## I2C Addresses

All sensors use 3.3V logic. Both AS5600 encoders share the same fixed address (0x36), so they are split across the two hardware I2C buses of the ESP32:

| Component | Bus / Pins | Address | Notes |
| :--- | :--- | :--- | :--- |
| MPU-6050 | I2C0 (GPIO 21 / 22) | 0x68 | IMU on laser bracket (clone chip, WHO_AM_I = 0x72) |
| SSD1306 | I2C0 (GPIO 21 / 22) | 0x3C | OLED display |
| BMP280 | I2C0 (GPIO 21 / 22) | 0x76 | Temp / pressure |
| AHT20 | I2C0 (GPIO 21 / 22) | 0x38 | Humidity |
| BH1750 | I2C0 (GPIO 21 / 22) | 0x23 | Target light sensor |
| INA219 | I2C0 (GPIO 21 / 22) | 0x40 | Laser current / voltage |
| AS5600 (Pan) | I2C0 (GPIO 21 / 22) | 0x36 | Pan angle |
| AS5600 (Tilt)| I2C1 (GPIO 18 / 19) | 0x36 | Tilt angle |

Other pins (servo PWM, laser transistor, SPI) are listed in docs/wiring.md.

## IMU Data & UART Control Test

MPU-6050 at 100 Hz (sample rate divider 9, DLPF 44 Hz), +-2 g and +-250 deg/s. Servo commands are sent from the PC over UART while the IMU keeps streaming. The IMU board is not mounted on the servos, so its motion is independent of them.

![IMU and servo test](docs/imu_100hz_validation.png)

- 0 - 1.7 s: board at rest, gravity mostly on X (~1 g)
- 1.7 - 8.8 s: I moved the breadboard by hand, so accel and gyro vary a lot (gyro up to about 250 deg/s)
- 1.67 s: pan 90 -> 45
- 2.67 s: tilt 90 -> 120
- 3.67 s: pan 45 -> 135
- 4.67 s: tilt 120 -> 60
- 8.8 - 11 s: board left still, gyro ~0 and accel flat
- 11 - 15 s: I tapped the board to generate vibrations (short spikes in accel and gyro) while the servos stayed at their last position
- 15 - 18 s: still again

Servos are moved one axis per second to avoid the inrush current (around 1.3 A) that can brown out the ESP32.

## How to run

Flash the ESP32 (ESP-IDF):
```bash
cd firmware
idf.py build
idf.py -p COM3 flash monitor
```

```bash
cd host
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python reader.py      # logs to data.csv (edit COM port inside)
python imuplot.py     # plots data.csv
```

## Prerequisites
Firmware Toolchain: ESP-IDF v5.x (installed via VS Code ESP-IDF Extension)
Host Environment: Python 3.10+ (pip install -r host/requirements.txt)

## Repository Structure

- `firmware/` – ESP-IDF C code and drivers
- `host/` – Python scripts for serial logging, plotting, and OpenCV
- `cad/` – 3D-printed mount parts and STEP files
- `docs/` – Pinouts and test plots