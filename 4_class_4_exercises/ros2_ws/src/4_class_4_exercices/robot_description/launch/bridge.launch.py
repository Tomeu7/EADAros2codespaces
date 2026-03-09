from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/laser/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan",
            "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
            "/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image",
        ],
        output="screen"
    )

    return LaunchDescription([bridge])
