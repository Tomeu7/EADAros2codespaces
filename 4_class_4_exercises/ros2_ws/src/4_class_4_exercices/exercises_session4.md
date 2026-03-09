# Session 4 — Sensors, Simulation, and Autonomous Behaviour

In this session you build on the ROS-Gazebo integration from Session 3. You will extend a base robot URDF step-by-step with real sensor plugins (LiDAR, IMU, camera), write Python nodes that process sensor data, and finish with a take-home exercise that combines everything into a reactive Finite State Machine.

Work in:

```bash
cd ~/ros2_ws/src/robot_description
source /opt/ros/jazzy/setup.bash
```

All exercises use the same ROS 2 package: `robot_description`.

---

# Exercise 1

## 1) Add the Differential Drive Plugin to robot_default.urdf

Add the following block inside `robot_default.urdf`, after the caster wheel section and before the closing `</robot>` tag.
This plugin allows the robot to receive velocity commands and publish odometry.

```xml
<!-- =========================================================
     DIFFERENTIAL DRIVE PLUGIN
     Listens to /cmd_vel (Twist) and drives the two wheels.
     Publishes odometry to /odom and TF transform odom->link_chassis.
     wheel_separation: distance between left and right wheel centres (m)
     wheel_radius: radius of the drive wheels (m)
========================================================= -->
<gazebo>
    <plugin
        filename="libgz-sim-diff-drive-system.so"
        name="gz::sim::systems::DiffDrive">
        <left_joint>joint_chassis_left_wheel</left_joint>   <!-- name of left wheel joint -->
        <right_joint>joint_chassis_right_wheel</right_joint> <!-- name of right wheel joint -->
        <wheel_separation>1.66</wheel_separation> <!-- metres between wheel centres -->
        <wheel_radius>0.4</wheel_radius>           <!-- wheel radius in metres -->
        <odom_publish_frequency>20</odom_publish_frequency> <!-- Hz -->
        <topic>cmd_vel</topic>         <!-- Gazebo topic for velocity commands -->
        <odom_topic>odom</odom_topic>  <!-- Gazebo topic for odometry output -->
        <tf_topic>tf</tf_topic>
        <frame_id>odom</frame_id>
        <child_frame_id>link_chassis</child_frame_id>
    </plugin>
</gazebo>
```

## 2) Bridge ROS to Gazebo

```bash
ros2 run ros_gz_bridge \
parameter_bridge /cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist
```

## 3) Run twist

```bash
ros2 topic pub /cmd_vel \
geometry_msgs/msg/Twist "{linear: {x: 0.5, y: 0.0, z: 0.0}, \
angular: {x: 0.0, y: 0.0, z: 0.5}}"
```

# Exercise 2 

1) Add Lidar

```xml
<!-- Gazebo tags - Laser scan -->
<gazebo reference="joint_laser_scan_chassis">
    <preserveFixedJoint>true</preserveFixedJoint>
</gazebo>
<gazebo reference="link_laser_scan">
    <material>Gazebo/DarkGrey</material>
</gazebo>

<!-- Laser scan -->
<joint name="joint_laser_scan_chassis" type="fixed">
    <origin rpy="0 0 0" xyz="0.8 0 0.3" />
    <child link="link_laser_scan" />
    <parent link="link_chassis" />
    <joint_properties damping="1.0" friction="1.0" />
</joint>


<link name="link_laser_scan">
    <inertial>
        <origin xyz="0 0 0" rpy="0 0 0" />
        <mass value="0.5" />
        <inertia ixx="0.000252666666667" ixy="0" ixz="0" 
        iyy="0.000252666666667" iyz="0" izz="0.0005"/>
    </inertial>
    <visual>
        <origin xyz="0 0 0" rpy="0 0 0" />
        <geometry>
            <cylinder radius="0.15" length="0.20"/>
        </geometry>
        <material name="Red">
            <color rgba="0.7 0.1 0.1 1" />
        </material>
    </visual>
    <collision>
        <origin xyz="0 0 0" rpy="0 0 0"/>
        <geometry>
            <cylinder radius="0.15" length="0.20"/>
        </geometry>
    </collision>
</link>

<gazebo>
    <plugin
    filename="libgz-sim-sensors-system"
    name="gz::sim::systems::Sensors">
    <!-- use ogre2 if ogre v2.x is installed
    , otherwise use ogre -->
    <render_engine>ogre2</render_engine>
    </plugin>
</gazebo>

<gazebo reference="link_laser_scan">
    <sensor type="gpu_lidar" name="head_hokuyo_sensor">
        <pose relative_to='lidar_frame'>0 0 0 0 0 0</pose>
        <always_on>1</always_on>
        <visualize>true</visualize>
        <update_rate>20</update_rate>
        <topic>/laser/scan</topic>
        <ray>
            <scan>
                <horizontal>
                    <samples>720</samples>
                    <resolution>1</resolution>
                    <min_angle>-1.570796</min_angle>
                    <max_angle>1.570796</max_angle>
                </horizontal>
            </scan>
            <range>
                <min>0.20</min>
                <max>10.0</max>
                <resolution>0.01</resolution>
            </range>
            <noise>
                <type>gaussian</type>
                <mean>0.0</mean>
                <stddev>0.01</stddev>
            </noise>
        </ray>
    </sensor>
</gazebo>
```

