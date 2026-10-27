const themeButton = document.querySelector<HTMLButtonElement>('#dark-mode-toggle');
function updateThemeButton() {
    themeButton?.setAttribute('aria-pressed', String(document.documentElement.dataset.scheme === 'dark'));
}
window.addEventListener('onColorSchemeChange', updateThemeButton);
updateThemeButton();

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        const navigation = document.querySelector<HTMLDetailsElement>('.mobile-navigation[open]');
        if (navigation) {
            navigation.open = false;
            navigation.querySelector<HTMLElement>('summary')?.focus();
        }
    }
});
