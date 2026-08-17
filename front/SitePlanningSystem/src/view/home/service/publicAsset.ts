/** Resolve files from `public/` against the Vite base (`/` locally, `/scatter/` in production). */
export const publicAsset = (path: string) => {
  const base = import.meta.env.BASE_URL || "/";
  const clean = String(path || "").replace(/^\/+/, "");
  return `${base.endsWith("/") ? base : `${base}/`}${clean}`;
};
