/**
 * ModuleCard Component
 * Displays a module with name, description, and chapter links
 */

import React from 'react';
import Link from '@docusaurus/Link';
import styles from './ModuleCard.module.css';

export default function ModuleCard({ module_id, name, description, chapters }) {
  return (
    <div className={`${styles.moduleCard} module-card`}>
      <div className={styles.moduleCardHeader}>
        <h3 className={`${styles.moduleCardTitle} module-card-title`}>
          {name}
        </h3>
      </div>
      <p className={`${styles.moduleCardDescription} module-card-description`}>
        {description}
      </p>
      <div className={styles.chapterList}>
        <h4 className={styles.chapterListTitle}>Chapters:</h4>
        <ul className={styles.chapterItems}>
          {chapters.map((chapter, index) => (
            <li key={index} className={styles.chapterItem}>
              <Link
                to={chapter.link}
                className={`${styles.chapterLink} chapter-link`}
              >
                <span className={styles.chapterNumber}>
                  {chapter.number}
                </span>
                <span className={styles.chapterTitle}>
                  {chapter.title}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