2) Create a Python script that drives the robot using linear and angular velocity arguments and prints the minimum LiDAR distance while the robot is moving.

## Connect rosbridge

```bash
ros2 run ros_gz_bridge parameter_bridge /cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist /laser/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan
```

## Result

Example result:
```
[INFO] [1772839603.179930964] [move_and_scan]: Minimum laser distance: 3.815 m
[INFO] [1772839603.278697426] [move_and_scan]: Minimum laser distance: 3.811 m
[INFO] [1772839603.381666853] [move_and_scan]: Minimum laser distance: 3.816 m
```

# Exercise 3 - Imu

```bash
ros2 run ros_gz_bridge parameter_bridge /cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist /imu@sensor_msgs/msg/Imu[gz.msgs.IMU
```

# Exercise 4 - Launchers and Topic Discovery

Now that the robot has LiDAR and IMU, use the provided launch files to bring everything up and explore what topics are available on both the Gazebo and ROS sides.

## 1) Launch Gazebo with the empty world

```bash
ros2 launch robot_description empty_world.launch.py
```

## 2) Spawn the robot

```bash
ros2 launch robot_description spawn.launch.py
```

## 3) Start the bridge

```bash
ros2 launch robot_description bridge.launch.py
```

## 4) Inspect Gazebo topics

```bash
gz topic -l
```

## 5) Inspect ROS topics

```bash
ros2 topic list
```

Compare the two lists. You should see `/laser/scan`, `/imu`, `/odom`, `/cmd_vel`, and `/camera/image_raw` on the ROS side.

## 6) Echo a topic to verify data is flowing

```bash
ros2 topic echo /imu
ros2 topic echo /laser/scan --no-arr
```

# Exercise 5 - RGB Camera

Add an RGB camera to your robot URDF. The camera should be mounted at the front of the chassis, above the LiDAR.

## 1) Add to robot_default.urdf

Add the following block inside `robot.urdf`, after the LiDAR section and before the closing `</robot>` tag:

```xml
<!-- Fixed joint attaching camera to chassis -->
<!-- xyz: x=0.8 (front), y=0 (centre), z=0.6 (above lidar) -->
<joint name="joint_camera_chassis" type="fixed">
    <origin rpy="0 0 0" xyz="0.8 0 0.6" />
    <child link="link_camera" />
    <parent link="link_chassis" />
</joint>

<!-- Preserve fixed joint so Gazebo does not merge the links -->
<gazebo reference="joint_camera_chassis">
    <preserveFixedJoint>true</preserveFixedJoint>
</gazebo>

<!-- Camera link: small box representing the physical camera body -->
<link name="link_camera">
    <inertial>
        <mass value="0.1" />
        <origin xyz="0 0 0" rpy="0 0 0" />
        <inertia ixx="0.000001" ixy="0" ixz="0" iyy="0.000001" iyz="0" izz="0.000001"/>
    </inertial>
    <visual>
        <origin xyz="0 0 0" rpy="0 0 0" />
        <geometry>
            <box size="0.05 0.1 0.05"/> <!-- width x depth x height in metres -->
        </geometry>
        <material name="DarkGrey">
            <color rgba="0.2 0.2 0.2 1" />
        </material>
    </visual>
    <collision>
        <origin xyz="0 0 0" rpy="0 0 0"/>
        <geometry>
            <box size="0.05 0.1 0.05"/>
        </geometry>
    </collision>
</link>

<!-- Gazebo camera sensor attached to link_camera -->
<gazebo reference="link_camera">
    <sensor type="camera" name="rgb_camera">
        <always_on>1</always_on>
        <visualize>true</visualize>
        <update_rate>10</update_rate>           <!-- Hz -->
        <topic>/camera/image_raw</topic>        <!-- GZ topic name -->
        <camera>
            <horizontal_fov>1.047</horizontal_fov> <!-- ~60 degrees in radians -->
            <image>
                <width>640</width>   <!-- pixels -->
                <height>480</height> <!-- pixels -->
                <format>R8G8B8</format> <!-- standard RGB format -->
            </image>
            <clip>
                <near>0.1</near>   <!-- minimum render distance (m) -->
                <far>100</far>     <!-- maximum render distance (m) -->
            </clip>
            <noise>
                <type>gaussian</type>
                <mean>0.0</mean>
                <stddev>0.007</stddev> <!-- small noise to simulate real sensor -->
            </noise>
        </camera>
    </sensor>
</gazebo>
```

