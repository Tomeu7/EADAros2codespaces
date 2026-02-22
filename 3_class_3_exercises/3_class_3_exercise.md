# Session 3 exercise (car + bridge + collisions + TF)

Work in:

```bash
cd /workspaces/EADAros2codespaces/EADA-Robotics-and-IoT-Course/3_class_3_exercises
source /opt/ros/jazzy/setup.bash
```

## Goal flow for this class

1. Spawn car
2. Move it with GUI
3. Inspect Gazebo topics
4. Move car with Gazebo service
5. Start ROS-Gazebo bridge
6. Inspect ROS topics
7. Drive with `/cmd_vel`
8. Spawn robot
9. Hit robot with car and observe collisions
10. Spawn/bridge TF
11. Take-home task

## Exercise 0: Start Gazebo world

```bash
gz sim empty_class3.sdf
```

Keep Gazebo open in this terminal.

## Exercise 1: Spawn the car

In a new terminal:

```bash
cd /workspaces/EADAros2codespaces/EADA-Robotics-and-IoT-Course/3_class_3_exercises
ros2 run ros_gz_sim create -entity simple_car -file simple_car.urdf -x 0 -y 0 -z 0.2
```

Expected: `simple_car` appears above ground.

## Exercise 2: Move car with Gazebo GUI

In Gazebo:
- Select `simple_car`
- Use the translate/rotate gizmo to move it manually
- Confirm it can be repositioned from GUI tools

## Exercise 3: Inspect Gazebo topics

```bash
gz topic -l
gz service -l
gz topic -e -t /world/empty_class3/pose/info
```

Expected: you can find pose/state streams and world services.

## Exercise 4: Move car with Gazebo service

Goal: change `simple_car` pose at runtime from CLI.

```bash
# Check service availability
gz service -l | grep set_pose

# Move simple_car
gz service -s /world/empty_class3/set_pose \
  --reqtype gz.msgs.Pose \
  --reptype gz.msgs.Boolean \
  --req 'name: "simple_car", position: {x: 1.5, y: -0.5, z: 0.2}'
```

Expected: `simple_car` jumps to the new position and `/world/empty_class3/pose/info` updates.

## Exercise 5: Start ROS to Gazebo bridge

Remember in bridge syntax, `[` means Gazebo to ROS and `]` means ROS to Gazebo.

Terminal A:

```bash
# Clock message: simulation time from Gazebo to ROS 2 (/clock)
ros2 run ros_gz_bridge parameter_bridge /clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock
```

Terminal B:

```bash
# Twist message: velocity command from ROS 2 to Gazebo (/cmd_vel)
ros2 run ros_gz_bridge parameter_bridge /cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
```

## Exercise 6: Inspect ROS topics

```bash
ros2 topic list
ros2 topic echo /clock
```

Expected: `/clock` is visible and publishing.

## Exercise 7: Drive car with `/cmd_vel`

Straight:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.0}}" -r 10
```

Turn:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.8}}" -r 10
```

Expected: car drives and turns.

## Exercise 8: Spawn robot target

```bash
ros2 run ros_gz_sim create   -world empty_class3   -entity service_bot   -file robot.urdf   -x 2 -y 0 -z 0.1
```

If it fails, the model is not in your local Gazebo resources yet.

Expected: a second robot appears ahead of the car.

## Exercise 9: Collision demo

- Keep publishing `/cmd_vel` to drive toward `robot_target`
- Observe contact/push behavior in Gazebo
- Open Gazebo Entity Tree and inspect both models while colliding

Optional check from CLI:

```bash
gz topic -l | grep -i contact
```

## Exercise 10: Spawn/bridge TF

Bridge pose stream into ROS TF message:

```bash
ros2 run ros_gz_bridge parameter_bridge /world/empty_class3/pose/info@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V
```

Then inspect in ROS:

```bash
ros2 topic echo /world/empty_class3/pose/info
```

Note: this is a direct bridge of Gazebo pose data to a TF-compatible ROS message type.

## Take-home exercise

Repeat one previous integration in Gazebo + ROS 2:

1. Option A: reproduce your turtle shape-drawing from exercise 1 logic in Gazebo (publish commands, observe motion).
2. Option B (Week 2 bonus, +1 point): two-robot follower behavior from exercise 2 (leader + follower) bridged through ROS topics.

Submission checklist:
* Short `README.md` with run commands
* Source code (publisher/subscriber/action if used)
* 30-60s screen recording showing behavior in Gazebo
* One paragraph of what you did and what changed from turtlesim to Gazebo
