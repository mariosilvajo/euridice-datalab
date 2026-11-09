/**
 * Keeps the learner's in-browser notebooks in step with published lessons.
 *
 * JupyterLite autosaves each open notebook to IndexedDB, and afterwards that
 * browser loads its own copy instead of the published file — so without this,
 * a lesson update would never reach anyone who had already opened the lesson.
 *
 * - On a new release (content version changed), saved copies of the
 *   PUBLISHED notebooks are dropped. The portfolio (reflections.json) and any
 *   file the learner created themselves are never touched.
 * - resetNotebook() lets a learner restore one lesson to its original.
 *
 * Every step fails safe: if storage is unavailable, notebooks simply load.
 */
import content from '../data/datalab-content.json';

const VERSION_KEY = 'datalab-content-version';
const STORES = ['files', 'checkpoints'];
const base = import.meta.env.BASE_URL.replace(/\/$/, '');
const DB_NAME = `JupyterLite Storage - ${base}/lab/`;

function openLiteDb(): Promise<IDBDatabase | null> {
	return new Promise((resolve) => {
		if (!('indexedDB' in window)) return resolve(null);
		let req: IDBOpenDBRequest;
		try {
			req = indexedDB.open(DB_NAME);
		} catch {
			return resolve(null);
		}
		// Never create JupyterLite's database ourselves — abort if it doesn't exist yet.
		req.onupgradeneeded = () => req.transaction?.abort();
		req.onsuccess = () => resolve(req.result);
		req.onerror = () => resolve(null);
		req.onblocked = () => resolve(null);
	});
}

/** Remove saved copies of `paths`; returns how many saved notebooks existed. */
async function forget(paths: string[]): Promise<number> {
	const db = await openLiteDb();
	if (!db) return 0;
	try {
		const stores = STORES.filter((s) => db.objectStoreNames.contains(s));
		if (!stores.length) return 0;
		return await new Promise<number>((resolve) => {
			let found = 0;
			const tx = db.transaction(stores, 'readwrite');
			for (const store of stores) {
				for (const path of paths) {
					const os = tx.objectStore(store);
					if (store === 'files') {
						const probe = os.getKey(path);
						probe.onsuccess = () => {
							if (probe.result !== undefined) found += 1;
						};
					}
					os.delete(path);
				}
			}
			tx.oncomplete = () => resolve(found);
			tx.onerror = () => resolve(found);
			tx.onabort = () => resolve(found);
		});
	} catch {
		return 0;
	} finally {
		db.close();
	}
}

async function syncWithRelease(): Promise<{ updated: boolean }> {
	let seen: string | null = null;
	try {
		seen = localStorage.getItem(VERSION_KEY);
	} catch {
		return { updated: false };
	}
	if (seen === content.version) return { updated: false };
	const removed = await forget(content.notebooks);
	try {
		localStorage.setItem(VERSION_KEY, content.version);
	} catch {
		/* private mode: we'll simply check again next time */
	}
	// Only a returning learner with saved copies needs telling.
	return { updated: seen !== null && removed > 0 };
}

/** Resolves once stale lesson copies are gone — load notebooks after this. */
export const ready: Promise<{ updated: boolean }> = syncWithRelease().catch(() => ({
	updated: false,
}));

/** Restore one published notebook to its original. */
export async function resetNotebook(path: string): Promise<void> {
	await forget([path]);
}
