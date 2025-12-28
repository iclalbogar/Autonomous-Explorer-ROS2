import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Config dosyasının yerini buluyoruz
    slam_params_file = os.path.join(get_package_share_directory('my_bot'), 'config', 'mapper_params_online_async.yaml')

    # SLAM Toolbox Node'unu tanımlıyoruz
    start_async_slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
          slam_params_file,
          {'use_sim_time': use_sim_time}
        ]
    )

    return LaunchDescription([
        start_async_slam_toolbox_node
    ])