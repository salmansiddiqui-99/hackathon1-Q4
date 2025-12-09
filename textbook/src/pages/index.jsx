/**
 * Home Page for Physical AI Textbook
 * Displays hero section and module cards
 */

import React from 'react';
import Layout from '@theme/Layout';
import HeroSection from '@site/src/components/HeroSection';
import ModuleCard from '@site/src/components/ModuleCard';
import ChatbotWidget from '@site/src/components/ChatbotWidget';
import styles from './index.module.css';

const modules = [
  {
    module_id: 1,
    name: 'Module 1: ROS 2 Fundamentals',
    description: 'Master the Robot Operating System 2 - the backbone of modern robotics. Learn nodes, topics, services, and how to build modular robot applications.',
    chapters: [
      { number: 'Ch 1', title: 'ROS 2 Architecture & Setup', link: '/docs/module1/chapter1' },
      { number: 'Ch 2', title: 'Nodes, Topics & Messages', link: '/docs/module1/chapter2' },
      { number: 'Ch 3', title: 'Services, Actions & Parameters', link: '/docs/module1/chapter3' },
    ],
  },
  {
    module_id: 2,
    name: 'Module 2: Simulation with Gazebo & Isaac Sim',
    description: 'Dive into physics-based simulation for testing and training robots in virtual environments before deploying to hardware.',
    chapters: [
      { number: 'Ch 4', title: 'Gazebo Classic & Fortress', link: '/docs/module2/chapter4' },
      { number: 'Ch 5', title: 'URDF & Robot Modeling', link: '/docs/module2/chapter5' },
      { number: 'Ch 6', title: 'Sensor Simulation & Testing', link: '/docs/module2/chapter6' },
    ],
  },
  {
    module_id: 3,
    name: 'Module 3: NVIDIA Isaac Platform',
    description: 'Leverage NVIDIA\'s GPU-accelerated tools for AI-powered robotics, including Isaac Sim, Isaac ROS, and GEM models.',
    chapters: [
      { number: 'Ch 7', title: 'Isaac Sim & Replicator', link: '/docs/module3/chapter7' },
      { number: 'Ch 8', title: 'Isaac ROS Perception', link: '/docs/module3/chapter8' },
      { number: 'Ch 9', title: 'GR00T & Humanoid Foundation', link: '/docs/module3/chapter9' },
    ],
  },
  {
    module_id: 4,
    name: 'Module 4: Vision-Language-Action & Capstone',
    description: 'Explore cutting-edge VLA models that combine vision, language, and action for intelligent robot control.',
    chapters: [
      { number: 'Ch 10', title: 'VLA Models (OpenVLA, RT-2)', link: '/docs/module4/chapter10' },
      { number: 'Ch 11', title: 'Fine-tuning for Custom Tasks', link: '/docs/module4/chapter11' },
      { number: 'Ch 12', title: 'Capstone Project', link: '/docs/module4/chapter12' },
    ],
  },
];

export default function Home() {
  return (
    <Layout
      title="Physical AI & Humanoid Robotics Course"
      description="Master the intersection of AI and robotics - from ROS 2 to Vision-Language-Action models"
    >
      <HeroSection />

      <main className={styles.main}>
        <section className={styles.modulesSection}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>Course Modules</h2>
            <p className={styles.sectionSubtitle}>
              Four comprehensive modules covering the full spectrum of Physical AI and Humanoid Robotics
            </p>
          </div>

          <div className={`${styles.modulesGrid} modules-grid`}>
            {modules.map((module) => (
              <ModuleCard
                key={module.module_id}
                module_id={module.module_id}
                name={module.name}
                description={module.description}
                chapters={module.chapters}
              />
            ))}
          </div>
        </section>
      </main>

      <ChatbotWidget />
    </Layout>
  );
}
