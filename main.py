import cv2
import mediapipe as mp
import math
import time

# === SETTINGS ===
FAIL_THRESHOLD = 2.5  # seconds to lockout before failure
DOWN_ANGLE = 90       # elbow angle for bottom position
UP_ANGLE = 175        # elbow angle for top position
ANGLE_TOLERANCE = 5   # +/- tolerance in degrees

# === MODE SETUP ===
MODE = input("Choose mode (endurance/time): ").strip().lower()
if MODE == "time":
    try:
        duration_minutes = float(input("Enter workout duration in minutes (can be decimal): "))
        duration_seconds = duration_minutes * 60
    except ValueError:
        print("Invalid input, defaulting to 1 minute.")
        duration_seconds = 60
else:
    duration_seconds = None

# === FUNCTIONS ===
def calculate_angle(a, b, c):
    """Returns the angle (in degrees) formed by points a-b-c."""
    a, b, c = (a.x, a.y), (b.x, b.y), (c.x, c.y)
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    dot = ba[0]*bc[0] + ba[1]*bc[1]
    mag_a = math.sqrt(ba[0]**2 + ba[1]**2)
    mag_c = math.sqrt(bc[0]**2 + bc[1]**2)
    if mag_a * mag_c == 0:
        return 180
    angle = math.degrees(math.acos(dot / (mag_a * mag_c)))
    return angle

def send_fail_command():
    # --- Placeholder for ESP32 WebSocket trigger ---
    print("FAILED")  # replace with socket send when ready


# === MEDIAPIPE SETUP ===
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)
cap = cv2.VideoCapture(0)

pushup_started = False
pushup_bottom_time = None
pushup_count = 0
failed = False
last_state = ""
start_time = time.time()

# === MAIN LOOP ===
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)
    frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    current_time = time.time()

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark

        # Landmarks for both sides
        left_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = lm[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST.value]

        right_shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_elbow = lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        right_wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST.value]

        # Calculate angles
        left_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        avg_angle = (left_angle + right_angle) / 2

        # Draw landmarks + elbows
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        cv2.putText(frame, f"L: {int(left_angle)}°  R: {int(right_angle)}°", (30, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

        # DOWN detection
        if avg_angle < (DOWN_ANGLE + ANGLE_TOLERANCE) and not pushup_started:
            pushup_started = True
            pushup_bottom_time = current_time
            last_state = "DOWN"

        # UP detection
        elif avg_angle > (UP_ANGLE - ANGLE_TOLERANCE) and pushup_started:
            elapsed = current_time - pushup_bottom_time
            if elapsed > FAIL_THRESHOLD:
                failed = True
                send_fail_command()
                last_state = "FAILED"
            else:
                pushup_count += 1
                last_state = "LOCKED OUT"
            pushup_started = False

        # === VISUAL FEEDBACK ===
        if last_state == "DOWN":
            cv2.putText(frame, "DOWN POSITION", (180, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 140, 255), 4)
        elif last_state == "LOCKED OUT":
            cv2.putText(frame, "LOCKED OUT", (200, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 0), 4)
        elif last_state == "FAILED":
            cv2.putText(frame, "FAIL DETECTED", (180, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 4)

    # === Timer / HUD ===
    elapsed_time = time.time() - start_time
    if MODE == "time" and elapsed_time > duration_seconds:
        print(f"⏱️ Time limit reached: {duration_minutes} minute(s)")
        break

    cv2.putText(frame, f"Mode: {MODE.upper()}", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.putText(frame, f"Pushups: {pushup_count}", (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    if MODE == "time":
        remaining = max(0, duration_seconds - elapsed_time)
        mins, secs = divmod(int(remaining), 60)
        cv2.putText(frame, f"Time Left: {mins:02}:{secs:02}", (30, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 255), 2)

    cv2.imshow("Push-up Tracker (Elbow Angle Debug)", frame)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
print(f"Workout ended. Total pushups: {pushup_count}")
