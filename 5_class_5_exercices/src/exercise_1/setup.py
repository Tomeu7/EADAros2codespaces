from setuptools import find_packages, setup

package_name = 'exercise_1'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='Exercise 1 — TurtleBot3 LifecycleNode (skeleton)',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turtlebot_lifecycle = exercise_1.turtlebot_lifecycle:main',
        ],
    },
)
