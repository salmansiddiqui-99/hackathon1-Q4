#!/usr/bin/env python3
"""
Simple Chapter Generation Script - Generates all 12 chapters using Claude API
"""

import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

from anthropic import Anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Chapter specifications with detailed descriptions
CHAPTERS_SPEC = [
    # Module 1: ROS 2
    {
        "module_id": "module1",
        "chapter_number": 1,
        "module_name": "Module 1: The Robotic Nervous System (ROS 2)",
        "title": "ROS 2 Basics: Architecture and Communication",
        "description": "Understand ROS 2 fundamentals, pub/sub architecture, and workspace setup for robotics development",
    },
    {
        "module_id": "module1",
        "chapter_number": 2,
        "module_name": "Module 1: The Robotic Nervous System (ROS 2)",
        "title": "Humanoid Control with ROS 2",
        "description": "Learn how to control humanoid robots using ROS 2 services, actions, and state machines for bipedal locomotion",
    },
    {
        "module_id": "module1",
        "chapter_number": 3,
        "module_name": "Module 1: The Robotic Nervous System (ROS 2)",
        "title": "URDF and Robot Descriptions",
        "description": "Define robot structure using URDF (Unified Robot Description Format), joints, links, and forward kinematics",
    },
    # Module 2: Gazebo & Unity
    {
        "module_id": "module2",
        "chapter_number": 4,
        "module_name": "Module 2: Simulation Environments (Gazebo & Unity)",
        "title": "Gazebo Simulation Fundamentals",
        "description": "Set up realistic physics simulations for humanoid robots using Gazebo with gravity, collisions, and dynamics",
    },
    {
        "module_id": "module2",
        "chapter_number": 5,
        "module_name": "Module 2: Simulation Environments (Gazebo & Unity)",
        "title": "Sensor Simulation and Perception",
        "description": "Simulate cameras, LiDAR, IMU sensors and implement perception pipelines in simulated environments",
    },
    {
        "module_id": "module2",
        "chapter_number": 6,
        "module_name": "Module 2: Simulation Environments (Gazebo & Unity)",
        "title": "Unity for Robot Visualization",
        "description": "Visualize simulated humanoid robots in Unity game engine with real-time rendering and interactive controls",
    },
    # Module 3: NVIDIA Isaac
    {
        "module_id": "module3",
        "chapter_number": 7,
        "module_name": "Module 3: AI-Powered Simulation (NVIDIA Isaac)",
        "title": "NVIDIA Isaac Sim for Humanoids",
        "description": "Use NVIDIA Isaac Sim for high-performance physics simulation and digital twins with GPU acceleration",
    },
    {
        "module_id": "module3",
        "chapter_number": 8,
        "module_name": "Module 3: AI-Powered Simulation (NVIDIA Isaac)",
        "title": "Isaac Perception and AI Models",
        "description": "Integrate computer vision models, object detection, and semantic segmentation in Isaac Sim",
    },
    {
        "module_id": "module3",
        "chapter_number": 9,
        "module_name": "Module 3: AI-Powered Simulation (NVIDIA Isaac)",
        "title": "Nav2 and Bipedal Navigation",
        "description": "Implement autonomous navigation for bipedal humanoid robots using Nav2 stack and motion planning",
    },
    # Module 4: VLA & Capstone
    {
        "module_id": "module4",
        "chapter_number": 10,
        "module_name": "Module 4: Vision-Language Action Systems",
        "title": "Voice and Language Action (VLA) Systems",
        "description": "Build voice-to-action systems for humanoid robots using large language models and speech recognition",
    },
    {
        "module_id": "module4",
        "chapter_number": 11,
        "module_name": "Module 4: Vision-Language Action Systems",
        "title": "Cognitive Planning and Reasoning",
        "description": "Implement task planning algorithms and reasoning systems for complex humanoid robot behaviors",
    },
    {
        "module_id": "module4",
        "chapter_number": 12,
        "module_name": "Module 4: Vision-Language Action Systems",
        "title": "Capstone: Autonomous Humanoid System",
        "description": "Build a complete autonomous humanoid system integrating perception, planning, control, and language understanding",
    },
]

