## URDF and Robot Descriptions

### Introduction

The Unified Robot Description Format (URDF) is an XML-based standard for describing robot kinematics and dynamics in ROS. [Citation: https://docs.ros.org/en/humble/Concepts/Intermediate/URDF/URDF-Introduction.html] URDF defines the structure of a robot through links (rigid bodies), joints (connections), and inertial properties, enabling accurate simulation and control of humanoid robots. This chapter explores how to construct URDF models for complex humanoid systems, calculate forward kinematics, and integrate dynamic properties essential for realistic physics simulation.

### Learning Objectives

- Define robot structure using URDF with links, joints, and kinematic chains
- Calculate forward kinematics for humanoid manipulators and locomotion systems
- Define inertial properties (mass, center of mass, moment of inertia) for realistic physics
- Create collision and visual models for simulation and rendering
- Implement joint limits and transmission characteristics for actuators
- Parse and load URDF models programmatically in ROS 2 applications
- Visualize URDF models in RViz and debug kinematic chains
- Validate URDF syntax and resolve common structural issues

### Core Concepts

#### URDF Structure and Hierarchy

URDF represents a robot as a tree of links connected by joints. [Citation: https://wiki.ros.org/urdf/XML] Each link represents a rigid body with geometry, inertia, and visual properties. Joints define degrees of freedom and transformations between links. For humanoid robots, the URDF hierarchy typically starts with a base link (torso) and branches into kinematic chains for arms, legs, and head. The hierarchical structure must form a single connected tree without cycles.

#### Links and Inertial Properties

A link in URDF contains three sub-elements: visual (for rendering), collision (for physics), and inertial (mass and moment of inertia). [Citation: https://wiki.ros.org/urdf/XML/link] Accurate inertial properties are critical for humanoid robot control, as they affect dynamic stability during locomotion. The moment of inertia tensor describes how mass is distributed around the center of mass. For humanoid robots, typical mass distributions include: torso (40%), legs (35%), arms (20%), head (5%).

#### Joint Types and Kinematic Constraints

URDF supports six joint types: revolute (bounded rotation), continuous (unbounded rotation), prismatic (linear translation), fixed (no movement), floating (6-DOF), and planar. [Citation: https://wiki.ros.org/urdf/XML/joint] Humanoid robots primarily use revolute joints for articulation. Each joint has origin (transform), axis (rotation direction), and limits (min/max position, velocity, effort). Joint limits protect actuators and ensure physically valid configurations.

#### Forward and Inverse Kinematics

Forward kinematics computes end-effector position and orientation from joint angles using Denavit-Hartenberg parameters or transformation matrices. [Citation: https://docs.ros.org/en/humble/Concepts/Intermediate/URDF/] Inverse kinematics solves the reverse problem: finding joint angles that achieve a desired end-effector pose. For humanoid arms with 7 degrees of freedom, inverse kinematics is essential for reaching and manipulation tasks. URDF provides the kinematic structure; solvers like IKFast compute solutions efficiently.

### Practical Examples

#### Example 1: Creating a Simple Humanoid URDF

This example builds a minimal 3-joint arm attached to a torso:

```xml
<?xml version="1.0"?>
<robot name="humanoid_basic">
  <!-- Base link (torso) -->
  <link name="torso">
    <inertial>
      <mass value="10.0"/>
      <origin xyz="0 0 0.3"/>
      <inertia ixx="0.5" ixy="0.0" ixz="0.0" iyy="0.5" iyz="0.0" izz="0.3"/>
    </inertial>
    <visual>
      <geometry>
        <box size="0.3 0.2 0.6"/>
      </geometry>
      <material name="dark_gray">
        <color rgba="0.2 0.2 0.2 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.6"/>
      </geometry>
    </collision>
  </link>

  <!-- Left shoulder joint -->
  <joint name="l_shoulder_pitch" type="revolute">
    <parent link="torso"/>
    <child link="l_upper_arm"/>
    <origin xyz="0.15 0.15 0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.5708" upper="1.5708" effort="20" velocity="1.0"/>
    <dynamics damping="0.1" friction="0.1"/>
  </joint>

  <!-- Left upper arm -->
  <link name="l_upper_arm">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 -0.15"/>
      <inertia ixx="0.02" ixy="0.0" ixz="0.0" iyy="0.02" iyz="0.0" izz="0.001"/>
    </inertial>
    <visual>
      <geometry>
        <cylinder length="0.3" radius="0.04"/>
      </geometry>
      <origin xyz="0 0 -0.15"/>
      <material name="light_gray">
        <color rgba="0.5 0.5 0.5 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.3" radius="0.04"/>
      </geometry>
      <origin xyz="0 0 -0.15"/>
    </collision>
  </link>

  <!-- Left elbow joint -->
  <joint name="l_elbow_pitch" type="revolute">
    <parent link="l_upper_arm"/>
    <child link="l_forearm"/>
    <origin xyz="0 0 -0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-2.0944" upper="0" effort="15" velocity="1.0"/>
    <dynamics damping="0.05" friction="0.05"/>
  </joint>

  <!-- Left forearm -->
  <link name="l_forearm">
    <inertial>
      <mass value="1.5"/>
      <origin xyz="0 0 -0.13"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.0005"/>
    </inertial>
    <visual>
      <geometry>
        <cylinder length="0.26" radius="0.035"/>
      </geometry>
      <origin xyz="0 0 -0.13"/>
      <material name="light_gray"/>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.26" radius="0.035"/>
      </geometry>
      <origin xyz="0 0 -0.13"/>
    </collision>
  </link>

  <!-- Left wrist joint -->
  <joint name="l_wrist_pitch" type="revolute">
    <parent link="l_forearm"/>
    <child link="l_hand"/>
    <origin xyz="0 0 -0.26" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.5708" upper="1.5708" effort="5" velocity="1.0"/>
    <dynamics damping="0.01" friction="0.01"/>
  </joint>

  <!-- Left hand (end effector) -->
  <link name="l_hand">
    <inertial>
      <mass value="0.5"/>
      <origin xyz="0 0 -0.05"/>
      <inertia ixx="0.0002" ixy="0.0" ixz="0.0" iyy="0.0002" iyz="0.0" izz="0.0001"/>
    </inertial>
    <visual>
      <geometry>
        <sphere radius="0.05"/>
      </geometry>
      <origin xyz="0 0 -0.05"/>
      <material name="light_gray"/>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.05"/>
      </geometry>
      <origin xyz="0 0 -0.05"/>
    </collision>
  </link>
</robot>
```

This URDF defines a simple kinematic chain: torso → upper_arm → forearm → hand. Each joint has rotation limits and damping characteristics.

#### Example 2: Computing Forward Kinematics in Python

```python
import rclpy
from rclpy.node import Node
import numpy as np
from tf_transformations import euler_from_matrix, quaternion_from_matrix
from urdf_parser_py.urdf import URDF

class ForwardKinematicsNode(Node):
    def __init__(self):
        super().__init__('forward_kinematics')

        # Load URDF from parameter or file
        urdf_param = self.get_parameter_or('robot_description', 'humanoid')
        if isinstance(urdf_param, str):
            self.robot = URDF.from_file(urdf_param)
        else:
            self.robot = URDF.from_parameter_server()

        self.get_logger().info(f"Loaded robot: {self.robot.name}")

    def compute_forward_kinematics(self, joint_angles: dict) -> np.ndarray:
        """
        Compute end-effector pose from joint angles.
        Args:
            joint_angles: Dict mapping joint names to angles in radians
        Returns:
            4x4 transformation matrix
        """
        # Get kinematic chain from root to end-effector
        chain = self.get_kinematic_chain('torso', 'l_hand')

        # Identity transformation
        T = np.eye(4)

        for joint_name in chain:
            joint = self.robot.joint_map[joint_name]
            if joint.type == 'fixed':
                # Apply fixed transform
                T = T @ self.transform_from_joint(joint, 0.0)
            elif joint.type == 'revolute':
                # Apply rotational joint with given angle
                angle = joint_angles.get(joint_name, 0.0)
                T = T @ self.transform_from_joint(joint, angle)
            elif joint.type == 'prismatic':
                # Apply prismatic joint with given displacement
                displacement = joint_angles.get(joint_name, 0.0)
                T = T @ self.transform_from_joint(joint, displacement)

        return T

    def transform_from_joint(self, joint, value: float) -> np.ndarray:
        """Create transformation matrix from joint origin and rotation/translation."""
        # Extract origin (translation)
        origin = np.array([joint.origin.xyz[0], joint.origin.xyz[1], joint.origin.xyz[2]])

        # Extract rotation from RPY
        rpy = joint.origin.rpy

        # Create base transformation
        T = np.eye(4)
        T[:3, 3] = origin

        # Apply RPY rotations
        from tf_transformations import euler_matrix
        R = euler_matrix(rpy[0], rpy[1], rpy[2])[:3, :3]

        # Apply joint rotation/translation
        axis = np.array(joint.axis)
        if joint.type == 'revolute':
            from tf_transformations import rotation_matrix
            rot = rotation_matrix(value, axis)
            R = R @ rot[:3, :3]
        elif joint.type == 'prismatic':
            origin += axis * value

        T[:3, :3] = R
        T[:3, 3] = origin

        return T

    def get_kinematic_chain(self, root: str, leaf: str) -> list:
        """Find path from root link to leaf link in URDF tree."""
        # BFS to find path
        from collections import deque
        queue = deque([(root, [root])])
        visited = {root}

        while queue:
            current, path = queue.popleft()
            if current == leaf:
                return path

            for joint in self.robot.joints:
                if joint.parent.link == current and joint.child.link not in visited:
                    visited.add(joint.child.link)
                    queue.append((joint.child.link, path + [joint.name]))

        return []

def main(args=None):
    rclpy.init(args=args)
    node = ForwardKinematicsNode()

    # Example: compute FK for given joint angles
    joint_angles = {
        'l_shoulder_pitch': 0.5,
        'l_elbow_pitch': -1.0,
        'l_wrist_pitch': 0.3
    }

    T = node.compute_forward_kinematics(joint_angles)
    node.get_logger().info(f"End-effector transformation:\n{T}")

    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

This example loads a URDF model, computes forward kinematics by multiplying transformation matrices along the kinematic chain.

#### Example 3: Validating URDF and Checking Joint Limits

```python
import rclpy
from rclpy.node import Node
from urdf_parser_py.urdf import URDF
import numpy as np

class URDFValidationNode(Node):
    def __init__(self):
        super().__init__('urdf_validator')
        self.robot = URDF.from_parameter_server()

    def validate_urdf(self) -> dict:
        """Comprehensive URDF validation."""
        issues = {
            'errors': [],
            'warnings': [],
            'info': []
        }

        # Check tree structure
        if not self.is_tree_connected():
            issues['errors'].append("URDF has disconnected components")

        # Validate all links
        for link in self.robot.links:
            if not link.inertial:
                issues['warnings'].append(f"Link '{link.name}' has no inertial properties")

            if link.inertial:
                mass = link.inertial.mass
                if mass < 0.01:
                    issues['warnings'].append(f"Link '{link.name}' has unrealistic mass: {mass}")

        # Validate all joints
        for joint in self.robot.joints:
            # Check joint limits
            if hasattr(joint, 'limit') and joint.limit:
                if joint.limit.effort <= 0:
                    issues['errors'].append(f"Joint '{joint.name}' has invalid effort limit")
                if joint.limit.velocity <= 0:
                    issues['errors'].append(f"Joint '{joint.name}' has invalid velocity limit")

                # Check lower < upper for revolute/prismatic
                if joint.type in ['revolute', 'prismatic']:
                    if joint.limit.lower >= joint.limit.upper:
                        issues['errors'].append(
                            f"Joint '{joint.name}': lower limit >= upper limit"
                        )

            # Check parent-child validity
            parent_exists = any(l.name == joint.parent.link for l in self.robot.links)
            child_exists = any(l.name == joint.child.link for l in self.robot.links)

            if not parent_exists:
                issues['errors'].append(f"Joint '{joint.name}' references non-existent parent link")
            if not child_exists:
                issues['errors'].append(f"Joint '{joint.name}' references non-existent child link")

        return issues

    def is_tree_connected(self) -> bool:
        """Check if URDF forms a connected tree."""
        if not self.robot.links:
            return False

        visited = set()
        start_link = self.robot.links[0].name
        self.dfs(start_link, visited)

        return len(visited) == len(self.robot.links)

    def dfs(self, link_name: str, visited: set):
        """Depth-first search to traverse URDF tree."""
        if link_name in visited:
            return
        visited.add(link_name)

        for joint in self.robot.joints:
            if joint.parent.link == link_name:
                self.dfs(joint.child.link, visited)
            elif joint.child.link == link_name:
                self.dfs(joint.parent.link, visited)

    def check_joint_limits(self, joint_angles: dict) -> dict:
        """Verify if joint angles are within limits."""
        violations = {}

        for joint_name, angle in joint_angles.items():
            joint = self.robot.joint_map.get(joint_name)
            if not joint or joint.type == 'fixed':
                continue

            if hasattr(joint, 'limit') and joint.limit:
                if angle < joint.limit.lower or angle > joint.limit.upper:
                    violations[joint_name] = {
                        'value': angle,
                        'lower': joint.limit.lower,
                        'upper': joint.limit.upper
                    }

        return violations

def main(args=None):
    rclpy.init(args=args)
    node = URDFValidationNode()

    # Validate URDF
    issues = node.validate_urdf()
    node.get_logger().info(f"Validation errors: {len(issues['errors'])}")
    node.get_logger().info(f"Validation warnings: {len(issues['warnings'])}")

    for error in issues['errors']:
        node.get_logger().error(error)

    # Check joint limits
    test_angles = {
        'l_shoulder_pitch': 0.5,
        'l_elbow_pitch': -1.0,
        'l_wrist_pitch': 0.3
    }

    violations = node.check_joint_limits(test_angles)
    if violations:
        node.get_logger().warn(f"Joint limit violations: {violations}")

    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

This validates URDF structure, checks joint limits, and detects common configuration errors.

### Step-by-Step Implementation Guide

1. **Design the Kinematic Structure**: Sketch the humanoid robot's skeleton with links and joints. Determine the hierarchy: typically torso as root, with kinematic chains for legs, arms, and head. [Citation: https://wiki.ros.org/urdf/Tutorials/Building%20a%20Visual%20Robot%20Model%20with%20URDF]

2. **Create URDF XML File**: Write the robot description with `<link>` and `<joint>` elements. Start with visual geometry (boxes, cylinders, spheres), then add collision geometry, and finally inertial properties. [Citation: https://docs.ros.org/en/humble/Concepts/Intermediate/URDF/]

3. **Define Inertial Properties**: Calculate or measure mass and moment of inertia for each link. Use CAD tools or simplified formulas (e.g., for a cylinder: I = 1/12 * m * (3*r² + h²)). [Citation: https://wiki.ros.org/urdf/XML/link]

4. **Set Joint Limits and Dynamics**: Specify min/max position limits based on physical constraints. Set velocity and effort limits according to actuator specifications. Add damping and friction coefficients for realistic simulation. [Citation: https://wiki.ros.org/urdf/XML/joint]

5. **Validate and Visualize**: Use `check_urdf` tool to verify syntax, then load in RViz to visualize the structure. Fix any visual artifacts (off-axis origins, incorrect orientations). [Citation: https://wiki.ros.org/urdf/Tutorials/Checking%20a%20URDF]

### Summary

- URDF is the standard ROS format for describing robot kinematics and dynamics using XML
- Links represent rigid bodies with geometry, collision, and inertial properties; joints connect them in a tree structure
- Forward kinematics computes end-effector pose from joint angles; URDF provides the kinematic structure for solvers
- Accurate inertial properties (mass, moment of inertia) are essential for physics simulation and dynamic control
- Joint limits, damping, and transmission characteristics ensure realistic and safe robot behavior
- URDF validation catches structural errors early and prevents runtime failures in simulation and control

### Glossary

- **URDF**: Unified Robot Description Format, an XML-based standard for describing robot structure
- **Link**: A rigid body in the robot with geometry, visual properties, collision bounds, and inertia
- **Joint**: A connection between two links defining a degree of freedom (DOF) with rotation or translation
- **Forward Kinematics**: Computing end-effector position and orientation from joint angles
- **Inverse Kinematics**: Finding joint angles that achieve a desired end-effector pose
- **Moment of Inertia**: A measure of resistance to rotational acceleration about an axis
- **Kinematic Chain**: A sequence of links and joints forming a path from base to end-effector

### References

- [URDF Introduction](https://docs.ros.org/en/humble/Concepts/Intermediate/URDF/URDF-Introduction.html)
- [URDF XML Documentation](https://wiki.ros.org/urdf/XML)
- [Building Visual Robot Models](https://wiki.ros.org/urdf/Tutorials/Building%20a%20Visual%20Robot%20Model%20with%20URDF)
- [Checking URDF Validity](https://wiki.ros.org/urdf/Tutorials/Checking%20a%20URDF)
