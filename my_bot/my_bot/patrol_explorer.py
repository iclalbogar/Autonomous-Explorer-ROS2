#!/usr/bin/env python3
import rclpy
import time
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

class PatrolExplorer(Node):
    def __init__(self):
        super().__init__('patrol_explorer')
        self.get_logger().info("DEVRİYE MODU: Kutuların Arkasına Geçiş Başlıyor! 👮")

def main():
    rclpy.init()
    node = PatrolExplorer()
    nav = BasicNavigator()

    print("⏳ Sistem hazırlanıyor (5 saniye)...")
    time.sleep(5.0) 
    
    # HEDEF LİSTESİ (STRATEJİK NOKTALAR)
    # Bu noktalar odanın en uç köşeleri ve kenarlarıdır.
    # Robot buralara gitmek için mecburen kutuların etrafından dolaşacaktır.
    waypoints = [
        {'x': 3.5, 'y': 3.5, 'name': "Sağ Üst Köşe"},
        {'x': 3.5, 'y': -3.5, 'name': "Sağ Alt Köşe"},
        {'x': -3.5, 'y': -3.5, 'name': "Sol Alt Köşe"},
        {'x': -3.5, 'y': 3.5, 'name': "Sol Üst Köşe"},
        {'x': 0.0, 'y': 3.5, 'name': "Üst Duvar Dibi (Kutu Arkası?)"},
        {'x': 0.0, 'y': -3.5, 'name': "Alt Duvar Dibi"},
        {'x': 0.0, 'y': 0.0, 'name': "Oda Merkezi"}
    ]

    print(" DEVRİYE BAŞLIYOR! Sırayla tüm noktalara gidilecek...")

    # Sonsuz döngü (Tüm noktalar bitince başa döner)
    while rclpy.ok():
        for wp in waypoints:
            target_x = wp['x']
            target_y = wp['y']
            target_name = wp['name']
            
            # Hedefi Hazırla
            goal_pose = PoseStamped()
            goal_pose.header.frame_id = 'map'
            goal_pose.header.stamp = nav.get_clock().now().to_msg()
            goal_pose.pose.position.x = float(target_x)
            goal_pose.pose.position.y = float(target_y)
            goal_pose.pose.orientation.w = 1.0 

            print(f"\n YENİ HEDEF: {target_name} (X={target_x}, Y={target_y})")
            print("   -> Rota hesaplanıyor (Kutuların etrafından)...")

            # Git
            nav.goToPose(goal_pose)
            
            start_time = time.time() # Zamanlayıcıyı başlat

            # Takip Et
            while not nav.isTaskComplete():
                feedback = nav.getFeedback()
                # 25 saniye içinde gidemezse pes et (Sıkışmış olabilir)
                if time.time() - start_time > 25.0:
                   print(f" {target_name} hedefine ulaşılamadı (Zaman Aşımı). Pas geçiliyor.")
                   nav.cancelTask()
                   break
                # CPU'yu yormamak için az bekle
                time.sleep(0.1)

            # Sonuç Raporu
            result = nav.getResult()
            if result == TaskResult.SUCCEEDED:
                print(f"{target_name} TAMAMLANDI!")
            else:
                print(f"{target_name} BAŞARISIZ OLDU.")
            
            # Hedefte 2 saniye bekle (Hocaya "Bakın geldim" demek için)
            time.sleep(2.0)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
