import cv2
import serial
import time
import csv
import threading
import statistics

PORT = 'COM4' #switch with current port
BAUD = 115200
FRAME_W, FRAME_H = 640, 480

DEGREES_PER_PIXEL_PAN = 0.072
DEGREES_PER_PIXEL_TILT = 0.058

KP = 0.7
MIN_STEP_DEGREES = 0.8
MAX_STEP_DEGREES = 3.0

DEADZONE_STOP = 10
DEADZONE_START = 13

PAN_APPROACH_DIRECTION = -1
TILT_APPROACH_DIRECTION = -1
SLACK_DEGREES = 3.0
PAUSE_BETWEEN_PHASES = 0.12

SETTLE_BASE = 0.18
SETTLE_PER_DEGREE = 0.04
NUMBER_OF_SAMPLES = 3

RAMP_STEP_DEGREES = 1.0
RAMP_DELAY = 0.02
PAUSE_BETWEEN_AXES = 0.10

REPOSITION_RAMP_STEP_DEGREES = 0.5
REPOSITION_RAMP_DELAY = 0.04
REPOSITION_PAUSE_BETWEEN_PHASES = 0.40

START_PAN_ANGLE = 105.0
START_TILT_ANGLE = 95.0
PAN_MIN = 50.0
PAN_MAX = 130.0
TILT_MIN = 40.0
TILT_MAX = 120.0

WAIT_AFTER_REPOSITION = 0.8
CAMERA_WARMUP_FRAMES = 15

BRIGHTNESS_THRESHOLD_MIN = 180
SPOT_MIN_AREA = 3
SPOT_MAX_AREA = 3000

SECONDS_BEFORE_SEARCH = 0.8
SEARCH_STEP_DEGREES = 8.0
SEARCH_MAX_RING = 5
SEARCH_SETTLE_TIME = 0.30
FRAMES_TO_CONFIRM_FOUND = 3
SEARCH_MAX_CYCLES = 2

ser = serial.Serial(None, BAUD, timeout=0.05, write_timeout=1)
ser.port = PORT
ser.dtr = False
ser.rts = False
ser.open()
ser.reset_input_buffer()
serial_buffer = ""

capture = None
camera_running = True
latest_frame_and_time = (None, 0.0)

pan_current_angle = 90.0
tilt_current_angle = 90.0
pan_target_angle = 90.0
tilt_target_angle = 90.0

time_of_last_command = time.time()
last_axis_moved = None

current_ramp_step = RAMP_STEP_DEGREES
current_ramp_delay = RAMP_DELAY
current_pause_between_phases = PAUSE_BETWEEN_PHASES

pan_last_move_time = 0.0
pan_last_step_size = 0.0
pan_error_samples = []
pan_is_active = False
pan_pending_target = None

tilt_last_move_time = 0.0
tilt_last_step_size = 0.0
tilt_error_samples = []
tilt_is_active = False
tilt_pending_target = None


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def read_serial_lines():
    global serial_buffer
    if ser.in_waiting > 0:
        serial_buffer += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    lines = serial_buffer.split("\n")
    serial_buffer = lines.pop()
    return [line.strip() for line in lines]


def read_camera():
    global latest_frame_and_time
    while camera_running:
        success, new_frame = capture.read()
        if not success:
            time.sleep(0.005)
            continue
        latest_frame_and_time = (new_frame, time.time())


def plan_move(axis, degrees_to_move, force_backlash_pass=False):
    global pan_target_angle, tilt_target_angle
    global pan_pending_target, tilt_pending_target
    global pan_last_step_size, tilt_last_step_size

    if axis == "pan":
        current_angle = pan_current_angle
        angle_min = PAN_MIN
        angle_max = PAN_MAX
        approach_direction = PAN_APPROACH_DIRECTION
    else:
        current_angle = tilt_current_angle
        angle_min = TILT_MIN
        angle_max = TILT_MAX
        approach_direction = TILT_APPROACH_DIRECTION

    final_angle = clamp(current_angle + degrees_to_move, angle_min, angle_max)

    if degrees_to_move * approach_direction > 0 and not force_backlash_pass:
        new_target_angle = final_angle
        new_step_size = abs(final_angle - current_angle)
        new_pending_target = None
    else:
        new_target_angle = clamp(final_angle - approach_direction * SLACK_DEGREES, angle_min, angle_max)
        new_step_size = 0.0
        new_pending_target = final_angle

    if axis == "pan":
        pan_target_angle = new_target_angle
        pan_last_step_size = new_step_size
        pan_pending_target = new_pending_target
    else:
        tilt_target_angle = new_target_angle
        tilt_last_step_size = new_step_size
        tilt_pending_target = new_pending_target


