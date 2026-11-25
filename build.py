"""Generate the offline-ready deck. Python 3 standard library only."""
import html
from pathlib import Path

from slide_source import load_deck

ROOT = Path(__file__).resolve().parent


def esc(value):
    return html.escape(str(value), quote=True)


def lines(value):
    return esc(value).replace('\n', '<br>')


LOGO = '''<svg viewBox="0 0 170.08 85.04" role="img" aria-label="DEVK"><path fill="#008746" d="M0 0h170.08v85.04H0z"/><g fill="#fff"><path d="M28.35 56.69V28.35H41c3 0 7.84 0 10.6 3s2.93 8.15 2.93 11c0 12.12-6.3 14.29-14.53 14.25zm8.28-5.13h2.75a12.25 12.25 0 0 0 2.88-.29c3.14-.73 3.89-2.83 4.23-5a27.32 27.32 0 0 0 .26-3.91 24.59 24.59 0 0 0-.3-4.36 6.33 6.33 0 0 0-1.4-3.3c-1.47-1.6-3.77-1.56-5.4-1.56h-3v18.42z"/><path d="M79.93 56.69H60.16V28.35h18.79v4.81H68.08v6.04H78.6v4.71H68.07v7.19h11.86v5.59z"/><path d="M103.29 56.69H91.44l-8-28.34H92l4.41 17.9c.52 2 .64 2.61 1.08 5.1.54-2.64.72-3.1 1.2-4.89l4.85-18.11h7.75l-7.95 28.34z"/><path d="M132.01 38.71l9.72 17.98h-8.2l-6.42-12.04-3.45 4.23v7.81h-8.17V28.35h8.17v11.76l8.84-11.76h8.02l-8.51 10.36z"/></g></svg>'''


def render_platform(diagram):
    products = ''.join(f'<div class="product-cluster">{esc(label)}</div>' for label in diagram['products'])
    cross_cutting = ''.join(f'<div class="cross-cutting-topic">{esc(label)}</div>' for label in diagram['crossCutting'])
    capabilities = []
    for label in diagram['capabilities']:
        highlighted = label == diagram['highlight']
        badge = '<span class="devrel-badge">DevRel</span>' if highlighted else ''
        capabilities.append(f'<div class="platform-capability{" is-devrel" if highlighted else ""}">{badge}<span>{esc(label)}</span></div>')
    return f'''<div class="platform-diagram" role="group" aria-label="Produkt-Cluster, Vertriebs-/Verkaufsplattform und Bausteine der Internal Developer Platform">
      <div class="platform-landscape"><div class="product-and-sales"><div class="product-clusters">{products}</div><div class="sales-platform">{esc(diagram['salesPlatform'])}</div></div><div class="cross-cutting">{cross_cutting}</div></div>
      <div class="platform-foundation"><h2>{esc(diagram['foundation'])}</h2><div class="platform-capabilities">{''.join(capabilities)}</div></div>
    </div>'''


def render_slide(slide, index, total, speakers):
    layout = slide['layout']
    cards = []
    for n, item in enumerate(slide.get('items', [])):
        number = f'<span class="number">{esc(item["number"])}</span>' if 'number' in item else ''
        heading = f'<h2>{lines(item["title"])}</h2>'
        text = f'<p>{lines(item["text"])}</p>'
        if 'url' in item:
            text = f'<p><a href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer">{esc(item["text"])}</a></p>'
        cards.append(f'<div class="card card-{n + 1}">{number}{heading}{text}</div>')
    items = render_platform(slide['diagram']) if layout == 'platform' else (f'<div class="items">{"".join(cards)}</div>' if cards else '')
    lead = f'<p class="lead">{lines(slide["lead"])}</p>' if slide.get('lead') else ''
    code = f'<pre class="terminal"><code>{esc(slide["code"])}</code></pre>' if slide.get('code') else ''
    art = '<div class="orbit" aria-hidden="true"><span>Cloud</span><span>Enablement</span><span>KI</span><i></i></div>' if layout == 'hero' else ''
    if layout == 'speaker':
        if 'portrait' in slide:
            art = f'<img class="speaker-portrait" src="{esc(slide["portrait"])}" alt="Porträt von {esc(slide["title"])}">'
        else:
            art = '<div class="speaker-portrait portrait-placeholder">Foto folgt</div>'
    backup = ' · Backup' if slide.get('backup') else ''
    minute = f'{slide["minutes"]} Min.' if slide['minutes'] else 'Optional'
    return f'''<section class="slide {esc(layout)}" id="{esc(slide['id'])}" aria-labelledby="title-{index}" data-chapter="{esc(slide['chapter'])}" data-minutes="{slide['minutes']}" data-backup="{str(bool(slide.get('backup'))).lower()}">
      <header class="slide-brand">{LOGO}<span>DevRel <b> / </b> DEVK Versicherungen</span><span class="event">IT-Tage 2026 · Frankfurt</span></header>
      <div class="slide-content"><p class="eyebrow">{esc(slide['chapter'])}{backup}</p><h1 id="title-{index}">{lines(slide['title'])}</h1>{lead}{items}{code}<p class="takeaway">{lines(slide['takeaway'])}</p></div>{art}
      <footer class="slide-footer"><span>Shift Happens</span><span>{esc(speakers)}</span><span>{index:02d} / {total:02d}</span></footer>
      <aside class="speaker-notes" aria-label="Sprechernotizen"><p class="note-meta">{esc(slide['chapter'])} · {minute}{backup}</p><p>{esc(slide['notes'])}</p><p class="note-sources">Quellen: {esc(', '.join(slide['sources']))} · Zuordnung in SOURCES.md (nicht im Hosting-Paket).</p></aside>
    </section>'''


