import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_my_bot = get_package_share_directory('my_bot')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # Navigasyon Parametre Dosyası
    nav2_params_file = os.path.join(pkg_my_bot, 'config', 'nav2_params.yaml')
    
    # 1. Gazebo'yu Başlat (Boş Dünya)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        ),
        # world argümanı yok, boş dünya 
    )

    # 2. Robot State Publisher (RSP) Başlat
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_my_bot, 'launch', 'rsp.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 3. Robotu Gazebo'ya Ekle (Spawn Entity)
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description',
                   '-entity', 'my_bot'],
        output='screen'
    )

  
    return LaunchDescription([
        gazebo,
        rsp,
        spawn_entity,
    ])