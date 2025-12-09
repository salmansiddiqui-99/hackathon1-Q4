## ROS 2 Basics: Architecture and Communication

### Introduction

ROS 2 (Robot Operating System 2) is a flexible, distributed middleware framework designed for building robot applications. As the successor to ROS 1, ROS 2 introduces improved security, real-time support, and a more modular architecture that is essential for developing humanoid robots. [Citation: https://docs.ros.org/en/humble/] This chapter covers the fundamental concepts of ROS 2, including its publish-subscribe communication model, workspace organization, and how nodes interact within the robotic ecosystem.

### Learning Objectives

- Understand ROS 2's core architecture and design philosophy
- Set up a ROS 2 development environment and create your first workspace
- Create and run ROS 2 nodes using Python and C++
- Implement pub/sub communication patterns for inter-process communication
- Debug ROS 2 applications using built-in tools like `ros2 topic`, `ros2 node`, and RViz
- Understand DDS (Data Distribution Service) as the middleware for ROS 2
- Apply ROS 2 best practices for scalable, maintainable robotics code

### Core Concepts

#### Pub/Sub Communication Model

ROS 2 uses a publish-subscribe (pub/sub) pattern for asynchronous communication between processes. [Citation: https://docs.ros.org/en/humble/Concepts/Intermediate/About-Topic-ROS-2.html] Publishers send messages to named topics, while subscribers listen on topics of interest. This decoupling allows components to evolve independently and enables flexible system architectures. For humanoid robots, this pattern is critical because different subsystems (perception, planning, control) can operate asynchronously without direct dependencies.

#### Nodes and the Computation Graph

A node is a process that performs computation in ROS 2. [Citation: https://docs.ros.org/en/humble/Concepts/Basic/About-Nodes.html] Nodes communicate via topics (one-to-many), services (request-response), or actions (long-running tasks). The ROS 2 Computation Graph visualizes all nodes and connections, providing a complete picture of your system. In a humanoid robot system, you might have nodes for joint control, sensor processing, motion planning, and behavior management.

#### DDS as the Communication Middleware

ROS 2 uses DDS (Data Distribution Service) as its underlying communication middleware instead of ROS 1's custom protocol. [Citation: https://design.ros2.org/articles/dds_middleware_interface.html] DDS provides real-time guarantees, Quality of Service (QoS) settings, and better security out of the box. This is crucial for humanoid robots where real-time responsiveness is essential for stable locomotion.

#### Quality of Service (QoS)

QoS settings in ROS 2 allow fine-grained control over message delivery and timing. [Citation: https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html] You can configure reliability (best-effort vs. reliable), durability, history depth, and deadlines. For humanoid robot control, you might use reliable communication for critical commands but best-effort for continuous sensor streams.

### Practical Examples

#### Example 1: Creating a Simple Publisher Node

This example demonstrates how to create a ROS 2 node that publishes joint angle commands:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import math
import time

class JointPublisher(Node):
    def __init__(self):
        super().__init__('joint_publisher')
        # Create a publisher for joint angles
        self.publisher_ = self.create_publisher(
            Float32MultiArray,
            'joint_commands',
            10  # Queue size
        )
        # Create a timer to publish every 100ms
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.counter = 0

    def timer_callback(self):
        # Create message with joint angles
        msg = Float32MultiArray()
        # Simulate sinusoidal motion for 6 joints
        msg.data = [
            float(math.sin(self.counter * 0.01 + i))
            for i in range(6)
        ]
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing joint angles: {msg.data}')
        self.counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = JointPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

This example shows the basic pattern: create a Node subclass, use `create_publisher()` to define a topic, and publish messages in a callback. [Citation: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html]

#### Example 2: Creating a Subscriber Node

This complementary subscriber listens to the published joint commands:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

class JointSubscriber(Node):
    def __init__(self):
        super().__init__('joint_subscriber')
        # Create a subscription to joint_commands
        self.subscription = self.create_subscription(
            Float32MultiArray,
            'joint_commands',
            self.listener_callback,
            10  # QoS history depth
        )
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        # Process incoming joint commands
        self.get_logger().info(f'Received joint angles: {msg.data}')
        # Here you would apply these commands to the actual robot hardware

def main(args=None):
    rclpy.init(args=args)
    node = JointSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Notice the loose coupling: the publisher doesn't need to know about the subscriber, and vice versa. [Citation: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html]

#### Example 3: Creating a Service Node

Services provide synchronous request-response communication, useful for one-shot actions:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.srv import Pose

class PoseService(Node):
    def __init__(self):
        super().__init__('pose_service')
        # Create a service
        self.srv = self.create_service(
            Pose,
            'get_end_effector_pose',
            self.pose_callback
        )
        self.current_pose = [0.5, 0.0, 0.8, 0.0, 0.0, 0.0, 1.0]  # x, y, z, qx, qy, qz, qw

    def pose_callback(self, request, response):
        # Calculate or retrieve end-effector pose
        response.position.x = self.current_pose[0]
        response.position.y = self.current_pose[1]
        response.position.z = self.current_pose[2]
        response.orientation.x = self.current_pose[3]
        response.orientation.y = self.current_pose[4]
        response.orientation.z = self.current_pose[5]
        response.orientation.w = self.current_pose[6]

        self.get_logger().info('Returning end-effector pose')
        return response

def main(args=None):
    rclpy.init(args=args)
    node = PoseService()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Services are ideal for queries that require an immediate response, such as asking for the current end-effector position. [Citation: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Service-And-Client-Cpp.html]

### Step-by-Step Implementation Guide

1. **Install ROS 2**: Visit the official ROS 2 documentation and install the Humble distribution on Ubuntu 22.04 LTS. [Citation: https://docs.ros.org/en/humble/Installation.html]

2. **Set Up Your Workspace**: Create a ROS 2 workspace directory and initialize it with the standard structure:
   ```bash
   mkdir -p ~/robot_ws/src
   cd ~/robot_ws
   colcon build
   source install/setup.bash
   ```

3. **Create a Package**: Generate a new ROS 2 package for your nodes:
   ```bash
   cd ~/robot_ws/src
   ros2 pkg create --build-type ament_python my_robot_package
   cd my_robot_package
   ```

4. **Write Your First Node**: Create a Python file in `my_robot_package/my_robot_package/` with the publisher or subscriber code from the examples above.

5. **Build and Run**: Compile your package and execute your nodes:
   ```bash
   cd ~/robot_ws
   colcon build --packages-select my_robot_package
   source install/setup.bash
   ros2 run my_robot_package joint_publisher
   ```

### Summary

- ROS 2's pub/sub model provides loose coupling and scalability for complex robotic systems
- Nodes are the fundamental units of computation, communicating via topics, services, and actions
- DDS middleware offers real-time capabilities and Quality of Service controls essential for humanoid robots
- Python and C++ APIs make ROS 2 accessible to developers with various programming backgrounds
- Tools like `ros2 topic list`, `ros2 node info`, and RViz help you understand and debug the computation graph
- Proper workspace organization and package structure support team collaboration and maintainability

### Glossary

- **Node**: A process in ROS 2 that performs computation and communicates with other nodes
- **Topic**: A named channel for one-way, asynchronous message passing (pub/sub pattern)
- **Service**: A named request-response channel for synchronous communication between nodes
- **Publisher**: A node component that sends messages to a topic
- **Subscriber**: A node component that receives messages from a topic
- **DDS**: Data Distribution Service, the middleware providing pub/sub communication in ROS 2
- **QoS**: Quality of Service settings controlling message delivery reliability, timing, and ordering

### References

- [ROS 2 Official Documentation](https://docs.ros.org/en/humble/)
- [ROS 2 Concepts](https://docs.ros.org/en/humble/Concepts.html)
- [ROS 2 Python Client Library](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/index.html)
- [DDS Middleware Interface Design](https://design.ros2.org/articles/dds_middleware_interface.html)