def build():
    data = load_deck(ROOT)
    slides = data['slides']
    assert len({s['id'] for s in slides}) == len(slides), 'Duplicate slide ID'
    rendered = '\n'.join(render_slide(s, i + 1, len(slides), data['speakers']) for i, s in enumerate(slides))
    toc = '\n'.join(f'<button type="button" data-slide="{esc(s["id"])}"><span>{i + 1:02d}</span><strong>{esc(s["title"].replace(chr(10), " "))}</strong><small>{esc(s["chapter"])}{" · Backup" if s.get("backup") else ""}</small></button>' for i, s in enumerate(slides))
    document = f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Shift Happens – DevRel als Treiber der KI-Transformation in der Softwareentwicklung. Vortragsdraft für die IT-Tage 2026.">
<meta name="robots" content="noindex,nofollow"><meta name="color-scheme" content="light">
<title>{esc(data['title'])} · DEVK · IT-Tage 2026</title><link rel="stylesheet" href="deck.css"><script src="deck.js" defer></script></head>
<body><a class="skip-link" href="#deck">Zum Foliensatz</a>
<main id="deck" aria-label="Vortragsfolien" tabindex="-1"><div id="stage">{rendered}</div></main>
<nav class="controls" aria-label="Präsentationssteuerung" hidden>
<div class="controls-brand">{LOGO}<span>Shift Happens <small>IT-Tage 2026 · Draft</small></span></div>
<div class="navigation"><button id="prev" type="button" aria-label="Vorherige Folie" title="Vorherige Folie (←)">←</button><span id="counter" role="status" aria-live="polite"></span><button id="next" type="button" aria-label="Nächste Folie" title="Nächste Folie (→)">→</button></div>
<div class="actions"><button id="overview" type="button" title="Folienübersicht (O)">Übersicht</button><button id="notes" type="button" title="Sprechernotizen (N)" aria-expanded="false" aria-controls="notes-panel">Notizen</button><button id="fullscreen" type="button" title="Vollbild (F)" aria-pressed="false">Vollbild</button><button id="print" type="button" title="Alle Folien als PDF drucken">PDF / Druck</button></div>
<div class="progress" aria-hidden="true"><span id="progress"></span></div></nav>
<aside id="notes-panel" aria-label="Sprechernotizen" hidden><header><h2>Sprechernotizen</h2><button id="close-notes" type="button" aria-label="Notizen schließen">×</button></header><div id="note-content"></div><p class="privacy-note">Notizen sind Teil dieser HTML-Datei, kein geschützter Privatbereich.</p></aside>
<dialog id="overview-dialog" aria-labelledby="overview-title"><header><div><p class="eyebrow">Shift Happens · {esc(data['version'])}</p><h2 id="overview-title">Folienübersicht</h2></div><button id="close-overview" type="button" aria-label="Übersicht schließen">×</button></header><div class="toc">{toc}</div><p class="help">← / → Navigation · N Notizen · O Übersicht · F Vollbild · Pos1 / Ende erste / letzte Folie</p></dialog>
<div id="notice" role="status" aria-live="polite" hidden></div>
<noscript><p class="no-js">Ohne JavaScript werden alle Folien untereinander angezeigt. Der PDF-Druck ist weiterhin möglich.</p></noscript>
</body></html>'''
    (ROOT / 'index.html').write_text(document, encoding='utf-8')
    print(f'Generated {len(slides)} slides; {sum(s["minutes"] for s in slides)} minutes + slot buffer.')


if __name__ == '__main__':
    build()
