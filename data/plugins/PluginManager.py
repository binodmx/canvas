from nicegui import ui
import os
import glob

class PluginManager:
    def __init__(self):
        @ui.page('/PluginManager')
        def index():
            with ui.header().classes('bg-primary text-white h-16'):
                with ui.row().classes('w-full h-full items-center justify-between px-4'):
                    ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')
                    
            def get_plugins():
                plugins = glob.glob('./data/plugins/*.py')
                return [os.path.basename(p) for p in plugins]

            def handle_upload(event):
                with open(f'./data/plugins/{event.name}', 'wb') as f:
                    f.write(event.content.read())
                ui.notify(f'Uploaded plugin: {event.name}')
                # Refresh the plugin list
                plugin_select.options = get_plugins()
                plugin_select.value = event.name
                load_plugin_code(event.name)

            def load_plugin_code(plugin_name):
                if not plugin_name:
                    code_editor.value = ''
                    return
                try:
                    with open(f'./data/plugins/{plugin_name}', 'r') as f:
                        code_editor.value = f.read()
                    ui.notify(f'Loaded plugin: {plugin_name}')
                except Exception as e:
                    ui.notify(f'Error loading plugin: {str(e)}', color='negative')
                    code_editor.value = ''

            def save_plugin_code():
                if not plugin_select.value:
                    ui.notify('Please select a plugin first!', color='warning')
                    return
                try:
                    with open(f'./data/plugins/{plugin_select.value}', 'w') as f:
                        f.write(code_editor.value)
                    ui.notify(f'Saved plugin: {plugin_select.value}')
                except Exception as e:
                    ui.notify(f'Error saving plugin: {str(e)}', color='negative')

            with ui.column().classes('w-full max-w-3xl mx-auto gap-4 p-4'):
                ui.markdown("## Plugin Manager")
                
                # Upload section
                with ui.card().classes('w-full'):
                    with ui.card_section():
                        ui.label('Upload New Plugin').classes('text-lg font-bold')
                        ui.upload(on_upload=handle_upload, auto_upload=True, label="Upload plugin").classes('w-full')

                # Edit section
                with ui.card().classes('w-full'):
                    with ui.card_section().classes('w-full'):
                        ui.label('Edit Existing Plugin').classes('text-lg font-bold')
                        
                        # Plugin selector
                        plugin_select = ui.select(
                            options=get_plugins(),
                            label='Select Plugin',
                            on_change=lambda e: load_plugin_code(e.value)
                        ).classes('w-full')

                        # Code editor container
                        with ui.column().classes('w-full gap-4 mt-4'):
                            code_editor = ui.codemirror(language='Python').classes('w-full font-mono').style('min-height: 250px')
                            
                            # Save button
                            with ui.row().classes('w-full justify-end'):
                                ui.button('Save Changes', on_click=save_plugin_code, color='primary')
