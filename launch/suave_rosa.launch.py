# Copyright 2023 Gustavo Rezende Silva
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import LaunchConfigurationEquals
from launch.conditions import LaunchConfigurationNotEquals
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    mission_type = LaunchConfiguration('mission_type')
    result_filename = LaunchConfiguration('result_filename')

    mission_type_arg = DeclareLaunchArgument(
        'mission_type',
        default_value='time_constrained_mission',
        description='Desired mission type' +
                    '[time_constrained_mission or const_dist_mission]'
    )

    result_filename_arg = DeclareLaunchArgument(
        'result_filename',
        default_value='',
        description='Name of the results file'
    )

    pkg_rosa_kb = get_package_share_directory(
        'rosa_kb')

    pkg_rosa_bringup = get_package_share_directory(
        'rosa_bringup')
    rosa_bringup_launch_path = os.path.join(
        pkg_rosa_bringup,
        'launch',
        'rosa_bringup.launch.py')

    pkg_suave_path = get_package_share_directory(
        'suave')
    suave_launch_path = os.path.join(
        pkg_suave_path,
        'launch',
        'suave.launch.py')

    pkg_suave_rosa = get_package_share_directory(
        'suave_rosa')

    schema_path = "[{0}, {1}]".format(
        os.path.join(pkg_rosa_kb, 'config', 'schema.tql'),
        os.path.join(pkg_rosa_kb, 'config', 'ros_schema.tql'))

    data_path = "[{}]".format(
        os.path.join(pkg_suave_rosa, 'config', 'suave.tql'))

    rosa_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(rosa_bringup_launch_path),
        launch_arguments={
            'schema_path': schema_path,
            'data_path': data_path,
            'database_name': 'suave_db',
            'force_data': 'True',
            'force_database': 'True',
            'infer': 'True',
        }.items()
    )

    suave_rosa_bt_node = Node(
        package='suave_rosa',
        executable='suave_rosa',
    )

    suave_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(suave_launch_path),
        launch_arguments={
            'task_bridge': 'False'}.items()
    )

    mission_config = os.path.join(
        get_package_share_directory('suave_missions'),
        'config',
        'mission_config.yaml'
    )

    mission_metrics_node = Node(
        package='suave_missions',
        executable='mission_metrics',
        name='mission_metrics',
        parameters=[mission_config, {
            'adaptation_manager': 'rosa',
            'mission_name': mission_type,
        }],
        condition=LaunchConfigurationEquals('result_filename', '')
    )

    mission_metrics_node_override = Node(
        package='suave_missions',
        executable='mission_metrics',
        name='mission_metrics',
        parameters=[mission_config, {
            'adaptation_manager': 'rosa',
            'mission_name': mission_type,
            'result_filename': result_filename,
        }],
        condition=LaunchConfigurationNotEquals('result_filename', '')
    )

    return LaunchDescription([
        mission_type_arg,
        result_filename_arg,
        rosa_bringup,
        suave_rosa_bt_node,
        suave_launch,
        mission_metrics_node,
        mission_metrics_node_override
    ])
