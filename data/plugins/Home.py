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
    with ui.header().classes('bg-primary text-white h-16'):
        with ui.row().classes('w-full h-full items-center justify-between px-4'):
            ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')

    with ui.column().classes('w-full items-center'):
        with ui.row().classes('gap-4 w-full'):
            for plugin_id in plugin_ids:
                with ui.card().classes('w-full md:w-1/2 lg:w-1/3 xl:w-1/5'):
                    with ui.link(target=f'/{plugin_id}', new_tab=False):
                        with ui.card_section():
                            ui.label(plugin_id).classes('text-xl font-bold')
                    with ui.row().classes('ml-auto'):
                        ui.button(icon='delete', color="negative", on_click=lambda pid=plugin_id: show_delete_dialog(pid)).classes('rounded-full w-9')

            with ui.card().classes('w-full md:w-1/2 lg:w-1/3 xl:w-1/5 h-36 justify-center'):
                ui.button(icon='add', color="primary", on_click=show_upload_dialog).props('fab').classes("mx-auto")
