from nicegui import ui
from datetime import datetime
import pytz
import json
import os

cache_dir = "data/cache"

ALL_TIMEZONES = [
    ("UTC",  "UTC",                 "Coordinated Universal Time"),
    ("GMT",  "Etc/GMT",             "Greenwich Mean Time"),
    ("EDT",  "America/New_York",    "Eastern Daylight Time"),
    ("CST",  "America/Chicago",     "Central Standard Time"),
    ("MST",  "America/Denver",      "Mountain Standard Time"),
    ("PST",  "America/Los_Angeles", "Pacific Standard Time"),
    ("BRT",  "America/Sao_Paulo",   "Brasília Time"),
    ("CET",  "Europe/Paris",        "Central European Time"),
    ("IST",  "Asia/Kolkata",        "India Standard Time"),
    ("SGT",  "Asia/Singapore",      "Singapore Time"),
    ("JST",  "Asia/Tokyo",          "Japan Standard Time"),
    ("AEST", "Australia/Sydney",    "Australian Eastern Standard Time"),
]

DEFAULT_ABBRS = ["UTC", "GMT", "EDT", "AEST"]


def load_active():
    try:
        with open(f'{cache_dir}/clock-timezones.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        defaults = [list(tz) for tz in ALL_TIMEZONES if tz[0] in DEFAULT_ABBRS]
        save_active(defaults)
        return defaults


def save_active(active):
    os.makedirs(cache_dir, exist_ok=True)
    with open(f'{cache_dir}/clock-timezones.json', 'w') as f:
        json.dump(active, f)


class Clock:
    def __init__(self):
        @ui.page('/Clock')
        def index():
            ui.add_head_html('''
                <style>
                    .clock-card {
                        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
                        border-radius: 12px !important;
                        border: none !important;
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18) !important;
                        transition: transform 0.15s ease, box-shadow 0.15s ease;
                    }
                    .clock-card:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.26) !important;
                    }
                    .clock-abbr {
                        font-size: 1.1rem;
                        font-weight: 700;
                        letter-spacing: 0.15em;
                        text-transform: uppercase;
                        color: #90caf9;
                    }
                    .clock-full-name {
                        font-size: 0.9rem;
                        color: rgba(255, 255, 255, 0.55);
                        letter-spacing: 0.03em;
                    }
                    .clock-time {
                        font-size: clamp(1.6rem, 7vw, 3rem);
                        font-weight: 700;
                        font-family: 'Courier New', monospace;
                        color: #ffffff;
                        letter-spacing: 0.05em;
                        line-height: 1.1;
                    }
                    .clock-date {
                        font-size: 0.9rem;
                        color: rgba(255, 255, 255, 0.5);
                    }
                    .clock-remove-btn .q-btn {
                        color: rgba(255, 255, 255, 0.35) !important;
                    }
                    .clock-remove-btn .q-btn:hover {
                        color: rgba(255, 255, 255, 0.85) !important;
                    }
                </style>
            ''')

            with ui.header().classes('bg-primary text-white h-16'):
                with ui.row().classes('w-full h-full items-center justify-between px-4'):
                    ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')

            active = load_active()
            clock_labels = []

            @ui.refreshable
            def clock_grid():
                nonlocal clock_labels
                clock_labels = []
                with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-4 w-full'):
                    for abbr, zone, full_name in active:
                        with ui.card().classes('w-full clock-card'):
                            with ui.card_section().classes('w-full'):
                                with ui.row().classes('w-full justify-between items-start clock-remove-btn'):
                                    ui.label(abbr).classes('clock-abbr')
                                    ui.button(icon='close', on_click=lambda a=abbr: remove_tz(a)).props('flat round dense')
                                ui.label(full_name).classes('clock-full-name')
                                time_el = ui.label('').classes('clock-time mt-3')
                                date_el = ui.label('').classes('clock-date mt-1')
                        clock_labels.append((zone, time_el, date_el))

            def remove_tz(abbr):
                nonlocal active
                active = [tz for tz in active if tz[0] != abbr]
                save_active(active)
                clock_grid.refresh()
                refresh_select()

            def add_tz():
                nonlocal active
                if not tz_select.value:
                    return
                abbr = tz_select.value
                entry = next((list(tz) for tz in ALL_TIMEZONES if tz[0] == abbr), None)
                if entry:
                    active.append(entry)
                    save_active(active)
                    clock_grid.refresh()
                    tz_select.value = None
                    refresh_select()

            def refresh_select():
                active_abbrs = {tz[0] for tz in active}
                tz_select.options = {tz[0]: f'{tz[0]} — {tz[2]}' for tz in ALL_TIMEZONES if tz[0] not in active_abbrs}
                tz_select.update()

            with ui.column().classes('w-full max-w-3xl mx-auto gap-4 p-4'):
                ui.markdown('## Clock')

                with ui.card().classes('w-full'):
                    with ui.card_section().classes('w-full'):
                        ui.label('Active Time Zones').classes('text-lg font-bold')
                    with ui.card_section().classes('w-full'):
                        clock_grid()

                with ui.card().classes('w-full'):
                    with ui.card_section().classes('w-full'):
                        ui.label('Add Time Zone').classes('text-lg font-bold')
                        active_abbrs = {tz[0] for tz in active}
                        tz_select = ui.select(
                            options={tz[0]: f'{tz[0]} — {tz[2]}' for tz in ALL_TIMEZONES if tz[0] not in active_abbrs},
                            label='Select a time zone'
                        ).classes('w-full')
                        with ui.row().classes('w-full justify-end mt-2'):
                            ui.button('Add', icon='add', on_click=add_tz, color='primary')

            def tick():
                for zone, time_el, date_el in clock_labels:
                    tz = pytz.timezone(zone)
                    now = datetime.now(tz)
                    time_el.set_text(now.strftime('%H:%M:%S'))
                    date_el.set_text(now.strftime('%a, %d %b %Y'))

            tick()
            ui.timer(1.0, tick)
