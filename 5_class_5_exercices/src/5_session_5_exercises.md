# Session 5 Exercises — Lifecycle Nodes & Diagnostics

## Overview

| Package | Description |
|---|---|
| `exercise_1` | TurtleBot3 LifecycleNode — **your starting point** |
| `exercise_2` | TurtleBot3 diagnostic node — **your starting point** |

Build everything once:

```bash
cd ~/ros2_ws   # or wherever your workspace root is
colcon build --packages-select exercise_1 exercise_2
source install/setup.bash
```

---

## Exercise 1 — TurtleBot3 LifecycleNode

### Concept

A `LifecycleNode` separates **creation** from **activation**.
Instead of doing everything in `__init__`, you split work across four callbacks:

| Callback | When it runs | What to do |
|---|---|---|
| `on_configure` | `configure` transition | Create publishers, load params, init hardware |
| `on_activate` | `activate` transition | Start timers, enable publishers |
| `on_deactivate` | `deactivate` transition | Stop timers, send stop command |
| `on_cleanup` | `cleanup` transition | Destroy publishers, release hardware |

### What TurtleBot3 Gazebo provides

When the simulation is running it exposes the robot's hardware interface as ROS 2 topics:

| Topic | Message type | What it represents |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | Velocity commands sent to the wheels |
| `/odom` | `nav_msgs/Odometry` | Wheel odometry (position + velocity) |
| `/scan` | `sensor_msgs/LaserScan` | 360° LiDAR distance readings |
| `/imu` | `sensor_msgs/Imu` | Accelerometer + gyroscope |
| `/battery_state` | `sensor_msgs/BatteryState` | Simulated battery voltage & percentage |
| `/joint_states` | `sensor_msgs/JointState` | Wheel encoder positions |

Your lifecycle node publishes to `/cmd_vel` — Gazebo receives those commands and moves the robot.

### Starting point

Open [exercise_1/exercise_1/turtlebot_lifecycle.py](exercise_1/exercise_1/turtlebot_lifecycle.py).
You will see four empty callbacks with `TODO` comments.

### Step 1 — `on_configure`: create the publisher

```python
def on_configure(self, state):
    self.get_logger().info('Configuring: creating publisher')
    self._publisher = self.create_lifecycle_publisher(TwistStamped, '/cmd_vel', 10)
    self._elapsed = 0.0
    self._phase = 'forward'
    return TransitionCallbackReturn.SUCCESS
```

> ROS 2 Jazzy uses `TwistStamped` on `/cmd_vel` (not plain `Twist`) — always set `msg.header.stamp`.
> Use `create_lifecycle_publisher` (not `create_publisher`) — it respects the node's active/inactive state automatically.

### Step 2 — `on_activate`: start the drive timer

```python
def on_activate(self, state):
    self.get_logger().info('Activating: starting drive timer')
    self._timer = self.create_timer(0.1, self._drive_square)
    return super().on_activate(state)   # <-- must call super() to activate publisher
```

### Step 3 — `on_deactivate`: stop the robot

```python
def on_deactivate(self, state):
    self.get_logger().info('Deactivating: stopping robot')
    if self._timer:
        self._timer.cancel()
        self._timer = None
    stop = TwistStamped()
    stop.header.stamp = self.get_clock().now().to_msg()
    self._publisher.publish(stop)       # zero velocity
    return super().on_deactivate(state) # <-- must call super() to deactivate publisher
```

### Step 4 — `on_cleanup`: release resources

```python
def on_cleanup(self, state):
    self.get_logger().info('Cleaning up')
    if self._publisher:
        self.destroy_publisher(self._publisher)
        self._publisher = None
    return TransitionCallbackReturn.SUCCESS
```

### Testing

