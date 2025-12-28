#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import subprocess
import os

class MissionController(Node):
    def __init__(self):
        super().__init__('mission_controller')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.loop)
        self.start_time = time.time()
        self.state = "CALIBRATING" # Başlangıç durumu
        
        # Kullanıcının dosya yolunu otomatik bul
        self.home = os.path.expanduser('~')
        self.config_file = os.path.join(self.home, 'ros2_ws/src/my_bot/config/explore_params.yaml')

        self.get_logger().info("🚀 GÖREV BAŞLATILDI: Harita Kalibrasyonu Yapılıyor...")

    def loop(self):
        twist = Twist()
        elapsed = time.time() - self.start_time

        # --- AŞAMA 1: HARİTA OLUŞTURMA (40 Saniye) ---
        # Robotu çok yavaş döndür ki SLAM duvarları net görsün.
        if self.state == "CALIBRATING":
            if elapsed < 40.0:
                twist.angular.z = 0.2  # Güvenli dönüş hızı
                self.publisher_.publish(twist)
                
                # Kullanıcıyı bilgilendir (Her 5 saniyede bir)
                if int(elapsed) % 5 == 0 and int(elapsed * 10) % 10 == 0:
                     self.get_logger().info(f"⏳ Harita işleniyor... ({int(40-elapsed)} sn kaldı)")
            else:
                # Süre bitti, robotu durdur
                twist.angular.z = 0.0
                self.publisher_.publish(twist)
                self.state = "EXPLORING"
                self.start_exploration()

    def start_exploration(self):
        self.get_logger().info("✅ Kalibrasyon Tamamlandı! Otonom Keşif Başlatılıyor...")
        
        # Explore Lite komutunu hazırla
        cmd = f"ros2 run explore_lite explore --ros-args --params-file {self.config_file}"
        
        # Komutu sistemde çalıştır
        try:
            subprocess.Popen(cmd, shell=True)
            self.get_logger().info("🏁 Explore Lite devrede! Robotun kontrolü yapay zekada.")
        except Exception as e:
            self.get_logger().error(f"HATA: Explore Lite başlatılamadı: {e}")
        
        # Bu scriptin işi bitti, kendini kapatsın ama Nav2 çalışmaya devam etsin
        self.destroy_node()
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = MissionController()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
