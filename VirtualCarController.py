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
        self.speed = 0
    def normalize_value(self, value, v_min, v_max):
        value = abs(value)

        if(value >= v_max):
            return 1
        if(value <= v_min):
            return 0
        
        return (value - v_min) / (v_max - v_min)

    def calculate_angle(self, p1, p2):
        delta_x = p2[0] - p1[0]
        delta_y = p2[1] - p1[1]
        theta = math.atan(delta_y/ delta_x)
        return math.degrees(theta)

    def calculate_distance(self,point1, point2):
        return int(math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2))

    def average_value(self, values):
        return sum(values)/len(values)
    
    def control_speed(self, hand1, hand2,thumb1,thumb2,base_thumb1, base_thumb2):
        max_value_to_speed_control = 100
        min_value_to_speed_control = 30

        thumb_distance1 = self.calculate_distance(thumb1,base_thumb1)
        thumb_distance2 = self.calculate_distance(thumb2,base_thumb2)
        
        value_to_speed_control = self.normalize_value(self.average_value([thumb_distance1,thumb_distance2]),min_value_to_speed_control,max_value_to_speed_control)
        self.speed = value_to_speed_control
        #print(value_to_speed_control)
        if thumb_distance1 >= min_value_to_speed_control and thumb_distance2 >= min_value_to_speed_control:
            self.gamepad.left_trigger_float(0)
            self.gamepad.right_trigger_float(value_to_speed_control)
            # print("speeds up!")
        elif (thumb_distance1 < min_value_to_speed_control and thumb_distance2 > min_value_to_speed_control) or (thumb_distance1 > min_value_to_speed_control and thumb_distance2 < min_value_to_speed_control):
            self.gamepad.right_trigger_float(0)
            self.gamepad.left_trigger_float(0.8)
            self.speed = 0
            # print("Brake!")
        else:
            self.gamepad.right_trigger_float(0)
            self.gamepad.left_trigger_float(0)
            # print("Normal!")


    def control_steering(self, angle):
        a_min, a_max = 0, 50
        steerling_error = 8192
        # multiple=1
        # if angle > a_min and angle < 10:
        #     multiple = 1.7
        # if angle < a_min and angle > -10:
        #     multiple = 1.7
            
        if angle >= a_min:
            if angle > a_max:
                angle = a_max
            self.gamepad.left_joystick(int(self.normalize_value(angle, a_min, a_max)*32768 + steerling_error), 0)
            # print("Right")
        elif angle < -a_min:
            if angle < -a_max:
                angle = -a_max
            self.gamepad.left_joystick(int(-self.normalize_value(angle, a_min, a_max)*32768 - steerling_error), 0)
            # print("Left")
        else:
            self.gamepad.left_joystick(0, 0)
            # print("Forward")
    
    def draw_speedometer(self, frame):
        bar_x = 50  
        bar_y = 100 
        bar_height = 300 
        bar_width = 20  

        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)

        filled_height = int(bar_height * self.speed)

        cv2.rectangle(frame, (bar_x, bar_y + bar_height - filled_height), (bar_x + bar_width, bar_y + bar_height), (0, 255, 0), cv2.FILLED)

        cv2.putText(frame, f"Speed: {int(self.speed * 100)}", (bar_x - 40, bar_y + bar_height + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


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
                        thumb1 = double_hands[0][4]
                        base_thumb1 = double_hands[0][6]
                        thumb2 = double_hands[1][4]
                        base_thumb2 = double_hands[1][6]

                        angle = self.calculate_angle(double_hands[0][0], double_hands[1][0])
                        cv2.putText(frame, f"Angle: {int(angle)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        self.control_steering(angle)
                        self.control_speed(double_hands[0], double_hands[1],thumb1,thumb2,base_thumb1,base_thumb2)

                        self.draw_speedometer(frame)

                        self.gamepad.update()
                        cv2.line(frame, double_hands[0][0], double_hands[1][0], (255, 0, 0), 3)
                        cv2.line(frame, thumb1, base_thumb1, (0, 255, 0), 2)
                        cv2.line(frame, thumb2, base_thumb2, (0, 255, 0), 2)
                    except Exception as e:
                          print(f"Error processing landmarks: {e}")

                cv2.imshow("Virtual driving control", frame)
            except:
                pass
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