```bash
# Terminal 1 — 3D Gazebo simulation
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# Terminal 2
ros2 run exercise_1 turtlebot_lifecycle

# Terminal 3 — drive through the lifecycle
ros2 lifecycle set /turtlebot_lifecycle configure
ros2 lifecycle set /turtlebot_lifecycle activate
# watch the robot move in a square in Gazebo ...
ros2 lifecycle set /turtlebot_lifecycle deactivate
ros2 lifecycle set /turtlebot_lifecycle cleanup

# See available transitions
ros2 lifecycle get /turtlebot_lifecycle
```

---

## Exercise 2 — TurtleBot3 Diagnostics

### Concept

`diagnostic_updater` lets you report health status for any subsystem.
Each check is a callback that receives a `DiagnosticStatusWrapper` (`stat`) and:

- calls `stat.summary(level, message)` to set the overall status
- calls `stat.add(key, value)` to attach key/value details

| Level constant | Meaning |
|---|---|
| `DiagnosticStatus.OK` | Everything is fine |
| `DiagnosticStatus.WARN` | Something is off but not critical |
| `DiagnosticStatus.ERROR` | Action required |

### Two sources of diagnostic data

Not everything comes from the robot simulation. Diagnostics typically mix both:

| Source | Examples | Available in Gazebo? |
|---|---|---|
| **Robot topics** | battery voltage, LiDAR range, IMU frequency | Yes — Gazebo publishes these |
| **Host system** | CPU temperature, disk usage, WiFi signal | No — read directly from the OS (`/sys`, `psutil`, etc.) |

The solved node demonstrates both: battery and LiDAR come from `/battery_state` and `/scan`, while CPU temperature and disk usage are read from the machine running the simulation.

### Starting point

Open [exercise_2/exercise_2/diagnostic_node.py](exercise_2/exercise_2/diagnostic_node.py).
The subscriptions and `Updater` are already created. Fill in the TODOs.

### Step 1 — Set the hardware ID

```python
self.updater.setHardwareID('turtlebot3')
```

### Step 2 — Add an IMU subscriber and FrequencyStatus

Add the import at the top:

```python
from diagnostic_updater import Updater, FrequencyStatus, FrequencyStatusParam
from sensor_msgs.msg import BatteryState, LaserScan, Imu
```

In `__init__`, after the existing subscribers:

```python
self.create_subscription(Imu, '/imu', self._imu_cb, 10)

freq_param = FrequencyStatusParam({'min': 190.0, 'max': 210.0}, 0.1, 10)
self._imu_freq = FrequencyStatus(freq_param, name='IMU Frequency')
self.updater.add(self._imu_freq)
```

Add the callback:

```python
def _imu_cb(self, _msg: Imu):
    self._imu_freq.tick()
```

### Step 3 — Register the checks

Uncomment the two `updater.add` lines:

```python
self.updater.add('Battery', self.check_battery)
self.updater.add('LiDAR',   self.check_lidar)
```

### Step 4 — Implement `check_battery`

```python
def check_battery(self, stat):
    if self._battery is None:
        stat.summary(DiagnosticStatus.WARN, 'No battery data yet')
        return stat

    v = self._battery.voltage
    if v < 10.0:
        stat.summary(DiagnosticStatus.ERROR, f'Battery critical: {v:.2f} V')
    elif v < 11.5:
        stat.summary(DiagnosticStatus.WARN,  f'Battery low: {v:.2f} V')
    else:
        stat.summary(DiagnosticStatus.OK,    f'Battery OK: {v:.2f} V')

    stat.add('voltage (V)',    f'{v:.2f}')
    stat.add('percentage (%)', f'{self._battery.percentage * 100:.0f}')
    return stat
```

### Step 5 — Implement `check_lidar`

```python
def check_lidar(self, stat):
    if self._scan is None:
        stat.summary(DiagnosticStatus.WARN, 'No scan data yet')
        return stat

    valid = [r for r in self._scan.ranges
             if self._scan.range_min <= r <= self._scan.range_max]
    min_range = min(valid) if valid else float('inf')

    if min_range < 0.15:
        stat.summary(DiagnosticStatus.ERROR, f'Obstacle very close: {min_range:.2f} m')
    elif min_range < 0.30:
        stat.summary(DiagnosticStatus.WARN,  f'Obstacle nearby: {min_range:.2f} m')
    else:
        stat.summary(DiagnosticStatus.OK,    'Surroundings clear')

    stat.add('min range (m)', f'{min_range:.2f}')
    stat.add('valid beams',   str(len(valid)))
    return stat
```

