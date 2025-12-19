import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/hackathon1-Q4/__docusaurus/debug',
    component: ComponentCreator('/hackathon1-Q4/__docusaurus/debug', 'c21'),
    exact: true
  },
  {
    path: '/hackathon1-Q4/__docusaurus/debug/config',
    component: ComponentCreator('/hackathon1-Q4/__docusaurus/debug/config', '9a5'),
    exact: true
  },
  {
    path: '/hackathon1-Q4/__docusaurus/debug/content',
    component: ComponentCreator('/hackathon1-Q4/__docusaurus/debug/content', 'b91'),
    exact: true
  },
  {
    path: '/hackathon1-Q4/__docusaurus/debug/globalData',
    component: ComponentCreator('/hackathon1-Q4/__docusaurus/debug/globalData', '8db'),
    exact: true
  },
  {
    path: '/hackathon1-Q4/__docusaurus/debug/metadata',
    component: ComponentCreator('/hackathon1-Q4/__docusaurus/debug/metadata', 'c47'),
    exact: true
  },
  {
    path: '/hackathon1-Q4/__docusaurus/debug/registry',
    component: ComponentCreator('/hackathon1-Q4/__docusaurus/debug/registry', 'b0d'),
    exact: true
  },
  {
    path: '/hackathon1-Q4/__docusaurus/debug/routes',
    component: ComponentCreator('/hackathon1-Q4/__docusaurus/debug/routes', 'c59'),
    exact: true
  },
  {
    path: '/hackathon1-Q4/docs',
    component: ComponentCreator('/hackathon1-Q4/docs', 'a87'),
    routes: [
      {
        path: '/hackathon1-Q4/docs/',
        component: ComponentCreator('/hackathon1-Q4/docs/', 'c1e'),
        exact: true
      },
      {
        path: '/hackathon1-Q4/docs/intro',
        component: ComponentCreator('/hackathon1-Q4/docs/intro', '419'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module1/',
        component: ComponentCreator('/hackathon1-Q4/docs/module1/', '235'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module1/chapter1',
        component: ComponentCreator('/hackathon1-Q4/docs/module1/chapter1', 'f95'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module1/chapter2',
        component: ComponentCreator('/hackathon1-Q4/docs/module1/chapter2', 'a4d'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module1/chapter3',
        component: ComponentCreator('/hackathon1-Q4/docs/module1/chapter3', '770'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module1/humanoid-control',
        component: ComponentCreator('/hackathon1-Q4/docs/module1/humanoid-control', '0b9'),
        exact: true
      },
      {
        path: '/hackathon1-Q4/docs/module1/ros2-basics',
        component: ComponentCreator('/hackathon1-Q4/docs/module1/ros2-basics', 'e15'),
        exact: true
      },
      {
        path: '/hackathon1-Q4/docs/module1/urdf-robot-descriptions',
        component: ComponentCreator('/hackathon1-Q4/docs/module1/urdf-robot-descriptions', 'dd5'),
        exact: true
      },
      {
        path: '/hackathon1-Q4/docs/module2/',
        component: ComponentCreator('/hackathon1-Q4/docs/module2/', 'd7d'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module2/chapter4',
        component: ComponentCreator('/hackathon1-Q4/docs/module2/chapter4', '474'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module2/chapter5',
        component: ComponentCreator('/hackathon1-Q4/docs/module2/chapter5', '97b'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module2/chapter6',
        component: ComponentCreator('/hackathon1-Q4/docs/module2/chapter6', '45d'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module2/gazebo-simulation',
        component: ComponentCreator('/hackathon1-Q4/docs/module2/gazebo-simulation', 'c03'),
        exact: true
      },
      {
        path: '/hackathon1-Q4/docs/module2/sensor-simulation',
        component: ComponentCreator('/hackathon1-Q4/docs/module2/sensor-simulation', '7f2'),
        exact: true
      },
      {
        path: '/hackathon1-Q4/docs/module2/unity-visualization',
        component: ComponentCreator('/hackathon1-Q4/docs/module2/unity-visualization', 'ef5'),
        exact: true
      },
      {
        path: '/hackathon1-Q4/docs/module3/',
        component: ComponentCreator('/hackathon1-Q4/docs/module3/', '313'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module3/chapter7',
        component: ComponentCreator('/hackathon1-Q4/docs/module3/chapter7', '06b'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module3/chapter8',
        component: ComponentCreator('/hackathon1-Q4/docs/module3/chapter8', '3d0'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module3/chapter9',
        component: ComponentCreator('/hackathon1-Q4/docs/module3/chapter9', 'b1c'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module3/isaac-perception-ai',
        component: ComponentCreator('/hackathon1-Q4/docs/module3/isaac-perception-ai', '874'),
        exact: true
      },
      {
        path: '/hackathon1-Q4/docs/module3/isaac-sim-humanoids',
        component: ComponentCreator('/hackathon1-Q4/docs/module3/isaac-sim-humanoids', '566'),
        exact: true
      },
      {
        path: '/hackathon1-Q4/docs/module3/nav2-navigation',
        component: ComponentCreator('/hackathon1-Q4/docs/module3/nav2-navigation', '317'),
        exact: true
      },
      {
        path: '/hackathon1-Q4/docs/module4/',
        component: ComponentCreator('/hackathon1-Q4/docs/module4/', '193'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module4/capstone-project',
        component: ComponentCreator('/hackathon1-Q4/docs/module4/capstone-project', '53e'),
        exact: true
      },
      {
        path: '/hackathon1-Q4/docs/module4/chapter10',
        component: ComponentCreator('/hackathon1-Q4/docs/module4/chapter10', '747'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module4/chapter11',
        component: ComponentCreator('/hackathon1-Q4/docs/module4/chapter11', 'f8d'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module4/chapter12',
        component: ComponentCreator('/hackathon1-Q4/docs/module4/chapter12', '269'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/hackathon1-Q4/docs/module4/cognitive-planning',
        component: ComponentCreator('/hackathon1-Q4/docs/module4/cognitive-planning', '9f3'),
        exact: true
      },
      {
        path: '/hackathon1-Q4/docs/module4/vla-systems',
        component: ComponentCreator('/hackathon1-Q4/docs/module4/vla-systems', '224'),
        exact: true
      }
    ]
  },
  {
    path: '/hackathon1-Q4/',
    component: ComponentCreator('/hackathon1-Q4/', 'bec'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
