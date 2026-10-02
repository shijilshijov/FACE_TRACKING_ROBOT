============================================================
FACE TRACKING ROBOT - SETUP & INSTALLATION GUIDE
============================================================

This project consists of a Python script running in PyCharm (handling computer vision and face detection via OpenCV) and an Arduino sketch (controlling pan/tilt servos and status LEDs using PID control).

---

### 1. PYTHON REQUIREMENTS (PyCharm)

The Python script requires a few external packages to work with your camera and communicate via serial.

Required Libraries:
- "opencv-python" (For camera streaming and face detection)
- "pyserial" (For sending tracking data to the Arduino)
- "numpy" (For mathematical and array operations)

How to Install in PyCharm:
1. Open your project in PyCharm.
2. Go to 'File' > 'Settings' (or 'Preferences' on macOS) > Project: "FACE_TRACKING_ROBOT" > 'Python Interpreter'.
3. Click the '+'(Install) button in the top-left or middle area.
4. Search for "opencv-python", select it, and click 'Install Package'.
5. Do the same for "pyserial" and "numpy".
6. Alternatively, you can open the PyCharm **Terminal** at the bottom and run:
   "pip install opencv-python pyserial numpy"

---

### 2. ARDUINO REQUIREMENTS (Arduino IDE)

The microcontroller code controls the hardware and expects specific libraries installed in your Arduino environment.

Required Libraries:
- "Servo" (Built-in standard Arduino library for controlling servo motors)

How to Add/Check in Arduino IDE:
1. Open the Arduino IDE.
2. Go to 'Sketch' > 'Include Library' > 'Manage Libraries...'
3. Search for "Servo" and ensure it is installed (it usually comes pre-installed with the Arduino IDE).
4. Open the Arduino code folder included in this project, upload the sketch to your board, and ensure the correct COM port and baud rate ("115200") match your settings.

---

### 3. CONFIGURATION & RUNNING

1. Connections: Plug your Arduino into your computer and check the COM port (e.g., "COM6" as specified in the Python settings, or update it in "Face_Tracking.py" to match yours).
2. Hardware: Make sure your camera index, servo pins, and RGB LED pins match your physical wiring.
3. Execution: Run "Face_Tracking.py" from PyCharm while your Arduino is powered and connected. 
4. Quit: Press "q" inside the camera viewport window to stop the program safely.


============================================================
AUTHOR / CREDITS
============================================================
Project Developed by: SHIJIL SHIJO
Team members: Karthik N Nair, Irfan S, Saheel Siraj, Shijil Shijo
College: KMEA Engineering College, Ernakulam
University: KTU (APJ Abdul Kalam Technological University)
Degree: B.Tech in Robotics and Automation Engineering

Feel free to reach out or use this project for your own robotics and automation learning!