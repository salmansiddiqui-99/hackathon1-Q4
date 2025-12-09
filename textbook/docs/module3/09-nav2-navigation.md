## Nav2 and Bipedal Navigation

### Introduction

The Navigation 2 (Nav2) stack provides a flexible, modular architecture for autonomous mobile robot navigation. [Citation: https://navigation.ros.org/] For bipedal humanoid robots, Nav2 enables path planning, obstacle avoidance, and locomotion control integrated with ROS 2. This chapter covers Nav2 components (map servers, planners, controllers), configuring for humanoid-specific constraints, and implementing closed-loop navigation combining planning with balance control.

### Learning Objectives

- Understand Nav2 architecture and key components (costmaps, planners, controllers)
- Create occupancy grid maps from sensor data for navigation
- Implement global path planning with A* and RRT algorithms
- Design bipedal-aware local controllers that maintain balance while navigating
- Integrate IMU feedback for stability during walking
- Handle dynamic obstacles and replanning scenarios
- Tune navigation parameters for humanoid robot characteristics
- Validate navigation in simulation before hardware deployment

### Core Concepts

#### Navigation Stack Architecture

Nav2 consists of: map server (environment representation), global planner (long-term path), local planner (immediate trajectory), and controller (motor commands). [Citation: https://navigation.ros.org/setup_guides/index.html] Costmaps represent traversable space, obstacles, and inflation zones. The planner generates paths avoiding obstacles; the controller executes paths while maintaining humanoid stability.

#### Costmaps and Grid Maps

Costmaps represent environment as 2D grids (occupancy grids) or 3D voxel grids. [Citation: https://navigation.ros.org/concepts/index.html] Grid cells are marked as free, occupied, or unknown. Inflation around obstacles prevents collisions. For humanoids, costmap resolution affects obstacle detection accuracy; typical resolution is 0.05m cells.

#### Global Path Planning Algorithms

A* (A-star) plans optimal paths in known environments. RRT* (Rapidly-exploring Random Trees) handles complex, high-dimensional spaces. Dijkstra provides guaranteed shortest path. [Citation: https://navigation.ros.org/concepts/index.html] Path smoothing (spline fitting) generates smooth, drivable trajectories. For humanoids, smooth paths reduce balance perturbations during following.

#### Local Control and DWA

Dynamic Window Approach (DWA) generates velocity commands (linear, angular) that avoid obstacles while following the global path. [Citation: https://navigation.ros.org/concepts/index.html] DWA samples command space, predicts robot motion, scores trajectories by distance to path and obstacle safety. For humanoids, DWA output must be converted to joint angles and balance corrections.

#### Bipedal Balance Control Integration

Humanoid navigation requires integrating balance control with path following. IMU feedback controls body tilt. Foot placement must anticipate slope and terrain. [Citation: https://ieeexplore.ieee.org/document/7402995] ZMP (Zero Moment Point) ensures stability: ZMP must remain inside support polygon (convex hull of foot contact). Advanced controllers predict humanoid stability while executing Nav2 trajectories.

### Practical Examples

#### Example 1: Creating and Loading an Occupancy Map

```python
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Pose
import numpy as np
from pathlib import Path

class MapPublisher(Node):
    """Publish occupancy grid map for navigation."""

    def __init__(self):
        super().__init__('map_publisher')

        # Create map publisher
        self.map_pub = self.create_publisher(OccupancyGrid, '/map', 1, is_transient_local=True)

        # Timer to publish once
        self.timer = self.create_timer(1.0, self.publish_map)
        self.published = False

    def publish_map(self):
        """Create and publish a synthetic occupancy map."""
        if self.published:
            return

        # Map parameters
        width, height = 100, 100  # 100x100 cells
        resolution = 0.05  # 0.05m per cell
        origin_x, origin_y = -2.5, -2.5  # Map origin in meters

        # Create empty map (0 = free, 100 = occupied, -1 = unknown)
        data = np.zeros((height, width), dtype=np.int8)

        # Add obstacles (walls, boxes)
        # Vertical wall at x=1m (20 cells)
        data[:, 20:22] = 100

        # Horizontal wall at y=1m (40 cells)
        data[40:42, :] = 100

        # Rectangular obstacle
        data[60:65, 30:35] = 100

        # Add small obstacles (chairs, boxes)
        data[25:30, 15:20] = 100
        data[70:75, 70:75] = 100

        # Flatten for OccupancyGrid message
        data_flat = data.flatten().tolist()

        # Create OccupancyGrid message
        msg = OccupancyGrid()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()

        # Map info
        msg.info.resolution = resolution
        msg.info.width = width
        msg.info.height = height
        msg.info.origin = Pose()
        msg.info.origin.position.x = origin_x
        msg.info.origin.position.y = origin_y
        msg.info.origin.position.z = 0.0
        msg.info.origin.orientation.w = 1.0

        # Map data
        msg.data = data_flat

        # Publish
        self.map_pub.publish(msg)
        self.get_logger().info(f"Published {width}x{height} occupancy grid")

        self.published = True

def main(args=None):
    rclpy.init(args=args)
    node = MapPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

#### Example 2: Configuring Nav2 for Humanoid Footprint

```yaml
# nav2_params.yaml - Nav2 parameters for humanoid robot

amcl:
  ros__parameters:
    use_sim_time: true
    alpha1: 0.2
    alpha2: 0.2
    alpha3: 0.2
    alpha4: 0.2
    alpha5: 0.2
    base_frame_id: "base_link"
    beam_search_increment: 0.05
    global_frame_id: "map"
    lambda_short: 0.1
    laser_likelihood_max_dist: 2.0
    laser_max_range: 100.0
    laser_min_range: -1.0
    max_beams: 60
    max_particles: 2000
    min_particles: 500
    pf_err: 0.05
    pf_z: 0.99
    recovery_alpha_fast: 0.0
    recovery_alpha_slow: 0.0
    resample_interval: 1
    robot_model_type: "differential"
    save_pose_rate: 0.5
    sigma_hit: 0.2
    sigma_short: 0.05
    tf_broadcast: true
    transform_tolerance: 1.0
    update_min_a: 0.2
    update_min_d: 0.25
    z_good: 0.9
    z_hit: 0.5
    z_max: 0.05
    z_rand: 0.05
    z_short: 0.1

bt_navigator:
  ros__parameters:
    use_sim_time: true
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odometry/filtered
    bt_loop_duration: 10
    default_server_timeout: 20
    enable_groot_monitoring: true
    groot_zmq_publisher_port: 1666
    groot_zmq_server_port: 1667
    default_nav_to_pose_bt_xml: "navigate_to_pose_w_replanning_and_recovery.xml"

controller_server:
  ros__parameters:
    use_sim_time: true
    controller_frequency: 10.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    failure_tolerance: 0.3
    progress_checker_plugin: "progress_checker"
    goal_checker_plugins: ["general_goal_checker"]
    controller_plugins: ["FollowPath"]

    progress_checker:
      plugin: "nav2_core::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0

    general_goal_checker:
      stateful: True
      plugin: "nav2_core::SimpleGoalChecker"
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25
      stateful_success_count: 3

    FollowPath:
      plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
      desired_linear_vel: 0.5
      lookahead_dist: 0.6
      min_lookahead_dist: 0.3
      max_lookahead_dist: 0.9
      lookahead_time: 1.5
      rotate_to_heading_angular_vel: 1.8
      transform_tolerance: 0.1
      use_velocity_scaled_lookahead_dist: false
      min_ampl_scaling: 0.1
      max_allow_reversing: true
      use_collision_detection: true
      collision_check_size: 0.025
      cost_scaling_dist: 0.6
      cost_scaling_gain: 1.0
      inflation_radius: 0.55

planner_server:
  ros__parameters:
    use_sim_time: true
    expected_planner_frequency: 20.0
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner::NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true

smoother_server:
  ros__parameters:
    use_sim_time: true
    smoother_plugins: ["simple_smoother"]
    simple_smoother:
      plugin: "nav2_smoother::SimpleSmoother"
      tolerance: 1e-10
      max_its: 1000
      do_refinement: true

recovery_server:
  ros__parameters:
    use_sim_time: true
    recovery_plugins: ["spin", "backup", "wait"]
    spin:
      plugin: "nav2_behaviors::Spin"
      simulate_ahead_time: 2.0
      max_rotations: 1
      max_effort: 100.0
      simulate_ahead_time: 2.0
    backup:
      plugin: "nav2_behaviors::BackUp"
      simulate_ahead_time: 2.0
      required_movement_radius: 0.5
      movement_time_allowance: 10.0
      min_linear_vel: -0.5
      max_linear_vel: -0.35
      min_angular_vel: 0.0
      max_angular_vel: 0.4
      simulate_ahead_time: 2.0
    wait:
      plugin: "nav2_behaviors::Wait"
      wait_duration: 2000
```

#### Example 3: Bipedal Balance Control During Navigation

```python
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray
import numpy as np
import math

class BipedalNavigationController(Node):
    """Control humanoid robot navigation with balance feedback."""

    def __init__(self):
        super().__init__('bipedal_nav_controller')

        # Subscribe to planned path
        self.path_sub = self.create_subscription(
            Path,
            '/plan',
            self.path_callback,
            10
        )

        # Subscribe to IMU for balance feedback
        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        # Subscribe to velocity commands from Nav2
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel_nav',  # From Nav2 controller
            self.cmd_vel_callback,
            10
        )

        # Publish joint commands (legs)
        self.left_leg_pub = self.create_publisher(
            Float32MultiArray,
            '/humanoid/left_leg_controller/commands',
            10
        )

        self.right_leg_pub = self.create_publisher(
            Float32MultiArray,
            '/humanoid/right_leg_controller/commands',
            10
        )

        # Control state
        self.current_path = None
        self.current_cmd_vel = Twist()
        self.imu_data = None
        self.time = 0.0

        # Timer for control loop
        self.timer = self.create_timer(0.02, self.control_loop)

        self.get_logger().info("Bipedal navigation controller started")

    def path_callback(self, msg):
        """Receive planned path from Nav2."""
        self.current_path = msg

    def cmd_vel_callback(self, msg):
        """Receive velocity commands from Nav2."""
        self.current_cmd_vel = msg

    def imu_callback(self, msg):
        """Receive IMU data for balance feedback."""
        self.imu_data = msg

    def control_loop(self):
        """Main control loop: convert velocities to joint angles with balance."""
        if self.current_cmd_vel is None or self.imu_data is None:
            return

        # Extract velocity commands
        linear_x = self.current_cmd_vel.linear.x
        angular_z = self.current_cmd_vel.angular.z

        # Extract IMU data for balance
        pitch_rate = self.imu_data.angular_velocity.y
        roll = self.imu_data.linear_acceleration.x

        # Map velocities to gait parameters
        walking_speed = linear_x  # m/s
        turning_rate = angular_z  # rad/s

        # Generate gait with balance correction
        left_angles = self.generate_gait_with_balance(
            phase=self.time * 2 * math.pi,
            leg='left',
            walking_speed=walking_speed,
            turning_rate=turning_rate,
            pitch_rate=pitch_rate,
            roll=roll
        )

        right_angles = self.generate_gait_with_balance(
            phase=self.time * 2 * math.pi + math.pi,  # Opposite phase
            leg='right',
            walking_speed=walking_speed,
            turning_rate=turning_rate,
            pitch_rate=pitch_rate,
            roll=roll
        )

        # Publish joint commands
        left_msg = Float32MultiArray()
        left_msg.data = left_angles
        self.left_leg_pub.publish(left_msg)

        right_msg = Float32MultiArray()
        right_msg.data = right_angles
        self.right_leg_pub.publish(right_msg)

        self.time += 0.02

    def generate_gait_with_balance(self, phase, leg, walking_speed, turning_rate, pitch_rate, roll):
        """Generate walking gait with balance corrections."""
        # Base gait (sinusoidal)
        hip_angle = walking_speed * math.sin(phase)
        knee_angle = -walking_speed * math.sin(phase + math.pi/4)
        ankle_angle = walking_speed * math.sin(phase)

        # Turning correction (yaw)
        yaw_correction = turning_rate * 0.1

        # Balance corrections from IMU
        # Roll correction for lateral balance
        roll_correction = -roll * 0.5
        ankle_angle += roll_correction

        # Pitch correction for forward/backward stability
        pitch_correction = pitch_rate * 0.1
        hip_angle += pitch_correction

        # Apply speed scaling
        speed_scale = max(0.5, min(1.5, abs(walking_speed)))

        return [
            hip_angle * speed_scale,
            knee_angle * speed_scale,
            ankle_angle * speed_scale
        ]

def main(args=None):
    rclpy.init(args=args)
    node = BipedalNavigationController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

#### Example 4: Navigation Goal Client

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Quaternion
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
import math

class NavigationClient(Node):
    """Client for sending navigation goals to Nav2."""

    def __init__(self):
        super().__init__('nav_client')

        self.nav_to_pose_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

        self.get_logger().info("Navigation client ready")

    def send_goal(self, x, y, theta=0.0):
        """Send navigation goal (x, y position and orientation)."""
        # Wait for action server
        self.nav_to_pose_client.wait_for_server()

        # Create goal
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

        # Position
        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.position.z = 0.0

        # Orientation (quaternion from yaw angle)
        quat = self.yaw_to_quaternion(theta)
        goal_msg.pose.pose.orientation = quat

        # Send goal asynchronously
        self.send_goal_future = self.nav_to_pose_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        self.send_goal_future.add_done_callback(self.goal_response_callback)
        self.get_logger().info(f"Goal sent: ({x}, {y}, {math.degrees(theta):.1f}°)")

    def yaw_to_quaternion(self, yaw):
        """Convert yaw angle to quaternion."""
        half_yaw = yaw / 2.0
        qx = 0.0
        qy = 0.0
        qz = math.sin(half_yaw)
        qw = math.cos(half_yaw)
        return Quaternion(x=qx, y=qy, z=qz, w=qw)

    def goal_response_callback(self, future):
        """Handle goal response."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info("Goal rejected")
            return

        self.get_logger().info("Goal accepted")
        self.result_future = goal_handle.get_result_async()
        self.result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, msg):
        """Process feedback (current position, remaining distance)."""
        feedback = msg.feedback
        self.get_logger().debug(f"Progress: {feedback.distance_remaining:.2f}m remaining")

    def result_callback(self, future):
        """Handle navigation result."""
        result = future.result()
        self.get_logger().info("Navigation goal reached!")

def main(args=None):
    rclpy.init(args=args)
    client = NavigationClient()

    # Send goal: navigate to (3.0, 2.0) with yaw 45°
    client.send_goal(x=3.0, y=2.0, theta=math.pi/4)

    rclpy.spin(client)
    client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Step-by-Step Implementation Guide

1. **Install Nav2**: Install nav2 packages via apt or build from source. Verify installation: `ros2 pkg list | grep nav2`. [Citation: https://navigation.ros.org/setup_guides/index.html]

2. **Configure Maps**: Create occupancy grid map from LiDAR/sensor data or pre-built map file. Load map via map_server. Configure map properties (resolution, origin). [Citation: https://navigation.ros.org/setup_guides/index.html]

3. **Tune Costmaps**: Configure costmap parameters: static layer (from map), obstacle layer (from sensors), inflation radius. Adjust inflation to prevent humanoid collisions. [Citation: https://navigation.ros.org/concepts/index.html]

4. **Configure Local Controller**: Select controller (DWA, TEB, RegulatedPurePursuit). Tune velocity limits to match humanoid walking speed. Configure lookahead distance and heading tolerance. [Citation: https://navigation.ros.org/setup_guides/index.html]

5. **Add Balance Control**: Implement balance feedback layer on top of Nav2 controller. Integrate IMU data for stability. Test navigation in simulation first. [Citation: https://ieeexplore.ieee.org/document/7402995]

### Summary

- Nav2 provides modular, production-ready navigation architecture for autonomous robots
- Costmaps represent environment with inflation zones for collision avoidance
- Global planners (A*, RRT) find paths; local controllers (DWA) execute paths with obstacle avoidance
- Bipedal humanoid robots require additional balance control integrated with navigation
- IMU feedback enables correcting balance perturbations during navigation
- Parameter tuning is critical for humanoid-specific constraints (speed, step height, stability)
- Navigation validated in simulation transfers well to hardware with minimal tuning
- Replanning and recovery behaviors handle dynamic environments and planning failures

### Glossary

- **Costmap**: 2D grid representation of navigable space with obstacle costs
- **Global Planner**: Algorithm (A*, RRT) finding path from start to goal
- **Local Planner**: Real-time controller generating velocities following global path
- **DWA (Dynamic Window Approach)**: Samples velocity space and scores trajectories
- **Inflation**: Buffer zone around obstacles to prevent collisions
- **ZMP (Zero Moment Point)**: Balance metric: point where ground reaction moment is zero
- **Footprint**: Collision boundary of robot base (critical for humanoid feet)

### References

- [Navigation 2 Official](https://navigation.ros.org/)
- [Nav2 Setup Guide](https://navigation.ros.org/setup_guides/index.html)
- [Nav2 Concepts](https://navigation.ros.org/concepts/index.html)
- [Bipedal Walking Control](https://ieeexplore.ieee.org/document/7402995)
