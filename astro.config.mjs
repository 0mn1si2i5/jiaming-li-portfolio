// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

// https://astro.build/config
const [owner, repository] = (process.env.GITHUB_REPOSITORY ?? '').split('/');
const isUserSite = repository === `${owner}.github.io`;
const localProjectBase = '/Oh-My-Portfolio';
const base = process.env.ASTRO_BASE
  ?? (repository ? (isUserSite ? '/' : `/${repository}`) : localProjectBase);

export default defineConfig({
  site: process.env.SITE_URL ?? 'https://0mn1si2i5.github.io',
  base,
  integrations: [mdx()],
});
