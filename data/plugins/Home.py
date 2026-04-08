from nicegui import ui
import os
import importlib

plugin_dir = "data/plugins"

def load_plugins():
    print("Loading plugins...")
    if os.path.isdir(plugin_dir):
        pids = [i[:-3] for i in os.listdir(plugin_dir) if i.endswith(".py") and i != "Home.py"]
        for pid in pids:
            plugin = importlib.import_module(f"data.plugins.{pid}")
            getattr(plugin, pid)()
        return sorted(pids)
    return []


def handle_delete(pid):
    print("Deleting plugin...")
    try:
        os.remove(f'{plugin_dir}/{pid}.py')
        ui.notify(f'Deleted plugin: {pid}')
    except Exception as e:
        print(f"Error deleting '{pid}': {e}")
        ui.notify(f"Error deleting '{pid}': {e}", type="negative")


def show_delete_dialog(pid):
    with ui.dialog() as dialog, ui.card():
        ui.label("Delete Plugin").classes("text-xl font-bold")
        ui.label(f"Are you sure you want to delete '{pid}'?")
        with ui.row().classes("ml-auto"):
            ui.button("Delete", color="negative", on_click=lambda: (
                handle_delete(pid),
                dialog.close()
            ))
            ui.button("Cancel", on_click=dialog.close)
    dialog.open()


def handle_upload(event):
    print("Uploading plugin...")
    pid = event.name.replace(".py", "")
    with open(f'{plugin_dir}/{pid}.py', 'wb') as f:
        f.write(event.content.read())
    ui.notify(f'Uploaded plugin: {pid}')


def show_upload_dialog():
    with ui.dialog() as dialog, ui.card():
        ui.label("Upload Plugin").classes("text-xl font-bold")
        file_input = ui.upload(on_upload=handle_upload, multiple=False)
        file_input.props('accept=".py" max-file-size="10485760"')
        ui.button("Cancel", on_click=dialog.close).classes("ml-auto")
    dialog.open()


plugin_ids = load_plugins()
print("Loaded Plugin IDs:", plugin_ids)


@ui.page('/')
def index():
    ui.add_head_html('''
       <style>
            .q-expansion-item .q-item__section--avatar {
                min-width: unset;
            }
            .q-expansion-item .q-item__section--avatar .q-icon {
                font-size: 1.125rem;
            }
            .sensor-card {
                background: linear-gradient(180deg, #bfcddc 0%, #3c8fcb 100%);
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
                color: white;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
        </style>
    ''')

    with ui.header().classes('bg-primary text-white h-16'):
        with ui.row().classes('w-full h-full items-center px-4'):
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
            ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')
            ui.space()
            ui.icon('account_circle').classes('text-3xl')
            

    with ui.left_drawer(top_corner=False, bottom_corner=False).style('background-color: #d7e3f4') as left_drawer:
        with ui.link(target='/', new_tab=False).classes('no-underline items-center gap-4 px-4 py-3 w-full hover:bg-[#bfcddc] cursor-pointer transition-colors'):
            with ui.row().classes('items-center'):
                ui.icon('home').classes('text-lg text-black')
                ui.label('Home').classes('text-lg text-black')
        ui.separator().classes('my-0')
        with ui.expansion('Editors', icon='edit', value=False).classes('w-full text-lg text-black'):
            with ui.link(target='/BibTexParser', new_tab=False).classes('no-underline items-center gap-4 px-4 py-3 w-full hover:bg-[#bfcddc] cursor-pointer transition-colors'):
                with ui.row():
                    ui.icon('menu_book').classes('text-lg text-black')
                    ui.label('BibTex Parser').classes('text-lg text-black')
            with ui.link(target='/MarkdownEditor', new_tab=False).classes('no-underline items-center gap-4 px-4 py-3 w-full hover:bg-[#bfcddc] cursor-pointer transition-colors'):
                with ui.row():
                    ui.icon('wysiwyg').classes('text-lg text-black')
                    ui.label('Markdown Editor').classes('text-lg text-black')
            with ui.link(target='/MermaidEditor', new_tab=False).classes('no-underline items-center gap-4 px-4 py-3 w-full hover:bg-[#bfcddc] cursor-pointer transition-colors'):
                with ui.row():
                    ui.icon('account_tree').classes('text-lg text-black')
                    ui.label('Mermaid Editor').classes('text-lg text-black')
            with ui.link(target='/TextEditor', new_tab=False).classes('no-underline items-center gap-4 px-4 py-3 w-full hover:bg-[#bfcddc] cursor-pointer transition-colors'):
                with ui.row():
                    ui.icon('text_fields').classes('text-lg text-black')
                    ui.label('Text Editor').classes('text-lg text-black')
        with ui.link(target='/PluginManager', new_tab=False).classes('no-underline items-center gap-4 px-4 py-3 w-full hover:bg-[#bfcddc] cursor-pointer transition-colors'):
            with ui.row().classes('items-center'):
                ui.icon('extension').classes('text-lg text-black')
                ui.label('Plugin Manager').classes('text-lg text-black')

    with ui.column().classes('w-full items-center'):
        with ui.row().classes('gap-4 w-full'):
            for plugin_id in plugin_ids:
                with ui.link(target=f'/{plugin_id}', new_tab=False).classes('no-underline w-full md:w-1/2 lg:w-1/3 xl:w-1/5'):
                    with ui.card().classes('sensor-card'):
                        with ui.card_section():
                            ui.label(plugin_id).classes('text-xl font-bold')
