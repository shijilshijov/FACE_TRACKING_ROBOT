import cv2
import serial
import time


# ============================================================
# SETTINGS
# ============================================================

CAMERA_INDEX = 1 # Internal camera = '0', External camera = '1'
COM_PORT = "COM6"
BAUD_RATE = 115200


# ============================================================
# CAMERA SETTINGS
# ============================================================

CAM_WIDTH = 640
CAM_HEIGHT = 480

PROCESS_WIDTH = 480

ROTATE_CAMERA = True

MIRROR_IMAGE = True


# ============================================================
# FACE DETECTION
# ============================================================

DETECT_EVERY = 1

SMOOTHING = 0.10

DEAD_ZONE = 30


# ============================================================
# SERIAL
# ============================================================

SERIAL_INTERVAL = 0.02


# ============================================================
# CONNECT TO ARDUINO
# ============================================================

try:

    arduino = serial.Serial(
        COM_PORT,
        BAUD_RATE,
        timeout=0
    )

    time.sleep(2)

    print("Arduino connected:", COM_PORT)

except Exception as e:

    print("Arduino connection failed:")
    print(e)

    arduino = None


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(
    CAMERA_INDEX,
    cv2.CAP_DSHOW
)


if not cap.isOpened():

    print("ERROR: Camera not found.")

    if arduino is not None:
        arduino.write(b"LED:OFF\n")
        arduino.close()

    exit()


# ============================================================
# CAMERA SETTINGS
# ============================================================

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    CAM_WIDTH
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    CAM_HEIGHT
)


# Request 30 FPS

cap.set(
    cv2.CAP_PROP_FPS,
    30
)


# Small camera buffer

cap.set(
    cv2.CAP_PROP_BUFFERSIZE,
    1
)


# Autofocus OFF
# Change to 1 if you want autofocus

cap.set(
    cv2.CAP_PROP_AUTOFOCUS,
    0
)


# ============================================================
# ACTUAL CAMERA INFORMATION
# ============================================================

actual_width = int(
    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
)

actual_height = int(
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
)

actual_fps = cap.get(
    cv2.CAP_PROP_FPS
)


print()
print("Camera:")
print(
    "Resolution:",
    actual_width,
    "x",
    actual_height
)

print(
    "FPS:",
    actual_fps
)

print()


# ============================================================
# FACE DETECTOR
# ============================================================

cascade_path = (
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)


face_detector = cv2.CascadeClassifier(
    cascade_path
)


if face_detector.empty():

    print("ERROR: Face detector failed.")

    cap.release()

    if arduino is not None:
        arduino.write(b"LED:OFF\n")
        arduino.close()

    exit()


# ============================================================
# VARIABLES
# ============================================================

frame_number = 0

smooth_x = None
smooth_y = None

last_send = 0

fps_counter = 0
fps_timer = time.time()

display_fps = 0


# ============================================================
# LED STATE
# ============================================================

# Possible states:
#
# BLUE
# RED
# GREEN
# OFF

last_led_state = None


# ============================================================
# FUNCTION: SEND LED COMMAND
# ============================================================

def set_led(state):

    global last_led_state

    # Don't repeatedly send the same command
    if state == last_led_state:
        return

    if arduino is None:
        return

    command = f"LED:{state}\n"

    try:

        arduino.write(
            command.encode()
        )

        last_led_state = state

        print("LED:", state)

    except:

        pass


# ============================================================
# CAMERA STARTING
# ============================================================

# Camera is open but OpenCV viewport
# has not yet been confirmed.

