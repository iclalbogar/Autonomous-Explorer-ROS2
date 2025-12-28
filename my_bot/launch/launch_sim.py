import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration 
from launch_ros.actions import Node

def generate_launch_description():
    package_name='my_bot'

    # Simülasyon zamanını kullanıp kullanmayacağımızı belirleyen argüman
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Robot State Publisher (RSP) dosyasını çağırıyoruz
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), 
                # Simülasyon zamanını RSP'ye iletiyoruz (TF hatasını çözen kısım)
                launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Gazebo'yu başlatıyoruz
    gazebo_params_file = os.path.join(get_package_share_directory(package_name),'config','sim_params.yaml')
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
                    launch_arguments={'extra_gazebo_args': '--ros-args --params-file ' + gazebo_params_file}.items()
             )

    # Robotu Gazebo içine "doğuruyoruz" (Spawn)
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'my_bot'],
                        output='screen')

    return LaunchDescription([
        # Argümanı tanımlıyoruz
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use sim time if true'),
        
        rsp,
        gazebo,
        spawn_entity,
    ])