## 2) Bridge the camera topic

Add `/camera/image_raw` to your bridge (already included in `bridge.launch.py`):

```bash
ros2 launch robot_description bridge.launch.py
```

## 3) View the camera feed

```bash
ros2 run rqt_image_view rqt_image_view
```

Then select `/camera/image_raw` from the dropdown.

# Exercise 6 - Red Object Detection with cv_bridge

Use the RGB camera and OpenCV to detect the red sphere placed in the world.

## 1) Launch the world with the red sphere

A custom world file is provided at `worlds/red_sphere_world.sdf`. Launch Gazebo with it:

```bash
ros2 launch robot_description red_sphere_world.launch.py
```

Then spawn the robot:
```bash
ros2 launch robot_description spawn.launch.py
```

## 2) Start the bridge

```bash
ros2 launch robot_description bridge.launch.py
```

## 3) Write the detector node

Create `red_object_detector.py` in `robot_description/robot_description/`. The node must:
- Subscribe to `/camera/image_raw`
- Use `cv_bridge` to convert the ROS image to OpenCV (`bgr8`)
- Convert BGR → HSV with `cv2.cvtColor`
- Apply a red colour mask using `cv2.inRange`
- Find contours with `cv2.findContours` and log the centroid and area of the largest red region

**HINT:** Red wraps around in HSV — you need **two** ranges combined with `cv2.bitwise_or`:
```python
lower_red1 = np.array([0,   120, 70])
upper_red1 = np.array([10,  255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])
```

## 4) Add entry point to setup.py

```python
'red_object_detector = robot_description.red_object_detector:main',
```

## 5) Build and run

```bash
cd ~/ros2_ws && colcon build --packages-select robot_description && source install/setup.bash
ros2 run robot_description red_object_detector
```

## Expected result

```
[INFO] [red_object_detector]: Red object detected! Area: 4823px | Centroid: (312, 241) | Bounding box: x=248 y=178 w=128 h=126
```

---

# Exercise 7 - Finite State Machine

Implement a robot behaviour using a **Finite State Machine (FSM)** with the following states:

| State | Behaviour |
|---|---|
| **EXPLORE** | Rotate slowly to search for the red target |
| **TRACK** | Move toward the red object (camera centroid) |
| **AVOID** | Turn away from a LiDAR obstacle |
| **STOP** | Halt — triggered by IMU anomaly (collision/tilt) |

State transitions:
- `EXPLORE` → `TRACK`: red object detected by camera
- `TRACK` → `EXPLORE`: target lost (no red pixels)
- `EXPLORE` / `TRACK` → `AVOID`: LiDAR detects obstacle closer than 0.6 m
- `AVOID` → `EXPLORE`: path is clear
- Any state → `STOP`: IMU angular velocity spike or tilt detected

## 1) Start the bridge

```bash
ros2 launch robot_description bridge.launch.py
```

## 2) Launch the world

```bash
ros2 launch robot_description red_sphere_world.launch.py
```

Then spawn the robot:
```bash
ros2 launch robot_description spawn.launch.py
```

## 3) Create `fsm_robot.py`

Create `robot_description/robot_description/fsm_robot.py`.

The node must:
- Subscribe to `/laser/scan` (`sensor_msgs/msg/LaserScan`)
- Subscribe to `/camera/image_raw` (`sensor_msgs/msg/Image`) via `cv_bridge`
- Subscribe to `/imu` (`sensor_msgs/msg/Imu`)
- Publish `/cmd_vel` (`geometry_msgs/msg/Twist`)
- Implement the four states above using a string variable `self.state`
- Log a message every time the state changes

## 4) Add entry point to `setup.py`

```python
'fsm_robot = robot_description.fsm_robot:main',
```

## 5) Build and run

```bash
cd ~/ros2_ws && colcon build --packages-select robot_description && source install/setup.bash
ros2 run robot_description fsm_robot
```

## Deliverables

Submit by **22nd March**:

1. **Code** — `fsm_robot.py` with all four states implemented
2. **Video** — screen recording of the robot running in Gazebo showing at least two state transitions
3. **Explanation** — short written description (one paragraph) of:
   - which sensors trigger each state transition
   - any problems you encountered and how you solved them

---

# Acknowledgements

Exercises inspired by [The Construct — Introduction to Gazebo Sim with ROS 2](https://www.theconstruct.ai/robotigniteacademy_learnros/ros-courses-library/introduction-to-gazebo-sim-with-ros2-online-course/)