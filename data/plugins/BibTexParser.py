from nicegui import ui

class BibTexParser:
    def __init__(self):
        @ui.page('/BibTexParser')
        def index():
            import bibtexparser # pip install bibtexparser

            FORMATS = ['IEEE', 'ACM', 'APA', 'MLA', 'Chicago']

            content_height = '75vh'

            def strip_braces(value: str) -> str:
                return value.strip('{}').replace('{', '').replace('}', '').strip()

            def get_field(entry: dict, *names, default='') -> str:
                for name in names:
                    val = entry.get(name)
                    if val is not None:
                        return strip_braces(str(val))
                return default

            def parse_authors(raw: str) -> list[str]:
                """Return list of author strings from BibTeX 'author' field."""
                if not raw:
                    return []
                parts = [a.strip() for a in raw.replace('\n', ' ').split(' and ')]
                return [p for p in parts if p]

            def fmt_author_last_initials(name: str) -> str:
                """'Doe, John Allen' or 'John Allen Doe' -> 'J. A. Doe'"""
                if ',' in name:
                    last, rest = name.split(',', 1)
                    initials = ' '.join(w[0] + '.' for w in rest.split() if w)
                    return f'{initials} {last.strip()}'
                else:
                    words = name.split()
                    if len(words) == 1:
                        return name
                    last = words[-1]
                    initials = ' '.join(w[0] + '.' for w in words[:-1])
                    return f'{initials} {last}'

            def fmt_author_last_first(name: str) -> str:
                """'Doe, John' or 'John Doe' -> 'Doe, J.'"""
                if ',' in name:
                    last, rest = name.split(',', 1)
                    first_init = rest.strip()[0] + '.' if rest.strip() else ''
                    return f'{last.strip()}, {first_init}'
                else:
                    words = name.split()
                    if len(words) == 1:
                        return name
                    return f'{words[-1]}, {words[0][0]}.'

            def fmt_author_apa(name: str) -> str:
                """'Doe, John Allen' -> 'Doe, J. A.'"""
                if ',' in name:
                    last, rest = name.split(',', 1)
                    initials = ' '.join(w[0] + '.' for w in rest.split() if w)
                    return f'{last.strip()}, {initials}'
                else:
                    words = name.split()
                    if len(words) == 1:
                        return name
                    last = words[-1]
                    initials = ' '.join(w[0] + '.' for w in words[:-1])
                    return f'{last}, {initials}'

            def join_authors_ieee(authors: list[str]) -> str:
                fmted = [fmt_author_last_initials(a) for a in authors]
                if len(fmted) > 6:
                    return fmted[0] + ' et al.'
                return ', '.join(fmted)

            def join_authors_apa(authors: list[str]) -> str:
                fmted = [fmt_author_apa(a) for a in authors]
                if len(fmted) > 7:
                    return ', '.join(fmted[:6]) + ', ... ' + fmted[-1]
                if len(fmted) == 1:
                    return fmted[0]
                return ', '.join(fmted[:-1]) + ', & ' + fmted[-1]

            def join_authors_mla(authors: list[str]) -> str:
                if not authors:
                    return ''
                if len(authors) == 1:
                    return authors[0] if ',' in authors[0] else authors[0]
                # First author Last, First; rest First Last
                first = authors[0]
                if ',' not in first:
                    words = first.split()
                    first = f'{words[-1]}, {" ".join(words[:-1])}' if len(words) > 1 else first
                if len(authors) == 2:
                    second = authors[1]
                    if ',' in second:
                        parts = second.split(',', 1)
                        second = parts[1].strip() + ' ' + parts[0].strip()
                    return f'{first}, and {second}'
                return first + ', et al.'

            def join_authors_chicago(authors: list[str]) -> str:
                if not authors:
                    return ''
                if len(authors) > 10:
                    first = authors[0]
                    if ',' not in first:
                        words = first.split()
                        first = f'{words[-1]}, {" ".join(words[:-1])}' if len(words) > 1 else first
                    return first + ' et al.'
                formatted = []
                for i, a in enumerate(authors):
                    if i == 0:
                        if ',' not in a:
                            words = a.split()
                            a = f'{words[-1]}, {" ".join(words[:-1])}' if len(words) > 1 else a
                    else:
                        if ',' in a:
                            parts = a.split(',', 1)
                            a = parts[1].strip() + ' ' + parts[0].strip()
                    formatted.append(a)
                if len(formatted) == 1:
                    return formatted[0]
                return ', '.join(formatted[:-1]) + ', and ' + formatted[-1]

            # ── Format functions ─────────────────────────────────────────────

            def fmt_ieee(entry) -> str:
                authors = parse_authors(get_field(entry, 'author'))
                author_str = join_authors_ieee(authors)
                title = get_field(entry, 'title')
                year = get_field(entry, 'year')
                etype = entry.get('ENTRYTYPE', '').lower()

                if etype == 'article':
                    journal = get_field(entry, 'journal', 'journaltitle')
                    vol = get_field(entry, 'volume')
                    num = get_field(entry, 'number')
                    pages = get_field(entry, 'pages')
                    parts = [author_str, f'"{title},"' if title else '']
                    if journal:
                        parts.append(f'*{journal}*,')
                    if vol:
                        parts.append(f'vol. {vol},')
                    if num:
                        parts.append(f'no. {num},')
                    if pages:
                        parts.append(f'pp. {pages},')
                    if year:
                        parts.append(year + '.')
                    return ' '.join(p for p in parts if p)

                elif etype in ('inproceedings', 'conference'):
                    booktitle = get_field(entry, 'booktitle')
                    pages = get_field(entry, 'pages')
                    parts = [author_str, f'"{title},"' if title else '']
                    if booktitle:
                        parts.append(f'in *{booktitle}*,')
                    if year:
                        parts.append(year + ',')
                    if pages:
                        parts.append(f'pp. {pages}.')
                    return ' '.join(p for p in parts if p)

                elif etype == 'book':
                    publisher = get_field(entry, 'publisher')
                    parts = [author_str, f'*{title}*.' if title else '']
                    if publisher:
                        parts.append(publisher + ',')
                    if year:
                        parts.append(year + '.')
                    return ' '.join(p for p in parts if p)

                else:
                    parts = [p for p in [author_str, f'"{title}"' if title else '', year] if p]
                    return ' '.join(parts) + '.'

            def fmt_acm(entry) -> str:
                authors = parse_authors(get_field(entry, 'author'))
                author_str = ', '.join(fmt_author_last_first(a) for a in authors)
                title = get_field(entry, 'title')
                year = get_field(entry, 'year')
                etype = entry.get('ENTRYTYPE', '').lower()

                if etype == 'article':
                    journal = get_field(entry, 'journal', 'journaltitle')
                    vol = get_field(entry, 'volume')
                    num = get_field(entry, 'number')
                    pages = get_field(entry, 'pages')
                    doi = get_field(entry, 'doi')
                    parts = [author_str + '.' if author_str else '']
                    if year:
                        parts.append(year + '.')
                    if title:
                        parts.append(title + '.')
                    if journal:
                        s = f'*{journal}*'
                        if vol:
                            s += f' {vol}'
                        if num:
                            s += f', {num}'
                        if year:
                            s += f' ({year})'
                        if pages:
                            s += f', {pages}'
                        parts.append(s + '.')
                    if doi:
                        parts.append(f'DOI: https://doi.org/{doi}')
                    return ' '.join(p for p in parts if p)

                elif etype in ('inproceedings', 'conference'):
                    booktitle = get_field(entry, 'booktitle')
                    pages = get_field(entry, 'pages')
                    location = get_field(entry, 'address', 'location')
                    parts = [author_str + '.' if author_str else '']
                    if year:
                        parts.append(year + '.')
                    if title:
                        parts.append(title + '.')
                    if booktitle:
                        s = f'In *{booktitle}*'
                        if location:
                            s += f', {location}'
                        if pages:
                            s += f', {pages}'
                        parts.append(s + '.')
                    return ' '.join(p for p in parts if p)

                elif etype == 'book':
                    publisher = get_field(entry, 'publisher')
                    parts = [author_str + '.' if author_str else '']
                    if year:
                        parts.append(year + '.')
                    if title:
                        parts.append(f'*{title}*.')
                    if publisher:
                        parts.append(publisher + '.')
                    return ' '.join(p for p in parts if p)

                else:
                    parts = [p for p in [author_str, title, year] if p]
                    return ' '.join(parts) + '.'

            def fmt_apa(entry) -> str:
                authors = parse_authors(get_field(entry, 'author'))
                author_str = join_authors_apa(authors)
                title = get_field(entry, 'title')
                year = get_field(entry, 'year')
                etype = entry.get('ENTRYTYPE', '').lower()

                if etype == 'article':
                    journal = get_field(entry, 'journal', 'journaltitle')
                    vol = get_field(entry, 'volume')
                    num = get_field(entry, 'number')
                    pages = get_field(entry, 'pages')
                    doi = get_field(entry, 'doi')
                    parts = []
                    if author_str:
                        parts.append(author_str + '.')
                    if year:
                        parts.append(f'({year}).')
                    if title:
                        parts.append(title + '.')
                    if journal:
                        s = f'*{journal}*'
                        if vol:
                            s += f', *{vol}*'
                        if num:
                            s += f'({num})'
                        if pages:
                            s += f', {pages}'
                        parts.append(s + '.')
                    if doi:
                        parts.append(f'https://doi.org/{doi}')
                    return ' '.join(p for p in parts if p)

                elif etype in ('inproceedings', 'conference'):
                    booktitle = get_field(entry, 'booktitle')
                    pages = get_field(entry, 'pages')
                    editors = get_field(entry, 'editor')
                    parts = []
                    if author_str:
                        parts.append(author_str + '.')
                    if year:
                        parts.append(f'({year}).')
                    if title:
                        parts.append(title + '.')
                    if booktitle:
                        s = f'In '
                        if editors:
                            s += f'{editors} (Eds.), '
                        s += f'*{booktitle}*'
                        if pages:
                            s += f' (pp. {pages})'
                        parts.append(s + '.')
                    return ' '.join(p for p in parts if p)

                elif etype == 'book':
                    publisher = get_field(entry, 'publisher')
                    edition = get_field(entry, 'edition')
                    parts = []
                    if author_str:
                        parts.append(author_str + '.')
                    if year:
                        parts.append(f'({year}).')
                    t = f'*{title}*' if title else ''
                    if edition:
                        t += f' ({edition} ed.)'
                    if t:
                        parts.append(t + '.')
                    if publisher:
                        parts.append(publisher + '.')
                    return ' '.join(p for p in parts if p)

                else:
                    parts = [p for p in [author_str, f'({year}).' if year else '', title] if p]
                    return ' '.join(parts) + '.'

            def fmt_mla(entry) -> str:
                authors = parse_authors(get_field(entry, 'author'))
                author_str = join_authors_mla(authors)
                title = get_field(entry, 'title')
                year = get_field(entry, 'year')
                etype = entry.get('ENTRYTYPE', '').lower()

                if etype == 'article':
                    journal = get_field(entry, 'journal', 'journaltitle')
                    vol = get_field(entry, 'volume')
                    num = get_field(entry, 'number')
                    pages = get_field(entry, 'pages')
                    parts = []
                    if author_str:
                        parts.append(author_str + '.')
                    if title:
                        parts.append(f'"{title}."')
                    if journal:
                        s = f'*{journal}*'
                        if vol:
                            s += f', vol. {vol}'
                        if num:
                            s += f', no. {num}'
                        if year:
                            s += f', {year}'
                        if pages:
                            s += f', pp. {pages}'
                        parts.append(s + '.')
                    return ' '.join(p for p in parts if p)

                elif etype in ('inproceedings', 'conference'):
                    booktitle = get_field(entry, 'booktitle')
                    pages = get_field(entry, 'pages')
                    parts = []
                    if author_str:
                        parts.append(author_str + '.')
                    if title:
                        parts.append(f'"{title}."')
                    if booktitle:
                        parts.append(f'*{booktitle}*,')
                    if year:
                        parts.append(year + ',')
                    if pages:
                        parts.append(f'pp. {pages}.')
                    return ' '.join(p for p in parts if p)

                elif etype == 'book':
                    publisher = get_field(entry, 'publisher')
                    parts = []
                    if author_str:
                        parts.append(author_str + '.')
                    if title:
                        parts.append(f'*{title}*.')
                    if publisher:
                        parts.append(publisher + ',')
                    if year:
                        parts.append(year + '.')
                    return ' '.join(p for p in parts if p)

                else:
                    parts = [p for p in [author_str, f'"{title}"' if title else '', year] if p]
                    return ' '.join(parts) + '.'

            def fmt_chicago(entry) -> str:
                authors = parse_authors(get_field(entry, 'author'))
                author_str = join_authors_chicago(authors)
                title = get_field(entry, 'title')
                year = get_field(entry, 'year')
                etype = entry.get('ENTRYTYPE', '').lower()

                if etype == 'article':
                    journal = get_field(entry, 'journal', 'journaltitle')
                    vol = get_field(entry, 'volume')
                    num = get_field(entry, 'number')
                    pages = get_field(entry, 'pages')
                    doi = get_field(entry, 'doi')
                    parts = []
                    if author_str:
                        parts.append(author_str + '.')
                    if title:
                        parts.append(f'"{title}."')
                    if journal:
                        s = f'*{journal}*'
                        if vol:
                            s += f' {vol}'
                        if num:
                            s += f', no. {num}'
                        if year:
                            s += f' ({year})'
                        if pages:
                            s += f': {pages}'
                        parts.append(s + '.')
                    if doi:
                        parts.append(f'https://doi.org/{doi}')
                    return ' '.join(p for p in parts if p)

                elif etype in ('inproceedings', 'conference'):
                    booktitle = get_field(entry, 'booktitle')
                    pages = get_field(entry, 'pages')
                    parts = []
                    if author_str:
                        parts.append(author_str + '.')
                    if title:
                        parts.append(f'"{title}."')
                    if booktitle:
                        parts.append(f'In *{booktitle}*,')
                    if pages:
                        parts.append(f'{pages}.')
                    if year:
                        parts.append(year + '.')
                    return ' '.join(p for p in parts if p)

                elif etype == 'book':
                    publisher = get_field(entry, 'publisher')
                    address = get_field(entry, 'address')
                    parts = []
                    if author_str:
                        parts.append(author_str + '.')
                    if title:
                        parts.append(f'*{title}*.')
                    location_pub = ''
                    if address:
                        location_pub += address
                    if publisher:
                        location_pub += (': ' if location_pub else '') + publisher
                    if location_pub:
                        parts.append(location_pub + ',')
                    if year:
                        parts.append(year + '.')
                    return ' '.join(p for p in parts if p)

                else:
                    parts = [p for p in [author_str, f'"{title}"' if title else '', year] if p]
                    return ' '.join(parts) + '.'

            FORMAT_FN = {
                'IEEE': fmt_ieee,
                'ACM': fmt_acm,
                'APA': fmt_apa,
                'MLA': fmt_mla,
                'Chicago': fmt_chicago,
            }

            # ── Default BibTeX sample ────────────────────────────────────────

            DEFAULT_BIBTEX = '''@inproceedings{DBLP:conf/nips/VaswaniSPUJGKP17,
  author       = {Ashish Vaswani and
                  Noam Shazeer and
                  Niki Parmar and
                  Jakob Uszkoreit and
                  Llion Jones and
                  Aidan N. Gomez and
                  Lukasz Kaiser and
                  Illia Polosukhin},
  editor       = {Isabelle Guyon and
                  Ulrike von Luxburg and
                  Samy Bengio and
                  Hanna M. Wallach and
                  Rob Fergus and
                  S. V. N. Vishwanathan and
                  Roman Garnett},
  title        = {Attention is All you Need},
  booktitle    = {Advances in Neural Information Processing Systems 30: Annual Conference
                  on Neural Information Processing Systems 2017, December 4-9, 2017,
                  Long Beach, CA, {USA}},
  pages        = {5998--6008},
  year         = {2017},
}
'''

            # ── State ────────────────────────────────────────────────────────

            selected_format = {'value': 'IEEE'}
            output_lines = []

            def render_output():
                bibtex_str = bibtex_input.value or ''
                fmt_name = selected_format['value']
                fmt_fn = FORMAT_FN[fmt_name]
                output_lines.clear()

                if not bibtex_str.strip():
                    output_container.clear()
                    with output_container:
                        ui.label('Paste BibTeX on the left to see formatted citations.').classes('text-gray-400 italic')
                    return

                try:
                    db = bibtexparser.loads(bibtex_str)
                except Exception as e:
                    output_container.clear()
                    with output_container:
                        ui.label(f'Parse error: {e}').classes('text-red-500')
                    return

                if not db.entries:
                    output_container.clear()
                    with output_container:
                        ui.label('No entries found.').classes('text-gray-400 italic')
                    return

                output_container.clear()
                with output_container:
                    for i, entry in enumerate(db.entries, 1):
                        citation = fmt_fn(entry)
                        if fmt_name == 'IEEE':
                            citation = f'[{i}] {citation}'
                        ui.markdown(citation).classes('mb-3 leading-relaxed')
                        output_lines.append(citation)

                    ui.separator()
                    with ui.row().classes('mt-2 gap-2 items-center'):
                        n = len(db.entries)
                        ui.label(f'{n} entr{"y" if n == 1 else "ies"}').classes('text-gray-500 text-sm')

            def on_format_change(e):
                selected_format['value'] = e.value
                render_output()

            def copy_all():
                text = '\n\n'.join(output_lines)
                ui.run_javascript(f'navigator.clipboard.writeText({repr(text)})')
                ui.notify('Copied to clipboard!')

            # ── UI ───────────────────────────────────────────────────────────

            with ui.header().classes('bg-primary text-white h-16'):
                with ui.row().classes('w-full h-full items-center justify-between px-4'):
                    ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')

            with ui.row().classes('w-full justify-end px-4 pt-2 gap-2 items-center'):
                ui.label('Format:')
                ui.select(
                    options=FORMATS,
                    value='IEEE',
                    on_change=on_format_change,
                ).props('dense outlined').classes('w-32')
                ui.button('Copy All', icon='content_copy', on_click=copy_all, color='primary')

            with ui.row().classes('w-full mx-auto flex-nowrap gap-4 px-4 pb-4'):
                bibtex_input = ui.codemirror(
                    value=DEFAULT_BIBTEX,
                    language='Python',
                    on_change=lambda _: render_output(),
                ).classes(
                    'w-1/2 text-sm border border-gray-300 rounded overflow-auto'
                ).style(f'height: {content_height}; min-height: {content_height};')

                with ui.scroll_area().classes(
                    'w-1/2 border border-gray-300 rounded bg-white p-4'
                ).style(f'height: {content_height}; min-height: {content_height};'):
                    output_container = ui.column().classes('w-full')

            ui.timer(0.3, render_output, once=True)
