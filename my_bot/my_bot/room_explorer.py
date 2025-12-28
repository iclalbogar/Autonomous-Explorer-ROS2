#!/usr/bin/env python3
import rclpy
import time
import random
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

class RoomExplorer(Node):
    def __init__(self):
        super().__init__('room_explorer')
        self.get_logger().info("ODA KEŞİFÇİSİ V2.1: Zamanlayıcı Düzeltildi! ")

def main():
    rclpy.init()
    node = RoomExplorer()
    nav = BasicNavigator()

    # AMCL beklemesini kaldırdık BURAYA SONRA BAKILACAK---------------------------------------------------
    print(" Sistem hazırlanıyor (5 saniye bekleniyor)...")
    time.sleep(5.0) 
    
    # Odanın sınırları (Rastgele hedef için)
    min_x, max_x = -3.5, 3.5
    min_y, max_y = -3.5, 3.5

    print(" KEŞİF BAŞLIYOR! Robot rastgele gezecek...")

    while rclpy.ok():
        # 1. Rastgele hedef belirle
        target_x = random.uniform(min_x, max_x)
        target_y = random.uniform(min_y, max_y)
        
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = nav.get_clock().now().to_msg()
        goal_pose.pose.position.x = target_x
        goal_pose.pose.position.y = target_y
        goal_pose.pose.orientation.w = 1.0 

        print(f" Yeni Hedef: X={target_x:.2f}, Y={target_y:.2f}")

        # 2. Nav2'ye git emri ver
        nav.goToPose(goal_pose)
        
        # ROS zamanı yerine standart Python zamanı kullanıyoruz.
        start_time = time.time() # Görev başlangıç zamanı

        # 3. Takip et
        i = 0
        while not nav.isTaskComplete():
            i += 1
            feedback = nav.getFeedback()
            if feedback and i % 10 == 0:
                print(f"   Mesafe: {feedback.distance_remaining:.2f}m")
            
            # Zaman aşımı kontrolü (25 saniye)
            # time.time() saniye cinsinden verir, 25 ile kıyaslamak yeterli.
            elapsed_time = time.time() - start_time
            if elapsed_time > 25.0:
               print(f" Hedef çok uzak (Geçen süre: {elapsed_time:.1f}s). İptal ediliyor...")
               nav.cancelTask()
               break

        # Sonuç kontrolü
        result = nav.getResult()
        if result == TaskResult.SUCCEEDED:
            print(" Hedefe Varıldı!")
        elif result == TaskResult.CANCELED:
            print(" Hedef İptal Edildi.")
        elif result == TaskResult.FAILED:
            print("Gidilemedi (Duvar içi veya engel).")

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
