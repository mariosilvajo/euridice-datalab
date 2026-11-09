/**
 * Lesson pages link root-absolute — [Datasets](/datasets/), <iframe src="/lab/…"> —
 * which is only right while the site sits at a domain root. This rehype plugin
 * prefixes Astro's `base` onto those links at build time, so the same content
 * also works under a sub-folder (a GitHub Pages project site:
 * https://<user>.github.io/<repo>/). At a domain root it does nothing.
 */
const ATTRS = ['href', 'src'];

export default function rehypeBaseLinks(base = '/') {
	const prefix = base.replace(/\/$/, '');

	/** "/datasets/" -> "/<repo>/datasets/"; external, relative and already-prefixed links untouched. */
	const fix = (url) =>
		typeof url === 'string' &&
		url.startsWith('/') &&
		!url.startsWith('//') &&
		!url.startsWith(`${prefix}/`)
			? prefix + url
			: url;

	function walk(node) {
		if (node.type === 'element' && node.properties) {
			for (const a of ATTRS) {
				if (a in node.properties) node.properties[a] = fix(node.properties[a]);
			}
		} else if (node.type === 'mdxJsxFlowElement' || node.type === 'mdxJsxTextElement') {
			// Raw HTML/JSX written in .mdx, e.g. the Playground's <iframe>.
			for (const attr of node.attributes ?? []) {
				if (attr.type === 'mdxJsxAttribute' && ATTRS.includes(attr.name)) attr.value = fix(attr.value);
			}
		}
		node.children?.forEach(walk);
	}

	return (tree) => {
		if (prefix) walk(tree);
	};
}
