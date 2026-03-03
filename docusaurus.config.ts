import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const app_name: string = 'openai_compliance_add-on_for_splunk';
const repo_name: string = 'openai_compliance_add-on_for_splunk';
const app_descr: string = 'This add-on retrieves compliance data from a ChatGPT Enterprise workspace via the OpenAI API.';

const config: Config = {
  title: app_name,
  tagline: app_descr,
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://splunk-platform-apps.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/' + repo_name + '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'splunk-platform-apps', // Usually your GitHub org/user name.
  projectName: repo_name,
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts'
        },
        theme: {
          customCss: ['./src/css/custom.css', './src/css/fonts.css']
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docs-readme-template.png',
    navbar: {
      logo: {
        alt: 'Splunk Logo',
        src: 'img/logo.svg',
        href: 'https://dev.splunk.com/',
        srcDark: 'img/logo-dark.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Documentation',
        },
        {
          href: 'https://github.com/splunk-platform-apps/' + repo_name,
          position: 'right',
          className: 'header-github-link',
          'aria-label': 'GitHub repository',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Documentation',
              to: 'docs',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/splunk-platform-apps',
            },
            {
              label: 'Community Slack',
              href: 'https://splunkcommunity.slack.com/archives/C04DC8JJ6'
            },
            {
              label: 'Contact',
              href: 'mailto:devinfo@splunk.com'
            }
          ],
        },
        {
          title: 'More',
          items: [
            {label: 'Legal', href: 'https://www.splunk.com/en_us/legal.html'},
            {label: 'Patents', href: 'https://www.splunk.com/en_us/legal/patents.html'},
            {label: 'Privacy', href: 'https://www.splunk.com/en_us/legal/privacy-policy.html?301=/en_us/legal/privacy/privacy-policy.html'}
          ],
        },
      ],
      copyright: `© ${new Date().getFullYear()} Splunk LLC All rights reserved.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
