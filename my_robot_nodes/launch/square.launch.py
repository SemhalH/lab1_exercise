from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    ExecuteProcess,
    TimerAction,
    RegisterEventHandler
)
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    diffdrive_launch = os.path.join(
        get_package_share_directory('diffdrive_bot'),
        'launch',
        'control.launch.py'
    )

    side_length = LaunchConfiguration('side_length')

    disable_drive_controller = ExecuteProcess(
        cmd=[
            'ros2', 'service', 'call',
            '/drive_enable',
            'std_srvs/srv/SetBool',
            '{data: false}'
        ],
        output='screen'
    )

    square_driver = Node(
        package='my_robot_nodes',
        executable='square_driver',
        parameters=[{'side_length': side_length}],
        output='screen'
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'side_length',
            default_value='0.5',
            description='Length of each square side in meters'
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(diffdrive_launch)
        ),

        Node(
            package='my_robot_nodes',
            executable='rotate_server',
            output='screen'
        ),

        RegisterEventHandler(
            OnProcessExit(
                target_action=disable_drive_controller,
                on_exit=[square_driver]
            )
        ),

        TimerAction(
            period=10.0,
            actions=[disable_drive_controller]
        ),

    ])
