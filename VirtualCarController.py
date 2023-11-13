import cv2
import math
import vgamepad as vg
import mediapipe as mp

class VirtualCarController:
    def __init__(self):
        self.gamepad = vg.VX360Gamepad()
        self.mpDraw = mp.solutions.drawing_utils
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=2)
        self.camera = cv2.VideoCapture(0)

    def normalize_angle(self, angle, a_min, a_max):
        return (abs(angle) - a_min) / (a_max - a_min)

    def calculate_angle(self, p1, p2):
        delta_x = p2[0] - p1[0]
        delta_y = p2[1] - p1[1]
        theta = math.atan(delta_y/ delta_x)
        return math.degrees(theta)

    def control_steering(self, angle):
        a_min, a_max = 1, 30
        print(angle)
        if angle > a_min:
            if angle > a_max:
                angle = a_max
            self.gamepad.left_joystick_float(self.normalize_angle(angle, a_min, a_max), 0)
            print("Right")
        elif angle < -a_min:
            if angle < -a_max:
                angle = -a_max
            self.gamepad.left_joystick_float(-self.normalize_angle(angle, a_min, a_max), 0)
            print("Left")
        else:
            self.gamepad.left_joystick_float(0, 0)
            print("Forward")
   

    def run(self):
        while True:
            try:
                ret, frame = self.camera.read()
                frame =cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(frame_rgb) 

                double_hands = ([], [])
                if results.multi_hand_landmarks:
                    for index, hands_lms in enumerate(results.multi_hand_landmarks):
                        for id, lm in enumerate(hands_lms.landmark):
                            h, w, _ = frame.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            double_hands[index].append((cx, cy))

                        self.mpDraw.draw_landmarks(frame, hands_lms, self.mpHands.HAND_CONNECTIONS)

                    try:
                        angle = self.calculate_angle(double_hands[0][0], double_hands[1][0])
                        cv2.putText(frame, f"Angle: {int(angle)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        self.control_steering(angle)

                        self.gamepad.update()
                        cv2.line(frame, double_hands[0][0], double_hands[1][0], (255, 0, 0), 3)
                    except Exception as e:
                          print(f"Error processing landmarks: {e}")

                cv2.imshow("Virtual driving control", frame)
            except:
                pass
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
