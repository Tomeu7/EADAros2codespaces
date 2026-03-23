from setuptools import find_packages, setup

package_name = 'exercise_2'

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
    description='Exercise 2 — TurtleBot3 diagnostics (skeleton)',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'diagnostic_node = exercise_2.diagnostic_node:main',
        ],
    },
)
