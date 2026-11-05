# Optomechanical Laser Alignment Testbench

Testbench built to evaluate how well camera feedback and mechanical spring preloading can compensate for backlash and vibration in cheap SG90 micro-servos when steering a laser beam.

An ESP32 controls a 2-axis pan-tilt mount carrying a 650 nm laser diode (KY-008), while reading an MPU-6050 IMU. A webcam connected to the PC tracks the laser spot and measures its offset from the center of the camera image. The PC sends pan/tilt corrections to the ESP32 over UART to bring the laser spot back to the center

## Hardware notes

The pan-tilt bracket is 3D-printed and uses springs to preload the servo gears. Since SG90 servos draw current spikes that can reset or add noise to the ESP32, the servos and laser run on a separate 5V rail from an LM2596 buck converter. The laser is switched through an NPN transistor.

Sensors on the rig:
- MPU-6050 IMU on the laser bracket to measure vibrations and impacts.

## Physical Setup

<p align="center">
  <img src="docs/testbench_setup.jpg" alt="Testbench physical setup" width="400">
</p>

Current bench setup with the 3D-printed pan-tilt mount, SG90 servos, KY-008 laser diode, and the MPU-6050 mounted directly on the top tilt bracket. The ESP32 sits on the breadboard with the 100 nF decoupling capacitor on the 5V rail and the NPN transistor switch (1k base resistor, 10k pull-down) driving the laser on GPIO 27.


## I2C Address

3.3V logic

| Component | Bus / Pins | Address | Notes |
| :--- | :--- | :--- | :--- |
| MPU-6050 | I2C0 (GPIO 21 / 22) | 0x68 | IMU on laser bracket (clone chip, WHO_AM_I = 0x72) |

Other pins (servo PWM, laser transistor, SPI) are listed in docs/wiring.md.

## Camera-Centering & IMU Validation Test

MPU-6050 at 100 Hz (sample rate divider 9, DLPF 44 Hz), ±2 g and ±250 deg/s. The IMU is mounted directly on the moving tilt bracket next to the laser. The test starts with the laser spot away from the center of the camera image. The PC detects the spot, calculates the horizontal and vertical error in pixels, and continuously sends servo corrections over UART.

![IMU and servo test](docs/imu_100hz_validation.png)

<p align="center">
  <img src="docs/setup.jpeg" alt="Testbench physical setup" height="513">
  <img src="docs/laser_centered.jpeg" alt="Laser spot centered in camera image" width="400">
</p>

Final alignment result, with the laser spot positioned close to the center of the camera image after the pan-tilt correction loop converges.

 - 0.0 - 0.2 s: Initial position, with the laser spot offset from the camera center (approximately +52 px on X and -165 px on Y). The servos start at around pan 105° and tilt 95°.
 - 0.2 - 1.0 s: The first corrections begin. Both servo angles decrease in steps, moving the laser closer to the center. The Y error starts dropping significantly, while the IMU records the initial movement and mechanical vibrations.
 - 1.0 - 1.8 s: The controller makes further corrections. Pan briefly moves back up to around 104° before returning toward 100°, while tilt continues moving down. This produces another change in the X error, while the Y error keeps getting closer to zero. The IMU records the largest angular velocity spikes during these movements.
 - 1.8 - 2.6 s: The servo positions settle around pan 100° and tilt 85.5°. Both X and Y errors converge toward zero as the laser spot reaches the center of the camera image. The vibrations measured by the IMU gradually die out.
 - 2.6 - 10.1 s: The system remains stable, with no significant servo movement. Both errors stay close to zero, acceleration remains nearly constant, and gyroscope readings stay around 0 deg/s. The laser spot is maintained near the center of the camera image.
 - 10.1 s: A short disturbance appears in the accelerometer and gyroscope readings. The servo positions remain unchanged, and the camera error shows only a small variation.
 - 10.1 - 12.3 s: The system remains stable after the disturbance, with the laser spot still close to the camera center and the IMU readings returning to their previous levels.

The servo angle plots show commanded positions rather than measured shaft angles. The camera provides the feedback used for positioning, while the IMU measures the movement and vibrations of the laser bracket during the alignment process.

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