def update_servos():
    global pan_current_angle, tilt_current_angle
    global pan_target_angle, tilt_target_angle
    global pan_pending_target, tilt_pending_target
    global pan_last_step_size, tilt_last_step_size
    global pan_last_move_time, tilt_last_move_time
    global time_of_last_command, last_axis_moved

    now = time.time()

    if now - time_of_last_command >= current_pause_between_phases:
        if pan_pending_target is not None and pan_current_angle == pan_target_angle:
            pan_target_angle = clamp(pan_pending_target, PAN_MIN, PAN_MAX)
            pan_last_step_size = abs(pan_target_angle - pan_current_angle)
            pan_pending_target = None
        if tilt_pending_target is not None and tilt_current_angle == tilt_target_angle:
            tilt_target_angle = clamp(tilt_pending_target, TILT_MIN, TILT_MAX)
            tilt_last_step_size = abs(tilt_target_angle - tilt_current_angle)
            tilt_pending_target = None

    if now - time_of_last_command < current_ramp_delay:
        return

    if pan_current_angle != pan_target_angle:
        axis = "pan"
    elif tilt_current_angle != tilt_target_angle:
        axis = "tilt"
    else:
        return

    if last_axis_moved is not None and axis != last_axis_moved and now - time_of_last_command < PAUSE_BETWEEN_AXES:
        return

    if axis == "pan":
        difference = pan_target_angle - pan_current_angle
        if abs(difference) <= current_ramp_step:
            pan_current_angle = pan_target_angle
        elif difference > 0:
            pan_current_angle += current_ramp_step
        else:
            pan_current_angle -= current_ramp_step
        pan_last_move_time = now
    else:
        difference = tilt_target_angle - tilt_current_angle
        if abs(difference) <= current_ramp_step:
            tilt_current_angle = tilt_target_angle
        elif difference > 0:
            tilt_current_angle += current_ramp_step
        else:
            tilt_current_angle -= current_ramp_step
        tilt_last_move_time = now

    ser.write(f"CMD,{pan_current_angle:.1f},{tilt_current_angle:.1f}\n".encode('utf-8'))
    time_of_last_command = now
    last_axis_moved = axis


search_points = [(0, 0)]
spiral_x = 0
spiral_y = 0
spiral_direction_x = 1
spiral_direction_y = 0
spiral_segment_length = 1
total_search_points = (2 * SEARCH_MAX_RING + 1) ** 2
while len(search_points) < total_search_points:
    for _ in range(2):
        for _ in range(spiral_segment_length):
            spiral_x += spiral_direction_x
            spiral_y += spiral_direction_y
            search_points.append((spiral_x, spiral_y))
        spiral_direction_x, spiral_direction_y = -spiral_direction_y, spiral_direction_x
    spiral_segment_length += 1
search_points = search_points[:total_search_points]

search_center_pan = 90.0
search_center_tilt = 90.0
search_index = 0
search_cycle = 0
search_confirm_count = 0
search_is_parked = False

csv_file = None
camera_thread = None

