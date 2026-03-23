"""
Exercise 2 — TurtleBot3 Diagnostic Node  (SKELETON)
====================================================
Your task: add diagnostic checks that monitor real TurtleBot3 data.

The node already subscribes to /battery_state and /scan.
Fill in the TODO sections to wire them up to the diagnostic_updater.

Monitor with:
  ros2 topic echo /diagnostics
  rqt → Plugins → Robot Tools → Runtime Monitor
"""

import rclpy
from rclpy.node import Node

from diagnostic_updater import Updater
from diagnostic_msgs.msg import DiagnosticStatus
from sensor_msgs.msg import BatteryState, LaserScan


class TurtlebotDiagnosticNode(Node):

    def __init__(self):
        super().__init__('turtlebot_diagnostic_node')

        # ── Updater ───────────────────────────────────────────────────────────
        self.updater = Updater(self)
        # TODO: set the hardware ID
        # self.updater.setHardwareID(...)

        # ── Latest sensor data ────────────────────────────────────────────────
        self._battery: BatteryState | None = None
        self._scan: LaserScan | None = None

        # ── Subscribers ───────────────────────────────────────────────────────
        self.create_subscription(BatteryState, '/battery_state', self._battery_cb, 10)
        self.create_subscription(LaserScan,    '/scan',          self._scan_cb,    10)

        # ── Register diagnostic tasks ─────────────────────────────────────────
        # TODO: add a battery check
        # self.updater.add('Battery', self.check_battery)

        # TODO: add a LiDAR check
        # self.updater.add('LiDAR', self.check_lidar)

        # ── Timer to drive the updater ────────────────────────────────────────
        self.create_timer(1.0, self.updater.force_update)

    # ── Subscriber callbacks ──────────────────────────────────────────────────

    def _battery_cb(self, msg: BatteryState):
        self._battery = msg

    def _scan_cb(self, msg: LaserScan):
        self._scan = msg

    # ── Diagnostic callbacks ──────────────────────────────────────────────────

    def check_battery(self, stat):
        """
        TODO: Use self._battery to fill in stat.
        Hint:
          stat.summary(DiagnosticStatus.OK, 'Battery OK')
          stat.add('voltage (V)', f'{self._battery.voltage:.2f}')
        """
        if self._battery is None:
            stat.summary(DiagnosticStatus.WARN, 'No battery data yet')
            return stat

        # TODO: check voltage levels and populate stat
        return stat

    def check_lidar(self, stat):
        """
        TODO: Use self._scan to check that the LiDAR is publishing
        and that no range reading is dangerously close (< 0.15 m).
        """
        if self._scan is None:
            stat.summary(DiagnosticStatus.WARN, 'No scan data yet')
            return stat

        # TODO: check min range and populate stat
        return stat


def main(args=None):
    rclpy.init(args=args)
    node = TurtlebotDiagnosticNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