set_led("BLUE")


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # READ CAMERA
    # --------------------------------------------------------

    ret, frame = cap.read()

    if not ret:
        continue


    frame_number += 1


    # --------------------------------------------------------
    # ROTATE CAMERA
    # --------------------------------------------------------

    if ROTATE_CAMERA:

        frame = cv2.rotate(
            frame,
            cv2.ROTATE_90_CLOCKWISE
        )


    # --------------------------------------------------------
    # MIRROR IMAGE
    # --------------------------------------------------------

    if MIRROR_IMAGE:

        frame = cv2.flip(
            frame,
            1
        )


    # --------------------------------------------------------
    # IMAGE SIZE
    # --------------------------------------------------------

    frame_height, frame_width = frame.shape[:2]

    center_x = frame_width // 2
    center_y = frame_height // 2


    # ========================================================
    # FACE DETECTION
    # ========================================================

    scale = PROCESS_WIDTH / frame_width

    process_height = int(
        frame_height * scale
    )


    small = cv2.resize(
        frame,
        (
            PROCESS_WIDTH,
            process_height
        )
    )


    gray = cv2.cvtColor(
        small,
        cv2.COLOR_BGR2GRAY
    )


    # Improve contrast

    gray = cv2.equalizeHist(
        gray
    )


    # --------------------------------------------------------
    # DETECT FACE
    # --------------------------------------------------------

    faces = face_detector.detectMultiScale(

        gray,

        scaleFactor=1.1,

        minNeighbors=7,

        minSize=(50, 50),

        flags=cv2.CASCADE_SCALE_IMAGE
    )


    # ========================================================
    # FACE FOUND
    # ========================================================

    if len(faces) > 0:

        # Select largest face

        face = max(
            faces,
            key=lambda f: f[2] * f[3]
        )


        x, y, w, h = face


        # ----------------------------------------------------
        # CONVERT COORDINATES
        # ----------------------------------------------------

        x = int(x / scale)
        y = int(y / scale)

        w = int(w / scale)
        h = int(h / scale)


        # Face center

        face_x = x + w // 2
        face_y = y + h // 2


        # ----------------------------------------------------
        # SMOOTH FACE POSITION
        # ----------------------------------------------------

        if smooth_x is None:

            smooth_x = float(face_x)
            smooth_y = float(face_y)

        else:

            smooth_x = (
                SMOOTHING * face_x
                +
                (1 - SMOOTHING) * smooth_x
            )

            smooth_y = (
                SMOOTHING * face_y
                +
                (1 - SMOOTHING) * smooth_y
            )


        smooth_x_int = int(smooth_x)
        smooth_y_int = int(smooth_y)


        # ----------------------------------------------------
        # DRAW FACE
        # ----------------------------------------------------

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )


        # Face center

        cv2.circle(
            frame,
            (
                smooth_x_int,
                smooth_y_int
            ),
            8,
            (0, 0, 255),
            -1
        )


        # ====================================================
        # FACE ERROR
        # ====================================================

        error_x = (
            smooth_x_int
            - center_x
        )

        error_y = (
            smooth_y_int
            - center_y
        )


        # ----------------------------------------------------
        # DEAD ZONE
        # ----------------------------------------------------

        if abs(error_x) < DEAD_ZONE:
            error_x = 0

        if abs(error_y) < DEAD_ZONE:
            error_y = 0


        # ====================================================
        # SEND FACE ERROR TO ARDUINO
        # ====================================================

        current_time = time.time()


        if (
            arduino is not None
            and
            current_time - last_send
            >= SERIAL_INTERVAL
        ):

            data = (
                str(error_x)
                + ","
                + str(error_y)
                + "\n"
            )


            try:

                arduino.write(
                    data.encode()
                )

                last_send = current_time

            except:

                pass


        # ====================================================
        # GREEN LED
        # ====================================================

        set_led("GREEN")


        # ====================================================
        # DISPLAY
        # ========================================================

        cv2.putText(
            frame,
            "FACE DETECTED",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )


        cv2.putText(
            frame,
            f"X Error: {error_x}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"Y Error: {error_y}",
            (20, 115),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )


    # ========================================================
    # NO FACE
    # ========================================================

    else:

        # ----------------------------------------------------
        # RED LED
        # ----------------------------------------------------

        set_led("RED")


        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        cv2.putText(
            frame,
            "NO FACE",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )


    # ========================================================
    # CENTER LINES
    # ========================================================

    cv2.line(
        frame,
        (center_x, 0),
        (center_x, frame_height),
        (255, 0, 0),
        1
    )


    cv2.line(
        frame,
        (0, center_y),
        (frame_width, center_y),
        (255, 0, 0),
        1
    )


    # ========================================================
    # FPS
    # ========================================================

    fps_counter += 1

    current_time = time.time()


    if current_time - fps_timer >= 1:

        display_fps = (
            fps_counter
            /
            (current_time - fps_timer)
        )

        fps_counter = 0

        fps_timer = current_time


    cv2.putText(
        frame,
        f"FPS: {display_fps:.1f}",
        (20, frame_height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # ========================================================
    # SHOW CAMERA VIEWPORT
    # ========================================================

    cv2.imshow(
        "Face Tracking Robot",
        frame
    )


    # ========================================================
    # CAMERA VIEWPORT CONFIRMATION
    # ========================================================

    # Once the OpenCV window exists,
    # turn BLUE OFF.

    try:

        window_status = cv2.getWindowProperty(
            "Face Tracking Robot",
            cv2.WND_PROP_VISIBLE
        )


        if window_status >= 1:

            # Blue is only needed during startup.
            # After viewport opens, the normal
            # face/no-face LED state takes over.

            pass

    except:

        pass


    # ========================================================
    # KEYBOARD
    # ========================================================

    key = cv2.waitKey(1) & 0xFF


    if key == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

# Turn LED OFF

set_led("OFF")


# Close camera

cap.release()


# Close Arduino

if arduino is not None:

    time.sleep(0.05)

    arduino.close()


# Close OpenCV

cv2.destroyAllWindows()


print("Program stopped.")