"""
Exercise 4 Take-home — MQTT Publisher (multiple topics) SKELETON
=================================================================
Extend the publisher to send both odometry position AND LiDAR minimum range.

Your task: fill in the TODO sections.

Run:
  python3 publisher_takehome.py
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
import paho.mqtt.client as mqtt

BROKER = 'broker.hivemq.com'
PORT   = 1883

# TODO: define two topics, one for odom and one for scan
TOPIC_ODOM = 'robotics_class/changeme/odom'
TOPIC_SCAN = 'robotics_class/changeme/scan'


class MqttPublisher(Node):

    def __init__(self):
        super().__init__('mqtt_publisher')

        # TODO: create the MQTT client, connect and start loop
        # self.mqtt = ...

        # TODO: subscribe to /odom and /scan
        # self.create_subscription(Odometry, ...)
        # self.create_subscription(LaserScan, ...)

        self.get_logger().info(f'Publishing to {BROKER}')

    def _odom_cb(self, msg: Odometry):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        # TODO: publish to TOPIC_ODOM
        pass

    def _scan_cb(self, msg: LaserScan):
        valid = [r for r in msg.ranges if msg.range_min <= r <= msg.range_max]
        min_range = min(valid) if valid else float('inf')
        # TODO: publish min_range to TOPIC_SCAN
        pass


def main():
    rclpy.init()
    node = MqttPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
