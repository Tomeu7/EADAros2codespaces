from setuptools import find_packages, setup
import os
from glob import glob
package_name = 'robot_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.*')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='Exercise 4',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'move_and_scan = robot_description.move_and_scan:main',
            'move_and_imu = robot_description.move_and_imu:main',
            'move_and_imu_odom = robot_description.move_and_imu_odom:main',
            'red_object_detector = robot_description.red_object_detector:main',
        ],
    },
)
