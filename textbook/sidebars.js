/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a set of docs in the sidebar
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  modules: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: ROS 2',
      items: [
        'module1/chapter1',
        'module1/chapter2',
        'module1/chapter3',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Simulation',
      items: [
        'module2/chapter4',
        'module2/chapter5',
        'module2/chapter6',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: NVIDIA Isaac',
      items: [
        'module3/chapter7',
        'module3/chapter8',
        'module3/chapter9',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: VLA & Capstone',
      items: [
        'module4/chapter10',
        'module4/chapter11',
        'module4/chapter12',
      ],
    },
  ],
};

module.exports = sidebars;
