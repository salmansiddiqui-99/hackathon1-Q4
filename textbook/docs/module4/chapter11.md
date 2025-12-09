## Cognitive Planning and Reasoning

### Introduction

Cognitive planning and reasoning systems enable humanoid robots to decompose high-level goals into sequences of executable tasks, reason about preconditions and effects, and adapt plans dynamically when facing uncertainties. [Citation: https://arxiv.org/abs/2203.14100] Task planning bridges the gap between language-based goals and low-level motion control. This chapter covers symbolic planning (PDDL), hierarchical task networks (HTNs), learning from demonstrations, and online planning strategies for humanoid robot autonomy.

### Learning Objectives

- Formalize robot tasks using PDDL (Planning Domain Definition Language)
- Design hierarchical task networks decomposing complex goals into primitives
- Implement backward and forward chaining search for task planning
- Learn task models from demonstrations using inverse reinforcement learning
- Perform cost estimation and plan optimization
- Handle temporal constraints and concurrent tasks
- Integrate planning with reactive control for dynamic environments
- Evaluate plan robustness and failure recovery strategies

### Core Concepts

#### Planning Domain Definition Language (PDDL)

PDDL is a standardized language for specifying planning problems: actions (preconditions, effects), objects, and goals. [Citation: https://arxiv.org/abs/1305.5924] PDDL enables using off-the-shelf planners (Fast Downward, FFHA). For humanoid robots, PDDL models describe manipulation actions: "pick(object, location)" has preconditions (robot at location, object visible) and effects (holding object, gripper occupied).

#### Hierarchical Task Networks (HTN)

HTN planning decomposes abstract tasks into subtasks recursively until reaching primitive actions executable by robot. [Citation: https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.5.1373] HTN captures domain knowledge: high-level task "prepare dinner" decomposes into "cook pasta" and "make sauce", each further decomposable. HTN is faster than searching flat action spaces and naturally maps to human task structures.

#### Inverse Reinforcement Learning (IRL)

IRL learns task models from human demonstrations by inferring reward functions that explain observed behavior. [Citation: https://arxiv.org/abs/1905.06675] Maximum entropy IRL finds reward functions most consistent with demonstrations. For humanoids, IRL learns manipulation preferences: why did demonstrator grasp object at that location? Learned rewards guide robot behavior on new tasks.

#### Temporal Planning and Constraints

Real-world tasks often have temporal constraints: deadlines, durations, ordering constraints. [Citation: https://arxiv.org/abs/1703.02193] Temporal planners reason about action durations and scheduling constraints. For humanoids: "walk to table (5s), pick cup (2s), walk to sink (5s)" must respect timing. Concurrent task execution allows multitasking where possible.

#### Online Planning and Replanning

Online planning recomputes plans as new information arrives, enabling reactive behavior in dynamic environments. [Citation: https://arxiv.org/abs/2004.14951] Replanning detects when current plan becomes invalid and computes alternatives. For humanoids navigating human environments, continuous replanning adapts to moving obstacles and dynamic human activity.

### Practical Examples

#### Example 1: PDDL Domain Definition for Humanoid Manipulation

```lisp
; humanoid_domain.pddl - Manipulation tasks for humanoid robot

(define (domain humanoid-manipulation)
  (:requirements :typing :durative-actions :equality)

  (:types
    robot location object - thing
    movable_object - object
    gripper - object
  )

  (:predicates
    ; State properties
    (at ?r:robot ?l:location)
    (holding ?r:robot ?o:movable_object)
    (on ?o:movable_object ?l:location)
    (gripper_free ?r:robot)
    (visible ?o:movable_object ?l:location)
    (surface_clear ?l:location)
    (gripper_occupied ?r:robot)
  )

  ; Action 1: Move robot to location
  (:durative-action move
    :parameters (?r:robot ?from:location ?to:location)
    :duration (= ?duration 5)  ; 5 seconds per move
    :condition (and
      (at start (at ?r ?from))
      (at start (not (= ?from ?to)))
    )
    :effect (and
      (at start (not (at ?r ?from)))
      (at end (at ?r ?to))
    )
  )

  ; Action 2: Pick up object
  (:durative-action pickup
    :parameters (?r:robot ?o:movable_object ?l:location)
    :duration (= ?duration 2)  ; 2 seconds to pick up
    :condition (and
      (at start (at ?r ?l))
      (at start (on ?o ?l))
      (at start (visible ?o ?l))
      (at start (gripper_free ?r))
    )
    :effect (and
      (at start (not (gripper_free ?r)))
      (at start (not (on ?o ?l)))
      (at end (holding ?r ?o))
      (at end (gripper_occupied ?r))
    )
  )

  ; Action 3: Place object
  (:durative-action place
    :parameters (?r:robot ?o:movable_object ?l:location)
    :duration (= ?duration 2)
    :condition (and
      (at start (at ?r ?l))
      (at start (holding ?r ?o))
      (at start (surface_clear ?l))
      (at start (gripper_occupied ?r))
    )
    :effect (and
      (at end (on ?o ?l))
      (at end (not (holding ?r ?o)))
      (at end (gripper_free ?r))
      (at end (not (gripper_occupied ?r)))
    )
  )

  ; Action 4: Push object to location
  (:durative-action push
    :parameters (?r:robot ?o:movable_object ?from:location ?to:location)
    :duration (= ?duration 8)
    :condition (and
      (at start (at ?r ?from))
      (at start (on ?o ?from))
      (at start (gripper_free ?r))
    )
    :effect (and
      (at start (not (on ?o ?from)))
      (at end (on ?o ?to))
    )
  )

  ; Action 5: Perception - look for object
  (:durative-action look
    :parameters (?r:robot ?o:movable_object ?l:location)
    :duration (= ?duration 1)
    :condition (at start (at ?r ?l))
    :effect (at end (visible ?o ?l))
  )
)
```

#### Example 2: Problem Instance (Goal and Initial State)

```lisp
; humanoid_problem.pddl - Specific problem instance

(define (problem humanoid-task-1)
  (:domain humanoid-manipulation)

  (:objects
    robot1 - robot
    kitchen living_room - location
    red_cup blue_cup table - movable_object
  )

  (:init
    (at robot1 living_room)
    (on red_cup living_room)
    (on blue_cup kitchen)
    (gripper_free robot1)
    (surface_clear kitchen)
  )

  (:goal
    (and
      (on red_cup kitchen)
      (on blue_cup living_room)
    )
  )

  (:metric minimize (total-time))
)
```

This describes the problem: move red cup to kitchen and blue cup to living room. The planner finds an optimal sequence of actions.

#### Example 3: HTN Planning in Python

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
from typing import List, Dict, Any

class HTNPlanner(Node):
    """Hierarchical Task Network planner for humanoid robot."""

    def __init__(self):
        super().__init__('htn_planner')

        # Subscribe to task goals
        self.goal_sub = self.create_subscription(
            String,
            '/task_goal',
            self.goal_callback,
            10
        )

        # Publish task plan
        self.plan_pub = self.create_publisher(
            String,
            '/task_plan',
            10
        )

        # Define task decompositions
        self.methods = {
            'prepare_table': [
                {
                    'name': 'prepare_table_v1',
                    'preconditions': [],
                    'subtasks': ['clear_table', 'set_place_settings', 'add_centerpiece']
                }
            ],
            'clear_table': [
                {
                    'name': 'clear_table_v1',
                    'preconditions': ['table_exists'],
                    'subtasks': ['go_to_table', 'pickup_items', 'move_items_to_sink']
                }
            ],
            'pickup_items': [
                {
                    'name': 'pickup_items_v1',
                    'preconditions': [],
                    'subtasks': [
                        ('pickup_object', {'object': 'plate'}),
                        ('pickup_object', {'object': 'cup'}),
                        ('pickup_object', {'object': 'napkin'})
                    ]
                }
            ],
            'go_to': [
                {
                    'name': 'go_to_v1',
                    'preconditions': [],
                    'subtasks': [('move_robot', {})]  # Primitive
                }
            ],
            'move_items_to_sink': [
                {
                    'name': 'move_to_sink_v1',
                    'preconditions': ['sink_exists'],
                    'subtasks': [
                        ('go_to', {'location': 'sink'}),
                        ('place_object', {})
                    ]
                }
            ]
        }

        # Primitive tasks (cannot be further decomposed)
        self.primitives = {
            'move_robot', 'pickup_object', 'place_object', 'speak'
        }

        self.get_logger().info("HTN Planner initialized")

    def goal_callback(self, msg):
        """Receive task goal and generate plan."""
        try:
            goal = json.loads(msg.data)
            task = goal.get('task')
            params = goal.get('parameters', {})

            self.get_logger().info(f"Planning task: {task}({params})")

            # Generate HTN plan
            plan = self.plan_task(task, params)

            if plan:
                self.get_logger().info(f"Plan found: {plan}")

                # Publish plan
                plan_msg = String()
                plan_msg.data = json.dumps({
                    'task': task,
                    'plan': plan
                })
                self.plan_pub.publish(plan_msg)
            else:
                self.get_logger().warn(f"No plan found for {task}")

        except Exception as e:
            self.get_logger().error(f"Planning error: {e}")

    def plan_task(self, task: str, params: Dict[str, Any] = None) -> List:
        """Recursively decompose task into primitive actions."""
        if params is None:
            params = {}

        # Check if primitive
        if task in self.primitives:
            return [(task, params)]

        # Check if decomposable
        if task not in self.methods:
            return None

        # Try each decomposition method
        for method in self.methods[task]:
            # Check preconditions (simplified)
            if self.check_preconditions(method['preconditions']):
                # Recursively plan subtasks
                plan = []
                success = True

                for subtask_spec in method['subtasks']:
                    if isinstance(subtask_spec, tuple):
                        subtask, subtask_params = subtask_spec
                    else:
                        subtask = subtask_spec
                        subtask_params = {}

                    subtask_plan = self.plan_task(subtask, subtask_params)

                    if subtask_plan is None:
                        success = False
                        break

                    plan.extend(subtask_plan)

                if success:
                    return plan

        return None  # No valid decomposition found

    def check_preconditions(self, preconditions: List[str]) -> bool:
        """Check if preconditions are met (simplified)."""
        # In real system, query world state
        return True

def main(args=None):
    rclpy.init(args=args)
    node = HTNPlanner()

    # Example goal
    goal = {
        'task': 'prepare_table',
        'parameters': {}
    }

    msg = String()
    msg.data = json.dumps(goal)
    node.goal_callback(msg)

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

#### Example 4: Learning Task Models from Demonstrations

```python
import numpy as np
from typing import List, Tuple
import json

class InverseReinforcementLearning:
    """Learn reward function from expert demonstrations."""

    def __init__(self, state_dim: int, n_features: int):
        self.state_dim = state_dim
        self.n_features = n_features
        self.weights = np.random.randn(n_features)

    def extract_features(self, state: np.ndarray) -> np.ndarray:
        """Extract features from state (simplified)."""
        # Features: distance to goal, holding object, gripper_free, etc.
        return np.array([
            np.linalg.norm(state[:2]),      # Distance to goal
            state[2] if len(state) > 2 else 0,  # Holding item
            state[3] if len(state) > 3 else 1   # Gripper free
        ])

    def compute_reward(self, state: np.ndarray) -> float:
        """Compute reward as weighted combination of features."""
        features = self.extract_features(state)
        return np.dot(self.weights, features)

    def learn_from_demos(self, demonstrations: List[List[Tuple[np.ndarray, np.ndarray]]]):
        """
        Learn weights from expert demonstrations.
        demonstrations: List of trajectories, each trajectory is list of (state, action) pairs.
        """
        n_demos = len(demonstrations)
        n_iterations = 100
        learning_rate = 0.01

        for iteration in range(n_iterations):
            # Compute feature expectations from expert demonstrations
            expert_features = np.zeros(self.n_features)
            for traj in demonstrations:
                for state, action in traj:
                    expert_features += self.extract_features(state)
            expert_features /= (n_demos * len(demonstrations[0]))

            # Compute feature expectations from current policy
            # (simplified: use random rollouts)
            policy_features = np.zeros(self.n_features)
            for _ in range(n_demos):
                state = np.random.randn(self.state_dim)
                for _ in range(10):
                    policy_features += self.extract_features(state)
                    state += np.random.randn(self.state_dim) * 0.1
            policy_features /= (n_demos * 10)

            # Update weights to match expert feature expectations
            feature_diff = expert_features - policy_features
            self.weights += learning_rate * feature_diff

            if iteration % 20 == 0:
                print(f"Iteration {iteration}: weights = {self.weights}")

        return self.weights

# Example usage
irl = InverseReinforcementLearning(state_dim=4, n_features=3)

# Synthetic expert demonstrations
expert_trajs = [
    [
        (np.array([2.0, 0.0, 1.0, 0.0]), np.array([1, 0])),  # At distance, holding item, at goal
        (np.array([1.0, 0.0, 1.0, 0.0]), np.array([1, 0])),
        (np.array([0.0, 0.0, 1.0, 1.0]), np.array([-1, 0]))  # Place item
    ]
    for _ in range(5)
]

learned_weights = irl.learn_from_demos(expert_trajs)
print(f"Learned weights: {learned_weights}")

# Test learned reward
test_state = np.array([0.5, 0.0, 1.0, 0.0])
reward = irl.compute_reward(test_state)
print(f"Reward for test state: {reward:.3f}")
```

### Step-by-Step Implementation Guide

1. **Model Domain in PDDL**: Write PDDL domain with robot actions (move, pickup, place) and their preconditions/effects. Define object types (robot, location, object). Test domain with planner. [Citation: https://arxiv.org/abs/1305.5924]

2. **Design HTN Decompositions**: Create method definitions for complex tasks. Decompose abstract tasks into subtasks recursively until reaching primitives. Implement HTN planner (backward chaining from goal). [Citation: https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.5.1373]

3. **Integrate Planner with Robot**: Create ROS 2 nodes that translate PDDL plans to robot actions. Subscribe to goals, generate plans, publish executable action sequences. Validate plans in simulation. [Citation: https://navigation.ros.org/setup_guides/index.html]

4. **Learn from Demonstrations**: Collect expert demonstrations of humanoid performing tasks. Apply IRL to infer reward functions. Use learned rewards to score candidate plans. [Citation: https://arxiv.org/abs/1905.06675]

5. **Implement Replanning**: Monitor plan execution. Detect failures (action preconditions not met). Trigger replanning when plan becomes invalid. Maintain current goal and constraints across replanning. [Citation: https://arxiv.org/abs/2004.14951]

### Summary

- Planning bridges high-level goals and low-level control for humanoid autonomy
- PDDL standardizes action modeling enabling use of off-the-shelf planners
- Hierarchical Task Networks decompose complex goals into manageable subtasks
- Inverse Reinforcement Learning infers preferences from expert demonstrations
- Temporal planning handles action durations and scheduling constraints
- Online replanning enables adaptive behavior in dynamic environments
- Plan quality metrics (cost, duration, robustness) guide plan selection
- Planning under uncertainty uses contingency handling and reactive strategies

### Glossary

- **PDDL**: Planning Domain Definition Language for specifying actions, preconditions, and effects
- **HTN**: Hierarchical Task Network decomposing abstract tasks recursively
- **IRL**: Inverse Reinforcement Learning inferring reward function from demonstrations
- **Precondition**: State property required for action execution
- **Effect**: State change resulting from action execution
- **Grounding**: Substituting concrete objects for variables in action schema
- **Replanning**: Recomputing plan when current plan becomes invalid

### References

- [Task Planning with PDDL](https://arxiv.org/abs/1305.5924)
- [Hierarchical Task Networks](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.5.1373)
- [Inverse Reinforcement Learning](https://arxiv.org/abs/1905.06675)
- [Temporal Planning](https://arxiv.org/abs/1703.02193)
- [Online Planning and Replanning](https://arxiv.org/abs/2004.14951)
