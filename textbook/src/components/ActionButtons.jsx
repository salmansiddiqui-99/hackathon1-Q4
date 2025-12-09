/**
 * ActionButtons Component (Stub)
 * Provides chapter-level actions like personalization and translation
 * Will be functional in future phases
 */

import React from 'react';
import styles from './ActionButtons.module.css';

export default function ActionButtons({ chapterTitle = '' }) {
  const handlePersonalize = () => {
    alert('Personalization feature coming soon! This will adapt content to your learning style.');
  };

  const handleTranslate = () => {
    alert('Translation to Urdu coming soon! This will translate the chapter to Urdu.');
  };

  return (
    <div className={styles.actionButtonsContainer}>
      <div className={styles.actionButtons}>
        <button
          className={`${styles.actionButton} ${styles.personalizeButton}`}
          onClick={handlePersonalize}
          title="Personalize this chapter to your learning style"
        >
          <svg
            className={styles.buttonIcon}
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z"
              fill="currentColor"
            />
          </svg>
          <span className={styles.buttonText}>Personalize</span>
        </button>

        <button
          className={`${styles.actionButton} ${styles.translateButton}`}
          onClick={handleTranslate}
          title="Translate this chapter to Urdu"
        >
          <svg
            className={styles.buttonIcon}
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12.87 15.07L10.33 12.56L10.36 12.53C12.1 10.59 13.34 8.36 14.07 6H17V4H10V2H8V4H1V6H12.17C11.5 7.92 10.44 9.75 9 11.35C8.07 10.32 7.3 9.19 6.69 8H4.69C5.42 9.63 6.42 11.17 7.67 12.56L2.58 17.58L4 19L9 14L12.11 17.11L12.87 15.07ZM18.5 10H16.5L12 22H14L15.12 19H19.87L21 22H23L18.5 10ZM15.88 17L17.5 12.67L19.12 17H15.88Z"
              fill="currentColor"
            />
          </svg>
          <span className={styles.buttonText}>Translate to Urdu</span>
        </button>
      </div>
      <p className={styles.comingSoonNote}>
        These features are coming in future updates
      </p>
    </div>
  );
}
