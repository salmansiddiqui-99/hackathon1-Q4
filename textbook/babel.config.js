/**
 * Babel Configuration for Docusaurus
 */

module.exports = {
  presets: [
    require.resolve('@docusaurus/core/lib/babel/preset'),
    ['@babel/preset-react', { runtime: 'automatic' }],
  ],
};
