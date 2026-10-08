# Optomechanical Laser Alignment Testbench

Experimental testbench setup for monitoring and stabilizing optical mounts during laser alignment experiments.

This repository hosts the ESP32 firmware and serial tools used to monitor optical mount motion and stability on a laser testbench.

## Current State

- [x] Basic I2C communication verified using ESP-IDF v5/v6 `i2c_master` driver.
- [x] Device validation via MPU-6050 `WHO_AM_I` register read (`0x72`/`0x68`).
- [x] Basic host-side serial receiver (`host/reader.py`).
- [ ] Raw accelerometer and gyroscope register polling loop.
- [ ] Sensor calibration and offset calculation.

## Hardware Connections

| MPU-6050 Pin | ESP32 GPIO | Notes |
| :--- | :--- | :--- |
| **VCC** | 3V3 | Regulated |
| **GND** | GND | Common ground |
| **SCL** | GPIO 22 | I2C Clock (Internal pull-up enabled) |
| **SDA** | GPIO 21 | I2C Data (Internal pull-up enabled) |

## Build & Flash

### Firmware (ESP-IDF)

```bash
idf.py build
idf.py -p COM3 flash monitor
```

### Host Receiver (Python)

```bash
cd host
pip install -r requirements.txt
python reader.py
```

## Repository Structure

- `firmware/` – ESP-IDF C source code and hardware configuration.
- `host/` – Python acquisition scripts.
- `cad/` – Fixtures and 3D-printed mounts.
- `docs/` – Schematics and test notes.

## License

MIT