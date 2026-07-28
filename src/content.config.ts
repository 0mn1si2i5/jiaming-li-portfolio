import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const localized = z.object({
  en: z.string(),
  zh: z.string(),
});

const projects = defineCollection({
  loader: glob({ base: './src/content/projects', pattern: '**/*.{md,mdx}' }),
  schema: z.object({
    title: localized,
    year: localized,
    status: localized,
    order: z.number(),
    featured: z.boolean(),
    kind: localized,
    summary: localized,
    role: localized,
    accent: z.enum(['violet', 'coral', 'blue']),
    media: z.object({
      type: z.enum(['video', 'image', 'placeholder']),
      src: z.string().optional(),
      preview: z.string().optional(),
      poster: z.string().optional(),
      walkthrough: z.object({ src: z.string(), poster: z.string().optional() }).optional(),
      alt: localized,
    }),
    links: z.array(z.object({ label: localized, href: z.string().url() })),
  }),
});

export const collections = { projects };
