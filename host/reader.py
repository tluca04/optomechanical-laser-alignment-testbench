import serial
import time

ser = serial.Serial('COM3', 115200, timeout=1)
f = open("data.csv", "w")
f.write("time_ms,ax,ay,az,temp_raw,gx,gy,gz,servo_deg\n")
f.flush()

try:
    while True:
        line = ser.readline()
        if line:
            final_text = line.decode('utf-8', errors='ignore').strip()
            #print("Brut:", final_text)
            if final_text.startswith("DATA,"):
                fields = final_text.split(",")
                if len(fields) == 10:
                    f.write(",".join(fields[1:]) + '\n')
                    #f.flush()
                    #print("Salvat:", fields[1])
                else:
                    print("Invalid DATA row:", final_text)
except KeyboardInterrupt:
    print("\nStopping...")
finally: 
    ser.close()
    f.close()

