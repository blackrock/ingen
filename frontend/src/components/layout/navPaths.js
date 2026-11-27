//  Hierarchical "up" navigation. Browser history (router.back) is unreliable here — the index route
//  redirects, so back can bounce or leave the app. Instead we compute the parent route from the
//  current path: deep pages → their config, a config → the pipelines index, the index → nowhere.

/**
 * @param {string|null|undefined} pathname
 * @returns {string|null} the parent route, or null when there is no "up" (the index).
 */
export function parentPath(pathname) {
  if (!pathname || pathname === '/') return null;
  const m = pathname.match(/^\/configs\/([^/]+)(\/.+)?$/);
  if (!m) return '/';                       // unknown route → home
  return m[2] ? `/configs/${m[1]}` : '/';   // sub-page → its config; config → home
}
