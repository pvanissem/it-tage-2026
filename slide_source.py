"""Read our small, documented slide-Markdown format (standard library only)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAYOUTS = {'hero', 'statement', 'cards', 'timeline', 'split', 'journey', 'pairs',
           'platform', 'architecture', 'demo', 'terminal', 'evidence', 'closing', 'speaker'}
FIELDS = {'id', 'chapter', 'layout', 'minutes', 'sources', 'backup', 'portrait'}


def scalar(value):
    """Plain strings, JSON double quotes, or YAML-style single quotes."""
    if value.startswith('"'):
        result = json.loads(value)
        if not isinstance(result, str):
            raise ValueError('Erwartet wird ein Textwert.')
        return result
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise ValueError('Nicht geschlossener Textwert.')
        return value[1:-1].replace("''", "'")
    return value


def key_values(rows, allowed):
    result = {}
    for row in rows:
        if not row.strip():
            continue
        key, separator, value = row.partition(':')
        key = key.strip()
        if not separator or key not in allowed:
            raise ValueError(f'Unbekanntes oder ungültiges Feld: {row}')
        if key in result:
            raise ValueError(f'Doppeltes Feld: {key}')
        result[key] = value.strip()
    return result


def sections(rows, heading):
    """Split structural headings, but never headings inside fenced code."""
    before, found = [], []
    current = before
    fenced = False
    for row in rows:
        if row.startswith('```'):
            fenced = not fenced
        if not fenced and row.startswith(heading):
            current = []
            found.append((row[len(heading):].strip(), current))
        else:
            current.append(row)
    if fenced:
        raise ValueError('Nicht geschlossener Codeblock (```).')
    return before, found


def block_text(rows):
    return '\n'.join(rows).strip()


def fenced_text(rows, language):
    rows = block_text(rows).splitlines()
    if len(rows) < 2 or rows[0] != f'```{language}' or rows[-1] != '```':
        raise ValueError(f'Erwartet wird genau ein ```{language}-Codeblock.')
    return '\n'.join(rows[1:-1])


def parse_slide(text, filename='<Folie>'):
    try:
        return _parse_slide(text)
    except (ValueError, KeyError) as error:
        raise ValueError(f'{filename}: {error}') from error


def _parse_slide(text):
    rows = text.splitlines()
    if not rows or rows[0] != '---':
        raise ValueError('Metadaten müssen mit --- beginnen.')
    try:
        end = rows.index('---', 1)
    except ValueError:
        raise ValueError('Abschließendes --- der Metadaten fehlt.') from None
    metadata = key_values(rows[1:end], FIELDS)
    missing = (FIELDS - {'backup', 'portrait'}) - metadata.keys()
    if missing:
        raise ValueError(f'Fehlende Metadaten: {", ".join(sorted(missing))}')
    slide = {key: scalar(metadata[key]) for key in ('id', 'chapter', 'layout')}
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slide['id']):
        raise ValueError('id muss eine stabile Kleinbuchstaben-/Ziffern-ID mit Bindestrichen sein.')
    if not slide['chapter'] or slide['layout'] not in LAYOUTS:
        raise ValueError('Kapitel fehlt oder Layout ist unbekannt.')
    if not re.fullmatch(r'\d+', metadata['minutes']):
        raise ValueError('minutes muss eine nichtnegative ganze Zahl sein.')
    slide['minutes'] = int(metadata['minutes'])
    sources = metadata['sources']
    if not (sources.startswith('[') and sources.endswith(']')):
        raise ValueError('sources muss eine Liste wie [S01, U02] sein.')
    slide['sources'] = [scalar(part.strip()) for part in sources[1:-1].split(',')]
    if not all(re.fullmatch(r'[A-Z]\d\d', source) for source in slide['sources']):
        raise ValueError('sources muss gültige Quellen-IDs enthalten, etwa [S01, U02].')
    if 'backup' in metadata:
        if metadata['backup'] not in {'true', 'false'}:
            raise ValueError('backup muss true oder false sein.')
        slide['backup'] = metadata['backup'] == 'true'
    if 'portrait' in metadata:
        portrait = scalar(metadata['portrait'])
        if slide['layout'] != 'speaker' or not re.fullmatch(r'portraits/[a-z0-9-]+\.(jpg|jpeg|png|webp)', portrait):
            raise ValueError('portrait benötigt das Layout speaker und eine lokale Datei unter portraits/.')
        slide['portrait'] = portrait

    preamble, parts = sections(rows[end + 1:], '## ')
    introduction = block_text(preamble).splitlines()
    if not introduction or not introduction[0].startswith('# '):
        raise ValueError('Ein Folientitel mit # fehlt.')
    title = [introduction[0][2:]]
    position = 1
    while position < len(introduction) and introduction[position].strip():
        title.append(introduction[position])
        position += 1
    slide['title'] = block_text(title)
    if not slide['title']:
        raise ValueError('Der Folientitel darf nicht leer sein.')
    lead = block_text(introduction[position:])
    if lead:
        slide['lead'] = lead
    seen = set()
    for name, content in parts:
        if name in seen:
            raise ValueError(f'Doppelter Abschnitt: {name}')
        seen.add(name)
        if name in {'Kernaussage', 'Sprechernotizen'}:
            slide['takeaway' if name == 'Kernaussage' else 'notes'] = block_text(content)
        elif name == 'Karten':
            before, cards = sections(content, '### ')
            if block_text(before) or not cards:
                raise ValueError('Karten müssen mit ### Kartentitel beginnen.')
            slide['items'] = []
            for title, card_rows in cards:
                card_rows = block_text(card_rows).splitlines()
                attributes = []
                while card_rows and card_rows[0].startswith('> '):
                    attributes.append(card_rows.pop(0)[2:])
                item = {'title': title, 'text': block_text(card_rows)}
                item.update({key: scalar(value) for key, value in
                             key_values(attributes, {'number', 'url'}).items()})
                if not title or not item['text']:
                    raise ValueError('Jede Karte braucht einen Titel und Text.')
                if 'url' in item and not re.fullmatch(r'https?://[^\s<>"\x27]+', item['url']):
                    raise ValueError('Karten-URLs müssen absolute HTTP(S)-URLs sein.')
                slide['items'].append(item)
        elif name == 'Code':
            slide['code'] = fenced_text(content, 'text')
        elif name == 'Diagramm':
            slide['diagram'] = json.loads(fenced_text(content, 'json'))
        else:
            raise ValueError(f'Unbekannter Abschnitt: {name}')
    for key in ('takeaway', 'notes'):
        if not slide.get(key):
            raise ValueError(f'Kernaussage oder Sprechernotizen fehlen ({key}).')
    if slide['layout'] == 'platform':
        validate_diagram(slide.get('diagram'))
    elif 'diagram' in slide:
        raise ValueError('Diagramm benötigt das Layout platform.')
    if 'diagram' in slide and ('items' in slide or 'code' in slide):
        raise ValueError('Plattformdiagramme können nicht mit Karten oder Code kombiniert werden.')
    return slide


def validate_diagram(diagram):
    keys = {'products', 'salesPlatform', 'crossCutting', 'foundation', 'capabilities', 'highlight'}
    if not isinstance(diagram, dict) or set(diagram) != keys:
        raise ValueError('Plattformdiagramm benötigt products, salesPlatform, crossCutting, foundation, capabilities und highlight.')
    for key in ('products', 'crossCutting', 'capabilities'):
        if not isinstance(diagram[key], list) or not diagram[key] or not all(isinstance(value, str) and value for value in diagram[key]):
            raise ValueError(f'Diagrammfeld {key} muss eine nichtleere Textliste sein.')
    for key in ('salesPlatform', 'foundation', 'highlight'):
        if not isinstance(diagram[key], str) or not diagram[key]:
            raise ValueError(f'Diagrammfeld {key} muss Text enthalten.')
    if diagram['capabilities'].count(diagram['highlight']) != 1:
        raise ValueError('highlight muss genau einen Plattformbaustein markieren.')


def load_deck(root=ROOT):
    root = Path(root)
    data = json.loads((root / 'deck.json').read_text(encoding='utf-8'))
    for key in ('title', 'subtitle', 'event', 'version', 'speakers'):
        if not isinstance(data.get(key), str) or not data[key]:
            raise ValueError(f'deck.json: Textfeld {key} fehlt.')
    files = list((root / 'slides').glob('*.md'))
    if not files:
        raise ValueError('slides/: Keine Markdown-Folien gefunden.')
    for path in files:
        if not re.fullmatch(r'\d{2,}-[a-z0-9-]+\.md', path.name):
            raise ValueError(f'{path.name}: Dateiname muss mit einer mindestens zweistelligen Nummer beginnen.')
    files.sort(key=lambda path: (int(path.name.split('-', 1)[0]), path.name))
    slides, ids = [], set()
    for path in files:
        slide = parse_slide(path.read_text(encoding='utf-8'), path.name)
        if 'portrait' in slide and not (root / slide['portrait']).is_file():
            raise ValueError(f'{path.name}: Porträtdatei fehlt: {slide["portrait"]}')
        if slide['id'] in ids:
            raise ValueError(f'{path.name}: Doppelte Folien-ID {slide["id"]}')
        ids.add(slide['id'])
        slides.append(slide)
    data['slides'] = slides
    return data
