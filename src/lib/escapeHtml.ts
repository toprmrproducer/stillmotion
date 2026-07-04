/**
 * Escapes HTML-significant characters in a string before it is interpolated
 * into innerHTML. Use this for ANY user-controlled text (filenames, error
 * messages derived from file names, etc.) that gets rendered via innerHTML,
 * to prevent DOM-based XSS from a maliciously named file.
 *
 * Canonical pattern carried over from the anyconvert project's
 * json-formatter.astro (see its AGENTS.md security notes).
 */
export function escapeHtml(value: string): string {
	return value
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&#39;');
}
