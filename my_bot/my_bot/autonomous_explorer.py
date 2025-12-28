#!/usr/bin/env python3
import time
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from tf_transformations import euler_from_quaternion
from rclpy.parameter import Parameter

class FinalExplorer(Node):
    def __init__(self):
        super().__init__('final_explorer')
        # Simülasyon zamanı ayarı 
        self.set_parameters([Parameter('use_sim_time', Parameter.Type.BOOL, True)])
        
        self.pub_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub_scan = self.create_subscription(LaserScan, '/scan', self.scan_cb, 10)
        self.sub_odom = self.create_subscription(Odometry, '/odom', self.odom_cb, 10)
            
        self.current_pose = None
        self.current_yaw = 0.0
        self.latest_scan = None
        
        # Sıkışma kontrolü için
        self.last_position = None
        self.stuck_start_time = time.time()
        
        self.get_logger().info("FİNAL KÂŞİF: Hedef -> En Geniş Boşluk! 🚀")

    def odom_cb(self, msg):
        self.current_pose = msg.pose.pose
        q = msg.pose.pose.orientation
        (r, p, y) = euler_from_quaternion([q.x, q.y, q.z, q.w])
        self.current_yaw = y

    def scan_cb(self, msg):
        self.latest_scan = msg

    def warmup_routine(self):
        print("ISINMA TURU: Harita genişletiliyor (10 saniye)...")
        twist = Twist()
        # Olduğu yerde dönerek etrafı tara
        twist.angular.z = 0.5
        
        end_time = time.time() + 10
        while time.time() < end_time:
            self.pub_cmd_vel.publish(twist)
            time.sleep(0.1)
            rclpy.spin_once(self, timeout_sec=0.0)
            
        self.pub_cmd_vel.publish(Twist()) # Dur
        print("Isınma Bitti. Nav2 Moduna Geçiliyor.")

    # --- EN İYİ HEDEFİ BULUCU ---
    def find_best_goal(self):
        if not self.latest_scan: return None

        ranges = self.latest_scan.ranges
        # Sonsuz verileri 10 metre kabul et
        clean_ranges = [10.0 if (r > 10.0 or r == float('inf')) else (0.0 if r < 0.1 else r) for r in ranges]
        
        # Basit "Sliding Window" yöntemi ile en geniş boşluğu bul
        window_size = 20 # 20 derecelik dilimlere bak
        best_score = -1.0
        best_index = 0
        
        for i in range(len(clean_ranges)):
            # Pencere içindeki ortalama mesafeye bak
            current_sum = 0
            count = 0
            for j in range(window_size):
                idx = (i + j) % len(clean_ranges)
                current_sum += clean_ranges[idx]
                count += 1
            
            avg = current_sum / count
            if avg > best_score:
                best_score = avg
                best_index = (i + window_size // 2) % len(clean_ranges) # Pencerenin ortası

        # Eğer en iyi yer bile çok darsa (Duvar dibi) -> None döndür
        if best_score < 0.5: return None

        # Hedef açısı
        angle = self.latest_scan.angle_min + (best_index * self.latest_scan.angle_increment)
        dist = clean_ranges[best_index]
        
        return angle, dist

    # --- KURTARMA MANEVRASI ---
    def unstuck_maneuver(self):
        print(" SIKIŞMA ALGILANDI! Geri çıkılıyor...")
        twist = Twist()
        twist.linear.x = -0.25 # Geri git
        for _ in range(15):
            self.pub_cmd_vel.publish(twist)
            time.sleep(0.1)
        
        twist.linear.x = 0.0
        twist.angular.z = 1.0 # Dön
        for _ in range(10):
            self.pub_cmd_vel.publish(twist)
            time.sleep(0.1)
        self.pub_cmd_vel.publish(Twist())
        self.stuck_start_time = time.time() # Zamanlayıcıyı sıfırla

def main():
    rclpy.init()
    node = FinalExplorer()
    nav = BasicNavigator()
    
    # 1. Nav2 öncesi harita oluştur
    node.warmup_routine()
    
    print(" OTONOM SÜRÜŞ BAŞLIYOR...")
    
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
            
            # --- SIKIŞMA KONTROLÜ ---
            # Robot 5 saniyedir aynı yerdeyse (0.1m hareket etmediyse)
            if node.current_pose:
                current_time = time.time()
                if node.last_position:
                    dx = node.current_pose.position.x - node.last_position.position.x
                    dy = node.current_pose.position.y - node.last_position.position.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist > 0.15: # Hareket var
                        node.stuck_start_time = current_time
                        node.last_position = node.current_pose
                    elif current_time - node.stuck_start_time > 5.0:
                        # Sıkıştı!
                        nav.cancelTask()
                        node.unstuck_maneuver()
                        continue
                else:
                    node.last_position = node.current_pose

            # --- NAVİGASYON ---
            if nav.isTaskComplete():
                result = node.find_best_goal()
                if result:
                    angle, raw_dist = result
                    
                    # Hedefi çok uzağa koyma, 1.5 metre ilerisi güvenli
                    target_dist = 1.5
                    
                    if node.current_pose:
                        final_yaw = node.current_yaw + angle
                        gx = node.current_pose.position.x + (target_dist * math.cos(final_yaw))
                        gy = node.current_pose.position.y + (target_dist * math.sin(final_yaw))
                        
                        print(f"📍 Yeni Hedef: {raw_dist:.2f}m uzaktaki boşluk. Gidiliyor...")
                        
                        goal = PoseStamped()
                        goal.header.frame_id = 'map'
                        goal.header.stamp = nav.get_clock().now().to_msg()
                        goal.pose.position.x = gx
                        goal.pose.position.y = gy
                        
                        from tf_transformations import quaternion_from_euler
                        q = quaternion_from_euler(0, 0, final_yaw)
                        goal.pose.orientation.x = q[0]
                        goal.pose.orientation.y = q[1]
                        goal.pose.orientation.z = q[2]
                        goal.pose.orientation.w = q[3]
                        
                        nav.goToPose(goal)
                else:
                    print("Yol bulunamadı, dönülüyor...")
                    twist = Twist()
                    twist.angular.z = 0.5
                    node.pub_cmd_vel.publish(twist)

    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
