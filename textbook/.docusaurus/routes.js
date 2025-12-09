import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/physical_ai_book/docs',
    component: ComponentCreator('/physical_ai_book/docs', 'd89'),
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
        path: '/physical_ai_book/docs/module1/chapter1',
        component: ComponentCreator('/physical_ai_book/docs/module1/chapter1', '485'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module1/chapter2',
        component: ComponentCreator('/physical_ai_book/docs/module1/chapter2', '361'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module1/chapter3',
        component: ComponentCreator('/physical_ai_book/docs/module1/chapter3', '6b6'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module2/chapter4',
        component: ComponentCreator('/physical_ai_book/docs/module2/chapter4', '154'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module2/chapter5',
        component: ComponentCreator('/physical_ai_book/docs/module2/chapter5', '517'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module2/chapter6',
        component: ComponentCreator('/physical_ai_book/docs/module2/chapter6', 'b3e'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module3/chapter7',
        component: ComponentCreator('/physical_ai_book/docs/module3/chapter7', '5ee'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module3/chapter8',
        component: ComponentCreator('/physical_ai_book/docs/module3/chapter8', '412'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module3/chapter9',
        component: ComponentCreator('/physical_ai_book/docs/module3/chapter9', '342'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module4/chapter10',
        component: ComponentCreator('/physical_ai_book/docs/module4/chapter10', 'f0e'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module4/chapter11',
        component: ComponentCreator('/physical_ai_book/docs/module4/chapter11', '803'),
        exact: true,
        sidebar: "modules"
      },
      {
        path: '/physical_ai_book/docs/module4/chapter12',
        component: ComponentCreator('/physical_ai_book/docs/module4/chapter12', '5ab'),
        exact: true,
        sidebar: "modules"
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
