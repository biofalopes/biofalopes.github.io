// Respect the sticky site header and the reader's reduced-motion preference.
export function setupSmoothAnchors() {
    document.querySelectorAll<HTMLAnchorElement>('a[href^="#"]').forEach((link) => {
        link.addEventListener('click', (event) => {
            if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
            const hash = link.getAttribute('href');
            if (!hash || hash === '#') return;

            let id: string;
            try { id = decodeURIComponent(hash.slice(1)); } catch { return; }
            const target = document.getElementById(id);
            if (!target) return;

            event.preventDefault();
            const offset = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0;
            window.history.pushState({}, '', hash);
            window.scrollTo({
                top: Math.max(0, target.getBoundingClientRect().top + window.scrollY - offset),
                behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',
            });
            if (link.classList.contains('skip-link')) target.focus({ preventScroll: true });
        });
    });
}
