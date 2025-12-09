## Unity for Robot Visualization

### Introduction

While Gazebo excels at physics simulation, Unity provides superior real-time 3D rendering and interactive visualization for humanoid robot systems. Unity enables photorealistic rendering, sophisticated animations, and integration with high-quality 3D assets for training, demonstration, and validation. [Citation: https://unity.com/] This chapter covers setting up Unity for robot visualization, integrating with ROS 2 via ROSSharp, and creating interactive humanoid robot simulations with advanced graphics.

### Learning Objectives

- Set up Unity development environment with robotics-focused plugins
- Import and configure humanoid robot 3D models with materials and animations
- Integrate ROS 2 communication via ROSSharp message subscribers
- Synchronize robot motion between ROS 2 control and Unity visualization
- Create interactive scenes with camera control and object interaction
- Implement real-time pose visualization and sensor data overlays
- Optimize rendering performance for complex humanoid scenes
- Build standalone executables for simulation distribution

### Core Concepts

#### ROSSharp and ROS 2 Integration

ROSSharp is a C# library that bridges ROS 2 and Unity through WebSocket connections. [Citation: https://github.com/siemens/ros-sharp] It provides message serialization/deserialization for ROS 2 message types, enabling real-time data exchange between ROS 2 nodes and Unity. For humanoid robots, ROSSharp enables visualization of joint states, sensor data, and planning results in real-time without modifying existing ROS 2 infrastructure.

#### 3D Model Import and Animation

Unity supports importing 3D models in FBX, GLTF, and other formats. Humanoid robot models require proper skeletal rigging and animation setup. [Citation: https://docs.unity3d.com/Manual/Humanoids.html] Unity's Humanoid Avatar system provides standardized skeleton mapping for humanoid characters. Imported robot models can be animated via C# scripts receiving joint angle commands from ROS 2.

#### Real-Time Rendering Pipeline

Unity's rendering engine provides photorealistic graphics with materials, lighting, shadows, and effects. [Citation: https://docs.unity3d.com/Manual/RenderingPipeline.html] Built-in Render Pipeline supports forward and deferred rendering. For VR/AR applications, Universal Render Pipeline (URP) enables cross-platform high-quality graphics. Proper material setup with PBR (Physically-Based Rendering) enhances visual realism.

#### Physics in Unity

Unity includes NVIDIA PhysX physics engine, distinct from Gazebo's simulation. [Citation: https://docs.unity3d.com/Manual/PhysicsSection.html] Unity physics is useful for interactive simulations but less suitable for humanoid control validation due to different dynamics models. Typically, humanoid motion is computed in ROS 2/Gazebo and only visualized in Unity to leverage superior graphics.

#### UI and User Interaction

Unity UI system enables interactive menus, sliders, and displays for robot control and monitoring. [Citation: https://docs.unity3d.com/Manual/UISystem.html] Interactive scenes allow operators to select objects, trigger actions, and adjust parameters in real-time. Combination of visualization, monitoring, and control in single interface streamlines robot operation.

### Practical Examples

#### Example 1: ROSSharp Unity Subscriber for Joint States

```csharp
using UnityEngine;
using RosSharp.RosBridgeClient;
using sensor_msgs = RosSharp.RosBridgeClient.MessageTypes.Sensor;

public class JointStateSubscriber : MonoBehaviour
{
    [SerializeField] private RosConnector rosConnector;
    [SerializeField] private string subscriberTopic = "/joint_states";

    // References to humanoid joint transforms
    [SerializeField] private Transform[] jointTransforms;
    [SerializeField] private string[] jointNames;

    private RosSubscriber<sensor_msgs.JointState> jointStateSubscriber;

    private void Start()
    {
        rosConnector.RosSocket.Subscribe<sensor_msgs.JointState>(
            subscriberTopic,
            OnJointStateReceived
        );
    }

    private void OnJointStateReceived(sensor_msgs.JointState message)
    {
        // Map joint angles to transforms
        for (int i = 0; i < message.name.Length; i++)
        {
            string jointName = message.name[i];
            float angle = (float)message.position[i];

            // Find matching joint transform
            for (int j = 0; j < jointNames.Length; j++)
            {
                if (jointNames[j] == jointName)
                {
                    // Apply rotation based on joint type
                    UpdateJointTransform(jointTransforms[j], jointName, angle);
                    break;
                }
            }
        }
    }

    private void UpdateJointTransform(Transform joint, string jointName, float angle)
    {
        // Determine rotation axis based on joint name
        Vector3 rotationAxis = Vector3.zero;

        if (jointName.Contains("pitch"))
        {
            rotationAxis = Vector3.right;  // X-axis rotation
        }
        else if (jointName.Contains("roll"))
        {
            rotationAxis = Vector3.forward;  // Z-axis rotation
        }
        else if (jointName.Contains("yaw"))
        {
            rotationAxis = Vector3.up;  // Y-axis rotation
        }

        // Apply rotation in degrees (convert from radians)
        float angleDegrees = angle * Mathf.Rad2Deg;
        joint.localRotation = Quaternion.AngleAxis(angleDegrees, rotationAxis);

        Debug.Log($"Joint: {jointName}, Angle: {angleDegrees:F2}°");
    }

    private void OnDestroy()
    {
        if (rosConnector?.RosSocket != null)
        {
            rosConnector.RosSocket.Unsubscribe(subscriberTopic);
        }
    }
}
```

#### Example 2: Publishing Twist Commands from Unity

```csharp
using UnityEngine;
using RosSharp.RosBridgeClient;
using geometry_msgs = RosSharp.RosBridgeClient.MessageTypes.Geometry;

public class TwistCommandPublisher : MonoBehaviour
{
    [SerializeField] private RosConnector rosConnector;
    [SerializeField] private string publisherTopic = "/humanoid/cmd_vel";

    // Movement parameters
    [SerializeField] private float moveSpeed = 1.0f;
    [SerializeField] private float rotationSpeed = 1.0f;

    private RosPublisher<geometry_msgs.Twist> twistPublisher;

    private void Start()
    {
        twistPublisher = rosConnector.RosSocket.Advertise<geometry_msgs.Twist>(publisherTopic);
    }

    private void Update()
    {
        // Read input from keyboard/gamepad
        float forwardInput = Input.GetAxis("Vertical");  // W/S or up/down arrow
        float turnInput = Input.GetAxis("Horizontal");   // A/D or left/right arrow

        // Create Twist message
        var twist = new geometry_msgs.Twist()
        {
            linear = new geometry_msgs.Vector3()
            {
                x = forwardInput * moveSpeed,
                y = 0,
                z = 0
            },
            angular = new geometry_msgs.Vector3()
            {
                x = 0,
                y = 0,
                z = turnInput * rotationSpeed
            }
        };

        // Publish command
        twistPublisher.Publish(twist);
    }

    private void OnDestroy()
    {
        if (rosConnector?.RosSocket != null)
        {
            rosConnector.RosSocket.Unadvertise(publisherTopic);
        }
    }
}
```

#### Example 3: Real-Time Sensor Data Visualization

```csharp
using UnityEngine;
using RosSharp.RosBridgeClient;
using sensor_msgs = RosSharp.RosBridgeClient.MessageTypes.Sensor;

public class IMUVisualization : MonoBehaviour
{
    [SerializeField] private RosConnector rosConnector;
    [SerializeField] private string imuTopic = "/imu";

    // UI elements
    [SerializeField] private UnityEngine.UI.Text accelerationText;
    [SerializeField] private UnityEngine.UI.Text angularVelocityText;
    [SerializeField] private UnityEngine.UI.Text orientationText;

    // Visual indicators
    [SerializeField] private Transform orientationIndicator;
    [SerializeField] private LineRenderer forceVector;

    private Quaternion currentOrientation = Quaternion.identity;
    private Vector3 currentAcceleration = Vector3.zero;

    private void Start()
    {
        rosConnector.RosSocket.Subscribe<sensor_msgs.Imu>(
            imuTopic,
            OnIMUDataReceived
        );
    }

    private void OnIMUDataReceived(sensor_msgs.Imu message)
    {
        // Extract accelerometer data
        currentAcceleration = new Vector3(
            (float)message.linear_acceleration.x,
            (float)message.linear_acceleration.y,
            (float)message.linear_acceleration.z
        );

        // Extract gyroscope data (angular velocity)
        Vector3 angularVelocity = new Vector3(
            (float)message.angular_velocity.x,
            (float)message.angular_velocity.y,
            (float)message.angular_velocity.z
        );

        // Extract orientation quaternion
        currentOrientation = new Quaternion(
            (float)message.orientation.x,
            (float)message.orientation.y,
            (float)message.orientation.z,
            (float)message.orientation.w
        );

        // Update UI text
        accelerationText.text = $"Acceleration: {currentAcceleration:F2} m/s²";
        angularVelocityText.text = $"Angular Velocity: {angularVelocity:F2} rad/s";
        orientationText.text = $"Orientation: {currentOrientation.eulerAngles:F2}°";

        // Update 3D indicators
        UpdateOrientationIndicator();
        UpdateForceVector();
    }

    private void UpdateOrientationIndicator()
    {
        if (orientationIndicator != null)
        {
            orientationIndicator.rotation = currentOrientation;
        }
    }

    private void UpdateForceVector()
    {
        if (forceVector != null)
        {
            // Normalize acceleration for visualization
            Vector3 visualForce = currentAcceleration.normalized;

            forceVector.SetPosition(0, Vector3.zero);
            forceVector.SetPosition(1, visualForce);

            // Color gradient based on magnitude
            float magnitude = currentAcceleration.magnitude;
            Color forceColor = Color.Lerp(Color.green, Color.red, magnitude / 20f);
            forceVector.startColor = forceColor;
            forceVector.endColor = forceColor;
        }
    }

    private void OnDestroy()
    {
        if (rosConnector?.RosSocket != null)
        {
            rosConnector.RosSocket.Unsubscribe(imuTopic);
        }
    }
}
```

#### Example 4: Camera Controller for Interactive Scene Navigation

```csharp
using UnityEngine;

public class CameraController : MonoBehaviour
{
    [SerializeField] private Camera mainCamera;
    [SerializeField] private Transform targetLookAt;  // Robot center of mass

    [SerializeField] private float orbitDistance = 3.0f;
    [SerializeField] private float orbitSpeed = 100.0f;
    [SerializeField] private float zoomSpeed = 2.0f;
    [SerializeField] private float minZoom = 1.0f;
    [SerializeField] private float maxZoom = 10.0f;

    private float horizontalAngle = 0.0f;
    private float verticalAngle = 30.0f;

    private void Update()
    {
        HandleMouseInput();
        UpdateCameraPosition();
    }

    private void HandleMouseInput()
    {
        // Right mouse button to rotate view
        if (Input.GetMouseButton(1))
        {
            float mouseX = Input.GetAxis("Mouse X");
            float mouseY = Input.GetAxis("Mouse Y");

            horizontalAngle += mouseX * orbitSpeed * Time.deltaTime;
            verticalAngle -= mouseY * orbitSpeed * Time.deltaTime;

            // Clamp vertical angle
            verticalAngle = Mathf.Clamp(verticalAngle, 10.0f, 80.0f);
        }

        // Scroll wheel to zoom
        float scrollDelta = Input.GetAxis("Mouse ScrollWheel");
        if (scrollDelta != 0)
        {
            orbitDistance -= scrollDelta * zoomSpeed;
            orbitDistance = Mathf.Clamp(orbitDistance, minZoom, maxZoom);
        }

        // Middle mouse button to pan/reset
        if (Input.GetMouseButtonDown(2))
        {
            horizontalAngle = 0.0f;
            verticalAngle = 30.0f;
        }
    }

    private void UpdateCameraPosition()
    {
        if (targetLookAt == null)
            return;

        // Calculate position on orbit sphere
        float radHorizontal = horizontalAngle * Mathf.Deg2Rad;
        float radVertical = verticalAngle * Mathf.Deg2Rad;

        Vector3 cameraOffset = new Vector3(
            orbitDistance * Mathf.Cos(radVertical) * Mathf.Sin(radHorizontal),
            orbitDistance * Mathf.Sin(radVertical),
            orbitDistance * Mathf.Cos(radVertical) * Mathf.Cos(radHorizontal)
        );

        // Position camera
        mainCamera.transform.position = targetLookAt.position + cameraOffset;

        // Look at target
        mainCamera.transform.LookAt(targetLookAt.position + Vector3.up * 0.5f);
    }
}
```

### Step-by-Step Implementation Guide

1. **Install Unity and ROSSharp**: Download Unity Hub and install latest LTS version. Clone ROSSharp from GitHub and import into Unity Assets. Configure ROSSharp WebSocket connection parameters. [Citation: https://github.com/siemens/ros-sharp]

2. **Set Up ROS Bridge**: In ROS 2, run `rosbridge_server` to enable WebSocket connections. Configure firewall and network to allow Unity connections. Test connection: `rostopic list` should work from Unity console. [Citation: https://docs.ros.org/en/humble/Concepts/About-Middleware/Middleware-Implementation-Guide.html]

3. **Import Humanoid Model**: Import 3D model (FBX/GLTF) into Unity Assets. Apply Humanoid Avatar for skeleton mapping. Attach materials and textures. Test model rigging in animation preview. [Citation: https://docs.unity3d.com/Manual/Humanoids.html]

4. **Create Joint Mapping Script**: Write C# script to map ROS joint state messages to Unity Transform rotations. Define joint name → Transform hierarchy mapping. Subscribe to `/joint_states` topic. [Citation: https://github.com/siemens/ros-sharp]

5. **Build and Deploy**: Test in Unity Editor with active ROS 2 system. Build standalone executable for distribution. Optimize performance: reduce polygon count, bake lighting, use Level-of-Detail (LOD) for distant objects. [Citation: https://docs.unity3d.com/Manual/OptimizingGraphicsPerformance.html]

### Summary

- Unity provides photorealistic real-time 3D visualization superior to Gazebo's rendering
- ROSSharp enables seamless ROS 2 integration via WebSocket for message exchange
- Joint state messages drive humanoid animation in real-time from ROS 2 control
- Sensor data visualization (IMU, camera, LiDAR) enhances operator situational awareness
- Interactive scenes with camera control and UI enable operator training and testing
- Combined Gazebo physics + Unity visualization provides optimal simulation-visualization pipeline
- Standalone executables enable distribution of simulations without requiring ROS 2 installation

### Glossary

- **ROSSharp**: C# library providing ROS 2 communication via WebSocket from Unity
- **Avatar**: Unity's skeletal mapping system for humanoid character animation
- **Forward Kinematics Visualization**: Rendering joint angles as 3D transforms
- **LOD (Level-of-Detail)**: Multiple mesh resolutions for performance optimization at different distances
- **WebSocket**: Bidirectional communication protocol enabling real-time ROS 2 data exchange
- **Render Pipeline**: Graphics architecture defining material, lighting, and output rendering process
- **Quaternion**: 4-component representation of 3D rotation avoiding gimbal lock

### References

- [ROSSharp GitHub Repository](https://github.com/siemens/ros-sharp)
- [Unity Manual - Humanoids](https://docs.unity3d.com/Manual/Humanoids.html)
- [Unity Rendering Pipeline](https://docs.unity3d.com/Manual/RenderingPipeline.html)
- [Optimizing Graphics Performance](https://docs.unity3d.com/Manual/OptimizingGraphicsPerformance.html)
