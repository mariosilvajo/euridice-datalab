// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import rehypeBaseLinks from './src/plugins/rehype-base-links.mjs';

// Deployment flexibility:
//  - root deploy (Netlify / custom domain): no env vars needed
//  - GitHub Pages: the workflow sets ASTRO_SITE + ASTRO_BASE from the repo's
//    Pages settings, so the same build works at <user>.github.io/<repo>/ or a custom domain
const base = process.env.ASTRO_BASE || '/';

export default defineConfig({
	site: process.env.ASTRO_SITE || 'https://datalab.euridice.eu',
	base,
	markdown: {
		// Content links are written root-absolute (/datasets/); this prefixes `base`.
		rehypePlugins: [[rehypeBaseLinks, base]],
	},
	integrations: [
		starlight({
			title: 'EURIDICE DataLab',
			description:
				'Hands-on data science in your browser. An open learning lab built by IIIM for the EURIDICE project — no installation, no account, no server.',
			customCss: ['./src/styles/custom.css'],
			social: [
				{ icon: 'external', label: 'EURIDICE', href: 'https://euridice.eu' },
				{ icon: 'github', label: 'IIIM on GitHub', href: 'https://github.com/IIIM-IS' },
			],
			components: {
				Footer: './src/components/Footer.astro',
			},
			sidebar: [
				{
					label: 'Start here',
					items: [
						{ label: 'Welcome', slug: 'getting-started' },
						{ label: 'How the DataLab works', slug: 'how-it-works' },
					],
				},
				{
					label: 'Track 1 · Python & Data Foundations',
					items: [
						{ label: 'Overview', slug: 'tracks/foundations' },
						{ label: '1 · Your first notebook', slug: 'tracks/foundations/01-first-notebook' },
						{ label: '2 · Choosing the right chart', slug: 'tracks/foundations/02-choosing-charts' },
						{ label: "3 · Seeing what's missing", slug: 'tracks/foundations/03-missing-data' },
					],
				},
				{
					label: 'Track 2 · Exploratory Data Analysis',
					items: [
						{ label: 'Overview', slug: 'tracks/eda' },
						{ label: '1 · Explore a real dataset', slug: 'tracks/eda/01-explore-a-dataset' },
						{ label: '2 · Graded exercise', slug: 'tracks/eda/02-exercise' },
					],
				},
				{
					label: 'Track 3 · Machine Learning Fundamentals',
					items: [
						{ label: 'Overview', slug: 'tracks/ml' },
						{ label: '1 · Train your first classifier', slug: 'tracks/ml/01-first-classifier' },
						{ label: '2 · Overfitting & choosing a model', slug: 'tracks/ml/02-choosing-a-model' },
						{ label: '3 · Capstone: audit a model', slug: 'tracks/ml/03-capstone' },
					],
				},
				{
					label: 'Resources',
					items: [
						{ label: 'Playground', slug: 'playground' },
						{ label: 'Learn more', slug: 'learn-more' },
						{ label: 'Datasets', slug: 'datasets' },
						{ label: 'Earning a microcredential', slug: 'credentials' },
						{ label: 'About EURIDICE & IIIM', slug: 'about' },
					],
				},
			],
		}),
	],
});
