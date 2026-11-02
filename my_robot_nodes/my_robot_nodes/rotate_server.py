
#!/usr/bin/env python3

import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from my_robot_interfaces.action import Rotate


def normalize_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


def get_yaw(q):
    return math.atan2(
        2.0 * (q.w * q.z + q.x * q.y),
        1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    )


class RotateServer(Node):

    def __init__(self):
        super().__init__('rotate_server')

        self.callback_group = ReentrantCallbackGroup()

        self.current_yaw = None

        self.cmd_vel_publisher = self.create_publisher(
            Twist, '/cmd_vel', 10
        )

        self.odom_subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10,
            callback_group=self.callback_group
        )

        self.action_server = ActionServer(
            self,
            Rotate,
            '/rotate',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info('Rotate action server started')

    def odom_callback(self, msg):
        self.current_yaw = get_yaw(msg.pose.pose.orientation)

    def goal_callback(self, goal_request):
        if goal_request.angle == 0.0:
            self.get_logger().warning('Rejecting zero-angle goal')
            return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Rotation cancellation requested')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        target_angle = float(goal_handle.request.angle)
        direction = 1.0 if target_angle > 0 else -1.0

        self.get_logger().info(
            f'Rotating {target_angle:.2f} radians'
        )

        # Wait until the first odometry measurement arrives
        while self.current_yaw is None:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.cmd_vel_publisher.publish(Twist())
                result = Rotate.Result()
                result.turned = 0.0
                return result

            time.sleep(0.05)

        previous_yaw = self.current_yaw
        turned = 0.0

        twist = Twist()
        twist.angular.z = direction * 0.5

        feedback = Rotate.Feedback()
        result = Rotate.Result()

        while abs(turned) < abs(target_angle):

            if goal_handle.is_cancel_requested:
                self.cmd_vel_publisher.publish(Twist())
                goal_handle.canceled()

                result.turned = float(turned)
                return result

            if self.current_yaw is not None:
                yaw_change = normalize_angle(
                    self.current_yaw - previous_yaw
                )

                turned += yaw_change
                previous_yaw = self.current_yaw

            feedback.turned = float(turned)
            goal_handle.publish_feedback(feedback)

            self.cmd_vel_publisher.publish(twist)

            time.sleep(0.05)

        self.cmd_vel_publisher.publish(Twist())

        goal_handle.succeed()

        result.turned = float(turned)

        self.get_logger().info(
            f'Rotation completed: {turned:.2f} radians'
        )

        return result


def main(args=None):
    rclpy.init(args=args)

    node = RotateServer()

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
