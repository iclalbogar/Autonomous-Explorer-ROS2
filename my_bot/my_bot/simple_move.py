#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class SimpleMover(Node):
    def __init__(self):
        super().__init__('simple_mover')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.5, self.move_robot)
        self.get_logger().info('Motor Testi Basladi! Robot ileri gitmeli...')

    def move_robot(self):
        msg = Twist()
        msg.linear.x = 0.5  # İleri hız
        msg.angular.z = 0.0 # Dönüş yok
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    simple_mover = SimpleMover()

    # 3 saniye çalıştır ve dur
    start_time = time.time()
    while rclpy.ok() and (time.time() - start_time) < 3.0:
        rclpy.spin_once(simple_mover)

    # Durdur
    stop_msg = Twist()
    simple_mover.publisher_.publish(stop_msg)
    simple_mover.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
