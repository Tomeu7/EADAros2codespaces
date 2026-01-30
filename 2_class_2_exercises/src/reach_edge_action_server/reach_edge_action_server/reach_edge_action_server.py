#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from action_msg.action import ReachEdgeAndReturn
from rclpy.executors import MultiThreadedExecutor
import time

CENTER_X = 5.5
CENTER_Y = 5.5
EDGE_THRESHOLD = 0.2
CENTER_THRESHOLD = 0.3


class ReachEdgeActionServer(Node):
    def __init__(self):
        super().__init__('reach_edge_action_server')

        self.pose = None

        self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.server = ActionServer(
            self,
            ReachEdgeAndReturn,
            'reach_edge_and_return',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
        )

        self.get_logger().info('ReachEdgeAndReturn Action Server ready.')

    def pose_callback(self, msg: Pose):
        self.pose = msg

    def goal_callback(self, goal_request):
        self.get_logger().info('Goal received.')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Cancel requested.')
        return CancelResponse.ACCEPT

    def stop(self):
        twist = Twist()
        self.cmd_pub.publish(twist)

    def move_forward(self, speed=2.0):
        twist = Twist()
        twist.linear.x = speed
        self.cmd_pub.publish(twist)

    def move_towards_center(self, speed=2.0, k_ang=4.0):
        """
        Simple proportional controller:
        - angular velocity depends on angle error to the center
        - linear velocity is constant
        """
        if self.pose is None:
            return

        dx = CENTER_X - self.pose.x
        dy = CENTER_Y - self.pose.y
        target_theta = math.atan2(dy, dx)

        # shortest angle difference in [-pi, pi]
        err = target_theta - self.pose.theta
        err = math.atan2(math.sin(err), math.cos(err))

        twist = Twist()
        twist.linear.x = speed
        twist.angular.z = k_ang * err
        self.cmd_pub.publish(twist)

    def is_at_edge(self) -> bool:
        """
        Return True if turtle is close to any wall.
        turtlesim bounds are ~[0, 11] in x and y.
        We treat "close" as <= EDGE_THRESHOLD from a wall.
        """
        if self.pose is None:
            return False

        x = self.pose.x
        y = self.pose.y

        # walls at x=0, x=11, y=0, y=11 (approx.)
        return (
            x < EDGE_THRESHOLD or x > (11.0 - EDGE_THRESHOLD) or
            y < EDGE_THRESHOLD or y > (11.0 - EDGE_THRESHOLD)
        )

    def is_at_center(self) -> bool:
        """
        Return True if turtle is close to the center.
        """
        if self.pose is None:
            return False

        dx = CENTER_X - self.pose.x
        dy = CENTER_Y - self.pose.y
        dist = math.sqrt(dx*dx + dy*dy)
        return dist < CENTER_THRESHOLD

    def distance_to_edge(self) -> float:
        """
        Compute distance to the closest wall.
        If pose is at (x,y), distances to each wall are:
          left:   x - 0
          right:  11 - x
          bottom: y - 0
          top:    11 - y
        Take the minimum.
        """
        if self.pose is None:
            return float('inf')

        x = self.pose.x
        y = self.pose.y

        d_left = x
        d_right = 11.0 - x
        d_bottom = y
        d_top = 11.0 - y

        return min(d_left, d_right, d_bottom, d_top)

    def distance_to_center(self) -> float:
        if self.pose is None:
            return float('inf')
        return math.sqrt((CENTER_X - self.pose.x)**2 + (CENTER_Y - self.pose.y)**2)

    async def execute_callback(self, goal_handle):
        feedback = ReachEdgeAndReturn.Feedback()
        result = ReachEdgeAndReturn.Result()

        # PHASE 1: GO TO EDGE
        # 1. While not at edge, send Twist(linear.x=2.0)
        # 2. Check if goal_handle.is_cancel_requested
        # 3. Update feedback.phase and feedback.distance, then publish
        # 4. Use time.sleep(0.1) for the loop rate
        
        # --- YOUR CODE HERE ---

        # PHASE 2: RETURN TO CENTER
        # 1. While not at center, move towards (5.5, 5.5)
        # 2. Update feedback
        
        # --- YOUR CODE HERE ---

        self.stop()
        goal_handle.succeed()
        result.success = True
        return result


def main():
    rclpy.init()
    node = ReachEdgeActionServer()
    
    # Use MultiThreadedExecutor to allow callbacks to run in parallel
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()