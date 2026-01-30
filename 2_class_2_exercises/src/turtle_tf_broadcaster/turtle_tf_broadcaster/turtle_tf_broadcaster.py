#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from math import sin, cos

class TurtleTFBroadcaster(Node):
    def __init__(self):
        super().__init__('turtle_tf_broadcaster')

        # Declare the parameter so we can pass 'turtle1' or 'turtle2' from the launch file
        self.declare_parameter('turtlename', 'turtle1')
        self.turtlename = self.get_parameter('turtlename').value

        self.br = TransformBroadcaster(self)
        
        # Subscribe to the specific turtle's pose based on the parameter
        self.sub = self.create_subscription(
            Pose,
            f'/{self.turtlename}/pose',
            self.handle_pose,
            10
        )

        self.get_logger().info(f"Broadcaster started for {self.turtlename}")

    def handle_pose(self, msg: Pose):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = self.turtlename # Use the parameter for the frame name

        t.transform.translation.x = msg.x
        t.transform.translation.y = msg.y
        t.transform.translation.z = 0.0

        # Quaternion conversion remains the same
        t.transform.rotation.z = sin(msg.theta / 2.0)
        t.transform.rotation.w = cos(msg.theta / 2.0)

        self.br.sendTransform(t)

def main():
    rclpy.init()
    node = TurtleTFBroadcaster()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
