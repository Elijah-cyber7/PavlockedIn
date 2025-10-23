====================================================
ESP32 PUSH-UP FAILURE DETECTION SYSTEM
====================================================

PROJECT OVERVIEW
----------------
This project uses a webcam (via OpenCV and MediaPipe) to monitor a person performing push-ups in real time.
It detects when a repetition is failed—meaning the user takes longer than 2.5 seconds to return from the
bottom position—and sends a signal to an ESP32 microcontroller, which triggers a relay for 0.25 seconds.

Two modes of operation are available:
1. ENDURANCE MODE – Continue until failure.
2. TIMED MODE – Perform push-ups for a user-specified duration (in minutes, decimals allowed).

The system displays real-time overlays including:
- Pose landmarks and elbow angles.
- “DOWN”, “RECOVERED”, and “FAILED” labels for feedback.
- Timer display (in timed mode).

----------------------------------------------------
SYSTEM COMPONENTS
----------------------------------------------------
Component           | Function
--------------------|-------------------------------------------
ESP32               | Hosts Wi-Fi socket server, controls relay.
Relay Module        | Energizes for 0.25 seconds on failure.
Webcam              | Captures live video for pose tracking.
Python + OpenCV     | Performs landmark and failure detection.

----------------------------------------------------
HARDWARE SETUP
----------------------------------------------------
REQUIRED COMPONENTS:
- ESP32 development board
- 1-channel or 2-channel relay module
- USB cable for programming
- Jumper wires

PIN CONFIGURATION:
ESP32 Pin | Component | Notes
-----------|------------|------------------------------
D6 (GPIO6) | Relay IN   | Trigger output (HIGH for 0.25s)
5V / VIN   | Relay VCC  | Power for relay
GND        | Relay GND  | Common ground with ESP32

NOTE: GPIO6–11 are reserved on some ESP32 boards.
If GPIO6 causes issues, replace it with GPIO23 or GPIO25.

----------------------------------------------------
ESP32 FIRMWARE DETAILS
----------------------------------------------------
FEATURES:
- Connects to Wi-Fi and prints its local IP address.
- Opens TCP server on port 8080.
- Waits for Python client connection.
- Listens for “FAIL” messages.
- Activates relay for 0.25 seconds on failure.
- Prints status messages via Serial Monitor.

SERIAL OUTPUT EXAMPLE:
Connecting to WiFi...
WiFi connected.
Server listening on IP: 192.168.1.123, Port: 8080
Client connected.
FAIL signal received — activating relay.
Relay deactivated.

----------------------------------------------------
PYTHON SCRIPT DETAILS
----------------------------------------------------
FUNCTIONALITY:
- Captures webcam video using OpenCV.
- Uses MediaPipe Pose to detect elbows and calculate angles.
- Detects DOWN when elbows bend beyond threshold (~180 ± 5 degrees).
- If the user remains in the DOWN position for more than 2.5 seconds,
  the script flags a FAILED condition and sends a signal to the ESP32.
- Displays a visual overlay for debugging and feedback.

DEBUG OVERLAY:
- Pose landmarks and elbow angle visualization.
- Text overlays: “DOWN”, “RECOVERED”, “FAILED”.
- In timed mode: countdown timer display.

OPERATION MODES:
1. ENDURANCE MODE – Runs indefinitely until a failure occurs.
2. TIMED MODE – Runs for a user-specified duration (e.g., 1.5 minutes).

----------------------------------------------------
SOFTWARE REQUIREMENTS
----------------------------------------------------
Component         | Version | Purpose
------------------|----------|--------------------------
Python            | ≥3.8     | Main runtime
OpenCV (cv2)      | Latest   | Image processing
MediaPipe         | Latest   | Pose tracking
ESP32 Arduino Core| ≥2.0     | Wi-Fi and socket features

INSTALL PYTHON DEPENDENCIES:
pip install opencv-python mediapipe

----------------------------------------------------
SETUP INSTRUCTIONS
----------------------------------------------------

1. FLASH THE ESP32
------------------
- Open the ESP32 .ino file in Arduino IDE.
- Replace Wi-Fi credentials:
  const char* ssid = "YourNetworkName";
  const char* password = "YourPassword";
- Upload the sketch.
- Open Serial Monitor and note the IP address printed after connection.

2. CONFIGURE THE PYTHON SCRIPT
------------------------------
- Open the Python file and update:
  ESP32_IP = "192.168.1.123"  # Use the IP shown in Serial Monitor
  ESP32_PORT = 8080
- Comment/uncomment the socket send command during testing.

3. RUN THE PYTHON SCRIPT
------------------------
python pushup_detection.py

You’ll be prompted to select a mode:
Select mode: (1) Endurance  (2) Timed

If choosing timed mode:
Enter duration in minutes (decimals allowed): 1.5

----------------------------------------------------
EXPECTED BEHAVIOR
----------------------------------------------------
Condition                  | System Action
----------------------------|----------------------------------
User begins push-ups        | Landmarks start tracking
User goes down              | “DOWN” overlay appears
User locks out arms         | “RECOVERED” overlay appears
Down position >2.5 seconds  | “FAILED” overlay + relay trigger
Timed session expires       | Automatic end of detection

----------------------------------------------------
TROUBLESHOOTING
----------------------------------------------------
Issue                         | Cause                        | Solution
-------------------------------|-------------------------------|--------------------------
ESP32 not connecting           | Wrong Wi-Fi credentials       | Check SSID/password
Relay not triggering           | Wrong GPIO or wiring          | Use GPIO23 or check wiring
Python can’t connect to ESP32  | Incorrect IP or port          | Check Serial output and update script
Pose not detected              | Poor camera angle or lighting | Ensure full body visible, good lighting

----------------------------------------------------
FUTURE ENHANCEMENTS
----------------------------------------------------
- Add MQTT or HTTP POST for remote logging.
- Add BLE option for wireless control.
- Multi-person pose tracking.
- Integration with fitness tracking APIs.
- OLED display on ESP32 for live stats.

----------------------------------------------------
AUTHOR & INFO
----------------------------------------------------
Project Lead: Andrew Allen
Technologies: ESP32, OpenCV, MediaPipe, Python, Sockets
Last Updated: October 2025
====================================================
