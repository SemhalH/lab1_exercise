# ROS 2 Lab 1 Exercise — Differential Drive Robot

## Project Overview

This repository contains the implementation of Lab 1 using ROS 2 Humble and Gazebo. It includes four ROS 2 packages:

- `diffdrive_bot` — Differential drive robot description, simulation, sensors, and control.
- `lab_interfaces` — Custom ROS 2 interfaces.
- `my_robot_interfaces` — Custom messages, services, and actions.
- `my_robot_nodes` — ROS 2 nodes implementing the robot behavior.

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo
- `colcon`
- RViz2

## Build Instructions

Clone this repository into the `src` directory of a ROS 2 workspace.

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Build the workspace:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Running the Exercises

All commands below should be run after sourcing ROS 2 and the workspace:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

### Step 1 — Robot Sensors

The robot description includes a rear-mounted depth camera and a center-mounted IMU.

Configured sensor topics:

- `/depth_camera/image`
- `/depth_camera/points`
- `/depth_camera/camera_info`
- `/imu`

Launch the Gazebo simulation:

```bash
ros2 launch diffdrive_bot gazebo.launch.py
```

Use RViz2 to visualize the depth image and point cloud.

### Step 2 — Obstacle Avoidance

The `turn_away` node subscribes to obstacle information and publishes velocity commands to `/cmd_vel`.

The robot moves forward when the path is clear and turns away when an obstacle is detected.

### Step 3 — Configurable Parameters

The obstacle avoidance node supports configurable parameters:

- `forward_speed` — default 0.2 m/s
- `turn_speed` — default 0.5 rad/s

### Step 4 — Robot Status

A custom `RobotStatus` message is used to publish robot status information through `/robot_status`.

### Step 5 — Services

The implementation includes:

- `/turn_away_enable` — enables or disables obstacle avoidance using `SetBool`.
- `/set_turn_speed` — changes the turning speed with validation against the configured maximum speed.

### Step 6 — Rotate Action

The `rotate_server` node provides the `/rotate` action server. It rotates the robot by a requested angle, supports cancellation, and reports feedback and results.

### Step 7 — Square Driving Action Client

The `square_driver` node drives the robot in a square using distance and rotation actions.

Launch the square exercise:

```bash
ros2 launch my_robot_nodes square.launch.py
```

The default side length is 0.5 meters.

## Known Issues and Limitations

During testing, some sensor topics did not publish data at their configured update rates.

- **Depth Camera:** Configured at 10 Hz, but the observed publishing rate was approximately 1.28 Hz.
- **Point Cloud:** Configured at 10 Hz, but the observed publishing rate was approximately 0.15–0.18 Hz.
- **IMU:** Configured at 50 Hz, but the observed publishing rate was approximately 5.4 Hz.

**Possible Cause:**

Gazebo's real-time factor fluctuated during testing. I suspect that simulation performance and resource limitations in the WSL2 environment may have contributed to the reduced sensor publishing rates. However, this cause has not been confirmed.

**Successful Testing:**

The square-driving exercise was successfully completed. The robot performed four forward movements and four rotations using the custom action server and client. The launch configuration also disables the default drive controller before starting the square driver to prevent competing velocity commands.

## Screenshots

Screenshots from the exercises are stored in the `screenshots/` directory.

- `rviz_sensors.png` — RViz depth image and point cloud visualization.
- `rqt_graph.png` — ROS 2 node graph while the square-driving launch is running.

## Technologies

- ROS 2 Humble
- Python
- Gazebo
- RViz2
- URDF / Xacro
- ROS 2 topics, services, and actions
