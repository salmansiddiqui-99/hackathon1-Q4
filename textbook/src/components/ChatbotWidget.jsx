/**
 * ChatbotWidget Component (Stub)
 * Floating chatbot icon with placeholder functionality
 * Will be implemented with AI capabilities in Phase 5
 */

import React, { useState } from 'react';
import styles from './ChatbotWidget.module.css';

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className={styles.chatbotContainer}>
      {/* Chat Window (Placeholder) */}
      {isOpen && (
        <div className={styles.chatWindow}>
          <div className={styles.chatHeader}>
            <h4 className={styles.chatTitle}>AI Assistant</h4>
            <button
              className={styles.closeButton}
              onClick={toggleChat}
              aria-label="Close chat"
            >
              ✕
            </button>
          </div>
          <div className={styles.chatBody}>
            <div className={styles.placeholderMessage}>
              <p className={styles.placeholderText}>
                Ask me anything about Physical AI & Robotics!
              </p>
              <p className={styles.comingSoon}>
                Coming soon in Phase 5...
              </p>
            </div>
          </div>
          <div className={styles.chatFooter}>
            <input
              type="text"
              className={styles.chatInput}
              placeholder="Type your question..."
              disabled
            />
            <button
              className={styles.sendButton}
              disabled
              aria-label="Send message"
            >
              ➤
            </button>
          </div>
        </div>
      )}

      {/* Floating Chat Button */}
      <button
        className={styles.chatButton}
        onClick={toggleChat}
        aria-label="Open AI Assistant"
        title="Ask me anything"
      >
        <svg
          className={styles.chatIcon}
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z"
            fill="currentColor"
          />
          <circle cx="8" cy="9" r="1.5" fill="var(--color-bg-dark)" />
          <circle cx="12" cy="9" r="1.5" fill="var(--color-bg-dark)" />
          <circle cx="16" cy="9" r="1.5" fill="var(--color-bg-dark)" />
        </svg>
      </button>
    </div>
  );
}
