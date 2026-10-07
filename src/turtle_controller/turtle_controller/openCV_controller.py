import cv2
import rclpy
from rclpy.node import Node
import mediapipe as mp
from geometry_msgs.msg import Twist


class Cv_bot(Node):
    def __init__(self):
        super().__init__('cv_bot')
        self.get_logger().info("The camera node has started...")



        # Create MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        # Drawing utility
        self.mp_draw = mp.solutions.drawing_utils
        self.finger_count = 0


        # Open webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.get_logger().error("Cannot open webcam")
            return

        self.timer = self.create_timer(0.03,self.process_frame)

        self.publisher_ = self.create_publisher(Twist,"/turtle1/cmd_vel",10)
        self.pub_timer = self.create_timer(0.1,self.movement)

    def movement(self):

        msg = Twist()
        self.get_logger().info("Movement...")   
        if self.finger_count == 0:
            self.get_logger().info("stop") 
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info(f"x = {msg.linear.x} . y = {msg.linear.y} ")    
            self.publisher_.publish(msg)

        elif self.finger_count == 1:  
            self.get_logger().info("forward") 
            msg.linear.x = 2.0
            msg.angular.z = 0.0
            self.get_logger().info(f"x = {msg.linear.x} . y = {msg.linear.y} ")    
            self.publisher_.publish(msg)

        elif self.finger_count == 2:  
            self.get_logger().info("backward") 
            msg.linear.x = -2.0
            msg.angular.z = 0.0
            self.get_logger().info(f"x = {msg.linear.x} . y = {msg.linear.y} ")    
            self.publisher_.publish(msg)

        elif self.finger_count == 3:  
            self.get_logger().info("left") 
            msg.linear.x = 0.0
            msg.angular.z = 2.0
            self.get_logger().info(f"x = {msg.linear.x} . y = {msg.linear.y} ")    
            self.publisher_.publish(msg)

        elif self.finger_count == 4:  
            self.get_logger().info("right")  
            msg.linear.x = 0.0
            msg.angular.z = -2.0
            self.get_logger().info(f"x = {msg.linear.x} . y = {msg.linear.y} ")    
            self.publisher_.publish(msg)

        elif self.finger_count == 5:  
            self.get_logger().info("stop")   
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info(f"x = {msg.linear.x} . y = {msg.linear.y} ")    
            self.publisher_.publish(msg)                                             
             
    def process_frame(self):
        

        # Read frame
        ret, frame = self.cap.read()

        if not ret:
            self.get_logger().info("Cannot read frame")
            # print("Cannot read frame")
            # break
            return

        # Flip camera
        frame = cv2.flip(frame, 1)

        # Convert BGR → RGB
        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Detect hand
        result = self.hands.process(rgb)

        self.finger_count = 0

        # If hand detected
        if result.multi_hand_landmarks:

            for hand_landmarks in result.multi_hand_landmarks:

                # Get landmarks
                landmarks = hand_landmarks.landmark

                # -------------------------
                # Thumb
                # -------------------------

                if landmarks[4].x < landmarks[3].x:
                    self.finger_count += 1

                # -------------------------
                # Index finger
                # -------------------------

                if landmarks[8].y < landmarks[6].y:
                    self.finger_count += 1

                # -------------------------
                # Middle finger
                # -------------------------

                if landmarks[12].y < landmarks[10].y:
                    self.finger_count += 1

                # -------------------------
                # Ring finger
                # -------------------------

                if landmarks[16].y < landmarks[14].y:
                    self.finger_count += 1

                # -------------------------
                # Little finger
                # -------------------------

                if landmarks[20].y < landmarks[18].y:
                    self.finger_count += 1


                # Draw hand landmarks
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )


        # Display finger count
        cv2.putText(
            frame,
            f"Fingers: {self.finger_count}",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 255, 0),
            3
        )


        # Show camera
        cv2.imshow(
            "Finger Detection",
            frame
        )


        # Press q to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            # break
            self.cap.release()
            cv2.destroyAllWindows()
            self.destroy_node()


    # Cleanup
        # self.cap.release()
        # cv2.destroyAllWindows()



def main(args = None):
    rclpy.init(args = args)
    node = Cv_bot()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()            

