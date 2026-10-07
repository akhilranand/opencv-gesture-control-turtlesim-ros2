import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class Control_bot(Node):
    def __init__(self):
        super().__init__('control_bot')
        self.get_logger().info("the contril node has started.....")

        self.publisher_ = self.create_publisher(Twist , '/turtle1/cmd_vel' , 10)
        self.timer = self.create_timer(1.0,self.cb)


    def cb(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 2.0
        self.publisher_.publish(msg)
        self.get_logger().info(f"x = {msg.linear.x} and z = {msg.angular.z}")
        

def main(args = None):
    rclpy.init(args = args)
    node = Control_bot()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()            