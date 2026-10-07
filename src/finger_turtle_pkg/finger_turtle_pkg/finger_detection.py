import math
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


class FingerCounterNode(Node):
    def __init__(self):
        super().__init__("finger_counter")

        # Parameters (defaults match the original script)
        self.declare_parameter("camera_index", 0)
        self.declare_parameter("roi", [350, 50, 600, 300])  # x1, y1, x2, y2
        self.declare_parameter("show_windows", True)

        cam_idx = self.get_parameter("camera_index").value
        self.x1, self.y1, self.x2, self.y2 = self.get_parameter("roi").value
        self.show = self.get_parameter("show_windows").value

        self.cap = cv2.VideoCapture(cam_idx)
        if not self.cap.isOpened():
            self.get_logger().error(f"Cannot open camera {cam_idx}")

        self.pub = self.create_publisher(Int32, "finger_count", 10)

        # ~30 Hz loop replaces the original `while True`
        self.timer = self.create_timer(1.0 / 30.0, self.process_frame)
        self.get_logger().info("Finger counter started. Press 'q' in the window to quit.")

    def process_frame(self):
        x1, y1, x2, y2 = self.x1, self.y1, self.x2, self.y2

        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn("Failed to read frame")
            return

        frame = cv2.flip(frame, 1)  # mirror view
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        roi = frame[y1:y2, x1:x2]

        # Skin-color mask (tweak these values for your lighting / skin tone)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0, 30, 60]), np.array([20, 150, 255]))
        mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)

        fingers = 0
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            cnt = max(contours, key=cv2.contourArea)

            if cv2.contourArea(cnt) > 3000:  # ignore small noise
                hull_pts = cv2.convexHull(cnt)
                cv2.drawContours(roi, [cnt], -1, (255, 0, 0), 2)
                cv2.drawContours(roi, [hull_pts], -1, (0, 255, 255), 2)

                hull_idx = cv2.convexHull(cnt, returnPoints=False)
                defects = cv2.convexityDefects(cnt, hull_idx)

                gaps = 0  # valleys between fingers
                if defects is not None:
                    # Newer OpenCV returns shape (N, 4), older returns (N, 1, 4)
                    for s, e, f, depth in defects.reshape(-1, 4):
                        start = tuple(cnt[s][0])
                        end = tuple(cnt[e][0])
                        far = tuple(cnt[f][0])

                        a = dist(end, start)
                        b = dist(far, start)
                        c = dist(end, far)
                        if b * c == 0:
                            continue

                        angle = math.degrees(
                            math.acos(max(-1, min(1, (b**2 + c**2 - a**2) / (2 * b * c))))
                        )

                        # A valley between two fingers: sharp angle and deep enough
                        if angle <= 90 and depth / 256 > 20:
                            gaps += 1
                            cv2.circle(roi, far, 5, (0, 0, 255), -1)

                if gaps > 0:
                    fingers = min(gaps + 1, 5)
                else:
                    # No valleys: either a fist (0) or a single finger (1)
                    _, _, w, h = cv2.boundingRect(cnt)
                    fingers = 1 if h / w > 1.4 else 0

        # Publish result
        self.pub.publish(Int32(data=int(fingers)))

        if self.show:
            cv2.putText(frame, f"Fingers: {fingers}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            cv2.imshow("Finger Counter", frame)
            cv2.imshow("Mask", mask)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.get_logger().info("Quit requested")
                rclpy.shutdown()

    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = FingerCounterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()