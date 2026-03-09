#!/usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu


class MoveAndImu(Node):
    def __init__(self, linear, angular):
        super().__init__('move_and_imu')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Imu,
            '/imu',
            self.imu_callback,
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

    def imu_callback(self, msg):
        q = msg.orientation
        ax = msg.linear_acceleration.x
        wz = msg.angular_velocity.z
        self.get_logger().info(
            f'Orientation: x={q.x:.3f} y={q.y:.3f} z={q.z:.3f} w={q.w:.3f} | '
            f'Linear Accel X: {ax:.3f} m/s^2 | '
            f'Angular Vel Z: {wz:.3f} rad/s'
        )


def main():
    if len(sys.argv) != 3:
        print('Usage: python3 move_and_imu.py <linear_velocity> <angular_velocity>')
        sys.exit(1)

    linear = float(sys.argv[1])
    angular = float(sys.argv[2])

    rclpy.init()
    node = MoveAndImu(linear, angular)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop_msg = Twist()
        node.publisher.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
