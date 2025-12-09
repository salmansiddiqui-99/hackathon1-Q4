/**
 * HeroSection Component
 * Full-width hero section with title, tagline, and CTA buttons
 */

import React from 'react';
import Link from '@docusaurus/Link';
import styles from './HeroSection.module.css';

export default function HeroSection() {
  return (
    <section className={`${styles.hero} hero`}>
      <div className={styles.heroContent}>
        <h1 className={`${styles.heroTitle} hero-title`}>
          Physical AI & Humanoid Robotics Course
        </h1>
        <p className={`${styles.heroSubtitle} hero-subtitle`}>
          Master the intersection of AI and robotics - from ROS 2 to Vision-Language-Action models
        </p>
        <div className={`${styles.heroButtons} hero-buttons`}>
          <Link
            className={`button button--primary button--lg ${styles.heroButton} hero-button`}
            to="/docs/intro"
          >
            Start Learning
          </Link>
          <Link
            className={`button button--secondary button--lg ${styles.heroButton} hero-button`}
            href="https://github.com/yourname/physical_ai_book"
            target="_blank"
            rel="noopener noreferrer"
          >
            View on GitHub
          </Link>
        </div>
      </div>
    </section>
  );
}