# Detailed prompt template for chapter generation
PROMPT_TEMPLATE = """You are an expert AI assistant generating professional technical textbook chapters on Physical AI and Humanoid Robotics.

CRITICAL REQUIREMENTS:
1. ZERO HALLUCINATIONS: Every claim must be verifiable from published documentation. If unsure, cite the source.
2. CITATIONS REQUIRED: Use [Citation: URL] format after every technical claim.
3. CODE VALIDITY: All code examples must be syntactically correct and executable.
4. STRUCTURE: Follow the exact format below.

CHAPTER CONTEXT:
Module: {module_name}
Chapter: {chapter_number}/12
Title: {title}
Description: {description}

TARGET AUDIENCE: Engineering students, roboticists, AI practitioners with basic Python knowledge

OUTPUT FORMAT (EXACT):

## {title}

### Introduction
Write 2-3 sentences introducing the chapter topic and relevance to Physical AI and humanoid robotics.
Include 1-2 citations to authoritative sources (ROS docs, papers, official guides).

### Learning Objectives
- Objective 1: Specific, measurable learning outcome
- Objective 2: Specific, measurable learning outcome
- Objective 3: Specific, measurable learning outcome
- Objective 4: Specific, measurable learning outcome
- Objective 5: Specific, measurable learning outcome

### Core Concepts

#### Concept 1: [Name]
Explanation with [Citation: source URL]. This concept explains...

#### Concept 2: [Name]
Explanation with [Citation: source URL]. This is important because...

#### Concept 3: [Name]
Explanation with [Citation: source URL]. For humanoid robots...

#### Concept 4: [Name]
Explanation with [Citation: source URL]. The technical details...

### Practical Examples

#### Example 1: [Title]
Brief description of what this example demonstrates.

```python
# Syntactically correct Python code
# Include imports, complete implementations
# Make it runnable
```

Explanation of the code and how it relates to the concepts above.

#### Example 2: [Title]
Brief description.

```bash
# Valid bash/shell commands if applicable
# Or more Python code with different use case
```

Explanation of this example.

#### Example 3: [Title]
Brief description.

```python
# Another complete, working example
# Different aspect of the topic
```

Explanation connecting to learning objectives.

### Step-by-Step Implementation Guide

1. **First Step**: Detailed instructions for setup or first task. [Citation: if applicable]
2. **Second Step**: How to accomplish the next part. [Citation: if applicable]
3. **Third Step**: Complete the implementation. [Citation: if applicable]
4. **Verification**: How to verify the implementation works correctly.

### Summary

Key takeaways from this chapter:
- Takeaway 1: Main learning point
- Takeaway 2: Practical application
- Takeaway 3: Relevance to humanoid robotics
- Takeaway 4: Next steps
- Takeaway 5: Recap of core concepts

### Glossary

- **Term 1**: Definition (10-20 words)
- **Term 2**: Definition (10-20 words)
- **Term 3**: Definition (10-20 words)
- **Term 4**: Definition (10-20 words)
- **Term 5**: Definition (10-20 words)
- **Term 6**: Definition (10-20 words)
- **Term 7**: Definition (10-20 words)

### References

- [Official Title](https://official.url)
- [Paper/Documentation](https://paper.url)
- [Tutorial/Guide](https://tutorial.url)
- [API Documentation](https://api.url)

---

QUALITY REQUIREMENTS:
✓ Total length: 3000-5000 tokens (~12-20 pages)
✓ Code examples: 2-4 complete, executable examples
✓ Citations: Minimum 8 unique authoritative sources
✓ Citations in format: [Citation: https://example.com/path]
✓ All concepts explained clearly for intermediate level
✓ All code is syntactically valid for Python/Bash
✓ Every technical statement has a citation nearby
✓ Focus on humanoid robotics applications

RESPONSE FORMAT:
- Output ONLY the Markdown chapter content
- Start with ## {title}
- No preamble, no explanations, no meta-commentary
- Ensure proper [Citation: ...] format throughout"""

client = Anthropic(api_key="") # Will be set from env


async def generate_chapter(spec: dict) -> tuple[int, str | None, str | None]:
    """Generate a single chapter."""
    chapter_num = spec["chapter_number"]
    title = spec["title"]
    module_name = spec["module_name"]
    description = spec["description"]

    try:
        logger.info(f"[Chapter {chapter_num}] Generating: {title}")

        # Format the prompt with chapter-specific details
        prompt = PROMPT_TEMPLATE.format(
            module_name=module_name,
            chapter_number=chapter_num,
            title=title,
            description=description,
        )

        # Call Claude API with Opus for high quality
        response = client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text

        # Validate response
        if not content.strip().startswith("##"):
            logger.warning(f"[Chapter {chapter_num}] Content doesn't start with ##, attempting recovery...")
            content = f"## {title}\n\n{content}"

        if "[Citation:" not in content:
            logger.warning(f"[Chapter {chapter_num}] No citations found - may be hallucinated content!")

        logger.info(f"[Chapter {chapter_num}] ✓ Generated successfully ({len(content)} chars)")
        return chapter_num, content, None

    except Exception as e:
        logger.error(f"[Chapter {chapter_num}] ✗ Failed: {str(e)}")
        return chapter_num, None, str(e)


async def save_chapter(spec: dict, content: str) -> bool:
    """Save chapter to filesystem."""
    try:
        # Parse module_id to get module number
        module_num = int(spec["module_id"].replace("module", ""))
        chapter_num = spec["chapter_number"]
        title = spec["title"]

        # Create module directory
        module_dir = Path("textbook/docs") / f"module{module_num}"
        module_dir.mkdir(parents=True, exist_ok=True)

        # Create filename
        sanitized_title = (
            title.lower()
            .replace(" ", "-")
            .replace(":", "")
            .replace("&", "and")
            .replace("/", "-")
        )[:50].rstrip("-")

        filename = f"{chapter_num:02d}-{sanitized_title}.md"
        filepath = module_dir / filename

        # Write file
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"[Chapter {chapter_num}] ✓ Saved to {filepath}")
        return True

    except Exception as e:
        logger.error(f"[Chapter {chapter_num}] ✗ Save failed: {str(e)}")
        return False


async def main():
    """Generate all 12 chapters."""
    logger.info("=" * 80)
    logger.info("GENERATING ALL 12 CHAPTERS FOR PHYSICAL AI TEXTBOOK")
    logger.info("=" * 80)
    logger.info(f"Start time: {datetime.utcnow().isoformat()}")
    logger.info(f"Using Claude Opus 4.5 for high-quality content generation")

    successful = 0
    failed = 0

    for spec in CHAPTERS_SPEC:
        chapter_num, content, error = await generate_chapter(spec)

        if content:
            # Save to filesystem
            if await save_chapter(spec, content):
                successful += 1
                logger.info(f"[Chapter {chapter_num}] COMPLETE\n")
            else:
                failed += 1
        else:
            failed += 1
            logger.error(f"[Chapter {chapter_num}] SKIPPED - {error}\n")

    # Summary
    logger.info("=" * 80)
    logger.info("GENERATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"✓ Successful: {successful}/12")
    logger.info(f"✗ Failed: {failed}/12")
    logger.info(f"End time: {datetime.utcnow().isoformat()}")
    logger.info("=" * 80)

    return successful == 12


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
