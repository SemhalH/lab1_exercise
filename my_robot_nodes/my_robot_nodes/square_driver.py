
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from lab_interfaces.action import DriveDistance
from my_robot_interfaces.action import Rotate


class SquareDriver(Node):

    def __init__(self):
        super().__init__('square_driver')

        self.declare_parameter('side_length', 0.5)

        self.drive_client = ActionClient(
            self,
            DriveDistance,
            '/drive_distance'
        )

        self.rotate_client = ActionClient(
            self,
            Rotate,
            '/rotate'
        )

        self.get_logger().info('Square Driver node started')

    def send_goal(self, client, goal):

        self.get_logger().info('Waiting for action server...')
        client.wait_for_server()

        future = client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)

        goal_handle = future.result()

        if goal_handle is None or not goal_handle.accepted:
            self.get_logger().error('Goal rejected!')
            return None

        self.get_logger().info('Goal accepted!')

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        response = result_future.result()

        if response is None or response.status != 4:
            self.get_logger().error('Goal failed!')
            return None

        return response.result

    def run_square(self):

        side_length = self.get_parameter('side_length').value

        for side in range(1, 5):

            self.get_logger().info(
                f'Driving side {side} of 4'
            )

            # Drive forward
            drive_goal = DriveDistance.Goal()
            drive_goal.distance = float(side_length)

            drive_result = self.send_goal(
                self.drive_client,
                drive_goal
            )

            if drive_result is None or not drive_result.reached:
                self.get_logger().error(
                    f'Drive failed on side {side}'
                )
                return

            self.get_logger().info(
                f'Side {side} completed: '
                f'{drive_result.travelled:.2f} meters'
            )

            # Rotate left by 90 degrees
            rotate_goal = Rotate.Goal()
            rotate_goal.angle = 1.57

            rotate_result = self.send_goal(
                self.rotate_client,
                rotate_goal
            )

            if rotate_result is None:
                self.get_logger().error(
                    f'Rotation failed after side {side}'
                )
                return

        self.get_logger().info(
            'Square completed successfully!'
        )


def main(args=None):

    rclpy.init(args=args)

    node = SquareDriver()

    try:
        node.run_square()

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