### Testing

```bash
# Terminal 1 — start TurtleBot3 simulation (or real robot)
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# Terminal 2
ros2 run exercise_2 diagnostic_node

# Terminal 3 — inspect raw output
ros2 topic echo /diagnostics

# Or use the GUI
# You might need to install sudo apt install ros-jazzy-rqt-runtime-monitor
ros2 run rqt_runtime_monitor rqt_runtime_monitor
# if it does not work try:
## rm -rf ~/.config/ros.org/rqt_gui.ini
## ros2 run rqt_runtime_monitor rqt_runtime_monitor --force-discover
```

### Bonus ideas

Once the basics work, try adding more checks to the updater:

| Check | Topic | What to look for |
|---|---|---|
| IMU frequency | `/imu` | Use `FrequencyStatus` to verify ~100 Hz |
| Odometry freshness | `/odom` | Use `TimeStampStatus` on `header.stamp` |
| Wheel encoder stall | `/odom` | Warn if velocity is zero while commanded to move |
| CPU temperature | `/proc/thermal` | Read `/sys/class/thermal/thermal_zone0/temp` |

```python
from diagnostic_updater import FrequencyStatus, FrequencyStatusParam

freq_param = FrequencyStatusParam({'min': 95.0, 'max': 105.0}, 0.1, 10)
self.imu_freq = FrequencyStatus(freq_param, name='IMU Frequency')
self.updater.add(self.imu_freq)

# inside your IMU subscriber callback:
self.imu_freq.tick()
```

---

## Exercise 3 — Diagnostics in the Browser (rosbridge)

### Concept

**rosbridge** exposes ROS 2 topics over a WebSocket so any browser or HTTP client can subscribe and publish without installing ROS.

```
ROS 2 node  →  /diagnostics  →  rosbridge (ws://localhost:9090)  →  browser
```

**roslibjs** is the JavaScript library that speaks the rosbridge protocol — two objects are all you need:

| Object | What it does |
|---|---|
| `ROSLIB.Ros` | Opens the WebSocket connection to rosbridge |
| `ROSLIB.Topic` | Subscribes or publishes to a ROS 2 topic |

### Setup

Install rosbridge if not already present:

```bash
sudo apt install ros-jazzy-rosbridge-server
```

Launch everything:

```bash
# Terminal 1 — skip if Gazebo is already running from a previous exercise
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# Terminal 2
ros2 run exercise_2 diagnostic_node

# Terminal 3
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

### The full webpage

Open [exercise_3/index.html](exercise_3/index.html) in a browser — no web server needed.

In the Chrome or Firefox address bar type:

```
file:///PATH_TO_WORKSPACE/5_class_5_exercices/exercise_3/index.html
```

For example:

```
file:///home/user/ros2_ws/5_class_5_exercices/exercise_3/index.html
```

The two key lines that connect it to ROS:

```javascript
// 1. Connect to rosbridge
const ros = new ROSLIB.Ros({ url: 'ws://localhost:9090' })

// 2. Subscribe to a topic
const diagTopic = new ROSLIB.Topic({
  ros,
  name: '/diagnostics',
  messageType: 'diagnostic_msgs/DiagnosticArray'
})
diagTopic.subscribe(message => updateDiagnostics(message))
```

Everything else (HTML, CSS, rendering the cards) is just webpage code. the ROS part is only those two objects.

### Take-home: drive the robot from the browser

To **publish** instead of subscribe, use `topic.publish()` with a `ROSLIB.Message`:

```javascript
const cmdVel = new ROSLIB.Topic({
  ros,
  name: '/cmd_vel',
  messageType: 'geometry_msgs/TwistStamped'
})

