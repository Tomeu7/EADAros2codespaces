cmake_minimum_required(VERSION 3.8)
project(action_msg)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Generate action interfaces
rosidl_generate_interfaces(${PROJECT_NAME}
  "action/ReachEdgeAndReturn.action"
)

# Needed so other packages can depend on these generated interfaces
ament_export_dependencies(rosidl_default_runtime)

ament_package()