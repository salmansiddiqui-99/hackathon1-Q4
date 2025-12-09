import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/physical_ai_book/docs',
    component: ComponentCreator('/physical_ai_book/docs', '344'),
    routes: [
      {
        path: '/physical_ai_book/docs/',
        component: ComponentCreator('/physical_ai_book/docs/', '52e'),
        exact: true
      },
      {
        path: '/physical_ai_book/docs/intro',
        component: ComponentCreator('/physical_ai_book/docs/intro', 'd6d'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module1/',
        component: ComponentCreator('/physical_ai_book/docs/module1/', '4b0'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module1/chapter1',
        component: ComponentCreator('/physical_ai_book/docs/module1/chapter1', '5d7'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module1/chapter2',
        component: ComponentCreator('/physical_ai_book/docs/module1/chapter2', 'ebe'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module1/chapter3',
        component: ComponentCreator('/physical_ai_book/docs/module1/chapter3', 'dcd'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module1/humanoid-control',
        component: ComponentCreator('/physical_ai_book/docs/module1/humanoid-control', '4d9'),
        exact: true
      },
      {
        path: '/physical_ai_book/docs/module1/ros2-basics',
        component: ComponentCreator('/physical_ai_book/docs/module1/ros2-basics', '2a3'),
        exact: true
      },
      {
        path: '/physical_ai_book/docs/module1/urdf-robot-descriptions',
        component: ComponentCreator('/physical_ai_book/docs/module1/urdf-robot-descriptions', '7d3'),
        exact: true
      },
      {
        path: '/physical_ai_book/docs/module2/',
        component: ComponentCreator('/physical_ai_book/docs/module2/', '599'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module2/chapter4',
        component: ComponentCreator('/physical_ai_book/docs/module2/chapter4', 'd6a'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module2/chapter5',
        component: ComponentCreator('/physical_ai_book/docs/module2/chapter5', 'ae4'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module2/chapter6',
        component: ComponentCreator('/physical_ai_book/docs/module2/chapter6', '1fb'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module2/gazebo-simulation',
        component: ComponentCreator('/physical_ai_book/docs/module2/gazebo-simulation', 'a7d'),
        exact: true
      },
      {
        path: '/physical_ai_book/docs/module2/sensor-simulation',
        component: ComponentCreator('/physical_ai_book/docs/module2/sensor-simulation', '4d2'),
        exact: true
      },
      {
        path: '/physical_ai_book/docs/module2/unity-visualization',
        component: ComponentCreator('/physical_ai_book/docs/module2/unity-visualization', '09a'),
        exact: true
      },
      {
        path: '/physical_ai_book/docs/module3/',
        component: ComponentCreator('/physical_ai_book/docs/module3/', '606'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module3/chapter7',
        component: ComponentCreator('/physical_ai_book/docs/module3/chapter7', '16b'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module3/chapter8',
        component: ComponentCreator('/physical_ai_book/docs/module3/chapter8', '358'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module3/chapter9',
        component: ComponentCreator('/physical_ai_book/docs/module3/chapter9', '5c0'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module3/isaac-perception-ai',
        component: ComponentCreator('/physical_ai_book/docs/module3/isaac-perception-ai', 'bb5'),
        exact: true
      },
      {
        path: '/physical_ai_book/docs/module3/isaac-sim-humanoids',
        component: ComponentCreator('/physical_ai_book/docs/module3/isaac-sim-humanoids', '75a'),
        exact: true
      },
      {
        path: '/physical_ai_book/docs/module3/nav2-navigation',
        component: ComponentCreator('/physical_ai_book/docs/module3/nav2-navigation', '80b'),
        exact: true
      },
      {
        path: '/physical_ai_book/docs/module4/',
        component: ComponentCreator('/physical_ai_book/docs/module4/', '0a6'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module4/capstone-project',
        component: ComponentCreator('/physical_ai_book/docs/module4/capstone-project', '344'),
        exact: true
      },
      {
        path: '/physical_ai_book/docs/module4/chapter10',
        component: ComponentCreator('/physical_ai_book/docs/module4/chapter10', '5a8'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module4/chapter11',
        component: ComponentCreator('/physical_ai_book/docs/module4/chapter11', 'ec3'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module4/chapter12',
        component: ComponentCreator('/physical_ai_book/docs/module4/chapter12', '8a9'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module4/cognitive-planning',
        component: ComponentCreator('/physical_ai_book/docs/module4/cognitive-planning', '6d0'),
        exact: true
      },
      {
        path: '/physical_ai_book/docs/module4/vla-systems',
        component: ComponentCreator('/physical_ai_book/docs/module4/vla-systems', '6ae'),
        exact: true
      }
    ]
  },
  {
    path: '/physical_ai_book/',
    component: ComponentCreator('/physical_ai_book/', 'e53'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
