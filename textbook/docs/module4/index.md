---
id: module4-index
title: Module 4 - Vision-Language-Action & Capstone
sidebar_label: Overview
sidebar_position: 0
---

# Module 4: Vision-Language-Action Models & Capstone Project

## Overview

Welcome to Module 4 - the culminating module of the Physical AI & Humanoid Robotics Course! In this module, you'll explore **Vision-Language-Action (VLA) models** - the cutting edge of AI-powered robot control. VLA models combine computer vision, natural language understanding, and robot actions into end-to-end learning systems.

## What You'll Learn

This module covers the latest advances in embodied AI:

- **VLA Architecture**: How vision, language, and action are unified in transformer-based models
- **OpenVLA**: Open-source VLA model trained on diverse robot tasks
- **RT-2 & RT-X**: Google's Robotics Transformer models for generalist manipulation
- **Fine-tuning VLA**: Adapting pre-trained models to custom tasks and robots
- **Deployment**: Running VLA models on real hardware (NVIDIA Jetson, edge devices)
- **Capstone Project**: Build an end-to-end Physical AI system integrating all course concepts

## Learning Outcomes

By the end of this module, you will be able to:

1. Understand the architecture and training of Vision-Language-Action models
2. Set up and run OpenVLA for robot manipulation tasks
3. Fine-tune VLA models on custom datasets using LoRA/QLoRA
4. Integrate VLA models with ROS 2 and Isaac Sim
5. Deploy VLA inference pipelines on GPU hardware
6. Design and implement a capstone project combining ROS 2, simulation, and AI
7. Evaluate model performance on real robot tasks
8. Understand the future directions of Physical AI and embodied intelligence

## Prerequisites

- Completion of Module 1 (ROS 2 Fundamentals)
- Completion of Module 2 (Simulation)
- Completion of Module 3 (NVIDIA Isaac Platform)
- **Recommended**: Basic deep learning knowledge (PyTorch, transformers)
- **Hardware**: NVIDIA GPU with 12GB+ VRAM (for fine-tuning)

## Module Structure

This module is organized into three chapters:

1. **Chapter 10: VLA Models (OpenVLA, RT-2)** - Architecture and inference
2. **Chapter 11: Fine-tuning for Custom Tasks** - Adapting models to your robot
3. **Chapter 12: Capstone Project** - Build your own Physical AI system

## Estimated Time

- **Total**: 20-24 hours
- **Chapter 10**: 6-7 hours
- **Chapter 11**: 6-7 hours
- **Chapter 12**: 8-10 hours (project)

## Tools & Versions

- **OpenVLA**: Latest release from openvla.github.io
- **PyTorch**: 2.0+ with CUDA support
- **Hugging Face Transformers**: Latest version
- **ROS 2**: Humble Hawksbill (LTS)
- **Isaac Sim**: 2023.1.1+ (for simulation testing)

## Hardware Requirements

- **GPU**: NVIDIA GPU with 12GB+ VRAM (RTX 3090, A5000, or higher recommended)
- **RAM**: 32GB minimum (64GB recommended for fine-tuning)
- **Storage**: 100GB+ free space (for models and datasets)
- **OS**: Ubuntu 22.04 LTS

## Capstone Project Options

Choose one of the following capstone projects or design your own:

1. **Language-Guided Robot Manipulation**: Build a system that follows natural language commands to pick and place objects
2. **Vision-based Navigation**: Create a robot that navigates using VLA-based visual reasoning
3. **Humanoid Task Execution**: Use GR00T + VLA for humanoid robot task planning
4. **Custom VLA Fine-tuning**: Fine-tune OpenVLA on a custom robot/task dataset

## Getting Started

Ready to explore the future of robotics? Start with [Chapter 10: VLA Models (OpenVLA, RT-2)](./chapter10.md) to understand and run state-of-the-art VLA models!

---

**Previous**: [Module 3 Overview ←](../module3/index.md) | **Next**: [Chapter 10 - VLA Models →](./chapter10.md)