// Send a forward command
cmdVel.publish(new ROSLIB.Message({
  header: { stamp: { sec: 0, nanosec: 0 }, frame_id: '' },
  twist: {
    linear:  { x: 0.2, y: 0.0, z: 0.0 },
    angular: { x: 0.0, y: 0.0, z: 0.0 }
  }
}))
```

Add two buttons to the page (Forward / Stop), attach `onclick` handlers that call `cmdVel.publish(...)`, and you have a browser-based robot controller.

---

## Exercise 4 — MQTT Bridge

### Concept

**MQTT** is a lightweight pub/sub protocol widely used in IoT.
Unlike ROS 2 (DDS) or rosbridge (WebSocket), MQTT works over any network — the **subscriber doesn't need ROS installed at all**.

```
Gazebo → ROS 2 node → paho-mqtt → HiveMQ broker → any Python subscriber (no ROS)
```

| Component | Role |
|---|---|
| `paho-mqtt` | Python MQTT library — publish and subscribe |
| `broker.hivemq.com` | Free public broker — no setup, works from anywhere |
| `publisher.py` | ROS 2 node that reads `/battery_state` and publishes over MQTT |
| `subscriber.py` | Plain Python script — no ROS needed, runs on any machine |

> **Note:** `broker.hivemq.com` is a public broker — anyone can see your messages. Fine for class demos, never use for real robots.

### Setup

```bash
sudo apt install python3-paho-mqtt
# or: pip install paho-mqtt
```

### Starting point

Open [exercise_4/scripts/publisher.py](exercise_4/scripts/publisher.py) and [exercise_4/scripts/subscriber.py](exercise_4/scripts/subscriber.py).
Fill in the TODO sections in both files.

### Step 1 — Publisher: connect and publish

In `publisher.py`:

```python
# Create and connect the MQTT client
self.mqtt = mqtt.Client()
self.mqtt.connect(BROKER, PORT)
self.mqtt.loop_start()

# Subscribe to the ROS 2 topic
self.create_subscription(Odometry, '/odom', self._odom_cb, 10)
```

In the callback, publish the position:

```python
def _odom_cb(self, msg: Odometry):
    x = msg.pose.pose.position.x
    y = msg.pose.pose.position.y
    value = f'x={x:.2f} y={y:.2f}'
    self.mqtt.publish(TOPIC, value)
```

### Step 2 — Subscriber: receive and print

In `subscriber.py`:

```python
def on_message(client, userdata, msg):
    value = msg.payload.decode()
    print(f'Update on {msg.topic}: {value}')

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC)
client.loop_forever()
```

### Testing

```bash
# Terminal 1 — Gazebo (skip if already running)
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# Terminal 2 — publish odometry over MQTT
python3 exercise_4/scripts/publisher.py

# Terminal 3 — receive it (no ROS needed, works from any machine)
python3 exercise_4/scripts/subscriber.py
```

You should see:
```
Listening on broker.hivemq.com → robotics_class/turtlebot/odom ...
Update on robotics_class/turtlebot/odom: x=0.00 y=0.00
Update on robotics_class/turtlebot/odom: x=0.02 y=0.00
```

### Take-home — publish multiple topics

Open [exercise_4/scripts/publisher_takehome.py](exercise_4/scripts/publisher_takehome.py).
Extend the publisher to send both `/odom` position and `/scan` minimum range over MQTT.

You need to:
1. Add a second MQTT topic constant `TOPIC_SCAN`
2. Add a second `create_subscription` for `/scan`
3. Implement `_scan_cb` — compute the minimum valid range and publish it

The subscriber (`subscriber.py`) will need to subscribe to `'robotics_class/changeme/#'` (wildcard) to receive both topics:

```python
client.subscribe('robotics_class/changeme/#')
```

Run:
```bash
python3 exercise_4/scripts/publisher_takehome.py
python3 exercise_4/scripts/subscriber.py
```
