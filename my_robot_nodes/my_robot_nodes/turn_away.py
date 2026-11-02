
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from lab_interfaces.msg import ObstacleInfo
from my_robot_interfaces.msg import RobotStatus
from std_srvs.srv import SetBool
from my_robot_interfaces.srv import SetTurnSpeed


class TurnAway(Node):
    def __init__(self):
        super().__init__('turn_away')

        self.declare_parameter('forward_speed', 0.2)
        self.declare_parameter('turn_speed', 0.5)
        self.declare_parameter('max_turn_speed', 1.5)

        self.enabled = False

        self.cmd_vel_publisher = self.create_publisher(
            Twist, '/cmd_vel', 10
        )

        self.status_publisher = self.create_publisher(
            RobotStatus, '/robot_status', 10
        )

        self.obstacle_subscription = self.create_subscription(
            ObstacleInfo, '/obstacle',
            self.obstacle_callback, 10
        )

        self.enable_service = self.create_service(
            SetBool,
            '/turn_away_enable',
            self.enable_callback
        )

        self.speed_service = self.create_service(
            SetTurnSpeed,
            '/set_turn_speed',
            self.set_turn_speed_callback
        )

        self.get_logger().info('Turn Away node started (disabled)')

    def enable_callback(self, request, response):
        self.enabled = request.data
        response.success = True

        if self.enabled:
            response.message = 'Turn away enabled'
        else:
            response.message = 'Turn away disabled'

            # Stop the robot once when disabling
            self.cmd_vel_publisher.publish(Twist())

        self.get_logger().info(response.message)
        return response

    def set_turn_speed_callback(self, request, response):
        speed = request.turn_speed
        max_speed = self.get_parameter('max_turn_speed').value

        if speed <= 0 or speed > max_speed:
            response.success = False
            response.message = (
                f'Invalid speed. Must be greater than 0 '
                f'and no higher than {max_speed}'
            )
        else:
            self.set_parameters([
                rclpy.parameter.Parameter(
                    'turn_speed',
                    rclpy.Parameter.Type.DOUBLE,
                    float(speed)
                )
            ])
            response.success = True
            response.message = f'Turn speed updated to {speed}'

        self.get_logger().info(response.message)
        return response

    def obstacle_callback(self, msg):
        status = RobotStatus()
        status.obstacle_distance = msg.distance

        if not self.enabled:
            status.state = 'stopped'
            self.status_publisher.publish(status)
            return

        forward_speed = self.get_parameter('forward_speed').value
        turn_speed = self.get_parameter('turn_speed').value

        twist = Twist()

        if not msg.too_close:
            twist.linear.x = forward_speed
            status.state = 'forward'
        else:
            twist.linear.x = 0.0

            if msg.angle > 0:
                twist.angular.z = -turn_speed
            else:
                twist.angular.z = turn_speed

            status.state = 'turning'

        self.cmd_vel_publisher.publish(twist)
        self.status_publisher.publish(status)


def main(args=None):
    rclpy.init(args=args)
    node = TurnAway()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

