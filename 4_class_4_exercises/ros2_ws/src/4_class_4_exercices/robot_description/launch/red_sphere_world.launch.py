import os
from ament_index_python.packages import get_package_prefix, get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import SetParameter


def generate_launch_description():

    package_description = "robot_description"
    package_directory = get_package_share_directory(package_description)

    # Add meshes and worlds to Gazebo resource path so it can find the SDF
    install_dir_path = get_package_prefix(package_description) + "/share"
    robot_meshes_path = os.path.join(package_directory, "meshes")
    worlds_path = os.path.join(package_directory, "worlds")
    gazebo_resource_paths = [install_dir_path, robot_meshes_path, worlds_path]

    if "GZ_SIM_RESOURCE_PATH" in os.environ:
        for resource_path in gazebo_resource_paths:
            if resource_path not in os.environ["GZ_SIM_RESOURCE_PATH"]:
                os.environ["GZ_SIM_RESOURCE_PATH"] += ":" + resource_path
    else:
        os.environ["GZ_SIM_RESOURCE_PATH"] = ":".join(gazebo_resource_paths)

    # Full path to the world SDF
    world_sdf = os.path.join(package_directory, "worlds", "red_sphere_world.sdf")

    gzsim_pkg = get_package_share_directory("ros_gz_sim")
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([gzsim_pkg, "launch", "gz_sim.launch.py"])
        ),
        launch_arguments={"gz_args": "-r " + world_sdf}.items(),
    )

    return LaunchDescription([
        SetParameter(name="use_sim_time", value=True),
        gz_sim,
    ])
