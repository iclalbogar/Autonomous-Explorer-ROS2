# Autonomous Explorer ROS2

## About the Project
This repository contains a mobile robot simulation developed using ROS 2 (Humble) and Gazebo. The primary objective of this project is to enable a differential drive robot to autonomously navigate and map an unknown environment in real-time. 

Developed as part of the CEN449 Autonomous Navigation coursework at Çukurova University, the system utilizes Simultaneous Localization and Mapping (SLAM) algorithms alongside a custom reactive navigation logic to explore its surroundings without relying on a pre-saved map.

## Technical Specifications
* **Framework:** ROS 2 (Humble Hawksbill)
* **Simulation Environment:** Gazebo
* **Robot Type:** Differential Drive Mobile Robot
* **Mapping:** Real-time SLAM integration for dynamic environment mapping.
* **Autonomous Navigation:** Reactive navigation algorithm implemented in Python (otonom_surucu.py), allowing the robot to dynamically detect and avoid obstacles while exploring unknown territories.

## Repository Structure
* **my_bot:** Contains the core ROS 2 packages, robot description files (URDF/XACRO), and Gazebo world configurations.
* **otonom_surucu.py:** The primary Python script responsible for executing the autonomous exploration and obstacle avoidance logic.

## Installation & Setup
1. Clone this repository into the `src` directory of your ROS 2 workspace.
2. Navigate to the root of your workspace and build the project using colcon: `colcon build`
3. Source your workspace environment: `source install/setup.bash`
4. Launch the Gazebo simulation and spawn the robot using the appropriate launch file provided inside the `my_bot` package.
5. In a new terminal, execute the autonomous navigation script (`otonom_surucu.py`) to initiate the exploration and mapping process.

## Developer
* Esra İclal Boğar - [@iclalbogar](https://github.com/iclalbogar)
