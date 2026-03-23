"""
Exercise 4 — MQTT Subscriber (SKELETON)
========================================
Listens for robot position published over MQTT.
No ROS required — pure Python.

Your task: fill in the TODO sections.

Run (from any machine):
  python3 subscriber.py
"""

import paho.mqtt.client as mqtt

BROKER = 'broker.hivemq.com'
PORT   = 1883
# TODO: change this to match your publisher topic
TOPIC  = 'robotics_class/changeme/odom'


def on_message(client, userdata, msg):
    # TODO: decode msg.payload and print the position
    pass


# TODO: create the client, attach on_message, connect, subscribe, loop_forever
