from nicegui import ui, run
import subprocess
import sys
import json


class PackageManager:
    def __init__(self):
        @ui.page('/PackageManager')
        def index():

            def get_packages():
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'list', '--format=json'],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    return []
                return json.loads(result.stdout)

            async def refresh_packages():
                packages = await run.io_bound(get_packages)
                grid.options['rowData'] = [
                    {'name': p['name'], 'version': p['version']} for p in packages
                ]
                pkg_count.set_text(f"{len(packages)} packages installed")
                grid.update()

            async def install_package():
                pkg = install_input.value.strip()
                if not pkg:
                    ui.notify('Enter a package name', type='warning')
                    return
                install_spinner.set_visibility(True)
                install_btn.disable()

                def do_install():
                    return subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', pkg],
                        capture_output=True, text=True
                    )

                result = await run.io_bound(do_install)
                install_spinner.set_visibility(False)
                install_btn.enable()

                if result.returncode == 0:
                    ui.notify(f'Installed: {pkg}', type='positive')
                    install_input.value = ''
                    await refresh_packages()
                else:
                    err = (result.stderr.strip().splitlines() or ['Unknown error'])[-1]
                    ui.notify(f'Install failed: {err}', type='negative')

            async def do_uninstall(pkg_name):
                def _run():
                    return subprocess.run(
                        [sys.executable, '-m', 'pip', 'uninstall', '-y', pkg_name],
                        capture_output=True, text=True
                    )

                result = await run.io_bound(_run)
                if result.returncode == 0:
                    ui.notify(f'Uninstalled: {pkg_name}', type='positive')
                    await refresh_packages()
                else:
                    err = (result.stderr.strip().splitlines() or ['Unknown error'])[-1]
                    ui.notify(f'Uninstall failed: {err}', type='negative')

            def on_cell_clicked(e):
                pkg_name = e.args.get('data', {}).get('name', '')
                if not pkg_name:
                    return
                with ui.dialog() as dialog, ui.card():
                    ui.label('Uninstall Package').classes('text-xl font-bold')
                    ui.label(f"Are you sure you want to uninstall '{pkg_name}'?")
                    with ui.row().classes('ml-auto mt-2'):
                        ui.button('Uninstall', color='negative', on_click=lambda: (
                            dialog.close(),
                            ui.timer(0.05, lambda: do_uninstall(pkg_name), once=True)
                        ))
                        ui.button('Cancel', on_click=dialog.close)
                dialog.open()

            # ── Header ──────────────────────────────────────────────────────────
            with ui.header().classes('bg-primary text-white h-16'):
                with ui.row().classes('w-full h-full items-center justify-between px-4'):
                    ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')

            with ui.column().classes('w-full max-w-4xl mx-auto gap-4 p-4'):
                ui.markdown('## Package Manager')

                # ── Install ──────────────────────────────────────────────────────
                with ui.card().classes('w-full'):
                    with ui.card_section().classes('w-full'):
                        ui.label('Install Package').classes('text-lg font-bold')
                        with ui.row().classes('w-full items-center gap-2 mt-2'):
                            install_input = ui.input(
                                placeholder='Package name (e.g. requests or requests==2.31.0)'
                            ).classes('flex-1').props('outlined dense')
                            install_input.on('keydown.enter', install_package)
                            install_btn = ui.button(
                                'Install', icon='download', color='primary',
                                on_click=install_package
                            )
                            install_spinner = ui.spinner('dots', size='sm').classes('text-primary')
                            install_spinner.set_visibility(False)

                # ── Packages list ────────────────────────────────────────────────
                with ui.card().classes('w-full'):
                    with ui.card_section().classes('w-full'):
                        with ui.row().classes('w-full items-center justify-between'):
                            ui.label('Installed Packages').classes('text-lg font-bold')
                            with ui.row().classes('items-center gap-2'):
                                pkg_count = ui.label('').classes('text-gray-500 text-sm')
                                ui.button(
                                    icon='refresh', color='primary',
                                    on_click=refresh_packages
                                ).props('flat round dense')

                        ui.label('Click on a package to uninstall.').classes('text-sm text-gray-400 mt-1 mb-1')

                        grid = ui.aggrid({
                            'columnDefs': [
                                {
                                    'headerName': 'Package',
                                    'field': 'name',
                                    'flex': 2,
                                    'filter': True,
                                    'sortable': True,
                                },
                                {
                                    'headerName': 'Version',
                                    'field': 'version',
                                    'flex': 1,
                                    'filter': True,
                                    'sortable': True,
                                },
                            ],
                            'rowData': [],
                            'defaultColDef': {'resizable': True},
                            'pagination': True,
                            'paginationPageSize': 20,
                        }).classes('w-full mt-1').style('height: 500px')

                        grid.on('cellClicked', on_cell_clicked)

            ui.timer(0.1, refresh_packages, once=True)
