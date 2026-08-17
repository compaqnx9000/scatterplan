const CURRENT_PROJECT_KEY = "scatter.currentProjectId";

export function rememberCurrentProjectId(id: string | number | null | undefined) {
  const value = id ? String(id) : "";
  if (value) sessionStorage.setItem(CURRENT_PROJECT_KEY, value);
  else sessionStorage.removeItem(CURRENT_PROJECT_KEY);
}

export function readCurrentProjectId() {
  return sessionStorage.getItem(CURRENT_PROJECT_KEY) || "";
}

export function homeRouteForCurrentProject() {
  const id = readCurrentProjectId();
  return id ? { path: "/", query: { project: id } } : { path: "/" };
}
