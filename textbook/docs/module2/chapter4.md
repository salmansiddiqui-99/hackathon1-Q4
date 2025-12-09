## Gazebo Simulation Fundamentals

### Introduction

Gazebo is a powerful, open-source 3D robotics simulator that provides realistic physics simulation, sensor modeling, and plugin systems for testing robot algorithms. [Citation: https://gazebosim.org/] Gazebo enables humanoid robot developers to test control algorithms, perception pipelines, and autonomous behaviors in a safe, repeatable virtual environment before deploying to hardware. This chapter covers Gazebo setup, world configuration, physics engines, and best practices for humanoid robot simulation.

### Learning Objectives

- Set up Gazebo simulation environment with ROS 2 integration
- Create and configure virtual worlds with terrain, obstacles, and physics properties
- Load humanoid robot URDF models into Gazebo with proper dynamics simulation
- Configure physics engines (ODE, Bullet, DART) for humanoid simulation
- Implement force/torque sensors, contact simulation, and constraint handling
- Create custom Gazebo plugins for extending simulation capabilities
- Monitor and visualize simulation state through ROS 2 topics and services
- Debug simulation issues and optimize performance for real-time control

### Core Concepts

#### Physics Simulation Engines

Gazebo supports multiple physics engines: ODE (Open Dynamics Engine), Bullet, and DART (Dynamic Animation and Robotics Toolkit). [Citation: https://gazebosim.org/docs/fortress/physics] Each engine has different accuracy and performance characteristics. ODE is widely used for humanoid simulation due to its stability with constraint-based joint models. DART excels at multi-body dynamics with efficient joint constraint handling. Physics engine choice significantly impacts simulation speed and accuracy of humanoid locomotion.

#### World Configuration and Gravity

A Gazebo world defines the environment: gravity vector, physics timestep, plugin libraries, and static elements (ground, obstacles, lights). [Citation: https://gazebosim.org/docs/fortress/worlds] Gravity for humanoid robots should be set to 9.81 m/s² downward (standard Earth gravity). Physics timestep (typically 0.001s) affects simulation accuracy and computational cost. Smaller timesteps improve accuracy but increase CPU usage; larger timesteps sacrifice fidelity but enable faster simulation.

#### Model Loading and Spawning

Humanoid robot models are loaded into Gazebo via SDF (Simulation Description Format) files or URDF (converted automatically). [Citation: https://gazebosim.org/docs/fortress/model_structure] Models specify visual geometry, collision shapes, inertial properties, and sensor attachments. Gazebo automatically creates physics bodies and constraints based on model definitions. Proper collision detection enables realistic foot contact during locomotion and manipulation task simulation.

#### Sensor Simulation and Ground Truth

Gazebo simulates sensor readings for cameras, LiDAR, IMU, and contact sensors. [Citation: https://gazebosim.org/docs/fortress/sensors] Simulated sensors can include realistic noise models (Gaussian noise for IMU, depth uncertainty for LiDAR). Ground truth data is available for validation and learning algorithm training. For humanoid control, accurate IMU simulation is critical for balance feedback, while force-torque sensors at joints are essential for dynamics control.

#### Contact Detection and Friction

Gazebo computes contacts between collision shapes using narrow-phase collision detection algorithms. [Citation: https://gazebosim.org/docs/fortress/physics] Contact properties (friction, restitution, surface velocity) define interaction physics. For humanoid walking, foot-ground friction must be configured realistically (typically μ > 0.5 for bipedal stability). Contact forces are transmitted through robot joints and affect joint torque requirements.

### Practical Examples

#### Example 1: Creating a Gazebo World with Humanoid Robot

```xml
<?xml version="1.0"?>
<sdf version="1.8">
  <world name="humanoid_walking">
    <!-- Physics engine configuration -->
    <physics name="default_physics" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
      <gravity>0 0 -9.81</gravity>

      <!-- ODE solver configuration -->
      <ode>
        <solver>
          <type>quick</type>
          <iters>50</iters>
          <precon_iters>0</precon_iters>
          <sor>1.3</sor>
        </solver>
        <constraints>
          <cfm>0</cfm>
          <erp>0.2</erp>
          <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
          <contact_surface_layer>0.001</contact_surface_layer>
        </constraints>
      </ode>
    </physics>

    <!-- ROS 2 integration plugin -->
    <plugin name="ignition::gazebo::systems::PhysicsSystem"/>
    <plugin name="ignition::gazebo::systems::RenderingServerSystem"/>
    <plugin name="ignition::gazebo::systems::SceneBroadcasterSystem"/>

    <!-- Ground plane -->
    <model name="ground_plane">
      <static>true</static>
      <pose>0 0 0 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>0.6</mu>
                <mu2>0.6</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Humanoid robot model -->
    <include>
      <uri>model://humanoid_robot</uri>
      <pose>0 0 0.9 0 0 0</pose>
    </include>

    <!-- Obstacles for navigation testing -->
    <model name="obstacle_box">
      <pose>2.0 0 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.5 0.5 1.0</size>
            </box>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>0.5</mu>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.5 0.5 1.0</size>
            </box>
          </geometry>
          <material>
            <ambient>0.5 0.3 0.3 1</ambient>
            <diffuse>0.5 0.3 0.3 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Lighting -->
    <light name="sun" type="directional">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <linear>0.01</linear>
        <constant>0.1</constant>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>
  </world>
</sdf>
```

This world file configures physics simulation with realistic humanoid walking parameters, ground friction, and obstacles.

#### Example 2: Launching Gazebo with ROS 2 and Publishing Joint Commands

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Twist
import math
import time

class GazeboControlNode(Node):
    def __init__(self):
        super().__init__('gazebo_controller')

        # Publishers for joint commands (Gazebo converts to physics)
        self.left_leg_pub = self.create_publisher(
            Float64MultiArray,
            '/humanoid_robot/left_leg_controller/commands',
            10
        )
        self.right_leg_pub = self.create_publisher(
            Float64MultiArray,
            '/humanoid_robot/right_leg_controller/commands',
            10
        )

        # Timer for control loop
        self.timer = self.create_timer(0.02, self.control_callback)
        self.elapsed_time = 0.0

    def control_callback(self):
        """Generate walking gait and publish commands."""
        # Simple sinusoidal gait pattern
        frequency = 1.0  # 1 Hz walking
        phase = 2 * math.pi * frequency * self.elapsed_time

        # Left leg (90-degree phase offset)
        left_hip_angle = 0.3 * math.sin(phase)
        left_knee_angle = -0.6 * math.sin(phase + math.pi/4)
        left_ankle_angle = 0.3 * math.sin(phase)

        # Right leg (180-degree phase offset for alternating steps)
        right_hip_angle = 0.3 * math.sin(phase + math.pi)
        right_knee_angle = -0.6 * math.sin(phase + math.pi + math.pi/4)
        right_ankle_angle = 0.3 * math.sin(phase + math.pi)

        # Publish left leg commands
        left_msg = Float64MultiArray()
        left_msg.data = [left_hip_angle, left_knee_angle, left_ankle_angle]
        self.left_leg_pub.publish(left_msg)

        # Publish right leg commands
        right_msg = Float64MultiArray()
        right_msg.data = [right_hip_angle, right_knee_angle, right_ankle_angle]
        self.right_leg_pub.publish(right_msg)

        self.elapsed_time += 0.02
        self.get_logger().debug(
            f"Left: hip={left_hip_angle:.3f}, knee={left_knee_angle:.3f}, ankle={left_ankle_angle:.3f}"
        )

def main(args=None):
    rclpy.init(args=args)
    node = GazeboControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Launch Gazebo with ROS 2:
```bash
# Start Gazebo with the world file
gazebo --verbose /path/to/humanoid_world.world

# In another terminal, source ROS 2 and run the controller
source /opt/ros/humble/setup.bash
source ~/robot_ws/install/setup.bash
ros2 run humanoid_control gazebo_controller

# Monitor joint states
ros2 topic echo /humanoid_robot/joint_states
```

#### Example 3: Subscribing to Gazebo Sensor Data

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState
from geometry_msgs.msg import WrenchStamped
import numpy as np

class SensorMonitorNode(Node):
    def __init__(self):
        super().__init__('sensor_monitor')

        # Subscribe to IMU data from left foot
        self.imu_sub = self.create_subscription(
            Imu,
            '/humanoid_robot/left_foot_imu',
            self.imu_callback,
            10
        )

        # Subscribe to joint states
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/humanoid_robot/joint_states',
            self.joint_state_callback,
            10
        )

        # Subscribe to foot contact force/torque
        self.ft_sub = self.create_subscription(
            WrenchStamped,
            '/humanoid_robot/left_foot_contact',
            self.ft_callback,
            10
        )

        self.get_logger().info("Sensor monitor initialized")

    def imu_callback(self, msg):
        """Process IMU data for balance feedback."""
        # Extract angular velocity
        angular_vel = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])

        # Extract linear acceleration
        linear_accel = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z
        ])

        # Estimate pitch and roll from accelerometer
        roll = np.arctan2(linear_accel[1], linear_accel[2])
        pitch = np.arctan2(-linear_accel[0],
                          np.sqrt(linear_accel[1]**2 + linear_accel[2]**2))

        self.get_logger().debug(
            f"IMU - Roll: {np.degrees(roll):.1f}°, Pitch: {np.degrees(pitch):.1f}°"
        )

    def joint_state_callback(self, msg):
        """Monitor joint angles and velocities."""
        for name, position, velocity in zip(msg.name, msg.position, msg.velocity):
            if 'hip' in name or 'knee' in name or 'ankle' in name:
                self.get_logger().debug(
                    f"{name}: pos={position:.3f}, vel={velocity:.3f}"
                )

    def ft_callback(self, msg):
        """Monitor foot contact forces during walking."""
        force = np.array([
            msg.wrench.force.x,
            msg.wrench.force.y,
            msg.wrench.force.z
        ])

        # Calculate total vertical force (stability metric)
        vertical_force = force[2]
        self.get_logger().info(f"Vertical foot force: {vertical_force:.2f} N")

def main(args=None):
    rclpy.init(args=args)
    node = SensorMonitorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Step-by-Step Implementation Guide

1. **Install Gazebo and ROS 2 Integration**: Install Gazebo (version 11 or newer) and gazebo_ros2_control packages. [Citation: https://gazebosim.org/docs/fortress/install] Ensure ROS 2 middleware (DDS) is configured for Gazebo communication.

2. **Create World and Model Files**: Define SDF world files with physics engine, ground plane, and initial objects. Create model SDF/URDF files for the humanoid robot with accurate geometry and inertial properties. [Citation: https://gazebosim.org/docs/fortress/worlds]

3. **Configure Physics Engine Parameters**: Select appropriate physics engine (ODE for humanoid preferred). Set timestep (0.001s), solver iterations (50), and constraint parameters (ERP, CFM). [Citation: https://gazebosim.org/docs/fortress/physics]

4. **Set Up ROS 2 Control**: Create ros2_control configuration YAML files defining joint controllers (position, velocity, effort). Bridge Gazebo simulation with ROS 2 topics for joint commands and state feedback. [Citation: https://control.ros.org/]

5. **Launch Simulation and Monitor**: Use launch files to start Gazebo, load robot models, and spawn controllers. Monitor simulation through ROS 2 topics (joint_states, sensor data) and RViz visualization. [Citation: https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Launch-Files/Understanding-ROS2-Launch-Files.html]

### Summary

- Gazebo provides realistic physics simulation essential for developing and testing humanoid robot algorithms
- Physics engine selection (ODE, Bullet, DART) affects simulation accuracy and computational performance
- World configuration controls gravity, timestep, friction, and environmental properties critical for locomotion
- URDF/SDF model files specify robot geometry, inertia, sensors, and constraints for accurate physics
- ROS 2 integration enables seamless communication between control algorithms and Gazebo simulation
- Sensor simulation with realistic noise models supports algorithm validation before hardware deployment
- Contact detection and friction modeling are essential for bipedal walking stability

### Glossary

- **SDF**: Simulation Description Format, XML-based format for defining Gazebo worlds and models
- **Physics Engine**: Software that simulates rigid body dynamics, collisions, and constraints
- **Timestep**: Discrete time interval for physics simulation updates (typically 1ms for humanoids)
- **ODE**: Open Dynamics Engine, popular physics solver supporting constrained rigid body dynamics
- **Constraint**: Mathematical relationship limiting joint motion (e.g., revolute joint rotation axis)
- **Collision Detection**: Algorithm identifying when objects make contact
- **Contact Modeling**: Simulation of friction, restitution, and normal forces at contact points

### References

- [Gazebo Official Documentation](https://gazebosim.org/)
- [Gazebo Physics Configuration](https://gazebosim.org/docs/fortress/physics)
- [SDF World Files](https://gazebosim.org/docs/fortress/worlds)
- [ROS 2 Control Integration](https://control.ros.org/)
