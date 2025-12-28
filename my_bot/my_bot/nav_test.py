#!/usr/bin/env python3
import time
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy

def main():
    rclpy.init()
    navigator = BasicNavigator()
    
    print("Nav2 sisteminin hazir olmasi bekleniyor...")
    # Hedef Belirle (x=2.0 metre ileri)
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose.pose.position.x = 2.0
    goal_pose.pose.position.y = 0.0
    goal_pose.pose.orientation.w = 1.0

    print("Hedef gonderiliyor...")
    navigator.goToPose(goal_pose)

    # Durumu Takip Et
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback:
            print(f'Hedefe kalan mesafe: {feedback.distance_remaining:.2f} m')
        # Bu süreyi kısalttık ki terminalde daha sık güncellensin
        time.sleep(1.0)

    # Sonuç
    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('HEDEFE ULASILDI! ')
    elif result == TaskResult.CANCELED:
        print('Gorev iptal edildi.')
    elif result == TaskResult.FAILED:
        print('Gorev BASARISIZ OLDU! ')

    rclpy.shutdown()

if __name__ == '__main__':
    main()
