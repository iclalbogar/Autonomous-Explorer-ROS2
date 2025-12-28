import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class OtonomSurucu(Node):
    def __init__(self):
        super().__init__('otonom_surucu')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.get_logger().info('Otonom Surucu Baslatildi! Robot gezmeye basliyor...')
        self.move_cmd = Twist()

    def scan_callback(self, msg):
        clean_ranges = [r for r in msg.ranges if not (r == float('inf')) and r > 0.0]
        
        min_mesafe = 10.0
        if len(clean_ranges) > 0:
            min_mesafe = min(clean_ranges)

        if min_mesafe < 0.6:
            self.move_cmd.linear.x = 0.0
            self.move_cmd.angular.z = 0.5  
            self.get_logger().info('Engel var! Donuyorum...')
        else:
            self.move_cmd.linear.x = 0.3   
            self.move_cmd.angular.z = 0.0
            
        self.publisher_.publish(self.move_cmd)

def main(args=None):
    rclpy.init(args=args)
    otonom_surucu = OtonomSurucu()
    try:
        rclpy.spin(otonom_surucu)
    except KeyboardInterrupt:
        pass
    finally:
        stop_cmd = Twist()
        otonom_surucu.publisher_.publish(stop_cmd)
        otonom_surucu.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

