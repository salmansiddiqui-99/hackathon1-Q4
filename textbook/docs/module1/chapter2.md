## Humanoid Control with ROS 2

### Introduction

Humanoid robots present unique control challenges due to their bipedal nature, high degrees of freedom, and the need for real-time feedback to maintain balance and execute coordinated movements. [Citation: https://docs.ros.org/en/humble/] This chapter explores how ROS 2 enables sophisticated humanoid control through service-based actions, state machines, and coordinated multi-joint movements essential for walking and manipulation tasks.

### Learning Objectives

- Implement ROS 2 Actions for long-running humanoid control tasks
- Design state machines for bipedal locomotion control
- Coordinate multiple joints using ROS 2 message passing
- Implement inverse kinematics (IK) solvers for arm control
- Use joint state feedback for real-time balance control
- Develop controllers for walking gaits and arm manipulation
- Monitor and debug humanoid robot motion using ROS 2 tools

### Core Concepts

#### ROS 2 Actions for Long-Running Tasks

Actions provide a mechanism for long-running tasks that can be canceled or monitored for progress. [Citation: https://docs.ros.org/en/humble/Concepts/Intermediate/About-Actions.html] Unlike services, actions allow continuous feedback during execution. For humanoids, this is ideal for walk commands where you want real-time progress feedback.

#### Joint State Publishing and Feedback

Humanoid robots must continuously publish their joint state (positions, velocities, efforts) for monitoring and feedback control. The `joint_state` publisher broadcasts the state of all joints, enabling visualization in RViz and use by other nodes for planning and control.

#### Inverse Kinematics (IK) for Arm Control

IK solvers compute joint angles from desired end-effector positions. ROS 2 integrates with MoveIt2, a motion planning framework that provides IK services. [Citation: https://moveit.ros.org/] For humanoid arms with 7+ degrees of freedom, IK is essential for reaching objects and performing manipulation tasks.

#### Walking Gait Generation

Bipedal walking requires coordinated timing of swing and stance phases across all leg joints. Walking gait generators compute joint trajectories based on desired walking speed and direction. Humanoid robots typically use parametric gait models that adapt to terrain and speed changes.

### Practical Examples

#### Example 1: Publishing Joint States for a Humanoid

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math

class HumanoidJointPublisher(Node):
    def __init__(self):
        super().__init__('humanoid_joint_publisher')
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)

        # Define all humanoid joint names
        self.joint_names = [
            'torso_pitch', 'torso_roll', 'torso_yaw',
            'l_shoulder_pitch', 'l_shoulder_roll',
            'r_shoulder_pitch', 'r_shoulder_roll',
            'l_hip_pitch', 'l_knee_pitch', 'l_ankle_pitch',
            'r_hip_pitch', 'r_knee_pitch', 'r_ankle_pitch',
        ]

        self.timer = self.create_timer(0.02, self.publish_joint_states)
        self.time_counter = 0

    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [
            math.sin(self.time_counter * 0.05 + i * 0.1)
            for i in range(len(self.joint_names))
        ]
        msg.velocity = [0.1 for _ in self.joint_names]
        msg.effort = [0.5 for _ in self.joint_names]

        self.joint_pub.publish(msg)
        self.time_counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = HumanoidJointPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

This example publishes the complete joint state of a humanoid robot, which can be visualized in RViz.

#### Example 2: Implementing a Walking Controller

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import math

class WalkingController(Node):
    def __init__(self):
        super().__init__('walking_controller')
        self.leg_publisher = self.create_publisher(
            Float32MultiArray,
            'leg_joint_commands',
            10
        )
        self.timer = self.create_timer(0.05, self.walk_step)
        self.step_counter = 0

    def walk_step(self):
        # Compute gait trajectory
        left_leg = self.compute_gait(self.step_counter, 'left')
        right_leg = self.compute_gait(self.step_counter, 'right')

        msg = Float32MultiArray()
        msg.data = left_leg + right_leg
        self.leg_publisher.publish(msg)
        self.step_counter += 1

    def compute_gait(self, step, leg):
        phase = (step % 20) / 20.0 * 2 * math.pi
        return [
            math.sin(phase),    # hip_pitch
            0.0,                # knee_pitch
            0.0,                # ankle_pitch
        ]

def main(args=None):
    rclpy.init(args=args)
    node = WalkingController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

This implements a basic walking gait using sinusoidal joint trajectories.

#### Example 3: Balance Control with IMU Feedback

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from std_msgs.msg import Float32MultiArray

class BalanceController(Node):
    def __init__(self):
        super().__init__('balance_controller')
        self.imu_sub = self.create_subscription(
            Imu,
            'imu',
            self.imu_callback,
            10
        )
        self.command_pub = self.create_publisher(
            Float32MultiArray,
            'balance_corrections',
            10
        )

    def imu_callback(self, msg):
        roll = msg.angular_velocity.x
        pitch = msg.angular_velocity.y

        hip_roll_correction = -roll * 0.5
        ankle_pitch_correction = pitch * 0.3

        cmd_msg = Float32MultiArray()
        cmd_msg.data = [hip_roll_correction, ankle_pitch_correction]
        self.command_pub.publish(cmd_msg)

def main(args=None):
    rclpy.init(args=args)
    node = BalanceController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

This demonstrates closed-loop feedback control for maintaining balance.

### Step-by-Step Implementation Guide

1. **Define Your Humanoid Model**: Create a URDF file describing all joints, links, and dynamics. [Citation: https://docs.ros.org/en/humble/]

2. **Set Up Joint Controllers**: Use ros2_control to manage actuator commands and feedback. [Citation: https://control.ros.org/]

3. **Implement Gait Generation**: Use a parametric gait model to generate walking trajectories.

4. **Build Feedback Loops**: Subscribe to IMU, joint states, and force sensors to implement balance control.

5. **Test in Simulation**: Validate your controller in Gazebo before deploying to hardware.

### Summary

- Actions provide the right abstraction for long-running humanoid tasks like walking
- Joint state publishing enables visualization and feedback control for all joints
- Inverse kinematics solvers enable high-level arm control commands
- Walking gaits require coordination of multiple leg joints with proper timing
- Closed-loop feedback from IMU sensors maintains balance during motion
- ROS 2's real-time capabilities support the low-latency control required for stability

### Glossary

- **Action**: Protocol for long-running tasks with feedback and cancellation support
- **Joint State**: Current position, velocity, and effort of all robot joints
- **Inverse Kinematics**: Computing joint angles from desired end-effector position
- **Gait**: Pattern and timing of leg movements during walking
- **ZMP (Zero Moment Point)**: Metric used to ensure stability in bipedal walking
- **Closed-Loop Control**: Feedback-based control that adjusts commands based on sensor output

### References

- [ROS 2 Actions](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Actions.html)
- [MoveIt2 Motion Planning](https://moveit.ros.org/)
- [ros2_control Framework](https://control.ros.org/)
- [ROS 2 Documentation](https://docs.ros.org/en/humble/)
