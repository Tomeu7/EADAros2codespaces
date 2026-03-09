#!/usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class MoveAndScan(Node):
    def __init__(self, linear, angular):
        super().__init__('move_and_scan')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            LaserScan,
            '/laser/scan',
            self.laser_callback,
            10
        )

        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.publish_velocity)

        self.linear = linear
        self.angular = angular

    def publish_velocity(self):
        msg = Twist()
        msg.linear.x = self.linear
        msg.angular.z = self.angular
        self.publisher.publish(msg)

    def laser_callback(self, msg):
        valid_ranges = [r for r in msg.ranges if msg.range_min <= r <= msg.range_max]
        if valid_ranges:
            min_distance = min(valid_ranges)
            self.get_logger().info(f'Minimum laser distance: {min_distance:.3f} m')


def main():
    if len(sys.argv) != 3:
        print('Usage: python3 move_and_scan.py <linear_velocity> <angular_velocity>')
        sys.exit(1)

    linear = float(sys.argv[1])
    angular = float(sys.argv[2])

    rclpy.init()
    node = MoveAndScan(linear, angular)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop the robot before exiting
        stop_msg = Twist()
        node.publisher.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()