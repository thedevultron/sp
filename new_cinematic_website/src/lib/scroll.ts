import type Lenis from "lenis";

let lenisRef: Lenis | null = null;

export function registerLenis(l: Lenis | null) {
  lenisRef = l;
}

export function getLenis() {
  return lenisRef;
}

export function scrollToTop(immediate = false) {
  if (lenisRef) lenisRef.scrollTo(0, { immediate, duration: 1.4 });
  else window.scrollTo({ top: 0, behavior: immediate ? "auto" : "smooth" });
}

export function scrollToId(id: string, immediate = false) {
  const el = document.getElementById(id);
  if (!el) return false;
  if (lenisRef) lenisRef.scrollTo(el, { immediate, duration: 1.4, offset: -88 });
  else el.scrollIntoView({ behavior: immediate ? "auto" : "smooth" });
  return true;
}
