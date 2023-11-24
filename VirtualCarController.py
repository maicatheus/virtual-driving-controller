import cv2
import math
import vgamepad as vg
import mediapipe as mp

class VirtualCarController:
    def __init__(self):
        self.gamepad = vg.VX360Gamepad()
        self.mpDraw = mp.solutions.drawing_utils
        self.mp_face_detection = mp.solutions.face_detection
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=2)
        self.camera = cv2.VideoCapture(0)
        self.speed = 0
        self.brake = 0

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

        if(delta_x==0):
            return 90
        
        theta = math.atan(delta_y/ delta_x)
        return math.degrees(theta)

    def calculate_distance(self,point1, point2):
        return int(math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2))

    def average_value(self, values):
        return sum(values)/len(values)
    
    def control_speed(self,thumb1,thumb2,base_thumb1, base_thumb2):
        max_value_to_speed_control = 110
        min_value_to_speed_control = 40

        thumb_distance1 = self.calculate_distance(thumb1,base_thumb1)
        thumb_distance2 = self.calculate_distance(thumb2,base_thumb2)
        
        self.speed = self.normalize_value(thumb_distance1,min_value_to_speed_control,max_value_to_speed_control)
        self.brake = self.normalize_value(thumb_distance2,min_value_to_speed_control,max_value_to_speed_control)
        #print(value_to_speed_control)
        if thumb_distance1 >= min_value_to_speed_control or thumb_distance2 >= min_value_to_speed_control:
            self.gamepad.left_trigger_float(self.brake*1.4)
            # print("Brake!")
            self.gamepad.right_trigger_float(self.speed)
            # print("speeds up!")
        else:
            self.gamepad.right_trigger_float(0)
            self.gamepad.left_trigger_float(0)
            # print("Normal!")


    def control_steering(self, angle):
        a_min, a_max = 0, 60
        steerling_error = 0.25
        multiple = 1
        if angle <= 0:
            multiple = -1

        angle_normalized = self.normalize_value(angle, a_min, a_max)+steerling_error if self.normalize_value(angle, a_min, a_max)+steerling_error<=1 else 1.0
         
        self.gamepad.left_joystick_float(multiple*(angle_normalized), 0)
    
    def fpv_control(self,nose, box):
        
        half_box_width = abs(box[0][0] - box[1][0])/2
        
        trashhold = 0#int(half_box_width*0.06)
        
        middle_box = half_box_width + box[0][0]


        multiple = 1
        distance_nose_middle_box = abs(nose[0] - middle_box)
        moviment_distance = self.normalize_value(distance_nose_middle_box,trashhold,half_box_width)

        if(nose[0]<middle_box - trashhold):
            multiple = -1
            # print("Left")

        self.gamepad.right_joystick_float(multiple*moviment_distance, 0)




        # print(moviment_distance*multiple)


    def draw_rectangle_of_speed(self, frame,text,mode,color, x_position):
        bar_x = x_position  
        bar_y = 100 
        bar_height = 300 
        bar_width = 20  

        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)

        filled_height = int(bar_height * mode)

        cv2.rectangle(frame, (bar_x, bar_y + bar_height - filled_height), (bar_x + bar_width, bar_y + bar_height), color, cv2.FILLED)

        cv2.putText(frame, f"{text}: {int(mode * 100)}", (bar_x - 40, bar_y + bar_height + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


    def run(self):
        with self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.5
        ) as face_detection:
            while True:
                try:
                    ret, frame = self.camera.read()
                    frame = cv2.flip(frame, 1)
                    
                    frame_rgb = frame #cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results_hand = self.hands.process(frame_rgb) 
                    
                    results_face = face_detection.process(frame_rgb)

                    face = []
                    box = 0
                    if results_face.detections:
                        for index, detections in enumerate(results_face.detections):
                            for i, lm in enumerate(detections.location_data.relative_keypoints):
                                
                                box_aux =  detections.location_data.relative_bounding_box
                                h, w, _ = frame.shape
                                box=( (int(box_aux.xmin*w) ,int(box_aux.ymin*h)), (int(box_aux.xmin*w + box_aux.width*w), int(box_aux.ymin*h + box_aux.height*h)) )
                                cx, cy = int(lm.x * w), int(lm.y * h)
                                face.append((cx, cy))
                            self.mpDraw.draw_detection(frame_rgb, detections)
                    
                    nose = face[2]

                    double_hands = ([], [])
                    if results_hand.multi_hand_landmarks:
                        for index, hands_lms in enumerate(results_hand.multi_hand_landmarks):
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
                            cv2.putText(frame, f"Angle: {int(angle)}", (100, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                            self.control_steering(angle)
                            self.control_speed(thumb1,thumb2,base_thumb1,base_thumb2)
                            self.fpv_control(nose, box)
                            self.draw_rectangle_of_speed(frame,"Speed", self.speed,(0,255,0),500)
                            self.draw_rectangle_of_speed(frame,"Brake", self.brake,(0,0,255),100)

                            self.gamepad.update()
                            cv2.line(frame, double_hands[0][0], double_hands[1][0], (255, 0, 0), 3)
                            cv2.line(frame, thumb1, base_thumb1, (0, 255, 0), 2)
                            cv2.line(frame, thumb2, base_thumb2, (0, 0, 255), 2)
                        except Exception as e:
                            self.speed = 0
                            self.brake = 0
                            self.gamepad.left_joystick(0, 0)
                            self.gamepad.update()

                            print(f"Error processing landmarks: {e}")

                    cv2.imshow("Virtual driving control", frame_rgb)
                except:
                    pass
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
