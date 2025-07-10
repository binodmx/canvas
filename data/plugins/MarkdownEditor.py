from nicegui import ui

class MarkdownEditor:
    def __init__(self):
        @ui.page('/MarkdownEditor')
        def index():
            content_height = '80vh'
            with ui.header().classes('bg-primary text-white h-16'):
                with ui.row().classes('w-full h-full items-center justify-between px-4'):
                    ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')
                    
            def download_markdown():
                ui.run_javascript(f'''
                    console.log("Downloading markdown file...");
                    const content = document.getElementById("rendered_output").innerHTML;
                    const printWindow = window.open('', '', 'width=595,height=842');
                    printWindow.document.write(`
                        <html>
                        <head>
                            <title>Print Preview</title>
                        </head>
                        <body>
                            ${{content}}
                        </body>
                        </html>
                    `);
                    printWindow.document.close();
                    printWindow.focus();
                    setTimeout(() => {{
                        printWindow.print();
                    }}, 500);
                    printWindow.onafterprint = function() {{
                        printWindow.close();
                    }};
                ''')

            with ui.row().classes('w-full justify-end'):
                ui.button(
                    'Download',
                    icon='picture_as_pdf',
                    on_click=download_markdown,
                    color='primary',
                ).classes('')

            with ui.row().classes('w-full mx-auto flex-nowrap gap-4'):
                markdown_input = ui.codemirror(language='Markdown').classes('w-1/2 text-base border border-gray-300 rounded p-4 overflow-auto').style(f'height: {content_height}; min-height: {content_height};')
                rendered_output = ui.markdown('').classes('w-1/2 text-base border border-gray-300 rounded p-4 overflow-auto').style(f'height: {content_height}; min-height: {content_height};').props('id="rendered_output"')
                
                def update_markdown():
                    rendered_output.set_content(markdown_input.value)
                
                markdown_input.on('keyup', update_markdown)
                