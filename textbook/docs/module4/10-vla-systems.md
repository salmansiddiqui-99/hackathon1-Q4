## Voice and Language Action (VLA) Systems

### Introduction

Voice-to-Action (VLA) systems enable humanoid robots to understand natural language commands, reason about intentions, and execute complex tasks through integration of speech recognition, language models, and action planning. [Citation: https://arxiv.org/abs/2405.04254] Large language models (LLMs) like GPT-4 or Llama 2 provide semantic understanding and reasoning. This chapter covers speech processing, language understanding, action mapping, and real-time voice control for humanoid robots, enabling intuitive human-robot interaction.

### Learning Objectives

- Implement speech-to-text (STT) processing with ROS 2 for voice input
- Integrate large language models (LLMs) for natural language understanding
- Design action mappings from semantic representations to robot commands
- Implement context-aware command interpretation and disambiguation
- Build real-time voice-based task planning for complex multi-step actions
- Integrate vision with language for grounded understanding (vision-language models)
- Handle uncertainty and user feedback in voice-based systems
- Evaluate and improve VLA system performance through human studies

### Core Concepts

#### Speech Recognition and Preprocessing

Speech-to-text (STT) converts voice input to text using acoustic models and language models. [Citation: https://arxiv.org/abs/2010.14094] Real-time STT requires low-latency processing (< 1 second from speech end to text output). Major providers: Google Cloud Speech-to-Text, Azure Speech Services, open-source Whisper. For humanoids, on-device STT improves privacy and latency by processing audio locally on GPU.

#### Large Language Models for Understanding

Large language models (LLMs) like GPT-4, Claude, or Llama 2 understand natural language intent. [Citation: https://arxiv.org/abs/2303.08774] In-context learning (few-shot examples) or fine-tuning enables robots to understand domain-specific commands. Prompt engineering shapes model outputs: explicitly including available actions helps models ground language to robot capabilities.

#### Action Grounding and Mapping

Action grounding maps semantic representations (parsed from language) to robot-executable actions. [Citation: https://arxiv.org/abs/2307.08995] Structured representations (RDF triples, semantic graphs) enable reasoning about complex actions. For humanoids: "pick up the red cube" → perception task (detect red cube) + manipulation task (reach, grasp, lift).

#### Vision-Language Models

Vision-Language Models (VLMs) like CLIP or LLaVA understand images and text jointly. [Citation: https://arxiv.org/abs/2305.13583] Enables grounded language understanding: "the object to the left of the table" is understood with reference to visual context. For humanoids, VLMs enable spatial reasoning about object locations and human intentions.

#### Real-Time Voice Loop and Latency

End-to-end latency (speech → text → action) must be < 2 seconds for responsive interaction. [Citation: https://arxiv.org/abs/1810.11895] Streaming STT reduces latency compared to batch processing. Caching LLM responses and pre-computing likely actions further reduces delays. For safety-critical actions, explicit confirmation mechanisms prevent errors from misrecognition.

### Practical Examples

#### Example 1: Speech-to-Text with Whisper

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from audio_common_msgs.msg import AudioData
import numpy as np
import queue
import threading

try:
    import whisper
except ImportError:
    print("Install: pip install openai-whisper")

class SpeechToTextNode(Node):
    """Convert speech to text using OpenAI Whisper."""

    def __init__(self):
        super().__init__('speech_to_text')

        # Audio input queue
        self.audio_queue = queue.Queue()

        # Subscribe to audio topic
        self.audio_sub = self.create_subscription(
            AudioData,
            '/audio_in',
            self.audio_callback,
            10
        )

        # Publish recognized text
        self.text_pub = self.create_publisher(
            String,
            '/recognized_speech',
            10
        )

        # Load Whisper model (base model, ~140M parameters)
        self.get_logger().info("Loading Whisper model...")
        self.model = whisper.load_model("base")
        self.get_logger().info("Whisper model loaded")

        # Buffering for continuous speech detection
        self.audio_buffer = np.array([], dtype=np.float32)
        self.sampling_rate = 16000
        self.silence_threshold = 0.02  # RMS energy threshold
        self.silence_duration = 2.0  # seconds

        # Start processing thread
        self.processing_thread = threading.Thread(target=self.process_audio, daemon=True)
        self.processing_thread.start()

    def audio_callback(self, msg):
        """Receive audio data from ROS topic."""
        # Convert bytes to numpy array
        audio_data = np.frombuffer(msg.data, dtype=np.int16).astype(np.float32) / 32768.0
        self.audio_buffer = np.concatenate((self.audio_buffer, audio_data))

    def detect_silence(self, audio_chunk, threshold=0.02):
        """Detect if audio chunk is silent."""
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        return rms < threshold

    def process_audio(self):
        """Process buffered audio for speech recognition."""
        while True:
            # Wait for enough audio (at least 2 seconds)
            if len(self.audio_buffer) < self.sampling_rate * 2:
                time.sleep(0.1)
                continue

            # Check for silence
            last_chunk = self.audio_buffer[-self.sampling_rate:]
            if self.detect_silence(last_chunk, self.silence_threshold):
                # Likely end of speech
                self.recognize_audio()

            time.sleep(0.1)

    def recognize_audio(self):
        """Transcribe buffered audio with Whisper."""
        if len(self.audio_buffer) < self.sampling_rate:
            return

        try:
            # Transcribe
            result = self.model.transcribe(
                self.audio_buffer,
                language="en",
                fp16=False
            )

            text = result["text"].strip()

            if text:
                self.get_logger().info(f"Recognized: {text}")

                # Publish result
                msg = String()
                msg.data = text
                self.text_pub.publish(msg)

            # Clear buffer
            self.audio_buffer = np.array([], dtype=np.float32)

        except Exception as e:
            self.get_logger().error(f"Recognition error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = SpeechToTextNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

#### Example 2: Language Understanding with LLM

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import os

try:
    from anthropic import Anthropic
except ImportError:
    print("Install: pip install anthropic")

class LanguageUnderstandingNode(Node):
    """Use Claude LLM to understand robot commands."""

    def __init__(self):
        super().__init__('language_understanding')

        # Subscribe to recognized speech
        self.speech_sub = self.create_subscription(
            String,
            '/recognized_speech',
            self.speech_callback,
            10
        )

        # Publish parsed actions
        self.action_pub = self.create_publisher(
            String,
            '/parsed_action',
            10
        )

        # Initialize Claude client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            self.get_logger().error("ANTHROPIC_API_KEY not set")
        self.client = Anthropic()

        # System prompt defining available actions
        self.system_prompt = """You are a robot command interpreter. Parse natural language commands into structured robot actions.

Available actions:
- move_to(location: str)
- pickup(object: str)
- place(object: str, location: str)
- follow_person()
- stop()
- rotate(degrees: float)
- speak(text: str)
- wait(seconds: float)

For each command, respond with JSON:
{"action": "action_name", "parameters": {...}, "confidence": 0.0-1.0, "explanation": "..."}

Example: "pick up the blue cube"
{"action": "pickup", "parameters": {"object": "blue cube"}, "confidence": 0.95}

Be confident (0.9+) only when intent is clear. For ambiguous commands, ask clarification."""

        self.conversation_history = []
        self.get_logger().info("Language understanding node initialized")

    def speech_callback(self, msg):
        """Process speech text with Claude."""
        user_input = msg.data

        self.get_logger().info(f"Processing: {user_input}")

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                system=self.system_prompt,
                messages=self.conversation_history
            )

            assistant_message = response.content[0].text

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            # Keep history to last 10 messages (context window)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            self.get_logger().info(f"Response: {assistant_message}")

            # Publish parsed action
            msg_out = String()
            msg_out.data = assistant_message
            self.action_pub.publish(msg_out)

        except Exception as e:
            self.get_logger().error(f"LLM error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = LanguageUnderstandingNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

#### Example 3: Action Execution from Parsed Commands

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import json
import time

class ActionExecutorNode(Node):
    """Execute parsed actions on robot."""

    def __init__(self):
        super().__init__('action_executor')

        # Subscribe to parsed actions
        self.action_sub = self.create_subscription(
            String,
            '/parsed_action',
            self.action_callback,
            10
        )

        # Publish velocity commands
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Service clients for manipulation, perception (not shown here)

        self.current_action = None
        self.get_logger().info("Action executor initialized")

    def action_callback(self, msg):
        """Parse and execute action."""
        try:
            # Try to parse JSON from Claude response
            # Claude might wrap it with text, so we extract JSON
            text = msg.data

            # Find JSON in response
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)

            if not json_match:
                self.get_logger().warn(f"No JSON found in: {text}")
                return

            action_dict = json.loads(json_match.group())

            # Check confidence threshold
            confidence = action_dict.get('confidence', 0.0)
            if confidence < 0.7:
                self.get_logger().warn(f"Low confidence ({confidence:.2f}): {text}")
                return

            # Execute action
            action_name = action_dict.get('action')
            parameters = action_dict.get('parameters', {})

            self.get_logger().info(f"Executing: {action_name}({parameters})")

            if action_name == 'move_to':
                self.execute_move_to(parameters.get('location'))
            elif action_name == 'pickup':
                self.execute_pickup(parameters.get('object'))
            elif action_name == 'place':
                self.execute_place(parameters.get('object'), parameters.get('location'))
            elif action_name == 'rotate':
                self.execute_rotate(parameters.get('degrees', 0))
            elif action_name == 'stop':
                self.execute_stop()
            else:
                self.get_logger().warn(f"Unknown action: {action_name}")

        except json.JSONDecodeError as e:
            self.get_logger().error(f"JSON parse error: {e}")
        except Exception as e:
            self.get_logger().error(f"Execution error: {e}")

    def execute_move_to(self, location):
        """Move robot to location."""
        self.get_logger().info(f"Moving to {location}")

        # Simple forward movement
        twist = Twist()
        twist.linear.x = 0.5  # m/s
        self.cmd_vel_pub.publish(twist)

        time.sleep(3)  # Move for 3 seconds

        # Stop
        twist.linear.x = 0.0
        self.cmd_vel_pub.publish(twist)

    def execute_pickup(self, obj):
        """Pick up object (simplified)."""
        self.get_logger().info(f"Picking up {obj}")
        # Call manipulation service (not shown)

    def execute_place(self, obj, location):
        """Place object at location."""
        self.get_logger().info(f"Placing {obj} at {location}")
        # Call manipulation service (not shown)

    def execute_rotate(self, degrees):
        """Rotate robot."""
        self.get_logger().info(f"Rotating {degrees}°")

        twist = Twist()
        twist.angular.z = 0.5  # rad/s
        self.cmd_vel_pub.publish(twist)

        duration = abs(degrees) / 57.3 / 0.5  # degrees to radians to time
        time.sleep(duration)

        twist.angular.z = 0.0
        self.cmd_vel_pub.publish(twist)

    def execute_stop(self):
        """Stop robot."""
        self.get_logger().info("Stopping")
        twist = Twist()
        self.cmd_vel_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = ActionExecutorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

#### Example 4: Vision-Language Grounding

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2

try:
    from transformers import CLIPProcessor, CLIPModel
    import torch
except ImportError:
    print("Install: pip install transformers torch")

class VisionLanguageGrounder(Node):
    """Ground language commands in visual context using CLIP."""

    def __init__(self):
        super().__init__('vision_language_grounder')

        # Subscribe to camera
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image',
            self.image_callback,
            10
        )

        # Subscribe to language commands
        self.command_sub = self.create_subscription(
            String,
            '/language_command',
            self.command_callback,
            10
        )

        self.bridge = CvBridge()

        # Load CLIP model
        self.get_logger().info("Loading CLIP model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.get_logger().info(f"CLIP model loaded on {self.device}")

        self.current_image = None

    def image_callback(self, msg):
        """Receive camera image."""
        self.current_image = self.bridge.imgmsg_to_cv2(msg)

    def command_callback(self, msg):
        """Process language command with visual context."""
        if self.current_image is None:
            self.get_logger().warn("No image available")
            return

        command = msg.data
        self.get_logger().info(f"Grounding command: {command}")

        # Extract noun phrases (objects) from command
        nouns = self.extract_objects(command)

        # Score candidate objects in image using CLIP
        scores = {}
        for noun in nouns:
            score = self.score_object_in_image(noun)
            scores[noun] = score
            self.get_logger().info(f"{noun}: {score:.2f}")

        # Select highest-scoring object
        if scores:
            best_object = max(scores, key=scores.get)
            self.get_logger().info(f"Selected: {best_object}")

    def extract_objects(self, text):
        """Extract object names from command (simplified)."""
        # Simple pattern matching
        colors = ['red', 'blue', 'green', 'yellow', 'cube', 'ball', 'block']
        objects = [w for w in text.lower().split() if w in colors]
        return objects if objects else ['object']

    def score_object_in_image(self, object_name):
        """Score likelihood of object in image using CLIP."""
        try:
            # Prepare image and text
            inputs = self.processor(
                text=[f"a photo of {object_name}", "a photo of other things"],
                images=[self.current_image],
                return_tensors="pt",
                padding=True
            ).to(self.device)

            # Get CLIP scores
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image

            # Softmax to get probabilities
            probs = torch.nn.functional.softmax(logits_per_image, dim=1)
            score = probs[0][0].item()  # Probability of first text description

            return score

        except Exception as e:
            self.get_logger().error(f"CLIP error: {e}")
            return 0.0

def main(args=None):
    rclpy.init(args=args)
    node = VisionLanguageGrounder()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Step-by-Step Implementation Guide

1. **Set Up Audio Pipeline**: Configure ROS 2 audio input from microphone or audio interface. Use audio_common packages or direct ALSA/PulseAudio. Test audio quality (sample rate, bit depth). [Citation: https://wiki.ros.org/audio_common]

2. **Integrate Speech Recognition**: Install Whisper (local) or configure cloud STT API (Google/Azure). Set up low-latency streaming mode. Implement silence detection for automatic speech endpoint detection. [Citation: https://arxiv.org/abs/2010.14094]

3. **Add Language Model**: Configure LLM API (OpenAI, Anthropic, local Llama). Design system prompts that map language to robot actions. Implement context caching for faster responses. [Citation: https://arxiv.org/abs/2303.08774]

4. **Implement Action Mapping**: Create structured action definitions with parameters. Build parser converting LLM output to executable robot commands. Add safety checks and confirmation for critical actions. [Citation: https://arxiv.org/abs/2307.08995]

5. **Integrate Vision (Optional)**: Add CLIP or multimodal LLM for grounded understanding. Reference vision in commands: "pick up the object on the table". Validate language understanding with vision context. [Citation: https://arxiv.org/abs/2305.13583]

### Summary

- Voice-to-Action systems enable intuitive natural language control of humanoid robots
- Speech-to-text (Whisper) converts voice to text with minimal latency
- Large language models (Claude, GPT-4) understand intent and ground commands in robot capabilities
- Action mapping translates semantic representations to executable robot commands
- Vision-language models enable grounded understanding of spatial references
- End-to-end latency management (< 2 seconds) ensures responsive interaction
- Confidence thresholds and user confirmation prevent errors from misrecognition
- Real-time voice loops enable continuous dialogue and task refinement

### Glossary

- **STT (Speech-to-Text)**: Converting audio to text using acoustic and language models
- **LLM (Large Language Model)**: Neural network trained on massive text for language understanding
- **In-Context Learning**: Few-shot examples provided in prompt to steer model behavior
- **Action Grounding**: Mapping semantic concepts to executable robot actions
- **VLM (Vision-Language Model)**: Joint embeddings understanding images and text together
- **Prompt Engineering**: Designing prompts to elicit desired model behaviors
- **Latency**: Delay from speech input to robot action execution

### References

- [Vision-Language-Action Models](https://arxiv.org/abs/2405.04254)
- [Large Language Models](https://arxiv.org/abs/2303.08774)
- [Action Grounding](https://arxiv.org/abs/2307.08995)
- [Vision-Language Models](https://arxiv.org/abs/2305.13583)
- [Whisper Speech Recognition](https://arxiv.org/abs/2212.04356)
