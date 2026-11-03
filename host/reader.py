import serial
import time

ser = serial.Serial(None, 115200, timeout=1, write_timeout=1)
ser.port = 'COM4'
ser.dtr = False
ser.rts = False
ser.open()
ser.reset_input_buffer()

f = open("data.csv", "w")
f.write("time_ms,ax,ay,az,temp_raw,gx,gy,gz,pan_deg,tilt_deg\n")
f.flush()


try:
    start_time = time.time()
    step = 0
    while True:
        elapsed = time.time() - start_time
        if elapsed > 1.0 and step == 0:
            ser.write(b"CMD,70.0,90.0\n")
            step = 1
        elif elapsed > 1.8 and step == 1:
            ser.write(b"CMD,70.0,105.0\n")
            step = 2
        elif elapsed > 2.6 and step == 2:   
            ser.write(b"CMD,110.0,105.0\n")
            step = 3
        elif elapsed > 3.4 and step == 3: 
            ser.write(b"CMD,110.0,85.0\n")
            step = 4
        elif elapsed > 4.2 and step == 4:
            ser.write(b"CMD,90.0,85.0\n")
            step = 5
        elif elapsed > 5.0 and step == 5:
            ser.write(b"CMD,90.0,90.0\n")
            step = 6
        elif elapsed > 6.0 and step == 6:
            break

        line = ser.readline()
        if line:
            final_text = line.decode('utf-8', errors='ignore').strip()
            if final_text.startswith("DATA,"):
                fields = final_text.split(",")
                if len(fields) == 11:
                    f.write(",".join(fields[1:]) + '\n')
                else:
                    print("Invalid DATA row:", final_text)
except KeyboardInterrupt:
    print("\nStopping...")
finally: 
    ser.close()
    f.close()