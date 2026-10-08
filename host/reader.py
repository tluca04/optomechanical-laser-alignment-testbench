import serial
import time

ser = serial.Serial('COM3', 115200, timeout=1)

try:
    while True:
        line = ser.readline()
        if line:
            final_text = line.decode('utf-8', errors='ignore').strip()
            print(final_text)
except KeyboardInterrupt:
    print("\nStopping...")
finally: 
    ser.close()

