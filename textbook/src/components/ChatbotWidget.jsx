/**
 * ChatbotWidget Component (T060)
 * Fully functional RAG-enabled chatbot widget with 3 retrieval modes
 * - Global: Search entire textbook
 * - Chapter-specific: Search only current chapter
 * - Text-selection: Use selected text as context
 */

import React, { useState, useEffect, useRef } from 'react';
import styles from './ChatbotWidget.module.css';

// Get API URL - use environment variable if available, otherwise default to localhost
const API_BASE_URL = typeof window !== 'undefined' && window.__DOCUSAURUS_API_URL__
  ? window.__DOCUSAURUS_API_URL__
  : 'http://localhost:8000/api';

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
  const chatBodyRef = useRef(null);

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
      // Determine which endpoint to use based on retrieval mode
      let endpoint = `${API_BASE_URL}/chatbot/query`;
      let requestBody = {
        query_text: query,
        chapter_id: retrievalMode === 'chapter-specific' ? getCurrentChapterId() : null,
        selected_text: retrievalMode === 'text-selection' ? selectedText : null,
      };

      // For text-selection mode, use the dedicated endpoint
      if (retrievalMode === 'text-selection') {
        endpoint = `${API_BASE_URL}/selected-text/query`;
        requestBody = {
          query_text: query,
          selected_text: selectedText,
        };
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      // For selected-text mode, handle non-streaming JSON response
      if (retrievalMode === 'text-selection') {
        const data = await response.json();
        if (data.success && data.response_text) {
          setResponse(data.response_text);
          if (!data.used_selection) {
            setError('Response may not be constrained to selected text');
          }
        } else {
          setError(data.response_text || 'Failed to generate response');
        }
      } else {
        // Handle streaming response (NDJSON format) for global/chapter-specific modes
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = '';
        let metadata = null;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const text = decoder.decode(value);
          const lines = text.split('\n').filter((l) => l.trim());

          for (const line of lines) {
            try {
              const json = JSON.parse(line);

              if (json.type === 'token') {
                fullResponse += json.data;
                setResponse(fullResponse);
              } else if (json.type === 'metadata') {
                metadata = json.data;
                setChunks(metadata.chunks_used || []);
              } else if (json.type === 'error') {
                setError(json.data);
              }
            } catch (e) {
              console.error('Failed to parse response line:', e);
            }
          }
        }

        if (!fullResponse) {
          setError('No response generated');
        }
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
                  value="chapter-specific"
                  checked={retrievalMode === 'chapter-specific'}
                  onChange={(e) => setRetrievalMode(e.target.value)}
                  disabled={selectedText !== ''}
                />
                Chapter
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
              placeholder="Ask a question..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
              aria-label="Chat input"
            />
            <button
              type="submit"
              className={styles.sendButton}
              disabled={loading || !query.trim()}
              aria-label="Send message"
              title="Send (Enter)"
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
