import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import math

class TurtleFollower(Node):
    def __init__(self):
        super().__init__('turtle_follower')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.publisher = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.on_timer)

    def on_timer(self):
        try:
            # TODO: Task 1 - Lookup the transform
            # Use the buffer to find where 'turtle1' is relative to 'turtle2'.
            # Syntax: self.tf_buffer.lookup_transform(target_frame, source_frame, time)
            
            trans = _________________________________________________

        except TransformException as ex:
            self.get_logger().info(f'Could not transform: {ex}')
            return

        msg = Twist()

        # TODO: Task 2 - Extract the relative distances from the transform
        # Hint: Look into trans.transform.translation.x and .y
        dx = ____ # FILL THIS IN
        dy = ____ # FILL THIS IN

        # Logic is provided so you can focus on TF data extraction
        msg.angular.z = 1.0 * math.atan2(dy, dx)
        msg.linear.x = 0.5 * math.sqrt(dx**2 + dy**2)

        self.publisher.publish(msg)

def main():
    rclpy.init()
    node = TurtleFollower()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()