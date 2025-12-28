#!/usr/bin/env python3
import time
import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

def main():
    rclpy.init()
    
    # --- BÖLÜM 1: MOTORLARI HAZIRLA (Nav2 Bypass) ---
    # Nav2'den bağımsız olarak robotu itmek için publisher oluşturuyoruz.
    node = rclpy.create_node('blind_mover')
    publisher = node.create_publisher(Twist, '/cmd_vel', 10)
    
    print("Isınma: Robot guvenli alana (x > 0) itiliyor...")
    
    # 3 Saniye boyunca ileri git komutu bas
    msg = Twist()
    msg.linear.x = 0.2  # Yavaşça ileri
    msg.angular.z = 0.0
    
    start_time = time.time()
    while (time.time() - start_time) < 3.0:
        publisher.publish(msg)
        time.sleep(0.1)
        
    # Durdur
    msg.linear.x = 0.0
    publisher.publish(msg)
    print("Robot güvenli alanda! Nav2 devreye giriyor...")
    
    # Node'u kapat (Nav2 ile çakışmasın)
    node.destroy_node()

    # --- BÖLÜM 2: NAVIGASYON BAŞLIYOR ---
    navigator = BasicNavigator()
    # Nav2'nin kendine gelmesi için kısa bir bekleme
    time.sleep(2.0) 

    # HEDEF LİSTESİ 
    waypoints = [
        {'x': 1.5, 'y': 0.0, 'name': 'Hedef A (İleri)'},
        {'x': 1.5, 'y': 1.0, 'name': 'Hedef B (Sol)'},
        {'x': 0.0, 'y': 0.0, 'name': 'Hedef C (Başlangıç)'}
    ]

    for wp in waypoints:
        print(f"--- {wp['name']} hedefine gidiliyor... ({wp['x']}, {wp['y']}) ---")
        
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = navigator.get_clock().now().to_msg()
        goal_pose.pose.position.x = wp['x']
        goal_pose.pose.position.y = wp['y']
        goal_pose.pose.orientation.w = 1.0

        navigator.goToPose(goal_pose)

        while not navigator.isTaskComplete():
            feedback = navigator.getFeedback()
            if feedback:
                # Kalan mesafeyi göster
                print(f"Mesafe: {feedback.distance_remaining:.2f} m", end='\r')
            time.sleep(0.5)

        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print(f"\n{wp['name']} TAMAMLANDI! ")
        else:
            print(f"\n{wp['name']} BAŞARISIZ!  Durum: {result}")

    print("GÖREV BİTTİ! ")
    rclpy.shutdown()

if __name__ == '__main__':
    main()
