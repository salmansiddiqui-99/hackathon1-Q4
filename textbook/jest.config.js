/**
 * Jest Configuration for Docusaurus Project
 */

module.exports = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.js', '**/*.test.jsx'],
  moduleNameMapper: {
    '^@site/(.*)$': '<rootDir>/src/$1',
    '^@docusaurus/(.*)$': '<rootDir>/node_modules/@docusaurus/$1',
    '^@theme/(.*)$': '<rootDir>/node_modules/@docusaurus/theme-classic/lib/theme/$1',
    '^@theme-original/(.*)$': '<rootDir>/node_modules/@docusaurus/theme-classic/lib/theme/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { configFile: './babel.config.js' }],
  },
  transformIgnorePatterns: [
    '/node_modules/(?!(@docusaurus|@mdx-js|remark-|unified|bail|is-plain-obj|trough|vfile|unist-|mdast-|micromark|decode-named-character-reference|character-entities)/)',
  ],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  collectCoverageFrom: [
    'src/components/**/*.{js,jsx}',
    'src/theme/**/*.{js,jsx}',
    '!src/**/*.test.{js,jsx}',
    '!**/node_modules/**',
  ],
  coverageThreshold: {
    global: {
      statements: 50,
      branches: 40,
      functions: 50,
      lines: 50,
    },
  },
};
