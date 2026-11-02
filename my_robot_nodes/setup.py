
from setuptools import setup
import os
from glob import glob

package_name = 'my_robot_nodes'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='semhal',
    maintainer_email='semhalhabte147@gmail.com',
    description='Robot control nodes for Lab 1',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turn_away = my_robot_nodes.turn_away:main',
            'rotate_server = my_robot_nodes.rotate_server:main',
            'square_driver = my_robot_nodes.square_driver:main',
        ],
    },
)

