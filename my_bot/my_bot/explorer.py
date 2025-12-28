#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class MazeSolverFinal(Node):
    def __init__(self):
        super().__init__('maze_solver')
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.move_cmd = Twist()
        self.state = 'FORWARD'
        self.state_end_time = 0.0
        self.seek_direction = 1.0 
        
        # BOŞLUK TEYİT SAYACI (YENİ)
        self.gap_confirmation_count = 0
        
        # Sıkışma takibi
        self.last_check_time = 0.0
        self.last_front_dist = 0.0
        
        self.get_logger().info("LABİRENT USTASI V19.0: BOŞLUK TEYİT MODU 🎯")

    def get_clock_sec(self):
        return self.get_clock().now().nanoseconds / 1e9

    def scan_callback(self, msg):
        current_time = self.get_clock_sec()
        ranges = msg.ranges
        size = len(ranges)

        # --- VERİ HAZIRLIĞI ---
        # 1. Ham Veri (Tampon)
        raw_segment = ranges[0:20] + ranges[-20:]
        valid_raw = [r for r in raw_segment if r > 0.05 and r < 10.0]
        raw_front = min(valid_raw) if valid_raw else 10.0

        # 2. Navigasyon Gözü (Filtreli)
        def get_clean_min(start, end):
            segment = ranges[start:end]
            valid = [x for x in segment if x > 0.25 and x < 10.0]
            if not valid: return 10.0
            return min(valid)

        d_left_side = get_clean_min(int(size*0.20), int(size*0.30))
        d_right_side = get_clean_min(int(size*0.70), int(size*0.80))
        d_left_diag = get_clean_min(int(size*0.10), int(size*0.20))

        # --- DURUM GEÇİŞLERİ ---
        
        # Geri gitme bitti -> ÇIKIŞ ARA
        if current_time > self.state_end_time and self.state == 'BACKWARD':
            self.state = 'SEEK_GAP'
            self.state_end_time = current_time + 4.0 # 4 saniye süre ver
            self.gap_confirmation_count = 0 # Sayacı sıfırla
            
            # Boş tarafa dön
            if d_left_side > d_right_side:
                self.seek_direction = 1.0 # Sol
                print("🔍 Geri hamle bitti. SOLA bakılıyor...")
            else:
                self.seek_direction = -1.0 # Sağ
                print("🔍 Geri hamle bitti. SAĞA bakılıyor...")
                
     
        
        if current_time < self.state_end_time:
            # A. ACİL FREN (Manevra sırasında çarpma)
            if self.state != 'BACKWARD' and raw_front < 0.15:
                print(f"ACİL DURUŞ! ({raw_front:.2f}m)...                 ", end='\r')
                self.state = 'BACKWARD'
                self.state_end_time = current_time + 1.2
                self.move_cmd.linear.x = -0.15
                self.move_cmd.angular.z = 0.0
                self.publisher.publish(self.move_cmd)
                return

            # B. BOŞLUK ARAMA MODU (Geliştirilmiş!)
            if self.state == 'SEEK_GAP':
                # Kural: Önümde en az 1.5 metre boşluk olmalı
                if raw_front > 1.5:
                    # HEMEN GİTME! Önce dur ve emin ol.
                    self.move_cmd.linear.x = 0.0
                    self.move_cmd.angular.z = 0.0
                    self.gap_confirmation_count += 1
                    print(f"Hedef kilitleniyor... ({self.gap_confirmation_count}/10)", end='\r')
                    
                    # 10 kare boyunca (yaklaşık 1 saniye) boşluk gördüysen GİT
                    if self.gap_confirmation_count > 10:
                        self.state = 'FORWARD'
                        self.state_end_time = 0.0 
                        print("\n ROTA ONAYLANDI! İlerliyorum...                 ")
                else:
                    # Boşluk yoksa dönmeye devam et
                    self.gap_confirmation_count = 0 # Sayacı sıfırla
                    self.move_cmd.linear.x = 0.0
                    self.move_cmd.angular.z = 0.6 * self.seek_direction # Yavaş dön
                    print(f"🔄 Tarıyorum... ({raw_front:.2f}m)               ", end='\r')
                
                self.publisher.publish(self.move_cmd)
                return

            self.publisher.publish(self.move_cmd)
            return

        # --- SIKIŞMA KONTROLÜ ---
        if current_time - self.last_check_time > 6.0:
            if self.state == 'FORWARD' and abs(raw_front - self.last_front_dist) < 0.05:
                self.state = 'RECOVERY'
                self.state_end_time = current_time + 2.0
                self.move_cmd.linear.x = -0.25
                self.move_cmd.angular.z = 1.0
                self.publisher.publish(self.move_cmd)
                return
            self.last_check_time = current_time
            self.last_front_dist = raw_front

        # --- NORMAL SÜRÜŞ ---

        # 1. TAMPON
        if raw_front < 0.25:
            self.state = 'BACKWARD'
            self.state_end_time = current_time + 1.0
            self.move_cmd.linear.x = -0.15
            self.move_cmd.angular.z = -0.2
            print(f" TAMPON ({raw_front:.2f}m)! Geri...                  ", end='\r')

        # 2. KAPI DÖNÜŞÜ (Hafifletilmiş)
        elif d_left_diag > 2.0 and raw_front < 2.0:
            self.state = 'TURN_LEFT'
            self.state_end_time = current_time + 0.65 
            self.move_cmd.linear.x = 0.25
            self.move_cmd.angular.z = 1.1 
            print(f" KAPI! Dönülüyor...                                  ", end='\r')

        # 3. İLERLEME
        else:
            self.state = 'FORWARD'
            self.move_cmd.linear.x = 0.40
            
            error = d_left_side - 0.70
            if error > 1.0: error = 1.0 
            self.move_cmd.angular.z = max(min(error * 0.8, 0.4), -0.4)
            
            print(f" İLERLİYORUM (Duvar: {d_left_side:.2f}m)               ", end='\r')

        self.publisher.publish(self.move_cmd)

def main(args=None):
    rclpy.init(args=args)
    node = MazeSolverFinal()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
