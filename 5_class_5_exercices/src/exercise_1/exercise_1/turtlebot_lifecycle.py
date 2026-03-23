"""
Exercise 1 — TurtleBot3 LifecycleNode
======================================
The _drive_square logic is already provided.
Your task: implement the four lifecycle callbacks so the robot
starts/stops correctly when transitions are triggered.

Lifecycle transitions to test:
  ros2 lifecycle set /turtlebot_lifecycle configure
  ros2 lifecycle set /turtlebot_lifecycle activate
  ros2 lifecycle set /turtlebot_lifecycle deactivate
  ros2 lifecycle set /turtlebot_lifecycle cleanup
"""

import rclpy
from rclpy.lifecycle import LifecycleNode, TransitionCallbackReturn
from geometry_msgs.msg import TwistStamped


FORWARD_SPEED = 0.2   # m/s
TURN_SPEED    = 0.5   # rad/s
FORWARD_TIME  = 1.0   # s
TURN_TIME     = 1.26  # s  ≈ π/2 / 0.5
TIMER_PERIOD  = 0.1   # s


class TurtlebotLifecycle(LifecycleNode):

    def __init__(self):
        super().__init__('turtlebot_lifecycle')
        self._publisher = None
        self._timer = None
        self._elapsed = 0.0
        self._phase = 'forward'  # 'forward' | 'turn'

    # ── 1. on_configure ───────────────────────────────────────────────────────
    def on_configure(self, state):
        """
        TODO: Initialize hardware.
        - Create a lifecycle publisher on /cmd_vel (TwistStamped, queue 10)
        - Reset _elapsed and _phase
        - Return TransitionCallbackReturn.SUCCESS
        """
        self.get_logger().info('on_configure() — TODO: implement me')
        return TransitionCallbackReturn.SUCCESS

    # ── 2. on_activate ────────────────────────────────────────────────────────
    def on_activate(self, state):
        """
        TODO: Start publishing.
        - Create a timer (TIMER_PERIOD) that calls self._drive_square
        - Call super().on_activate(state) and return its result
        """
        self.get_logger().info('on_activate() — TODO: implement me')
        return super().on_activate(state)

    # ── 3. on_deactivate ──────────────────────────────────────────────────────
    def on_deactivate(self, state):
        """
        TODO: Stop publishing.
        - Cancel and clear self._timer
        - Publish a zero TwistStamped to stop the robot
        - Call super().on_deactivate(state) and return its result
        """
        self.get_logger().info('on_deactivate() — TODO: implement me')
        return super().on_deactivate(state)

    # ── 4. on_cleanup ─────────────────────────────────────────────────────────
    def on_cleanup(self, state):
        """
        TODO: Release resources.
        - Destroy self._publisher and set it to None
        - Return TransitionCallbackReturn.SUCCESS
        """
        self.get_logger().info('on_cleanup() — TODO: implement me')
        return TransitionCallbackReturn.SUCCESS

    # ── Drive logic (already implemented) ────────────────────────────────────
    def _drive_square(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        if self._phase == 'forward':
            msg.twist.linear.x = FORWARD_SPEED
            self._elapsed += TIMER_PERIOD
            if self._elapsed >= FORWARD_TIME:
                self._elapsed, self._phase = 0.0, 'turn'
        else:
            msg.twist.angular.z = TURN_SPEED
            self._elapsed += TIMER_PERIOD
            if self._elapsed >= TURN_TIME:
                self._elapsed, self._phase = 0.0, 'forward'
        self._publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TurtlebotLifecycle()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