try:
    initial_angles = None
    start_time = time.time()
    while initial_angles is None and time.time() - start_time < 2.0:
        for line in read_serial_lines():
            if line.startswith("DATA,"):
                parts = line.split(",")
                if len(parts) >= 11:
                    try:
                        initial_angles = (float(parts[9]), float(parts[10]))
                    except ValueError:
                        pass
        time.sleep(0.01)

    if initial_angles is None:
        print("Did not receive DATA from the ESP32, assuming 90/90.")
        initial_angles = (90.0, 90.0)
    else:
        print(f"Current position: pan={initial_angles[0]:.1f}, tilt={initial_angles[1]:.1f}")

    pan_current_angle, tilt_current_angle = initial_angles
    pan_target_angle, tilt_target_angle = initial_angles
    time_of_last_command = time.time()

    current_ramp_step = REPOSITION_RAMP_STEP_DEGREES
    current_ramp_delay = REPOSITION_RAMP_DELAY
    current_pause_between_phases = REPOSITION_PAUSE_BETWEEN_PHASES
    print("Moving to the start position...")

    start_pan = clamp(START_PAN_ANGLE, PAN_MIN, PAN_MAX)
    start_tilt = clamp(START_TILT_ANGLE, TILT_MIN, TILT_MAX)
    plan_move("pan", start_pan - pan_current_angle, start_pan == pan_current_angle)
    plan_move("tilt", start_tilt - tilt_current_angle, start_tilt == tilt_current_angle)

    while not (pan_current_angle == pan_target_angle and tilt_current_angle == tilt_target_angle
               and pan_pending_target is None and tilt_pending_target is None):
        update_servos()
        read_serial_lines()
        time.sleep(0.002)
    time.sleep(WAIT_AFTER_REPOSITION)

    current_ramp_step = RAMP_STEP_DEGREES
    current_ramp_delay = RAMP_DELAY
    current_pause_between_phases = PAUSE_BETWEEN_PHASES
    print("Reached the start position. Starting the camera...")

    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not capture.isOpened():
        raise RuntimeError("Cannot open the camera")
    capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
    capture.set(cv2.CAP_PROP_FPS, 30)
    capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    camera_thread = threading.Thread(target=read_camera, daemon=True)
    camera_thread.start()

    start_time = time.time()
    frames_seen = 0
    previous_frame_time = 0.0
    while frames_seen < CAMERA_WARMUP_FRAMES and time.time() - start_time < 5.0:
        frame, frame_time = latest_frame_and_time
        if frame is not None and frame_time != previous_frame_time:
            previous_frame_time = frame_time
            frames_seen += 1
        time.sleep(0.005)

    ser.reset_input_buffer()
    serial_buffer = ""

    pan_last_move_time = 0.0
    pan_last_step_size = 0.0
    pan_pending_target = None
    pan_is_active = False
    pan_error_samples.clear()
    tilt_last_move_time = 0.0
    tilt_last_step_size = 0.0
    tilt_pending_target = None
    tilt_is_active = False
    tilt_error_samples.clear()

    csv_file = open("data.csv", "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["time_ms", "ax", "ay", "az", "gx", "gy", "gz", "pan_deg", "tilt_deg", "err_x", "err_y"])

    program_start_time = time.time()
    last_flush_time = time.time()
    previous_frame_time = 0.0
    error_x = None
    error_y = None
    mode = "TRACK"
    lost_since = None
    print("Started. Press 'q' to stop.")

    while True:
        update_servos()

        for line in read_serial_lines():
            if line.startswith("DATA,"):
                parts = line.split(",")
                if len(parts) >= 9:
                    time_ms = int((time.time() - program_start_time) * 1000)
                    csv_writer.writerow([time_ms] + parts[2:5] + parts[6:9] + [round(pan_current_angle, 1), round(tilt_current_angle, 1), error_x, error_y])
        if time.time() - last_flush_time > 1.0:
            csv_file.flush()
            last_flush_time = time.time()

        frame, frame_time = latest_frame_and_time
        if frame is None or frame_time == previous_frame_time:
            time.sleep(0.002)
            continue
        previous_frame_time = frame_time

        image_height, image_width, _ = frame.shape
        center_x = image_width / 2.0
        center_y = image_height / 2.0

        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        threshold = max(BRIGHTNESS_THRESHOLD_MIN, int(gray_image.max()) - 15)
        _, binary_mask = cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_contour = None
        best_contour_area = -1
        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)
            box_area = width * height
            if box_area < SPOT_MIN_AREA or box_area > SPOT_MAX_AREA:
                continue
            area = cv2.contourArea(contour)
            if area > best_contour_area:
                best_contour = contour
                best_contour_area = area

        spot = None
        if best_contour is not None:
            moments = cv2.moments(best_contour)
            if moments["m00"] > 0:
                spot = (moments["m10"] / moments["m00"], moments["m01"] / moments["m00"])
            else:
                x, y, width, height = cv2.boundingRect(best_contour)
                spot = (x + width / 2.0, y + height / 2.0)

        if spot is None:
            error_x = None
            error_y = None
        else:
            spot_x, spot_y = spot
            error_x = round(center_x - spot_x, 1)
            error_y = round(center_y - spot_y, 1)
            cv2.circle(frame, (int(spot_x), int(spot_y)), 10, (0, 255, 0), 2)

        servos_are_busy = not (pan_current_angle == pan_target_angle and tilt_current_angle == tilt_target_angle and pan_pending_target is None and tilt_pending_target is None)

        if spot is None:
            if lost_since is None:
                lost_since = frame_time
        else:
            lost_since = None

        if mode == "TRACK":
            if lost_since is not None and frame_time - lost_since > SECONDS_BEFORE_SEARCH and not servos_are_busy:
                print("Laser is not found in the frame. Searching for it...")
                mode = "SEARCH"
                search_center_pan = pan_current_angle
                search_center_tilt = tilt_current_angle
                search_index = 0
                search_cycle = 0
                search_confirm_count = 0
                search_is_parked = False
                pan_error_samples.clear()
                tilt_error_samples.clear()
                pan_is_active = False
                tilt_is_active = False
        else:
            if not servos_are_busy and frame_time > time_of_last_command + SEARCH_SETTLE_TIME:
                if spot is not None:
                    search_confirm_count += 1
                    if search_confirm_count >= FRAMES_TO_CONFIRM_FOUND:
                        print("Laser found, going back to tracking.")
                        mode = "TRACK"
                        pan_error_samples.clear()
                        tilt_error_samples.clear()
                        pan_is_active = False
                        tilt_is_active = False
                        pan_last_step_size = 0.0
                        tilt_last_step_size = 0.0
                else:
                    search_confirm_count = 0
                    while not search_is_parked:
                        if search_index >= len(search_points):
                            search_cycle += 1
                            search_index = 0
                            if search_cycle >= SEARCH_MAX_CYCLES:
                                search_is_parked = True
                                print("Laser not found. Going back to the start and waiting...")
                                pan_target_angle = search_center_pan
                                tilt_target_angle = search_center_tilt
                            continue
                        offset_i, offset_j = search_points[search_index]
                        search_index += 1
                        new_pan = clamp(search_center_pan + offset_i * SEARCH_STEP_DEGREES, PAN_MIN, PAN_MAX)
                        new_tilt = clamp(search_center_tilt + offset_j * SEARCH_STEP_DEGREES, TILT_MIN, TILT_MAX)
                        if abs(new_pan - pan_current_angle) < 0.5 and abs(new_tilt - tilt_current_angle) < 0.5:
                            continue
                        pan_target_angle = new_pan
                        tilt_target_angle = new_tilt
                        break

        if mode == "TRACK":
            a_servo_is_moving = (pan_current_angle != pan_target_angle) or (tilt_current_angle != tilt_target_angle)

            if not (pan_current_angle == pan_target_angle and pan_pending_target is None):
                pan_error_samples.clear()
            elif spot is not None and not a_servo_is_moving \
                    and frame_time > pan_last_move_time + SETTLE_BASE + SETTLE_PER_DEGREE * pan_last_step_size:
                pan_error_samples.append(error_x)
                if len(pan_error_samples) >= NUMBER_OF_SAMPLES:
                    median_error = statistics.median(pan_error_samples)
                    pan_error_samples.clear()
                    if abs(median_error) > DEADZONE_START:
                        pan_is_active = True
                    elif abs(median_error) <= DEADZONE_STOP:
                        pan_is_active = False
                    if pan_is_active:
                        step = clamp(KP * abs(median_error) * DEGREES_PER_PIXEL_PAN, MIN_STEP_DEGREES, MAX_STEP_DEGREES)
                        if median_error > 0:
                            plan_move("pan", -step)
                        else:
                            plan_move("pan", step)

            if not (tilt_current_angle == tilt_target_angle and tilt_pending_target is None):
                tilt_error_samples.clear()
            elif spot is not None and not a_servo_is_moving \
                    and frame_time > tilt_last_move_time + SETTLE_BASE + SETTLE_PER_DEGREE * tilt_last_step_size:
                tilt_error_samples.append(error_y)
                if len(tilt_error_samples) >= NUMBER_OF_SAMPLES:
                    median_error = statistics.median(tilt_error_samples)
                    tilt_error_samples.clear()
                    if abs(median_error) > DEADZONE_START:
                        tilt_is_active = True
                    elif abs(median_error) <= DEADZONE_STOP:
                        tilt_is_active = False
                    if tilt_is_active:
                        step = clamp(KP * abs(median_error) * DEGREES_PER_PIXEL_TILT, MIN_STEP_DEGREES, MAX_STEP_DEGREES)
                        if median_error > 0:
                            plan_move("tilt", step)
                        else:
                            plan_move("tilt", -step)

        cv2.circle(frame, (int(center_x), int(center_y)), DEADZONE_STOP, (0, 0, 255), 2)
        cv2.putText(frame, mode, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) == ord('q'):
            break

except serial.SerialException as e:
    print(f"Serial error: {e}")
    print("The port disappeared, probably the ESP32 reset or the USB got disconnected.")
    print(f"Last angles: pan={pan_current_angle:.1f}, tilt={tilt_current_angle:.1f}")
except KeyboardInterrupt:
    pass
finally:
    camera_running = False
    if camera_thread is not None:
        camera_thread.join(timeout=1.0)
    if csv_file is not None:
        csv_file.close()
    if capture is not None:
        capture.release()
    try:
        ser.close()
    except Exception:
        pass
    cv2.destroyAllWindows()