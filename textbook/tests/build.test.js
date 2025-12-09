/**
 * Integration Test: Build Process
 * Tests that the Docusaurus build completes successfully
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

describe('Docusaurus Build', () => {
  const buildDir = path.join(__dirname, '../build');

  test('Build completes without errors', () => {
    // Run build command
    const result = execSync('npm run build', {
      cwd: path.join(__dirname, '..'),
      encoding: 'utf8',
      stdio: 'pipe',
    });

    expect(result).toContain('Generated static files');
  }, 120000); // 2 minute timeout

  test('Build directory exists after build', () => {
    expect(fs.existsSync(buildDir)).toBe(true);
  });

  test('Index.html is generated', () => {
    const indexPath = path.join(buildDir, 'index.html');
    expect(fs.existsSync(indexPath)).toBe(true);

    const content = fs.readFileSync(indexPath, 'utf8');
    expect(content).toContain('Physical AI');
  });

  test('CSS files are generated', () => {
    const cssFiles = fs.readdirSync(buildDir, { recursive: true })
      .filter(file => file.endsWith('.css'));

    expect(cssFiles.length).toBeGreaterThan(0);
  });

  test('JS bundles are generated', () => {
    const jsFiles = fs.readdirSync(buildDir, { recursive: true })
      .filter(file => file.endsWith('.js'));

    expect(jsFiles.length).toBeGreaterThan(0);
  });

  test('Module pages are generated', () => {
    const module1Path = path.join(buildDir, 'docs/module1/chapter1/index.html');
    const module2Path = path.join(buildDir, 'docs/module2/chapter4/index.html');
    const module3Path = path.join(buildDir, 'docs/module3/chapter7/index.html');
    const module4Path = path.join(buildDir, 'docs/module4/chapter10/index.html');

    expect(fs.existsSync(module1Path)).toBe(true);
    expect(fs.existsSync(module2Path)).toBe(true);
    expect(fs.existsSync(module3Path)).toBe(true);
    expect(fs.existsSync(module4Path)).toBe(true);
  });
});
