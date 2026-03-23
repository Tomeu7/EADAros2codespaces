"""
Exercise 4 — MQTT Publisher (SKELETON)
=======================================
Reads odometry from the TurtleBot3 and publishes position to an MQTT broker.

Your task: fill in the TODO sections.

Run:
  python3 publisher.py
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import paho.mqtt.client as mqtt

BROKER = 'broker.hivemq.com'
PORT   = 1883
# TODO: change this to something unique (e.g. robotics_class/your_name/odom)
TOPIC  = 'robotics_class/changeme/odom'


class MqttPublisher(Node):

    def __init__(self):
        super().__init__('mqtt_publisher')

        # TODO: create the MQTT client and connect to the broker
        # self.mqtt = mqtt.Client()
        # self.mqtt.connect(...)
        # self.mqtt.loop_start()

        # TODO: subscribe to /odom and call self._odom_cb
        # self.create_subscription(...)

        self.get_logger().info(f'Publishing to {BROKER} on topic {TOPIC}')

    def _odom_cb(self, msg: Odometry):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        # TODO: publish position as a string to the MQTT topic
        # self.mqtt.publish(TOPIC, ...)
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
