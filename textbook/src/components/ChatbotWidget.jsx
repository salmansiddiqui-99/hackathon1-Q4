/**
 * ChatbotWidget Component (T060)
 * Fully functional RAG-enabled chatbot widget with 3 retrieval modes
 * - Global: Search entire textbook
 * - Chapter-specific: Search only current chapter
 * - Text-selection: Use selected text as context
 */

import React, { useState, useEffect, useRef } from 'react';
import styles from './ChatbotWidget.module.css';

// Get direct API endpoints set by api-url-config.js
// These are specific endpoints, NOT base URLs
const CHATBOT_QUERY_ENDPOINT = typeof window !== 'undefined' && window.CHATBOT_QUERY_ENDPOINT
  ? window.CHATBOT_QUERY_ENDPOINT
  : 'http://localhost:8000/api/chatbot/query';

const HEALTH_CHECK_ENDPOINT = typeof window !== 'undefined' && window.HEALTH_CHECK_ENDPOINT
  ? window.HEALTH_CHECK_ENDPOINT
  : 'http://localhost:8000/api/ready';

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [retrievalMode, setRetrievalMode] = useState('global');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedText, setSelectedText] = useState('');
  const [chunks, setChunks] = useState([]);
  const [showChunks, setShowChunks] = useState(false);
  const [backendAvailable, setBackendAvailable] = useState(true); // T046: Backend health state
  const [healthCheckAttempts, setHealthCheckAttempts] = useState(0); // Track retry attempts
  const chatBodyRef = useRef(null);

  // T046: Health check on component mount with 2-second timeout
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000); // 2-second timeout

        const response = await fetch(HEALTH_CHECK_ENDPOINT, {
          method: 'GET',
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          setBackendAvailable(true);
          setHealthCheckAttempts(0);
        } else {
          setBackendAvailable(false);
        }
      } catch (err) {
        console.warn('Backend health check failed:', err.message);
        setBackendAvailable(false);
      }
    };

    // Check health immediately on mount
    checkBackendHealth();

    // Optional: Periodically re-check health (every 30 seconds)
    const healthCheckInterval = setInterval(checkBackendHealth, 30000);

    return () => clearInterval(healthCheckInterval);
  }, []);

  // T047: Retry health check function
  const retryHealthCheck = async () => {
    setHealthCheckAttempts((prev) => prev + 1);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);

      const response = await fetch(HEALTH_CHECK_ENDPOINT, {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        setBackendAvailable(true);
        setHealthCheckAttempts(0);
        setError(null);
      } else {
        setBackendAvailable(false);
      }
    } catch (err) {
      console.warn('Retry health check failed:', err.message);
      setBackendAvailable(false);
    }
  };

  // Auto-detect selected text on page
  useEffect(() => {
    const handleTextSelection = () => {
      const selected = window.getSelection().toString().trim();
      if (selected && selected.length > 20) {
        setSelectedText(selected);
        setRetrievalMode('text-selection');
        setIsOpen(true);
      }
    };

    document.addEventListener('mouseup', handleTextSelection);
    return () => document.removeEventListener('mouseup', handleTextSelection);
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [response]);

  const handleQuerySubmit = async (e) => {
    e.preventDefault();

    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }

    if (query.length < 10) {
      setError('Question must be at least 10 characters');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse('');
    setChunks([]);

    try {
      // Unified request body for all modes
      const requestBody = {
        query: query,
        mode: retrievalMode,
      };

      // Add selected_text if in text-selection mode
      if (retrievalMode === 'text-selection') {
        requestBody.selected_text = selectedText;
      }

      const response = await fetch(CHATBOT_QUERY_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      // Stream response as NDJSON (newline-delimited JSON)
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';
      let buffer = ''; // Buffer for incomplete lines

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete lines
        const lines = buffer.split('\n');

        // Keep the last incomplete line in buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const json = JSON.parse(line);

            // Handle token chunks - append to response in real-time
            if (json.type === 'token') {
              fullResponse += json.data;
              setResponse(fullResponse);
            }
            // Handle metadata separately
            else if (json.type === 'metadata') {
              const metadata = json.data;
              if (metadata.chunks_used && metadata.chunks_used.length > 0) {
                setChunks(metadata.chunks_used);
              }
            }
            // Handle errors
            else if (json.type === 'error') {
              setError(json.data);
            }
          } catch (parseErr) {
            console.error('Failed to parse NDJSON line:', line, parseErr);
          }
        }
      }

      // Process any remaining data in buffer
      if (buffer.trim()) {
        try {
          const json = JSON.parse(buffer);
          if (json.type === 'token') {
            fullResponse += json.data;
            setResponse(fullResponse);
          } else if (json.type === 'metadata') {
            const metadata = json.data;
            if (metadata.chunks_used && metadata.chunks_used.length > 0) {
              setChunks(metadata.chunks_used);
            }
          }
        } catch (parseErr) {
          console.error('Failed to parse final NDJSON line:', buffer, parseErr);
        }
      }

      if (!fullResponse && !error) {
        setError('No response generated');
      }
    } catch (err) {
      setError(err.message || 'Failed to get response');
      console.error('Query error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getCurrentChapterId = () => {
    // Extract chapter ID from current URL or page metadata
    // Placeholder: returns null for now, can be enhanced with router integration
    return null;
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (isOpen) {
      setQuery('');
      setResponse('');
      setError(null);
    }
  };

  return (
    <div className={styles.chatbotContainer}>
      {/* Chat Window */}
      {isOpen && (
        <div className={styles.chatWindow}>
          <div className={styles.chatHeader}>
            <h4 className={styles.chatTitle}>📚 AI Assistant</h4>
            <button
              className={styles.closeButton}
              onClick={toggleChat}
              aria-label="Close chat"
            >
              ✕
            </button>
          </div>

          {/* Retrieval Mode Selector */}
          <div className={styles.modeSelector}>
            <label className={styles.modeLabel}>Mode:</label>
            <div className={styles.radioGroup}>
              <label className={styles.radioLabel}>
                <input
                  type="radio"
                  value="global"
                  checked={retrievalMode === 'global'}
                  onChange={(e) => setRetrievalMode(e.target.value)}
                  disabled={selectedText !== ''}
                />
                Global
              </label>
              <label className={styles.radioLabel}>
                <input
                  type="radio"
                  value="text-selection"
                  checked={retrievalMode === 'text-selection'}
                  onChange={(e) => setRetrievalMode(e.target.value)}
                  disabled={selectedText === ''}
                />
                Selection
              </label>
            </div>
          </div>

          {/* T048: Backend Unavailable Message */}
          {!backendAvailable && (
            <div className={styles.backendErrorContainer}>
              <div className={styles.backendErrorMessage}>
                <strong>⚠️ Backend Temporarily Unavailable</strong>
                <p>The AI assistant is currently offline. Please refresh the page or try again later.</p>
                <button
                  className={styles.retryButton}
                  onClick={retryHealthCheck}
                  title="Attempt to reconnect to backend"
                >
                  🔄 Retry Connection
                </button>
              </div>
            </div>
          )}

          {/* Chat Body */}
          <div className={styles.chatBody} ref={chatBodyRef}>
            {error && (
              <div className={styles.errorMessage}>
                <strong>⚠️ Error:</strong> {error}
              </div>
            )}

            {response && (
              <div className={styles.assistantMessage}>
                <div className={styles.messageContent}>{response}</div>
                {showChunks && chunks > 0 && (
                  <div className={styles.chunksInfo}>
                    Retrieved {chunks} context chunks
                  </div>
                )}
              </div>
            )}

            {loading && (
              <div className={styles.loadingMessage}>
                <div className={styles.spinner}></div>
                <span>Searching textbook...</span>
              </div>
            )}

            {!response && !error && !loading && (
              <div className={styles.placeholderMessage}>
                <p className={styles.placeholderText}>
                  💡 Ask me anything about Physical AI & Humanoid Robotics!
                </p>
                <p className={styles.hintText}>
                  {selectedText
                    ? `📍 Using selected text: "${selectedText.substring(0, 50)}..."`
                    : 'Tip: Select text on the page to use it as context'}
                </p>
              </div>
            )}
          </div>

          {/* Chat Footer */}
          <form className={styles.chatFooter} onSubmit={handleQuerySubmit}>
            <input
              type="text"
              className={styles.chatInput}
              placeholder={backendAvailable ? "Ask a question..." : "Backend offline..."}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading || !backendAvailable}
              aria-label="Chat input"
            />
            <button
              type="submit"
              className={styles.sendButton}
              disabled={loading || !query.trim() || !backendAvailable}
              aria-label="Send message"
              title={backendAvailable ? "Send (Enter)" : "Backend offline"}
            >
              {loading ? '⏳' : '➤'}
            </button>
          </form>
        </div>
      )}

      {/* Floating Chat Button */}
      <button
        className={styles.chatButton}
        onClick={toggleChat}
        aria-label="Open AI Assistant"
        title="Ask me anything (or select text)"
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
