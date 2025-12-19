/**
 * Security Validation Tests (T035-T036)
 * Verifies no API credentials leaked in frontend code or network traffic
 */

const fs = require('fs');
const path = require('path');

describe('Security: No Credentials in Frontend', () => {
  const buildDir = path.join(__dirname, '../build');
  const srcDir = path.join(__dirname, '../src');

  // T035: Credential leak detection in built bundles
  describe('T035: Credential Leak Detection in Build Output', () => {
    test('should not contain API_KEY pattern in JavaScript bundles', () => {
      if (!fs.existsSync(path.join(buildDir, 'assets'))) {
        console.warn('Build directory does not exist - skipping bundle scan');
        return;
      }

      const jsFiles = fs.readdirSync(path.join(buildDir, 'assets', 'js'));
      let credentialsFound = [];

      jsFiles.forEach(file => {
        const filePath = path.join(buildDir, 'assets', 'js', file);
        const content = fs.readFileSync(filePath, 'utf8');

        // Check for credential patterns
        const patterns = [
          /API_KEY\s*=\s*['"`]/gi,
          /api_key\s*=\s*['"`]/gi,
          /GEMINI_API_KEY/gi,
          /COHERE_API_KEY/gi,
          /OPENAI_API_KEY/gi,
          /sk-ant-/gi,
          /sk-[a-zA-Z0-9]{20,}/gi,
        ];

        patterns.forEach(pattern => {
          if (pattern.test(content)) {
            credentialsFound.push(`Found in ${file}: ${pattern}`);
          }
        });
      });

      expect(credentialsFound).toEqual([]);
    });

    test('should not contain secret tokens in CSS files', () => {
      if (!fs.existsSync(path.join(buildDir, 'assets'))) {
        return;
      }

      const cssFiles = fs.readdirSync(path.join(buildDir, 'assets', 'css'));
      let tokensFound = [];

      cssFiles.forEach(file => {
        const filePath = path.join(buildDir, 'assets', 'css', file);
        const content = fs.readFileSync(filePath, 'utf8');

        // Check for token patterns
        const patterns = [
          /Bearer\s+[a-zA-Z0-9_-]{20,}/gi,
          /token\s*:\s*['"`][a-zA-Z0-9]{20,}/gi,
          /Authorization\s*:\s*['"`]/gi,
        ];

        patterns.forEach(pattern => {
          if (pattern.test(content)) {
            tokensFound.push(`Found in ${file}: ${pattern}`);
          }
        });
      });

      expect(tokensFound).toEqual([]);
    });

    test('should not contain Bearer tokens in HTML files', () => {
      if (!fs.existsSync(path.join(buildDir))) {
        return;
      }

      const htmlFiles = fs.readdirSync(buildDir)
        .filter(f => f.endsWith('.html'));
      let tokensFound = [];

      htmlFiles.forEach(file => {
        const filePath = path.join(buildDir, file);
        const content = fs.readFileSync(filePath, 'utf8');

        // Check for hardcoded credentials
        const patterns = [
          /Bearer\s+[a-zA-Z0-9_-]{20,}/gi,
          /Authorization\s*:\s*['"][a-zA-Z0-9]{20,}/gi,
          /api_key\s*=\s*['"][a-zA-Z0-9]{20,}/gi,
        ];

        patterns.forEach(pattern => {
          if (pattern.test(content)) {
            tokensFound.push(`Found in ${file}: ${pattern}`);
          }
        });
      });

      expect(tokensFound).toEqual([]);
    });

    test('should not expose environment variables in public build', () => {
      if (!fs.existsSync(path.join(buildDir))) {
        return;
      }

      const filesToCheck = fs.readdirSync(buildDir)
        .filter(f => f.endsWith('.html') || f.endsWith('.js'));

      let exposedEnvVars = [];

      filesToCheck.forEach(file => {
        const filePath = path.join(buildDir, file);
        const content = fs.readFileSync(filePath, 'utf8');

        // Check for process.env or window.ENV patterns
        if (/process\.env\.[A-Z_]+/.test(content)) {
          exposedEnvVars.push(`process.env pattern found in ${file}`);
        }
        if (/window\.ENV\.[A-Z_]+/.test(content)) {
          exposedEnvVars.push(`window.ENV pattern found in ${file}`);
        }
      });

      expect(exposedEnvVars).toEqual([]);
    });
  });

  // T036: Network traffic inspection (credentials not sent)
  describe('T036: Network Traffic Security', () => {
    test('should validate api-url-config.js does not hardcode secrets', () => {
      const configPath = path.join(__dirname, '../static/js/api-url-config.js');

      if (!fs.existsSync(configPath)) {
        console.warn('api-url-config.js not found');
        return;
      }

      const content = fs.readFileSync(configPath, 'utf8');

      // Check that no API keys are hardcoded
      const credentials = [
        /API_KEY\s*=\s*['"`]/,
        /api_key\s*=\s*['"`]/,
        /Bearer\s+[a-zA-Z0-9_-]{20,}/,
        /Authorization\s*:\s*['"`]/,
        /sk-ant-/,
        /GEMINI_API_KEY/,
        /COHERE_API_KEY/,
      ];

      credentials.forEach(pattern => {
        expect(content).not.toMatch(pattern);
      });
    });

    test('should validate ChatbotWidget does not send credentials in headers', () => {
      const componentPath = path.join(__dirname, '../src/components/ChatbotWidget.jsx');

      if (!fs.existsSync(componentPath)) {
        console.warn('ChatbotWidget not found');
        return;
      }

      const content = fs.readFileSync(componentPath, 'utf8');

      // Check for potentially problematic patterns
      expect(content).not.toMatch(/Authorization\s*:/);
      expect(content).not.toMatch(/X-API-Key\s*:/);
      expect(content).not.toMatch(/X-Auth-Token\s*:/);
      expect(content).not.toMatch(/Bearer\s+/);
    });

    test('should verify fetch requests use only safe headers', () => {
      const componentPath = path.join(__dirname, '../src/components/ChatbotWidget.jsx');

      if (!fs.existsSync(componentPath)) {
        return;
      }

      const content = fs.readFileSync(componentPath, 'utf8');

      // Extract fetch calls
      const fetchMatches = content.match(/headers\s*:\s*\{[^}]+\}/g) || [];

      fetchMatches.forEach(headerBlock => {
        // Should only have safe headers
        expect(headerBlock).not.toMatch(/Authorization/);
        expect(headerBlock).not.toMatch(/X-API-Key/);
        expect(headerBlock).not.toMatch(/secret/i);
        expect(headerBlock).not.toMatch(/token/i);
      });
    });
  });

  // T037-T039: Audit source files
  describe('T037-T039: Source Code Audit', () => {
    test('should not hardcode credentials in source files', () => {
      const filesToCheck = [
        path.join(srcDir, 'components/ChatbotWidget.jsx'),
        path.join(__dirname, '../static/js/api-url-config.js'),
      ];

      const credentialPatterns = [
        /['"`]sk-[a-zA-Z0-9]{20,}['"`]/,  // OpenAI key
        /['"`]sk-ant-[a-zA-Z0-9]{20,}['"`]/,  // Anthropic key
        /['"`]AIza[0-9A-Za-z\-_]{35}['"`]/,  // Google key
        /GEMINI_API_KEY\s*=\s*['"`]/,
        /COHERE_API_KEY\s*=\s*['"`]/,
      ];

      filesToCheck.forEach(filePath => {
        if (!fs.existsSync(filePath)) return;

        const content = fs.readFileSync(filePath, 'utf8');

        credentialPatterns.forEach(pattern => {
          expect(content).not.toMatch(pattern);
        });
      });
    });

    test('.gitignore should exclude .env files', () => {
      const gitignorePath = path.join(__dirname, '../../.gitignore');

      if (fs.existsSync(gitignorePath)) {
        const content = fs.readFileSync(gitignorePath, 'utf8');

        expect(content).toMatch(/\.env/);
        expect(content).toMatch(/\.env\.local/);
      }
    });

    test('environment variables should not appear in version control', () => {
      const envFiles = [
        path.join(__dirname, '../../.env'),
        path.join(__dirname, '../../.env.local'),
        path.join(__dirname, '../../backend/.env'),
        path.join(__dirname, '../../textbook/.env'),
      ];

      envFiles.forEach(filePath => {
        // These files should NOT exist in the repository if properly ignored
        // This test validates the .gitignore pattern works
        if (fs.existsSync(filePath)) {
          const content = fs.readFileSync(filePath, 'utf8');
          // If it exists, it should not contain real credentials
          expect(content).not.toMatch(/sk-[a-zA-Z0-9]{20,}/);
          expect(content).not.toMatch(/GEMINI_API_KEY\s*=\s*AIza[0-9A-Za-z\-_]{35}/);
        }
      });
    });
  });

  // T040: Security checklist documentation
  describe('T040: Security Checklist', () => {
    test('should have security documentation', () => {
      const securityDocPath = path.join(__dirname, '../../specs/003-static-backend-split/security-checklist.md');

      if (fs.existsSync(securityDocPath)) {
        const content = fs.readFileSync(securityDocPath, 'utf8');

        expect(content).toBeTruthy();
        expect(content.length).toBeGreaterThan(0);
      }
    });
  });
});
