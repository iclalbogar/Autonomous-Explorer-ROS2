#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import subprocess # Terminal komutu çalıştırmak için
import os

class AutoManager(Node):
    def __init__(self):
        super().__init__('auto_manager')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.start_time = time.time()
        self.scanning = True
        self.get_logger().info("SİSTEM OTONOM OLARAK BAŞLATILIYOR... 🎬")
        self.get_logger().info("Aşama 1: Çevre Taraması ve Harita Oluşturma (15 sn)")

    def timer_callback(self):
        twist = Twist()
        elapsed_time = time.time() - self.start_time

        # --- AŞAMA 1: HARİTAYI AÇMAK İÇİN DÖN ---
        if elapsed_time < 50.0:
            twist.angular.z = 0.2  # Dönüş hızı
            self.publisher_.publish(twist)
        
        # --- AŞAMA 2: PİLOTU ÇAĞIR ---
        elif self.scanning:
            # 1. Robotu Durdur
            twist.angular.z = 0.0
            self.publisher_.publish(twist)
            
            self.get_logger().info("✅ Harita Hazır! Explore Lite (Otonom Pilot) Başlatılıyor...")
            
            # 2. Explore Lite Komutunu Hazırla
            # Config dosyasının tam yolunu buluyoruz
            home_dir = os.path.expanduser('~')
            config_path = os.path.join(home_dir, 'ros2_ws/src/my_bot/config/explore_params.yaml')
            
            cmd = f"ros2 run explore_lite explore --ros-args --params-file {config_path}"
            
            # 3. Yeni bir terminalde veya arka planda çalıştır
            # shell=True ile komutu terminale yazar gibi çalıştırıyoruz
            subprocess.Popen(cmd, shell=True)
            
            self.scanning = False
            self.get_logger().info("🚀 Görev Explore Lite'a devredildi. Benim işim bitti.")
            
            # Kendini kapat
            self.destroy_node()
            rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = AutoManager()
    rclpy.spin(node)
    
if __name__ == '__main__':
    main()
