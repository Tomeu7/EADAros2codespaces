#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np


class RedObjectDetector(Node):
    def __init__(self):
        super().__init__('red_object_detector')

        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

    def image_callback(self, msg):
        # Convert ROS Image message to OpenCV BGR image
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Convert BGR to HSV - HSV makes colour thresholding much easier
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # Define red colour range in HSV
        # Red wraps around 0/180 in the hue channel, so we need two ranges
        lower_red1 = np.array([0,   120, 70])
        upper_red1 = np.array([10,  255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        # Create masks for both red ranges and combine them
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        # Count red pixels
        red_pixels = cv2.countNonZero(mask)

        # Find contours of red regions
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Get the largest contour (most likely the sphere)
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)

            if area > 100:  # ignore tiny blobs
                # Get bounding box and centroid
                x, y, w, h = cv2.boundingRect(largest)
                cx = x + w // 2
                cy = y + h // 2

                self.get_logger().info(
                    f'Red object detected! Area: {area:.0f}px | '
                    f'Centroid: ({cx}, {cy}) | '
                    f'Bounding box: x={x} y={y} w={w} h={h}'
                )
            else:
                self.get_logger().info('No significant red object detected.')
        else:
            self.get_logger().info('No red object detected.')


def main():
    rclpy.init()
    node = RedObjectDetector()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
