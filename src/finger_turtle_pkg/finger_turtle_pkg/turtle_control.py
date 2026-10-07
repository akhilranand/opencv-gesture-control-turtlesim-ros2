from rclpy.node import Node
import rclpy
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist


class TurtleControlNode(Node):

    def __init__(self):
        super().__init__("turtle_control")

        # Subscribe to finger count
        self.subscription = self.create_subscription(
            Int32,
            "finger_count",
            self.finger_callback,
            10
        )

        # Publish velocity to turtlesim
        self.publisher = self.create_publisher(
            Twist,
            "/turtle1/cmd_vel",
            10
        )

        self.get_logger().info("Turtle control node started")

    def finger_callback(self, msg):

        fingers = msg.data

        cmd = Twist()

        if fingers == 0:
            # Stop
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        elif fingers == 1:
            # Forward
            cmd.linear.x = 2.0
            cmd.angular.z = 0.0

        elif fingers == 2:
            # Backward
            cmd.linear.x = -2.0
            cmd.angular.z = 0.0

        elif fingers == 3:
            # Turn left
            cmd.linear.x = 0.0
            cmd.angular.z = 2.0

        elif fingers == 4:
            # Turn right
            cmd.linear.x = 0.0
            cmd.angular.z = -2.0

        elif fingers == 5:
            # Stop
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        else:
            # Safety: stop for unexpected values
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        self.publisher.publish(cmd)

        self.get_logger().info(
            f"Fingers: {fingers}"
        )


def main(args=None):

    rclpy.init(args=args)

    node = TurtleControlNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        # Stop turtle before shutting down
        stop_cmd = Twist()
        node.publisher.publish(stop_cmd)

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
