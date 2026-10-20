import serial
import time

ser = serial.Serial('COM3', 115200, timeout=1)
f = open("data.csv", "w")
f.write("time_ms,ax,ay,az,temp_raw,gx,gy,gz,pan_deg,tilt_deg\n")
f.flush()


try:
    start_time = time.time()
    step = 0
    while True:
        elapsed = time.time() - start_time
        if elapsed > 2.0 and step == 0:
            ser.write(b"CMD,45.0,90.0\n")
            step = 1
        elif elapsed > 3.0 and step == 1:
            ser.write(b"CMD,45.0,120.0\n")
            step = 2
        elif elapsed > 4.0 and step == 2:   
            ser.write(b"CMD,135.0,120.0\n")
            step = 3
        elif elapsed > 5.0 and step == 3: 
            ser.write(b"CMD,135.0,60.0\n")
            step = 4

        line = ser.readline()
        if line:
            final_text = line.decode('utf-8', errors='ignore').strip()
            #print("Brut:", final_text)
            if final_text.startswith("DATA,"):
                fields = final_text.split(",")
                if len(fields) == 11:
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

