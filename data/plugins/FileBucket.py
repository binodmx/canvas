from nicegui import ui
import os

cache_dir = "data/cache"

class FileBucket:
    def __init__(self):
        @ui.page('/FileBucket')
        def index():
            with ui.header().classes('bg-primary text-white h-16'):
                with ui.row().classes('w-full h-full items-center justify-between px-4'):
                    ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')

            def get_entries(path, prefix=''):
                entries = []
                for entry in sorted(os.scandir(path), key=lambda e: e.name):
                    rel_id = f"{prefix}/{entry.name}" if prefix else entry.name
                    if entry.is_dir():
                        entries.append({'id': rel_id, 'label': f"📁 {entry.name}", 'children': get_entries(entry.path, rel_id)})
                    else:
                        entries.append({'id': rel_id, 'label': entry.name})
                return entries

            def download_file(rel_path):
                try:
                    ui.download.file(cache_dir + "/" + rel_path)
                    ui.notify(f'Downloaded: {os.path.basename(rel_path)}', type='positive')
                except Exception as ex:
                    ui.notify(f'Error downloading file: {str(ex)}', type='negative')

            def handle_upload(event):
                with open(f'./{cache_dir}/{event.name}', 'wb') as f:
                    f.write(event.content.read())
                ui.notify(f'Uploaded plugin: {event.name}')
                # Refresh the file tree and upload button
                file_tree.props["nodes"] = get_entries(cache_dir)
                file_tree.update()
                upload_button.reset()

            def handle_select(event):
                rel_path = event.value
                full_path = os.path.join(cache_dir, rel_path)
                if os.path.isdir(full_path):
                    return
                file_name = os.path.basename(rel_path)
                with ui.dialog() as dialog, ui.card().style('width: 300px; max-width: 500px'):
                    ui.label(f'{file_name}').classes('text-sm text-gray-500 text-center break-all')
                    with ui.row().classes('w-full justify-end'):
                        ui.button('Cancel', on_click=dialog.close).props('flat')
                        ui.button('Download', on_click=lambda: (dialog.close(), download_file(rel_path))).props('color=primary')    
                        
                dialog.open()
                
            with ui.column().classes('w-full max-w-3xl mx-auto gap-4 p-4'):
                ui.markdown("## File Bucket")

                # Upload section
                with ui.card().classes('w-full'):
                    with ui.card_section().classes('w-full'):
                        ui.label('Upload').classes('text-lg font-bold')
                        upload_button =ui.upload(on_upload=handle_upload, auto_upload=True, label="Upload a File").classes('w-full mt-3')

                # Download section
                with ui.card().classes('w-full'):
                    with ui.card_section().classes('w-full'):
                        ui.label("Download").classes('text-lg font-bold')
                        file_tree = ui.tree(get_entries(cache_dir), label_key='label', on_select=handle_select).props("no-selection-unset=true")
            