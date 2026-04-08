from nicegui import ui

class TextEditor:
    def __init__(self):
        @ui.page('/TextEditor')
        def index():
            content_height = '80vh'

            def load_text():
                try:
                    with open('./data/cache/text-editor-data.txt', 'r') as f:
                        return f.read()
                except FileNotFoundError:
                    return ""

            def save_text():
                with open('./data/cache/text-editor-data.txt', 'w') as f:
                    f.write(editor.value)
                ui.notify('Saved successfully!')

            with ui.header().classes('bg-primary text-white h-16'):
                with ui.row().classes('w-full h-full items-center justify-between px-4'):
                    ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')

            with ui.row().classes('w-full justify-end px-4 pt-2 gap-2'):
                ui.button('Clear', icon='delete', on_click=lambda: editor.set_value(''), color='negative')
                ui.button('Save', icon='save', on_click=save_text, color='primary')

            editor = ui.editor(value=load_text(), placeholder='Type something here...') \
                .props('id="text_editor_content"') \
                .classes('w-full px-4 pb-4 text-base font-mono') \
                .style(f'height: {content_height}; min-height: {content_height};')
