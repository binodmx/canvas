from nicegui import ui

class PasteBin:
    def __init__(self):
        @ui.page('/PasteBin')
        def index():
            with ui.header().classes('bg-primary text-white h-16'):
                with ui.row().classes('w-full h-full items-center justify-between px-4'):
                    ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')
                
            def load_text():
                try:
                    with open(f'./data/cache/paste-bin-data.txt', 'r') as f:
                        return f.read()
                except FileNotFoundError:
                    return ""

            def save_text():
                with open(f'./data/cache/paste-bin-data.txt', 'w') as f:
                    f.write(text_input.value)
                ui.notify(f'Saved successfully!')

            with ui.column().classes('w-full max-w-3xl mx-auto gap-4 p-4'):
                ui.markdown("## Paste Bin")

                with ui.card().classes('w-full'):
                    text_input = ui.textarea(value=load_text(), placeholder="Type text here").classes('w-full text-base')
                    with ui.row().classes('w-full justify-end'):
                        clear_button = ui.button("Clear", on_click=lambda: text_input.set_value(""), color="red")
                        save_button = ui.button("Save", on_click=save_text, color="primary")
