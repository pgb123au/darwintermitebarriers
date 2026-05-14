// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://darwintermitebarriers.com.au',
  trailingSlash: 'always',
  compressHTML: true,
  build: {
    inlineStylesheets: 'auto',
  },
  integrations: [sitemap({
    filter: (page) => !page.includes('/thanks/') && !page.includes('/404'),
  })],
});
