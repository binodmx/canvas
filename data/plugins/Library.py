from nicegui import ui
import os

LIBRARY_DIR = 'data/library'

class Library:
    def __init__(self):
        os.makedirs(LIBRARY_DIR, exist_ok=True)

        @ui.page('/Library')
        def index():
            ui.query('body').style('background-color: #F2F2F7;')
            content_height = '80vh'
            col_style = f'height: {content_height}; overflow-y: auto;'

            ui.add_head_html('''
                <style>
                    body, * {
                        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif;
                    }
                    .lib-item {
                        padding: 7px 10px;
                        cursor: pointer;
                        border-radius: 8px;
                        margin: 1px 4px;
                        font-size: 0.9375rem;
                        font-weight: 400;
                        color: #1C1C1E;
                        letter-spacing: -0.01em;
                        transition: background-color 0.12s ease;
                        user-select: none;
                    }
                    .lib-item:hover { background-color: rgba(0, 0, 0, 0.05); }
                    .lib-item.active {
                        background-color: rgba(0, 122, 255, 0.12);
                        font-weight: 500;
                        color: #007AFF;
                    }
                    .lib-section-label {
                        font-size: 0.6875rem;
                        font-weight: 600;
                        letter-spacing: 0.055em;
                        text-transform: uppercase;
                        color: #6C6C70;
                    }
                    .nicegui-markdown ol { list-style-type: decimal; }
                    .nicegui-markdown ol ol { list-style-type: lower-alpha; }
                    .nicegui-markdown ol ol ol { list-style-type: lower-roman; }
                    .nicegui-markdown ul { list-style-type: disc; }
                    .nicegui-markdown ul ul { list-style-type: circle; }
                    .nicegui-markdown ul ul ul { list-style-type: square; }
                </style>
            ''')

            # ── state ──────────────────────────────────────────────────────
            state = {'book': None, 'chapter': None, 'page': None, 'path': None, 'content': '', 'editing': False}

            # ── helpers ────────────────────────────────────────────────────
            def get_books():
                if not os.path.isdir(LIBRARY_DIR):
                    return []
                return sorted([d for d in os.listdir(LIBRARY_DIR)
                               if os.path.isdir(os.path.join(LIBRARY_DIR, d))])

            def get_chapters(book):
                if not book:
                    return []
                p = os.path.join(LIBRARY_DIR, book)
                return sorted([d for d in os.listdir(p)
                               if os.path.isdir(os.path.join(p, d))]) if os.path.isdir(p) else []

            def get_pages(book, chapter):
                if not book or not chapter:
                    return []
                p = os.path.join(LIBRARY_DIR, book, chapter)
                return sorted([f for f in os.listdir(p) if f.endswith('.md')]) if os.path.isdir(p) else []

            # ── selection handlers ─────────────────────────────────────────
            def select_chapter(ch):
                state['chapter'] = ch
                state['page'] = None
                state['path'] = None
                state['content'] = ''
                state['editing'] = False
                refresh_chapters()
                refresh_pages(ch)
                note_area.refresh()

            def select_page(pg):
                state['page'] = pg
                path = os.path.join(LIBRARY_DIR, state['book'], state['chapter'], pg)
                state['path'] = path
                state['editing'] = False
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        state['content'] = f.read()
                except Exception as e:
                    ui.notify(f'Error loading file: {e}', type='negative')
                    state['content'] = ''
                refresh_pages(state['chapter'])
                note_area.refresh()

            def on_book_change(e):
                state['book'] = e.value
                state['chapter'] = None
                state['page'] = None
                state['path'] = None
                state['content'] = ''
                state['editing'] = False
                refresh_chapters()
                page_list.clear()
                note_area.refresh()

            def toggle_edit():
                state['editing'] = not state['editing']
                note_area.refresh()

            def add_chapter():
                if not state['book']:
                    ui.notify('Select a book first', type='warning')
                    return
                with ui.dialog() as dlg, ui.card().style('border-radius: 14px; padding: 20px; min-width: 300px;'):
                    ui.label('New Chapter').style('font-size: 1.0625rem; font-weight: 600; color: #1C1C1E; margin-bottom: 12px;')
                    name_input = ui.input(placeholder='Chapter name').classes('w-full')
                    with ui.row().classes('justify-end gap-2 w-full').style('margin-top: 12px;'):
                        ui.button('Cancel', on_click=dlg.close).props('flat dense size=sm').style('color: #6C6C70; font-size: 0.9375rem;')
                        def _create_chapter():
                            name = name_input.value.strip()
                            if not name:
                                ui.notify('Name cannot be empty', type='warning')
                                return
                            path = os.path.join(LIBRARY_DIR, state['book'], name)
                            os.makedirs(path, exist_ok=True)
                            dlg.close()
                            refresh_chapters()
                        ui.button('Create', on_click=_create_chapter).props('flat dense size=sm').style('color: #007AFF; font-size: 0.9375rem; font-weight: 500;')
                dlg.open()

            def add_page():
                if not state['chapter']:
                    ui.notify('Select a chapter first', type='warning')
                    return
                with ui.dialog() as dlg, ui.card().style('border-radius: 14px; padding: 20px; min-width: 300px;'):
                    ui.label('New Page').style('font-size: 1.0625rem; font-weight: 600; color: #1C1C1E; margin-bottom: 12px;')
                    name_input = ui.input(placeholder='Page name (without .md)').classes('w-full')
                    with ui.row().classes('justify-end gap-2 w-full').style('margin-top: 12px;'):
                        ui.button('Cancel', on_click=dlg.close).props('flat dense size=sm').style('color: #6C6C70; font-size: 0.9375rem;')
                        def _create_page():
                            name = name_input.value.strip()
                            if not name:
                                ui.notify('Name cannot be empty', type='warning')
                                return
                            filename = name if name.endswith('.md') else f'{name}.md'
                            path = os.path.join(LIBRARY_DIR, state['book'], state['chapter'], filename)
                            if not os.path.exists(path):
                                open(path, 'w').close()
                            dlg.close()
                            refresh_pages(state['chapter'])
                        ui.button('Create', on_click=_create_page).props('flat dense size=sm').style('color: #007AFF; font-size: 0.9375rem; font-weight: 500;')
                dlg.open()

            def save_page():
                if not state['path']:
                    ui.notify('No file selected', type='warning')
                    return
                abs_base = os.path.abspath(LIBRARY_DIR)
                abs_path = os.path.abspath(state['path'])
                if not abs_path.startswith(abs_base):
                    ui.notify('Invalid path', type='negative')
                    return
                with open(abs_path, 'w', encoding='utf-8') as f:
                    f.write(state['content'] or '')
                ui.notify('Saved!', type='positive')
                state['editing'] = False
                note_area.refresh()

            # ── list renderers ─────────────────────────────────────────────
            def refresh_chapters():
                chapter_list.clear()
                with chapter_list:
                    for ch in get_chapters(state['book']):
                        classes = 'lib-item w-full' + (' active' if ch == state['chapter'] else '')
                        lbl = ui.label(ch).classes(classes)
                        lbl.on('click', lambda _, c=ch: select_chapter(c))

            def refresh_pages(chapter):
                page_list.clear()
                with page_list:
                    for pg in get_pages(state['book'], chapter):
                        display = pg[:-3] if pg.endswith('.md') else pg
                        classes = 'lib-item w-full' + (' active' if pg == state['page'] else '')
                        lbl = ui.label(display).classes(classes)
                        lbl.on('click', lambda _, p=pg: select_page(p))

            # ── header ─────────────────────────────────────────────────────
            with ui.header().classes('bg-primary text-white h-16'):
                with ui.row().classes('w-full h-full items-center justify-between px-4'):
                    ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')

            # ── book dropdown ──────────────────────────────────────────────
            with ui.row().classes('items-center gap-3 px-4 pt-3 pb-1'):
                ui.select(
                    options=get_books(),
                    label='Book',
                    on_change=on_book_change,
                ).classes('min-w-48').style('font-size: 0.9375rem;')

            # ── 3-column layout ────────────────────────────────────────────
            with ui.row().classes('w-full flex-nowrap gap-3 px-4 pb-4'):

                # Column 1 — Chapters (~15%)
                with ui.column().classes('flex-none gap-0').style(
                    f'width: 15%; {col_style}; background: #FFFFFF; border: 1px solid #D1D1D6; border-radius: 12px; overflow: hidden;'
                ):
                    with ui.row().classes('w-full items-center justify-between px-3').style(
                        'height: 40px; min-height: 40px; max-height: 40px; border-bottom: 1px solid #E5E5EA;'
                    ):
                        ui.label('Chapters').classes('lib-section-label')
                        ui.button(icon='add', on_click=add_chapter).props('flat round dense size=sm').style('color: #007AFF;')
                    chapter_list = ui.column().classes('w-full gap-0 p-1').style('padding-right: 8px;')

                # Column 2 — Pages (~15%)
                with ui.column().classes('flex-none gap-0').style(
                    f'width: 15%; {col_style}; background: #FFFFFF; border: 1px solid #D1D1D6; border-radius: 12px; overflow: hidden;'
                ):
                    with ui.row().classes('w-full items-center justify-between px-3').style(
                        'height: 40px; min-height: 40px; max-height: 40px; border-bottom: 1px solid #E5E5EA;'
                    ):
                        ui.label('Pages').classes('lib-section-label')
                        ui.button(icon='add', on_click=add_page).props('flat round dense size=sm').style('color: #007AFF;')
                    page_list = ui.column().classes('w-full gap-0 p-1').style('padding-right: 8px;')

                # Column 3 — Note view / edit
                with ui.column().classes('flex-grow gap-0').style(
                    f'height: {content_height}; overflow: hidden; background: #FFFFFF; border: 1px solid #D1D1D6; border-radius: 12px;'
                ):

                    @ui.refreshable
                    def note_area():
                        # Column header with optional edit/save/cancel buttons
                        with ui.row().classes('w-full items-center justify-between px-3 flex-none').style(
                            'height: 40px; min-height: 40px; max-height: 40px; border-bottom: 1px solid #E5E5EA;'
                        ):
                            page_label = state['page'][:-3] if state['page'] and state['page'].endswith('.md') else (state['page'] or '')
                            ui.label(page_label).classes('lib-section-label')
                            if state['path']:
                                if state['editing']:
                                    with ui.row().classes('gap-1'):
                                        ui.button('Save', icon='check_circle_outline', on_click=save_page).props('flat dense size=sm').style('color: #007AFF; font-size: 0.8125rem; font-weight: 500;')
                                        ui.button('Cancel', icon='cancel', on_click=toggle_edit).props('flat dense size=sm').style('color: #6C6C70; font-size: 0.8125rem;')
                                else:
                                    ui.button(icon='edit_note', on_click=toggle_edit).props('flat round dense size=sm').style('color: #6C6C70;')

                        # Content area
                        if state['editing']:
                            ui.codemirror(
                                value=state['content'],
                                language='Markdown',
                                on_change=lambda e: state.update(content=e.value),
                            ).classes('w-full').style('height: calc(80vh - 52px);')
                        elif state['content']:
                            with ui.scroll_area().classes('w-full').style('height: calc(80vh - 52px);'):
                                ui.markdown(state['content'], extras=['mermaid', 'tables', 'fenced-code-blocks', 'alerts', 'latex', 'strike', 'admonitions']).classes('p-4').style('font-size: 0.9375rem; color: #1C1C1E; line-height: 1.6;')
                        else:
                            with ui.column().classes('w-full h-full items-center justify-center').style('height: calc(80vh - 52px);'):
                                ui.icon('book_2').style('font-size: 2.5rem; color: #C7C7CC;')
                                ui.label('Select a page to read').style('font-size: 0.9375rem; color: #8E8E93; margin-top: 8px;')

                    note_area()
