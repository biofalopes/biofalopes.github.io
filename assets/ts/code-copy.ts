import * as params from '@params';

export function setupCodeCopy() {
    if (!navigator.clipboard) return;

    document.querySelectorAll<HTMLElement>('.article-content div.highlight').forEach((highlight) => {
        const code = highlight.querySelector<HTMLElement>('code[data-lang]');
        if (!code) return;

        const toolbar = highlight.closest('.code-example')?.querySelector('.code-toolbar');
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'copyCodeButton';
        button.textContent = params.codeblock.copy;
        (toolbar || highlight).appendChild(button);

        button.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(code.textContent || '');
                button.textContent = params.codeblock.copied;
            } catch {
                button.textContent = document.documentElement.lang.startsWith('pt')
                    ? 'Não foi possível copiar' : 'Unable to copy';
            }
            window.setTimeout(() => { button.textContent = params.codeblock.copy; }, 2000);
        });
    });
}
