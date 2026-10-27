const themeButton = document.querySelector<HTMLButtonElement>('#dark-mode-toggle');
function updateThemeButton() {
    themeButton?.setAttribute('aria-pressed', String(document.documentElement.dataset.scheme === 'dark'));
}
window.addEventListener('onColorSchemeChange', updateThemeButton);
updateThemeButton();

// Close the native mobile contents panel after choosing a section.
document.querySelectorAll<HTMLAnchorElement>('.article-toc a').forEach((link) => {
    link.addEventListener('click', () => {
        const panel = link.closest('details');
        if (panel) panel.open = false;
    });
});

// Keep deep links to highlighted lines usable even when a source file is collapsed.
function revealCodeTarget() {
    let id: string;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = id ? document.getElementById(id) : null;
    const panel = target?.closest<HTMLDetailsElement>('details.code-disclosure');
    if (panel && !panel.open) {
        panel.open = true;
        target?.scrollIntoView({ block: 'start' });
    }
}
window.addEventListener('hashchange', revealCodeTarget);
window.addEventListener('load', revealCodeTarget);

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        const navigation = document.querySelector<HTMLDetailsElement>('.mobile-navigation[open]');
        if (navigation) {
            navigation.open = false;
            navigation.querySelector<HTMLElement>('summary')?.focus();
        }
    }
});
