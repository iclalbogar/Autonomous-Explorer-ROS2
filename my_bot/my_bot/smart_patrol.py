#!/usr/bin/env python3
import time
import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

def spin_robot(node, publisher):
    # Robotu Nav2'den bağımsız olarak fiziksel döndürür
    # Bu, Lidar'ın etrafı taramasını ve Costmap'in şişmesini sağlar.
    print("UYANMA MODU: Haritayı açmak için dönülüyor...")
    msg = Twist()
    msg.angular.z = 0.5
    
    # 8 saniye boyunca dön (Yaklaşık 360 derece)
    for _ in range(80):
        publisher.publish(msg)
        time.sleep(0.1)
        
    # Durdur
    msg.angular.z = 0.0
    publisher.publish(msg)
    print("Robot uyandı! Navigasyon başlıyor.")

def main():
    rclpy.init()
    
    # Nav2 Başlatıcı
    navigator = BasicNavigator()
    
    # Manuel sürüş için publisher (Nav2 kilitlenirse robotu dürtmek için)
    temp_node = rclpy.create_node('waker_upper')
    cmd_vel_pub = temp_node.create_publisher(Twist, '/cmd_vel', 10)

    # 1. BAŞLANGIÇ RİTÜELİ
    # Önce Nav2'yi ayağa kaldır
    print("Navigasyon sistemi başlatılıyor...")
    navigator.lifecycleStartup() 
    
    # Başlangıç konumu ata (0,0)
    initial_pose = PoseStamped()
    initial_pose.header.frame_id = 'map'
    initial_pose.header.stamp = navigator.get_clock().now().to_msg()
    initial_pose.pose.position.x = 0.0
    initial_pose.pose.position.y = 0.0
    initial_pose.pose.orientation.w = 1.0
    navigator.setInitialPose(initial_pose)
    
    # *** KRİTİK HAMLE: ZORLA DÖNDÜR ***
    # Nav2 hazır olmasa bile robotu döndür ki harita açılsın.
    spin_robot(temp_node, cmd_vel_pub)
    
    # Nav2'nin kendine gelmesi için bekle
    time.sleep(3.0)

    # --- HEDEF LİSTESİ ---
    goals = [
        # Hedef 1: Odanın ortasına/kapısına doğru
        {'x': 1.0, 'y': 0.0, 'w': 1.0},
        
        # Hedef 2: Kapıdan geçiş (Köşeyi dön)
        {'x': 1.8, 'y': 0.0, 'w': 1.0},
        
        # Hedef 3: Koridor (Sola dönüş)
        {'x': 1.8, 'y': 1.5, 'w': 0.707}
    ]

    for i, goal in enumerate(goals):
        print(f"--- HEDEF {i+1} GİDİLİYOR: X={goal['x']}, Y={goal['y']} ---")
        
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = navigator.get_clock().now().to_msg()
        goal_pose.pose.position.x = goal['x']
        goal_pose.pose.position.y = goal['y']
        goal_pose.pose.orientation.w = goal['w']

        navigator.goToPose(goal_pose)

        while not navigator.isTaskComplete():
            # İlerleme durumunu göster
            feedback = navigator.getFeedback()
            pass

        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print(f"HEDEF {i+1} TAMAMLANDI! ")
        else:
            print(f"HEDEF {i+1} BAŞARISIZ!  Durum: {result}")

    # Temizlik
    temp_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
