###############################################################################
# Scheduler
# 
# This plugin allows you to schedule python functions to run at specific times.
# It uses the crontab command to schedule the jobs.
# Python functions should be stored in the data/functions directory.
# If crond is not running, run `crond` to start it.
###############################################################################

from nicegui import ui
import subprocess
import os

function_dir = "data/functions"

def get_functions():
    if os.path.isdir(function_dir):
        fids = [i for i in os.listdir(function_dir) if i.endswith(".py")]
        return fids
    return []

def get_crond_status():
    crond_status = subprocess.run('pgrep crond', shell=True, capture_output=True, text=True).stdout
    if crond_status:
        return True
    return False

def get_scheduled_jobs():
    scheduled_jobs = []
    crontab_list = subprocess.run('crontab -l', shell=True, capture_output=True, text=True).stdout
    for line in crontab_list.splitlines():
        if line.strip() and not line.startswith('#'):
            scheduled_jobs.append(line.strip())
    return scheduled_jobs

def delete_scheduled_jobs(job_ids):
    crontab_list = subprocess.run('crontab -l', shell=True, capture_output=True, text=True).stdout
    crontab_input = ''
    job_id = 0
    for line in crontab_list.splitlines():
        if line.strip() and not line.startswith('#'):
            if job_id not in job_ids:
                crontab_input += line + '\n'
            job_id += 1
            continue
        crontab_input += line
    crontab_edit = subprocess.run(f'echo "{crontab_input}" | crontab -', shell=True, capture_output=True, text=True)
    if crontab_edit.returncode == 0:
        return True
    else:
        return False

def schedule_job(crontab_format, function):
    python_path = subprocess.run('which python', shell=True, capture_output=True, text=True).stdout.strip()
    crontab_edit = subprocess.run(f'(crontab -l; echo "{crontab_format} {python_path} /app/data/functions/{function}") | crontab -', shell=True, capture_output=True, text=True)
    if crontab_edit.returncode == 0:
        return True
    else:
        return False

class Scheduler:
    def __init__(self):
        @ui.page('/Scheduler')
        def index():
            with ui.header().classes('bg-primary text-white h-16'):
                with ui.row().classes('w-full h-full items-center justify-between px-4'):
                    ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')

            with ui.column().classes('w-full max-w-3xl mx-auto gap-4 p-4'):
                ui.markdown(f"## Scheduler")

                with ui.card().classes('w-full'):
                    ui.label('Add New').classes('text-lg font-bold')

                    function_select = ui.select(options=get_functions(), label='Function to Execute').classes('w-full')
                    cron_format_input = ui.input(label='Cron Format', placeholder='mm hh dd MM W').classes('w-full text-base')

                    def handle_schedule_click():
                        schedule_job(cron_format_input.value, function_select.value)
                        ui.run_javascript('window.location.reload()')


                    with ui.row().classes('w-full justify-end'):
                        ui.button('Schedule', color='primary', on_click=handle_schedule_click)

                with ui.card().classes('w-full'):
                    with ui.row().classes('w-full justify-between'):
                        ui.label("Current Schedules").classes('text-lg font-bold')
                        ui.label(f"{'🟢' if get_crond_status() else '🔴'}").classes('text-lg font-bold')

                    columns = [
                        {'name': 'mm', 'label': 'mm', 'field': 'mm', 'align': 'right'},
                        {'name': 'hh', 'label': 'hh', 'field': 'hh', 'align': 'right'},
                        {'name': 'DD', 'label': 'DD', 'field': 'DD', 'align': 'right'},
                        {'name': 'MM', 'label': 'MM', 'field': 'MM', 'align': 'right'},
                        {'name': 'ww', 'label': 'ww', 'field': 'ww', 'align': 'right'},
                        {'name': 'command', 'label': 'Command', 'field': 'command', 'align': 'left'}
                    ]

                    rows = []
                    for i, job in enumerate(get_scheduled_jobs()):
                        parts = job.split()
                        if len(parts) >= 5:
                            rows.append({
                                'id': i,
                                'mm': parts[0],
                                'hh': parts[1],
                                'DD': parts[2],
                                'MM': parts[3],
                                'ww': parts[4],
                                'command': ' '.join(parts[5:])
                            })
                    
                    selected_rows = []
                    def handle_selection(e):
                        global selected_rows
                        selected_rows = e.selection
                        if len(selected_rows) > 0:
                            delete_button.enable()
                        else:
                            delete_button.disable()

                    table = ui.table(
                        columns=columns, 
                        rows=rows, 
                        row_key='id', 
                        on_select=lambda e: handle_selection(e)
                    ).classes('w-full')
                    table.set_selection("multiple")

                    def handle_delete_click():
                        global selected_rows
                        job_ids = [row['id'] for row in selected_rows]
                        delete_scheduled_jobs(job_ids)
                        ui.run_javascript('window.location.reload()')
                        selected_rows = []
                        delete_button.disable()

                    with ui.row().classes('w-full justify-end'):
                        delete_button = ui.button('Delete Selected', color='negative', on_click=handle_delete_click)
                        delete_button.disable()
