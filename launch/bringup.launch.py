"""Arranca el adaptador RC-0 con el agente del carro ya conectado."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    config_file = os.path.join(
        get_package_share_directory('capytown_esan'),
        'config',
        'odom_adapter.yaml',
    )
    return LaunchDescription([
        Node(
            package='capytown_esan',
            executable='odom_adapter',
            name='odom_adapter',
            output='screen',
            parameters=[config_file],
        ),
    ])
