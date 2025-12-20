import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/ur/docs',
    component: ComponentCreator('/ur/docs', '6a9'),
    routes: [
      {
        path: '/ur/docs',
        component: ComponentCreator('/ur/docs', '337'),
        routes: [
          {
            path: '/ur/docs',
            component: ComponentCreator('/ur/docs', 'f92'),
            routes: [
              {
                path: '/ur/docs/chapter-1',
                component: ComponentCreator('/ur/docs/chapter-1', 'bd0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-2',
                component: ComponentCreator('/ur/docs/chapter-2', 'cb6'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-3',
                component: ComponentCreator('/ur/docs/chapter-3', '7af'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-4',
                component: ComponentCreator('/ur/docs/chapter-4', 'b43'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-5',
                component: ComponentCreator('/ur/docs/chapter-5', '61c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-6',
                component: ComponentCreator('/ur/docs/chapter-6', 'ec3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/glossary',
                component: ComponentCreator('/ur/docs/glossary', 'c97'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/intro',
                component: ComponentCreator('/ur/docs/intro', 'c82'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/module-summaries',
                component: ComponentCreator('/ur/docs/module-summaries', '6fd'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/syllabus',
                component: ComponentCreator('/ur/docs/syllabus', '0cf'),
                exact: true
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/ur/',
    component: ComponentCreator('/ur/', '3b1'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
