# Optomechanical Laser Alignment Testbench

A testbench to evaluate how well software feedback and mechanical preloading can stabilize a low-cost laser pan-tilt mechanism against vibration, gear backlash, and thermal drift.

The setup steers a 650 nm laser diode (KY-008) using two SG90 micro-servos. The system measures mount position, mechanical vibration, ambient conditions, and beam alignment using several sensors and a host-side webcam.

## How the setup works

- **Laser & Mount:** A KY-008 5 mW laser diode on a 3D-printed 2-DOF pan-tilt bracket driven by two SG90 servos (with spring preloading to reduce gear backlash). The laser is powered from 5V and gated via an NPN transistor.
- **Power Delivery:** An LM2596 DC-DC step-down buck converter provides a separate 5V rail for the servos and laser, keeping motor current spikes away from the ESP32 supply rail.
- **Angle & Vibration Feedback:**
  - **2x AS5600 (12-bit magnetic encoders):** Mounted on each servo axis with diametric magnets to measure the actual axis position and quantify gear backlash.
  - **MPU-6050 (GY-521):** Mounted directly on the laser bracket to detect vibration frequencies and mechanical disturbances.
- **Environmental & Electrical Monitoring:**
  - **BMP280 + AHT20:** Temperature, pressure, and humidity sensing to check whether environmental changes correlate with beam drift.
  - **INA219:** Current and voltage monitor on the laser supply to track electrical changes during operation.
- **Target & Vision Feedback:**
  - **BH1750:** Digital light sensor placed behind a pinhole aperture on the target to detect optical alignment peak.
  - **Webcam + OpenCV:** A host-side camera pointed at the target tracks the laser spot centroid (X, Y) and streams position corrections back to the ESP32 over serial.
- **Local Telemetry & Storage:** An SSD1306 OLED (I2C) for live stats and a MicroSD card module (SPI) for standalone data logging.

## Current status

- [x] ESP-IDF I2C driver running (`i2c_master`)
- [x] MPU-6050 responds to `WHO_AM_I`
- [x] Basic Python serial listener working (`host/reader.py`)
- [ ] Read continuous accelerometer and gyroscope registers
- [ ] Integrate BMP280 / AHT20 environmental readout
- [ ] Read dual AS5600 magnetic encoders (primary I2C bus + secondary bus)
- [ ] Configure LEDC PWM for servo angle control & add transistor gate for KY-008
- [ ] Integrate BH1750 aperture sensor reading
- [ ] Add SSD1306 status display and MicroSD FATFS SPI logging
- [ ] OpenCV script to extract spot coordinates (X, Y)
- [ ] Closed-loop corrective tracking over serial

## I2C Bus Allocation

All sensors operate on 3.3V logic. The ESP32 utilizes two hardware I2C controllers to accommodate the duplicate fixed address of the two AS5600 encoders (`0x36`):

| Device | Bus / Interface | Default Address | Function |
| :--- | :--- | :--- | :--- |
| **MPU-6050** | I2C0 (GPIO 21 / 22) | `0x68` | Mount vibration |
| **SSD1306** | I2C0 (GPIO 21 / 22) | `0x3C` | Local display |
| **BMP280** | I2C0 (GPIO 21 / 22) | `0x76` | Ambient temperature / pressure |
| **AHT20** | I2C0 (GPIO 21 / 22) | `0x38` | Ambient humidity |
| **BH1750** | I2C0 (GPIO 21 / 22) | `0x23` | Target alignment peak |
| **INA219** | I2C0 (GPIO 21 / 22) | `0x40` | Laser current / voltage |
| **AS5600 (Pan)** | I2C0 (GPIO 21 / 22) | `0x36` | Horizontal axis actual angle |
| **AS5600 (Tilt)**| I2C1 (GPIO 18 / 19) | `0x36` | Vertical axis actual angle |

*Remaining pinouts (servo PWM, transistor gate, and SPI lines for SD card) will be documented in `docs/wiring.md`.*

## Quick Start

### Build and flash ESP32

```bash
cd firmware
idf.py build
idf.py -p COM3 flash monitor
```

### Run PC serial reader

```bash
cd host
pip install -r requirements.txt
python reader.py
```

## Repository Structure

- `firmware/` – ESP-IDF source code, peripheral drivers, and FreeRTOS tasks
- `host/` – Python serial logging and OpenCV tracking scripts
- `cad/` – 3D printed brackets, sensor fixtures, and mount linkages
- `docs/` – Wiring diagrams, bus maps, and bench test notes

## License

MIT