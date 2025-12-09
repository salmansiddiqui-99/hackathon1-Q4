## Sensor Simulation and Perception

### Introduction

Accurate sensor simulation is critical for developing perception pipelines for humanoid robots before deploying to hardware. Gazebo provides plugins to simulate cameras, LiDAR, IMU, and depth sensors with configurable noise models and output formats. [Citation: https://gazebosim.org/docs/fortress/sensors] This chapter covers sensor simulation setup, noise modeling, data processing pipelines, and integration with ROS 2 perception algorithms for humanoid robot applications.

### Learning Objectives

- Configure and simulate RGB cameras with realistic optical properties and noise
- Implement depth cameras (RGB-D) and LiDAR sensors for 3D perception
- Model realistic sensor noise (Gaussian noise, quantization) for algorithm testing
- Process simulated sensor data in ROS 2 perception pipelines
- Implement computer vision algorithms on simulated images (edge detection, feature extraction)
- Integrate point cloud processing for obstacle detection and navigation
- Calibrate virtual sensor parameters to match hardware specifications
- Validate perception algorithms in simulation before hardware deployment

### Core Concepts

#### Camera Simulation and Intrinsic Parameters

Gazebo simulates cameras with configurable intrinsic parameters: focal length, principal point, distortion coefficients. [Citation: https://gazebosim.org/docs/fortress/sensors] Camera intrinsics are encoded in the CameraInfo ROS message. For humanoid robots, front-facing head cameras (60-90° field-of-view) enable object detection and navigation. Simulation allows testing vision algorithms across different camera specifications without hardware swaps.

#### Depth and RGB-D Cameras

Depth cameras measure distance to objects using structured light, time-of-flight, or stereo matching. RGB-D sensors (like Kinect) combine color and depth information. [Citation: https://gazebosim.org/docs/fortress/sensors] Gazebo simulates depth cameras by raycasting or projecting depth maps. Output is published as `sensor_msgs::Image` (depth) and optional color image. Depth sensors have maximum range, field-of-view, and angular resolution parameters.

#### LiDAR Sensor Simulation

LiDAR (Light Detection and Ranging) sensors scan environment by measuring time-of-flight for reflected laser pulses. [Citation: https://gazebosim.org/docs/fortress/sensors] Gazebo simulates multi-beam LiDAR (typically 32-64 beams) outputting point clouds. Point clouds are published as `sensor_msgs::PointCloud2` with 3D coordinates in sensor frame. LiDAR parameters include beam count, angular resolution, range, and noise characteristics.

#### IMU Sensor Modeling

Inertial Measurement Units measure acceleration (accelerometer) and angular velocity (gyroscope). Gazebo simulates IMU with configurable noise: white noise on accelerometer/gyroscope, bias drift, and scale factor errors. [Citation: https://gazebosim.org/docs/fortress/sensors] Accurate IMU simulation is essential for humanoid balance control, which relies on gravity-compensated accelerometer readings and angular velocity feedback.

#### Sensor Noise and Uncertainty

Realistic noise models are critical for algorithm validation. Gazebo supports Gaussian noise (specified by mean and variance) and quantization effects. [Citation: https://gazebosim.org/docs/fortress/sensor_noise] Depth sensor noise typically increases with distance (squared relationship). IMU bias drift simulates slow changes in sensor bias over time. Testing algorithms with realistic noise prevents overfitting to perfect simulation data.

### Practical Examples

#### Example 1: Configuring a Simulated RGB Camera

```xml
<model name="humanoid_head">
  <link name="head_link">
    <!-- Head geometry... -->

    <!-- Front-facing RGB camera -->
    <sensor name="head_camera" type="camera">
      <pose relative_to="head_link">0 0 0.1 0 0 0</pose>
      <camera name="head_camera">
        <!-- Intrinsic parameters -->
        <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
        <image>
          <width>640</width>
          <height>480</height>
        </image>
        <clip>
          <near>0.05</near>
          <far>50.0</far>
        </clip>

        <!-- Distortion model (Brown-Conrady) -->
        <distortion>
          <k1>-0.1</k1>
          <k2>0.05</k2>
          <k3>0.0</k3>
          <p1>0.0</p1>
          <p2>0.0</p2>
        </distortion>

        <!-- Noise model -->
        <noise>
          <type>gaussian</type>
          <mean>0.0</mean>
          <stddev>0.001</stddev>
        </noise>
      </camera>

      <!-- Update rate -->
      <update_rate>30</update_rate>

      <!-- ROS publisher -->
      <plugin name="camera_controller"
              filename="libgazebo_ros_camera.so">
        <ros>
          <namespace>humanoid/head</namespace>
          <remapping>image_raw:=camera/image</remapping>
          <remapping>camera_info:=camera/camera_info</remapping>
        </ros>
        <camera_name>head_camera</camera_name>
      </plugin>
    </sensor>
  </link>
</model>
```

#### Example 2: Processing Camera Images for Object Detection

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import numpy as np

class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detector')
        self.bridge = CvBridge()

        # Subscribe to camera image
        self.image_sub = self.create_subscription(
            Image,
            '/humanoid/head/camera/image',
            self.image_callback,
            10
        )

        # Subscribe to camera info for intrinsics
        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            '/humanoid/head/camera/camera_info',
            self.camera_info_callback,
            10
        )

        self.camera_matrix = None
        self.dist_coeffs = None

    def camera_info_callback(self, msg):
        """Extract camera intrinsics from CameraInfo."""
        self.camera_matrix = np.array(msg.k).reshape(3, 3)
        self.dist_coeffs = np.array(msg.d)
        self.get_logger().info("Camera matrix loaded")

    def image_callback(self, msg):
        """Detect edges and corners in camera image."""
        # Convert ROS image to OpenCV format
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        # Undistort image using camera intrinsics
        if self.camera_matrix is not None:
            gray = cv2.undistort(gray, self.camera_matrix, self.dist_coeffs)

        # Detect edges using Canny
        edges = cv2.Canny(gray, 100, 200)

        # Detect corners using Harris corner detection
        corners = cv2.cornerHarris(gray, 2, 3, 0.04)
        corners = cv2.dilate(corners, None)

        # Mark strong corners
        cv_image[corners > 0.01 * corners.max()] = [0, 0, 255]  # Red

        # Detect contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by area (remove noise)
        filtered_contours = [c for c in contours if cv2.contourArea(c) > 100]

        # Draw contours
        cv2.drawContours(cv_image, filtered_contours, -1, (0, 255, 0), 2)

        # Log detections
        self.get_logger().debug(
            f"Detected {len(filtered_contours)} objects, {np.sum(corners > 0.01 * corners.max())} corners"
        )

        # Display (optional, for debugging)
        # cv2.imshow('Object Detection', cv_image)
        # cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

#### Example 3: LiDAR Point Cloud Processing

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2
import numpy as np

class LiDARProcessor(Node):
    def __init__(self):
        super().__init__('lidar_processor')

        # Subscribe to LiDAR point cloud
        self.cloud_sub = self.create_subscription(
            PointCloud2,
            '/humanoid/lidar',
            self.cloud_callback,
            10
        )

        # Publisher for obstacle detection
        self.obstacle_pub = self.create_publisher(
            PointCloud2,
            '/humanoid/obstacles',
            10
        )

    def cloud_callback(self, msg):
        """Process point cloud for obstacle detection."""
        # Extract points from point cloud
        points = np.array(list(pc2.read_points(msg, skip_nans=True)))

        if len(points) == 0:
            return

        # Filter points by height (obstacles above ground, below head)
        height_min, height_max = 0.1, 2.0  # meters
        obstacle_mask = (points[:, 2] > height_min) & (points[:, 2] < height_max)
        obstacle_points = points[obstacle_mask]

        # Filter points by distance from robot (forward sensing)
        distance_mask = (points[:, 0] > 0) & (points[:, 0] < 5.0)  # 5 meter range
        distant_obstacles = obstacle_points[distance_mask]

        # Cluster points into obstacles using DBSCAN
        if len(distant_obstacles) > 10:
            clusters = self.dbscan(distant_obstacles, eps=0.3, min_points=5)
            self.get_logger().info(f"Detected {len(clusters)} obstacles")

            # Find nearest obstacle
            if clusters:
                nearest_obstacle = min(
                    clusters,
                    key=lambda c: np.linalg.norm(np.mean(c, axis=0))
                )
                dist = np.linalg.norm(np.mean(nearest_obstacle, axis=0))
                self.get_logger().warn(f"Nearest obstacle: {dist:.2f} m")

    def dbscan(self, points, eps=0.3, min_points=5):
        """Simple DBSCAN clustering for point cloud."""
        clusters = []
        visited = set()
        labels = [-1] * len(points)

        for i, point in enumerate(points):
            if i in visited:
                continue

            visited.add(i)

            # Find neighbors within eps distance
            neighbors = []
            for j, other_point in enumerate(points):
                if j not in visited:
                    dist = np.linalg.norm(point - other_point)
                    if dist < eps:
                        neighbors.append(j)

            if len(neighbors) >= min_points:
                # Start new cluster
                cluster = [points[i]]
                cluster_label = len(clusters)

                for neighbor_idx in neighbors:
                    if neighbor_idx not in visited:
                        visited.add(neighbor_idx)
                        cluster.append(points[neighbor_idx])
                        labels[neighbor_idx] = cluster_label

                clusters.append(np.array(cluster))

        return clusters

def main(args=None):
    rclpy.init(args=args)
    node = LiDARProcessor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

#### Example 4: IMU Data Processing for Balance Control

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from std_msgs.msg import Float32
import numpy as np
from collections import deque

class IMUBalanceController(Node):
    def __init__(self):
        super().__init__('imu_balance_controller')

        # Subscribe to IMU
        self.imu_sub = self.create_subscription(
            Imu,
            '/humanoid/imu',
            self.imu_callback,
            10
        )

        # Publisher for balance correction commands
        self.balance_pub = self.create_publisher(
            Float32,
            '/humanoid/balance_correction',
            10
        )

        # History for filtering
        self.accel_history = deque(maxlen=10)
        self.gyro_history = deque(maxlen=10)

        # Calibration
        self.accel_bias = np.array([0.0, 0.0, 0.0])
        self.gyro_bias = np.array([0.0, 0.0, 0.0])

    def imu_callback(self, msg):
        """Process IMU data for balance feedback."""
        # Extract accelerometer and gyroscope data
        accel = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z
        ])

        gyro = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])

        # Apply bias correction
        accel_corrected = accel - self.accel_bias
        gyro_corrected = gyro - self.gyro_bias

        # Store in history for filtering
        self.accel_history.append(accel_corrected)
        self.gyro_history.append(gyro_corrected)

        # Compute moving average for noise reduction
        if len(self.accel_history) >= 5:
            accel_filtered = np.mean(list(self.accel_history), axis=0)
        else:
            accel_filtered = accel_corrected

        # Estimate pitch and roll from accelerometer
        # Pitch: rotation around Y axis
        pitch = np.arctan2(
            accel_filtered[0],
            np.sqrt(accel_filtered[1]**2 + accel_filtered[2]**2)
        )

        # Roll: rotation around X axis
        roll = np.arctan2(
            accel_filtered[1],
            np.sqrt(accel_filtered[0]**2 + accel_filtered[2]**2)
        )

        # Gyroscope gives angular velocity
        angular_velocity_y = gyro_corrected[1]  # Pitch rate

        # PID controller for balance
        kp_pitch = 0.5
        kd_pitch = 0.1

        balance_correction = kp_pitch * pitch + kd_pitch * angular_velocity_y

        # Publish correction command
        msg_out = Float32()
        msg_out.data = balance_correction
        self.balance_pub.publish(msg_out)

        self.get_logger().debug(
            f"Pitch: {np.degrees(pitch):.1f}°, "
            f"Roll: {np.degrees(roll):.1f}°, "
            f"Correction: {balance_correction:.3f}"
        )

    def calibrate_imu(self, num_samples=100):
        """Calibrate IMU bias by averaging readings at rest."""
        self.get_logger().info("Calibrating IMU... please keep robot stationary")
        accel_samples = []
        gyro_samples = []

        for _ in range(num_samples):
            # Wait for samples
            rclpy.spin_once(self, timeout_sec=0.01)
            if self.accel_history:
                accel_samples.append(self.accel_history[-1])
            if self.gyro_history:
                gyro_samples.append(self.gyro_history[-1])

        if accel_samples and gyro_samples:
            self.accel_bias = np.mean(accel_samples, axis=0)
            self.gyro_bias = np.mean(gyro_samples, axis=0)
            self.get_logger().info(f"Calibration complete. Accel bias: {self.accel_bias}")

def main(args=None):
    rclpy.init(args=args)
    node = IMUBalanceController()

    # Calibrate IMU on startup
    node.calibrate_imu()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Step-by-Step Implementation Guide

1. **Configure Sensor Plugins in SDF**: Add sensor elements to robot SDF with type (camera, ray, imu, contact), update rate, and plugin configuration. Specify output ROS topics and message types. [Citation: https://gazebosim.org/docs/fortress/sensors]

2. **Set Intrinsic and Extrinsic Parameters**: Define camera focal length, principal point, resolution for cameras. Set sensor mounting pose (position/orientation) relative to parent link. [Citation: https://gazebosim.org/docs/fortress/sensors]

3. **Configure Noise Models**: Add noise elements to sensors with type (gaussian), mean, and standard deviation. Noise is sampled and added to sensor output. Calibrate noise parameters to match hardware sensors. [Citation: https://gazebosim.org/docs/fortress/sensor_noise]

4. **Implement Perception Pipelines**: Subscribe to sensor topics in ROS 2 nodes. Process image/point cloud data using OpenCV, PCL (Point Cloud Library), or TensorFlow. Test algorithms across different sensor types and noise levels. [Citation: https://docs.ros.org/en/humble/Tutorials/Intermediate/ROS2-Perception/]

5. **Validate Against Hardware**: Record real sensor data from hardware, compare with simulation. Adjust simulation noise models to match hardware characteristics. Use hardware ground truth to validate algorithm accuracy.

### Summary

- Gazebo simulates realistic camera, depth, LiDAR, and IMU sensors with configurable parameters
- Sensor noise models enable testing perception algorithms in presence of realistic uncertainty
- Camera intrinsics and distortion parameters enable undistortion and precise 3D vision
- Point cloud processing enables obstacle detection and navigation for humanoid robots
- IMU simulation with noise and bias supports development of balance control algorithms
- Simulation validation prevents algorithm overfitting and improves hardware deployment success
- Sensor calibration and multi-modal fusion enhance humanoid perception robustness

### Glossary

- **Intrinsic Parameters**: Camera focal length, principal point, and distortion coefficients
- **Point Cloud**: 3D data representation with XYZ coordinates (possibly with color/intensity)
- **Depth Sensor**: Measures distance to objects, outputs depth maps or point clouds
- **LiDAR**: Light Detection and Ranging sensor measuring 3D environment via laser scanning
- **IMU**: Inertial Measurement Unit with accelerometer and gyroscope
- **White Noise**: Random noise with constant power across all frequencies
- **Bias Drift**: Slow variation in sensor offset over time

### References

- [Gazebo Sensor Simulation](https://gazebosim.org/docs/fortress/sensors)
- [Gazebo Sensor Noise](https://gazebosim.org/docs/fortress/sensor_noise)
- [ROS 2 Perception Tutorials](https://docs.ros.org/en/humble/Tutorials/Intermediate/ROS2-Perception/)
- [Point Cloud Library](https://pointclouds.org/)
