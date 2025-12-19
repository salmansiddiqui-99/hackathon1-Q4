module.exports = {
  testEnvironment: 'node',
  transform: {},
  testMatch: ['**/tests/**/*.test.js'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    'static/**/*.js',
    '!**/node_modules/**',
    '!**/dist/**',
    '!**/build/**'
  ],
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/build/',
    '/.docusaurus/',
    '/dist/'
  ]
};
