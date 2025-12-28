#!/usr/bin/env python3
import time
import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

def wake_up_spin(node, pub):
    print("SLAM HARİTASI GÜNCELLENİYOR (Etraf taranıyor)...")
    msg = Twist()
    msg.angular.z = 0.8 # Hızlı dön
    
    # 5 saniye boyunca dön (Harita sınırları açılsın)
    for _ in range(50):
        pub.publish(msg)
        time.sleep(0.1)
    
    # Dur
    msg.angular.z = 0.0
    pub.publish(msg)
    print("Harita güncellendi. Navigasyon başlıyor!")

def main():
    rclpy.init()
    navigator = BasicNavigator()
    
    # Manuel motor kontrolü için (Spin atmak için)
    temp_node = rclpy.create_node('spinner')
    cmd_vel_pub = temp_node.create_publisher(Twist, '/cmd_vel', 10)

    # 1. BAŞLAT
    print("NAV2 SİSTEMİ BAŞLATILIYOR...")
    navigator.lifecycleStartup()
    
    # Konumu Sıfırla (Başlangıç noktası 0,0 kabul edilir)
    initial_pose = PoseStamped()
    initial_pose.header.frame_id = 'map'
    initial_pose.header.stamp = navigator.get_clock().now().to_msg()
    initial_pose.pose.position.x = 0.0
    initial_pose.pose.position.y = 0.0
    initial_pose.pose.orientation.w = 1.0
    navigator.setInitialPose(initial_pose)
    
    # Nav2'nin kendine gelmesi için bekle
    navigator.waitUntilNav2Active()
    
    # 2. ETRAFI TARA (SLAM Haritasını Şişir)
    wake_up_spin(temp_node, cmd_vel_pub)

    # --- 3. HEDEFLERİ BELİRLE (STRATEJİK NOKTALAR) ---
    
    waypoints = [
        # HEDEF 1: Odanın kapısına yaklaş (Düz ilerle)
        {'x': 1.5, 'y': 0.0, 'w': 1.0},
        
        # HEDEF 2: Kapıdan geç ve koridora gir (Sol tarafa doğru)
        {'x': 2.5, 'y': 1.0, 'w': 0.707}, 
        
        # HEDEF 3: Koridorun sonuna git (Çıkış)
        {'x': 4.0, 'y': 1.0, 'w': 1.0}
    ]

    # --- 4. GÖREVİ BAŞLAT ---
    for i, wp in enumerate(waypoints):
        print(f"HEDEF {i+1} GİDİLİYOR: X={wp['x']}, Y={wp['y']}...")
        
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = navigator.get_clock().now().to_msg()
        goal_pose.pose.position.x = wp['x']
        goal_pose.pose.position.y = wp['y']
        goal_pose.pose.orientation.w = wp['w']

        navigator.goToPose(goal_pose)

        # Gidene kadar bekle
        while not navigator.isTaskComplete():
            feedback = navigator.getFeedback()
            # print(f"Mesafe: {feedback.distance_remaining:.2f}m", end='\r')
            pass

        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print(f"HEDEF {i+1} TAMAMLANDI!")
        else:
            print(f" HEDEF {i+1} BAŞARISIZ! (Robot sıkıştı veya yol bulamadı)")
            # Başarısız olsa bile bir sonraki hedefe şans ver (Belki orası açıktır)

    print(" GÖREV BİTTİ! EVE DÖNÜLÜYOR...")
    
    # navigator.goToPose(initial_pose)

    temp_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
