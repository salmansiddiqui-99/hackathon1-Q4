// docusaurus.config.js
const {themes: prismThemes} = require('prism-react-renderer');
const lightCodeTheme = prismThemes.github;
const darkCodeTheme = prismThemes.dracula;

module.exports = {
  title: "Physical AI & Humanoid Robotics",
  tagline: "Master the intersection of AI and robotics",
  favicon: "img/favicon.ico",

  url: "https://salmansiddiqui-99.github.io",
  baseUrl: "/hackathon1-Q4/",
  organizationName: "salmansiddiqui-99",
  projectName: "hackathon1-Q4",
  deploymentBranch: "gh-pages",

  onBrokenLinks: "warn",
  onBrokenMarkdownLinks: "warn",

  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: './sidebars.js',
          editUrl:
            "https://github.com/salmansiddiqui-99/hackathon1-Q4/tree/main/",
        },
        blog: {
          showReadingTime: true,
          editUrl:
            "https://github.com/salmansiddiqui-99/hackathon1-Q4/tree/main/",
        },
        theme: {
          customCss: [
            './src/css/custom.css',
            './src/css/colors.css',
            './src/css/animations.css',
            './src/css/responsive.css',
          ],
        },
      },
    ],
  ],

  themeConfig: {
    colorMode: {
      defaultMode: "dark",
      disableSwitch: true,
    },
    navbar: {
      title: "Physical AI",
      logo: { alt: "Physical AI Logo", src: "img/logo.svg" },
      items: [
        { type: "docSidebar", sidebarId: "modules", label: "Modules", position: "left" },
        { href: "https://github.com/salmansiddiqui-99/hackathon1-Q4", label: "GitHub", position: "right" },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "Modules",
          items: [
            { label: "Module 1: ROS 2", to: "/docs/module1/chapter1" },
            { label: "Module 2: Simulation", to: "/docs/module2/chapter4" },
            { label: "Module 3: NVIDIA Isaac", to: "/docs/module3/chapter7" },
            { label: "Module 4: VLA", to: "/docs/module4/chapter10" },
          ],
        },
        {
          title: "Community",
          items: [
            { label: "GitHub", href: "https://github.com/salmansiddiqui-99/hackathon1-Q4" },
          ],
        },
      ],
      copyright: "Copyright © 2025 Physical AI Textbook. Built with Docusaurus.",
    },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
      additionalLanguages: ["python", "bash", "cpp", "yaml"],
    },
  },

  staticDirectories: ["static"],
};
