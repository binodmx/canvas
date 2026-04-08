from nicegui import ui

class MermaidEditor:
    def __init__(self):
        @ui.page('/MermaidEditor')
        def index():
            content_height = '80vh'

            # Load mermaid.js from CDN
            ui.add_head_html('''
                <script type="module">
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
                    mermaid.initialize({ startOnLoad: false, theme: 'default' });
                    window.mermaidAPI = mermaid;
                </script>
            ''')

            with ui.header().classes('bg-primary text-white h-16'):
                with ui.row().classes('w-full h-full items-center justify-between px-4'):
                    ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')

            def download_mermaid():
                ui.run_javascript('''
                    const content = document.getElementById("mermaid_output").innerHTML;
                    const printWindow = window.open('', '', 'width=800,height=600');
                    printWindow.document.write(`
                        <html>
                        <head>
                            <title>Mermaid Diagram</title>
                            <style>
                                body { display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
                                svg { max-width: 100%; height: auto; }
                            </style>
                        </head>
                        <body>
                            ${content}
                        </body>
                        </html>
                    `);
                    printWindow.document.close();
                    printWindow.focus();
                    setTimeout(() => {
                        printWindow.print();
                    }, 500);
                    printWindow.onafterprint = function() {
                        printWindow.close();
                    };
                ''')

            with ui.row().classes('w-full justify-end'):
                ui.button(
                    'Download',
                    icon='picture_as_pdf',
                    on_click=download_mermaid,
                    color='primary',
                )

            default_code = '''graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Do Something]
    B -->|No| D[Do Something Else]
    C --> E[End]
    D --> E'''

            async def render_mermaid():
                code = mermaid_input.value or ''
                escaped = code.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
                await ui.run_javascript(f'''
                    (async () => {{
                        const output = document.getElementById("mermaid_output");
                        if (!output) return;
                        try {{
                            const {{ svg }} = await window.mermaidAPI.render(
                                "mermaid-svg-" + Date.now(),
                                `{escaped}`
                            );
                            output.innerHTML = svg;
                        }} catch (e) {{
                            output.innerHTML = '<pre style="color: #e53e3e; padding: 1rem;">' + e.message + '</pre>';
                        }}
                    }})();
                ''')

            with ui.row().classes('w-full mx-auto flex-nowrap gap-4'):
                mermaid_input = ui.codemirror(
                    value=default_code,
                    language='Markdown',
                    on_change=lambda _: render_mermaid(),
                ).classes(
                    'w-1/2 text-base border border-gray-300 rounded p-4 overflow-auto'
                ).style(f'height: {content_height}; min-height: {content_height};')

                mermaid_output = ui.html(
                    '<div id="mermaid_output" style="display:flex; justify-content:center; align-items:flex-start; padding:1rem;"></div>'
                ).classes(
                    'w-1/2 text-base border border-gray-300 rounded p-4 overflow-auto bg-white'
                ).style(f'height: {content_height}; min-height: {content_height};')

                # Render the default diagram on initial load
                ui.timer(1.5, render_mermaid, once=True)
