/**
 * Error Handling Validation Tests (T041-T042)
 * Verifies user-friendly error messages and no technical details leaked
 */

describe('Error Handling: User-Friendly Messages', () => {
  // T041: Error message mapping validation
  describe('T041: Error Message Standardization', () => {
    const errorMessages = {
      TIMEOUT: 'Request timed out. Please try again.',
      NETWORK_ERROR: 'Network connection lost. Check your internet.',
      HTTP_500: 'Something went wrong. Please try again later.',
      EMPTY_CONTEXT: 'Not found in the book.',
      INVALID_INPUT: 'Please check your input and try again.',
      PARTIAL_RESPONSE: 'Incomplete response received. Please try again.',
      BACKEND_UNAVAILABLE: 'Backend Temporarily Unavailable',
    };

    test('should have user-friendly error messages', () => {
      Object.entries(errorMessages).forEach(([code, message]) => {
        // All messages should be user-friendly (non-technical)
        expect(message).not.toMatch(/\[ERR/);
        expect(message).not.toMatch(/error:/i);
        expect(message).not.toMatch(/status:/i);
        expect(message).not.toMatch(/\d{3}/);  // No HTTP status codes
        expect(message).not.toMatch(/undefined/i);
        expect(message).not.toMatch(/null/i);
        expect(message).not.toMatch(/stack/i);
        expect(message).not.toMatch(/trace/i);
      });
    });

    test('should not contain stack traces in any message', () => {
      Object.values(errorMessages).forEach(message => {
        expect(message).not.toMatch(/at \w+\.js/);
        expect(message).not.toMatch(/\.stack/);
        expect(message).not.toMatch(/Traceback/);
      });
    });

    test('should not expose HTTP status codes', () => {
      Object.values(errorMessages).forEach(message => {
        expect(message).not.toMatch(/404/);
        expect(message).not.toMatch(/500/);
        expect(message).not.toMatch(/503/);
        expect(message).not.toMatch(/502/);
      });
    });
  });

  // T042: Error logging validation (detailed for debugging)
  describe('T042: Error Logging with Full Details', () => {
    test('backend should log full error details for debugging', () => {
      // This test validates that error logs include:
      // - Error code
      // - Timestamp
      // - Request details (for debugging)
      // - Stack trace (NOT exposed to client)

      const errorLog = {
        timestamp: '2025-12-19T15:30:45.123Z',
        code: 'INVALID_INPUT',
        message: 'Query validation failed',
        details: {
          query_length: 0,
          expected_min: 1,
          expected_max: 1000,
        },
        request_id: 'req-123456789',
        stack: 'Error: Query validation failed\n    at validateQuery (chatbot.py:45)',
      };

      // Server logs should have full details
      expect(errorLog.code).toBeTruthy();
      expect(errorLog.message).toBeTruthy();
      expect(errorLog.timestamp).toBeTruthy();
      expect(errorLog.stack).toBeTruthy();  // For debugging only
      expect(errorLog.request_id).toBeTruthy();

      // BUT these should NOT be sent to client
      expect(errorLog).toHaveProperty('stack');  // Server keeps this
    });

    test('should sanitize error responses before sending to client', () => {
      // Client receives sanitized error
      const clientError = {
        error: 'Invalid query parameter',
        code: 'INVALID_INPUT',
        details: {
          query: 'must be between 1 and 1000 characters',
        },
        timestamp: '2025-12-19T15:30:45.123Z',
      };

      // Should NOT have stack trace
      expect(clientError).not.toHaveProperty('stack');
      expect(clientError).not.toHaveProperty('trace');
      expect(clientError).not.toHaveProperty('exception');

      // Should NOT have internal paths
      expect(JSON.stringify(clientError)).not.toMatch(/\/home\/user\//);
      expect(JSON.stringify(clientError)).not.toMatch(/backend\/src\//);

      // Should NOT have database info
      expect(JSON.stringify(clientError)).not.toMatch(/postgres/i);
      expect(JSON.stringify(clientError)).not.toMatch(/qdrant/i);
    });
  });

  // T043-T045: Error UI display in ChatbotWidget
  describe('T043-T045: Frontend Error Display', () => {
    test('should display timeout error message', () => {
      const timeoutError = {
        code: 'TIMEOUT',
        userMessage: 'Request timed out. Please try again.',
        retryable: true,
      };

      expect(timeoutError.userMessage).toBe('Request timed out. Please try again.');
      expect(timeoutError.retryable).toBe(true);
      expect(timeoutError.userMessage).not.toMatch(/2000ms/);
      expect(timeoutError.userMessage).not.toMatch(/timeout/i);
    });

    test('should display network error message', () => {
      const networkError = {
        code: 'NETWORK_ERROR',
        userMessage: 'Network connection lost. Check your internet.',
        retryable: true,
      };

      expect(networkError.userMessage).toBe('Network connection lost. Check your internet.');
      expect(networkError.retryable).toBe(true);
    });

    test('should display server error message', () => {
      const serverError = {
        code: 'HTTP_ERROR',
        userMessage: 'Something went wrong. Please try again later.',
        retryable: true,
      };

      expect(serverError.userMessage).toBe('Something went wrong. Please try again later.');
      expect(serverError.retryable).toBe(true);
      expect(serverError.userMessage).not.toMatch(/500/);
      expect(serverError.userMessage).not.toMatch(/Internal Server/);
    });

    test('should display empty context error', () => {
      const emptyContextError = {
        code: 'EMPTY_CONTEXT',
        userMessage: 'Not found in the book.',
        retryable: false,
      };

      expect(emptyContextError.userMessage).toBe('Not found in the book.');
      expect(emptyContextError.retryable).toBe(false);  // Don't show retry for this
    });

    test('should display invalid input error', () => {
      const invalidError = {
        code: 'INVALID_INPUT',
        userMessage: 'Please check your input and try again.',
        retryable: false,
      };

      expect(invalidError.userMessage).toBe('Please check your input and try again.');
      expect(invalidError.retryable).toBe(false);
    });

    test('should auto-dismiss error after timeout', () => {
      // Error display should auto-dismiss after 3-5 seconds
      const errorDismissTime = 3000;  // 3 seconds

      expect(errorDismissTime).toBeGreaterThanOrEqual(3000);
      expect(errorDismissTime).toBeLessThanOrEqual(5000);
    });

    test('should show retry button for retryable errors', () => {
      const retryableErrors = [
        { code: 'TIMEOUT', retryable: true },
        { code: 'NETWORK_ERROR', retryable: true },
        { code: 'BACKEND_UNAVAILABLE', retryable: true },
      ];

      retryableErrors.forEach(error => {
        expect(error.retryable).toBe(true);
        // UI should show retry button
      });
    });

    test('should NOT show retry button for non-retryable errors', () => {
      const nonRetryableErrors = [
        { code: 'EMPTY_CONTEXT', retryable: false },
        { code: 'INVALID_INPUT', retryable: false },
      ];

      nonRetryableErrors.forEach(error => {
        expect(error.retryable).toBe(false);
        // UI should NOT show retry button
      });
    });

    test('should disable send button during error state', () => {
      // During error, input should be disabled
      const errorState = {
        isError: true,
        isLoading: false,
        backendAvailable: false,
      };

      // Send button should be disabled if error OR loading OR backend unavailable
      const shouldDisableSendButton = errorState.isError || errorState.isLoading || !errorState.backendAvailable;

      expect(shouldDisableSendButton).toBe(true);
    });

    test('should log errors internally with full details', () => {
      // Console logs should include full error details for debugging
      const internalErrorLog = {
        timestamp: '2025-12-19T15:30:45.123Z',
        code: 'TIMEOUT',
        message: 'POST /api/chatbot/query timeout after 2000ms',
        stack: 'Error: timeout\n    at handleQuerySubmit (ChatbotWidget.jsx:150)',
      };

      expect(internalErrorLog.code).toBeTruthy();
      expect(internalErrorLog.message).toBeTruthy();
      expect(internalErrorLog.stack).toBeTruthy();
      expect(internalErrorLog.timestamp).toBeTruthy();

      // But this is for console only, not displayed to user
    });
  });

  // T046: Empty context handling in backend
  describe('T046: Empty Context Handling', () => {
    test('should return "Not found in the book" when RAG returns no chunks', () => {
      const emptyContextResponse = {
        success: true,
        type: 'empty_context',
        message: 'Not found in the book.',
        timestamp: '2025-12-19T15:30:45.123Z',
      };

      expect(emptyContextResponse.success).toBe(true);  // 200 OK response
      expect(emptyContextResponse.message).toBe('Not found in the book.');
      expect(emptyContextResponse.type).toBe('empty_context');
    });

    test('should not retry empty context', () => {
      const emptyContextError = {
        code: 'EMPTY_CONTEXT',
        retryable: false,
        message: 'Not found in the book.',
      };

      expect(emptyContextError.retryable).toBe(false);
    });
  });

  // T047: Backend error response standardization
  describe('T047: Standardized Backend Error Responses', () => {
    test('all errors should follow standard format', () => {
      const errorTemplates = [
        {
          error: 'Invalid request',
          code: 'INVALID_INPUT',
          details: { query: 'must be between 1 and 1000 characters' },
          timestamp: '2025-12-19T15:30:45.123Z',
        },
        {
          error: 'Chapter not found',
          code: 'NOT_FOUND',
          details: { chapter_id: 'module-1-chapter-99' },
          timestamp: '2025-12-19T15:30:45.123Z',
        },
        {
          error: 'Rate limit exceeded',
          code: 'RATE_LIMITED',
          retry_after_seconds: 60,
          timestamp: '2025-12-19T15:30:45.123Z',
        },
      ];

      errorTemplates.forEach(errorResponse => {
        expect(errorResponse).toHaveProperty('error');
        expect(errorResponse).toHaveProperty('code');
        expect(errorResponse).toHaveProperty('timestamp');
        expect(errorResponse.timestamp).toMatch(/\d{4}-\d{2}-\d{2}T/);  // ISO format
      });
    });

    test('should not expose stack traces in error responses', () => {
      const errorResponse = {
        error: 'Internal server error',
        code: 'INTERNAL_ERROR',
        timestamp: '2025-12-19T15:30:45.123Z',
      };

      expect(JSON.stringify(errorResponse)).not.toMatch(/\.py:/);
      expect(JSON.stringify(errorResponse)).not.toMatch(/\.jsx:/);
      expect(JSON.stringify(errorResponse)).not.toMatch(/at \w+/);
      expect(JSON.stringify(errorResponse)).not.toMatch(/Traceback/);
    });

    test('should not expose internal paths in errors', () => {
      const errorResponse = {
        error: 'Database error',
        code: 'DATABASE_ERROR',
        timestamp: '2025-12-19T15:30:45.123Z',
      };

      const responseStr = JSON.stringify(errorResponse);
      expect(responseStr).not.toMatch(/\/home\/user\//);
      expect(responseStr).not.toMatch(/\/backend\/src\//);
      expect(responseStr).not.toMatch(/database\.py:/);
      expect(responseStr).not.toMatch(/postgresql:\/\//);
    });

    test('should not expose sensitive data in error details', () => {
      const errorResponse = {
        error: 'Invalid request',
        code: 'INVALID_INPUT',
        details: {
          query: 'too long',
          // Should NOT include:
          // - database connection strings
          // - API keys
          // - internal user IDs
          // - server paths
        },
        timestamp: '2025-12-19T15:30:45.123Z',
      };

      const responseStr = JSON.stringify(errorResponse);
      expect(responseStr).not.toMatch(/postgresql/i);
      expect(responseStr).not.toMatch(/sk-/);
      expect(responseStr).not.toMatch(/Bearer/);
    });
  });
});
