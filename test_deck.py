"""Structure tests (stdlib); optional JS state tests when quickjs is installed."""
import importlib.util
import json
import re
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from slide_source import load_deck, parse_slide

ROOT = Path(__file__).resolve().parent
DATA = load_deck(ROOT)


class Elements(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class DeckStructure(unittest.TestCase):
    def setUp(self):
        self.markup = (ROOT / 'index.html').read_text()
        self.elements = Elements(self.markup).elements

    def test_slide_count_and_unique_ids(self):
        sections = [a for tag, a in self.elements if tag == 'section']
        self.assertEqual(len(sections), len(DATA['slides']))
        self.assertGreater(len(sections), 0)
        ids = [a['id'] for _, a in self.elements if 'id' in a]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual([a['id'] for a in sections], [s['id'] for s in DATA['slides']])

    def test_offline_dependencies_and_no_internal_links(self):
        resources = [a.get('src') or a.get('href') for tag, a in self.elements if tag in {'script', 'link', 'img'}]
        self.assertEqual(resources, ['deck.css', 'deck.js', 'portraits/patrick.jpeg'])
        for path in resources:
            self.assertTrue((ROOT / path).is_file())
        for internal in ['confluence.hv.devk.de', 'git.hv.devk.de', 'jira.devk.me', 'nexus.hv.devk.de']:
            self.assertNotIn(internal, self.markup)
        self.assertNotIn('fetch(', (ROOT / 'deck.js').read_text())
        self.assertNotIn('localStorage', (ROOT / 'deck.js').read_text())

    def test_accessibility_and_toc_targets(self):
        ids = {a['id'] for _, a in self.elements if 'id' in a}
        sections = [a for tag, a in self.elements if tag == 'section']
        for attrs in sections:
            self.assertIn(attrs['aria-labelledby'], ids)
        targets = [a['data-slide'] for _, a in self.elements if 'data-slide' in a]
        self.assertEqual(targets, [s['id'] for s in DATA['slides']])
        for tag, a in self.elements:
            if tag == 'button':
                self.assertEqual(a.get('type'), 'button')
            if tag == 'a' and a.get('target') == '_blank':
                self.assertIn('noopener', a['rel'])

    def test_notes_sources_and_timing(self):
        source_ids = set(re.findall(r'^\| (\w\d\d) \|', (ROOT / 'SOURCES.md').read_text(), re.M))
        for slide in DATA['slides']:
            self.assertGreater(len(slide['notes']), 60)
            self.assertTrue(set(slide['sources']).issubset(source_ids), slide['id'])
        self.assertEqual(sum(s['minutes'] for s in DATA['slides']), 43)
        self.assertEqual(next(s['minutes'] for s in DATA['slides'] if s['id'] == 'live-demo'), 8)

    def test_html_is_generated_from_current_data(self):
        import build
        for i, slide in enumerate(DATA['slides']):
            self.assertIn(build.render_slide(slide, i + 1, len(DATA['slides']), DATA['speakers']), self.markup)

    def test_footer_uses_speakers_and_overview_retains_version(self):
        self.assertIn(DATA['version'], self.markup)
        footers = re.findall(r'<footer class="slide-footer">(.*?)</footer>', self.markup)
        self.assertEqual(len(footers), len(DATA['slides']))
        for footer in footers:
            self.assertIn(DATA['speakers'], footer)
            self.assertNotIn('Draft', footer)
        import build
        rendered = build.render_slide(DATA['slides'][0], 1, len(DATA['slides']), 'Namen <hier>')
        self.assertIn('Namen &lt;hier&gt;', rendered)

    def test_speaker_slides_follow_the_title_and_use_local_portraits(self):
        title, lofi, patrick, *_ = DATA['slides']
        self.assertEqual([title['id'], lofi['id'], patrick['id']],
                         ['shift-happens', 'speaker-lofi', 'speaker-patrick'])
        self.assertEqual([(s['layout'], s['minutes']) for s in (lofi, patrick)], [('speaker', 1)] * 2)
        self.assertIn('portrait-placeholder">Foto folgt', self.markup)
        self.assertIn('alt="Porträt von Patrick van Issem"', self.markup)
        self.assertNotIn('397120563', self.markup)
        self.assertTrue((ROOT / patrick['portrait']).read_bytes().startswith(b'\xff\xd8\xff'))

    def test_researched_timeline_and_historical_boundaries(self):
        slides = {slide['id']: slide for slide in DATA['slides']}
        ids = list(slides)
        self.assertLess(ids.index('was-ist-ein-agent'), ids.index('warum-devkcode'))
        self.assertLess(ids.index('warum-devkcode'), ids.index('opencode-devkcode'))
        team = slides['team-im-aufbau']
        self.assertEqual(len(team['items']), 4)
        # Wording is editable content, not a technical contract.
        for item in team['items']:
            self.assertTrue(item['title'].strip())
            self.assertTrue(item['text'].strip())
        self.assertTrue({'U01', 'S20', 'S21'}.issubset(team['sources']))
        self.assertIn('S20', slides['ki-als-turbo']['sources'])
        self.assertIn('S21', slides['ki-als-turbo']['sources'])
        self.assertIn('S20', slides['warum-devkcode']['sources'])
        self.assertIn('12.11.', slides['was-2026-entstanden-ist']['notes'])
        self.assertEqual(slides['was-2026-entstanden-ist']['items'][0]['number'], '8')

    def test_kickoff_outlook_distinguishes_focus_experiment_and_open_questions(self):
        slides = {slide['id']: slide for slide in DATA['slides']}
        outlook = slides['naechster-schritt']
        self.assertEqual([item['title'] for item in outlook['items']],
                         ['Im Fokus', 'Im Experiment', 'Noch offen'])
        for slide_id in ('team-im-aufbau', 'unser-auftrag', 'opencode-devkcode', 'sdd', 'naechster-schritt'):
            self.assertIn('S24', slides[slide_id]['sources'])
        self.assertNotIn('478449336', self.markup)
        self.assertNotRegex(self.markup, r'\bDMS\b')
        self.assertNotIn('Pilot ab Januar', ' '.join(item['text'] for item in outlook['items']))

    def test_devrel_intro_precedes_the_devk_specific_context(self):
        slides = DATA['slides']
        ids = [slide['id'] for slide in slides]
        intro = ids.index('was-ist-devrel')
        self.assertEqual(ids[intro - 1:intro + 2], ['die-eigentliche-frage', 'was-ist-devrel', 'was-ihr-mitnehmt'])
        self.assertLess(ids.index('was-ist-devrel'), ids.index('unser-auftrag'))
        self.assertEqual(slides[intro]['chapter'], 'Auftakt')
        self.assertEqual(slides[intro]['minutes'], 1)
        self.assertIn('S25', slides[intro]['sources'])
        self.assertNotIn('275058113', self.markup)

    def test_one_markdown_source_per_slide(self):
        files = list((ROOT / 'slides').glob('*.md'))
        self.assertEqual(len(files), len(DATA['slides']))
        self.assertFalse((ROOT / 'slides.json').exists(), 'Keine konkurrierende JSON-Inhaltsquelle behalten')

    def test_pages_pipeline_builds_tests_and_publishes_only_runtime_files(self):
        config = (ROOT / '.gitlab-ci.yml').read_text(encoding='utf-8')
        script = config.split('  script:\n', 1)[1].split('  pages:\n', 1)[0]
        commands = [row.strip()[2:] for row in script.splitlines() if row.strip()]
        self.assertEqual(commands, ['python3 -B build.py', 'python3 -B test_deck.py',
                                    'mkdir public', 'cp index.html deck.css deck.js public/',
                                    'mkdir public/portraits', 'cp portraits/patrick.jpeg public/portraits/'])
        self.assertIn('    publish: public\n', config)
        self.assertIn('    access: developer\n', config)
        self.assertIn("    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'", config)
        reference = (ROOT / 'gitlab-pages.example.yml').read_text(encoding='utf-8')
        significant = lambda text: [row for row in text.splitlines() if row.strip() and not row.startswith('#')]
        self.assertEqual(significant(config), significant(reference))

    def test_print_rules_and_terminal_scope(self):
        css = (ROOT / 'deck.css').read_text()
        self.assertIn('@media print', css)
        self.assertIn('break-after:page', css)
        self.assertIn('pre.terminal{', css)
        self.assertNotRegex(css, r'(?<![\w.])\.terminal\{')

    def test_fullscreen_control_and_stage(self):
        elements = {a['id']: a for _, a in self.elements if 'id' in a}
        self.assertEqual(elements['fullscreen']['aria-pressed'], 'false')
        self.assertEqual(elements['deck']['tabindex'], '-1')
        self.assertEqual(elements['notes']['aria-controls'], 'notes-panel')
        self.assertIn('html.enhanced:fullscreen #deck{bottom:0}', (ROOT / 'deck.css').read_text())

    def test_platform_context(self):
        ids = [s['id'] for s in DATA['slides']]
        self.assertEqual(ids.index('plattform-kontext') + 1, ids.index('unser-auftrag'))
        slide = next(s for s in DATA['slides'] if s['id'] == 'plattform-kontext')
        self.assertIn('U02', slide['sources'])
        self.assertEqual(len(slide['diagram']['products']), 5)
        self.assertEqual(len(slide['diagram']['capabilities']), 10)
        self.assertEqual(slide['diagram']['capabilities'].count(slide['diagram']['highlight']), 1)
        import build
        rendered = build.render_platform(slide['diagram'])
        elements = Elements(rendered).elements
        self.assertEqual(sum(a.get('class') == 'platform-capability is-devrel' for _, a in elements), 1)
        for label in [*slide['diagram']['products'], *slide['diagram']['capabilities'], *slide['diagram']['crossCutting'], slide['diagram']['salesPlatform'], slide['diagram']['foundation']]:
            self.assertIn(build.esc(label), rendered)
        self.assertIn(rendered, self.markup)


SAMPLE_SLIDE = '''---
id: beispiel
chapter: Test
layout: statement
minutes: 1
sources: [S01, U02]
---

# Erste Zeile
Zweite Zeile

Einleitung mit Umlauten: äöü und einem Doppelpunkt: hier.

## Kernaussage

Eine klare Aussage.

## Sprechernotizen

Notizen für die Vortragenden.
'''


class MarkdownSource(unittest.TestCase):
    def test_slide_template_is_valid_and_not_included_in_deck(self):
        template = parse_slide((ROOT / 'SLIDE_TEMPLATE.md').read_text(encoding='utf-8'), 'SLIDE_TEMPLATE.md')
        self.assertEqual(len(template['items']), 3)
        self.assertNotIn(template['id'], [s['id'] for s in DATA['slides']])

    def test_multiline_title_lead_and_metadata(self):
        slide = parse_slide(SAMPLE_SLIDE)
        self.assertEqual(slide['title'], 'Erste Zeile\nZweite Zeile')
        self.assertIn('äöü', slide['lead'])
        self.assertEqual(slide['sources'], ['S01', 'U02'])
        self.assertEqual(slide['minutes'], 1)
        self.assertNotIn('backup', slide)

    def test_cards_numbers_links_and_line_breaks(self):
        cards = '''## Karten

### Ein Titel
> number: 01
> url: https://example.com/

Erste Textzeile
Zweite Textzeile

'''
        text = SAMPLE_SLIDE.replace('layout: statement', 'layout: cards').replace('## Kernaussage', cards + '## Kernaussage')
        item = parse_slide(text)['items'][0]
        self.assertEqual(item, {'title': 'Ein Titel', 'text': 'Erste Textzeile\nZweite Textzeile',
                                'number': '01', 'url': 'https://example.com/'})

    def test_backup_and_quoted_values(self):
        text = SAMPLE_SLIDE.replace('chapter: Test', 'chapter: "Cloud & Needs"').replace('sources: [S01, U02]', "sources: ['S01', \"U02\"]\nbackup: true")
        slide = parse_slide(text)
        self.assertTrue(slide['backup'])
        self.assertEqual(slide['chapter'], 'Cloud & Needs')
        self.assertEqual(slide['sources'], ['S01', 'U02'])
        self.assertFalse(parse_slide(text.replace('backup: true', 'backup: false'))['backup'])

    def test_code_preserves_indentation_and_structural_heading_text(self):
        code = '  eingerückt\n\n## Kernaussage\n### Kein Kartentitel\n<script>'
        text = SAMPLE_SLIDE.replace('## Kernaussage', '## Code\n\n```text\n' + code + '\n```\n\n## Kernaussage')
        slide = parse_slide(text)
        self.assertEqual(slide['code'], code)
        import build
        rendered = build.render_slide(slide, 1, 1, DATA['speakers'])
        self.assertIn('&lt;script&gt;', rendered)
        self.assertNotIn('<script>', rendered)

    def test_invalid_metadata_reports_filename(self):
        for before, after in [('id: beispiel', 'id: Ungültig'), ('minutes: 1', 'minutes: -1'),
                              ('layout: statement', 'layout: unbekannt'),
                              ('chapter: Test', 'chapter: Test\nchapter: Doppelung'),
                              ('chapter: Test', 'chapter: Test\nunknown: value'),
                              ('sources: [S01, U02]', 'sources: S01'),
                              ('sources: [S01, U02]', 'sources: []'),
                              ('sources: [S01, U02]', 'sources: [S01]\nbackup: yes'),
                              ('minutes: 1\n', '')]:
            with self.subTest(after=after), self.assertRaisesRegex(ValueError, 'kaputt.md:'):
                parse_slide(SAMPLE_SLIDE.replace(before, after), 'kaputt.md')

    def test_invalid_or_missing_sections(self):
        cases = [SAMPLE_SLIDE.replace('## Sprechernotizen', '## Unbekannt'),
                 SAMPLE_SLIDE + '\n## Kernaussage\nDoppelt',
                 SAMPLE_SLIDE.split('## Sprechernotizen')[0],
                 SAMPLE_SLIDE.replace('# Erste Zeile', 'Erste Zeile'),
                 SAMPLE_SLIDE.replace('## Kernaussage', '## Code\n```text\nOffen\n## Kernaussage')]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_slide(text)

    def test_rejects_malformed_cards_and_unsafe_urls(self):
        for content in ['Kein Kartentitel', '### Titel', '### Titel\n> number: 1\n> number: 2\nText',
                        '### Titel\n> url: javascript:alert(1)\nText']:
            with self.subTest(content=content), self.assertRaises(ValueError):
                parse_slide(SAMPLE_SLIDE.replace('## Kernaussage', '## Karten\n' + content + '\n\n## Kernaussage'))

    def test_rejects_invalid_diagram(self):
        diagram = next(s['diagram'] for s in DATA['slides'] if s['layout'] == 'platform')
        for broken in [{}, dict(diagram, highlight='Fehlt'), dict(diagram, products='Keine Liste')]:
            text = SAMPLE_SLIDE.replace('layout: statement', 'layout: platform').replace('## Kernaussage', '## Diagramm\n\n```json\n' + json.dumps(broken) + '\n```\n\n## Kernaussage')
            with self.subTest(diagram=broken), self.assertRaises(ValueError):
                parse_slide(text)

    def test_numeric_file_order_independent_of_ids(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = Path(folder)
            (root / 'deck.json').write_text(json.dumps({k: DATA[k] for k in ('title', 'subtitle', 'event', 'version', 'speakers')}), encoding='utf-8')
            (root / 'slides').mkdir()
            for name, slide_id in [('100-spaet.md', 'a-spaet'), ('20-frueh.md', 'z-frueh')]:
                (root / 'slides' / name).write_text(SAMPLE_SLIDE.replace('id: beispiel', 'id: ' + slide_id), encoding='utf-8')
            self.assertEqual([s['id'] for s in load_deck(root)['slides']], ['z-frueh', 'a-spaet'])

    def test_rejects_empty_deck_duplicate_ids_and_invalid_filenames(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = Path(folder)
            (root / 'deck.json').write_text(json.dumps({k: DATA[k] for k in ('title', 'subtitle', 'event', 'version', 'speakers')}), encoding='utf-8')
            (root / 'slides').mkdir()
            with self.assertRaisesRegex(ValueError, 'Keine Markdown-Folien'):
                load_deck(root)
            (root / 'slides' / '01-test.md').write_text(SAMPLE_SLIDE, encoding='utf-8')
            (root / 'slides' / '02-test.md').write_text(SAMPLE_SLIDE, encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Doppelte Folien-ID'):
                load_deck(root)
            (root / 'slides' / 'falsch.md').write_text(SAMPLE_SLIDE, encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Dateiname'):
                load_deck(root)

    def test_portrait_is_only_allowed_for_speakers_and_must_be_local(self):
        key = 'portrait: portraits/person.png\n'
        template = SAMPLE_SLIDE.replace('minutes: 1\n', key + 'minutes: 1\n')
        with self.assertRaisesRegex(ValueError, 'portrait benötigt'):
            parse_slide(template)
        speaker = template.replace('layout: statement', 'layout: speaker')
        self.assertEqual(parse_slide(speaker)['portrait'], 'portraits/person.png')
        for path in ('https://example.org/person.png', 'portraits/../person.png'):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'portrait benötigt'):
                parse_slide(speaker.replace('portraits/person.png', path))


MOCK_DOM = r'''
class Element {
  constructor(id='') { this.id=id; this.hidden=false; this.attrs={}; this.style={}; this.handlers={}; this.dataset={}; this.innerHTML=''; this.textContent=''; }
  setAttribute(k,v) { this.attrs[k]=v; }
  addEventListener(k,fn) { this.handlers[k]=fn; }
  focus() { globalThis.focused=this.id; }
  closest() { return null; }
}
const elements={};
for (const id of ['deck','prev','next','counter','progress','note-content','notes','close-notes','fullscreen','print','overview','close-overview','notice','notes-panel','overview-dialog']) elements[id]=new Element(id);
elements.deck.clientWidth=1600; elements.deck.clientHeight=900;
elements['notes-panel'].hidden=true;
const slides=slideData.map(s=> {
  const e=new Element(s.id);
  e.querySelector=selector=> selector==='h1' ? {innerText:s.title} : {innerHTML:s.notes};
  return e;
});
const buttons=slides.map(s=> {const e=new Element(); e.dataset.slide=s.id; return e;});
elements['overview-dialog'].querySelectorAll=()=>buttons;
elements['overview-dialog'].showModal=function(){this.open=true};
elements['overview-dialog'].close=function(){this.open=false};
const controls=new Element(); const docHandlers={}; const winHandlers={};
globalThis.document={
  querySelectorAll:()=>slides, querySelector:()=>controls, getElementById:id=>elements[id],
  documentElement:{classList:{add(){}}, style:{setProperty(k,v){globalThis.lastScale=v;}}},
  addEventListener:(k,fn)=>{docHandlers[k]=fn;}
};
globalThis.location={hash:initialHash};
globalThis.history={replaceState:(a,b,url)=>{if(failHistory)throw Error('file'); location.hash=url;}};
globalThis.window={addEventListener:(k,fn)=>{winHandlers[k]=fn;},print:()=>{globalThis.printed=true;}};
globalThis.setTimeout=()=>1; globalThis.clearTimeout=()=>{};
globalThis.focused=''; globalThis.printed=false;
function key(k, opts={}) {
  docHandlers.keydown({key:k,target:{closest:()=>null},preventDefault(){},...opts});
}
function check(ok,msg){if(!ok) throw Error(msg);}
'''


@unittest.skipUnless(importlib.util.find_spec('quickjs'), 'Optional quickjs not installed; structure tests still run')
class JavaScriptState(unittest.TestCase):
    def context(self, initial_hash='', fail_history=False):
        import quickjs
        ctx = quickjs.Context()
        ctx.eval('const slideData=' + json.dumps(DATA['slides']) + '; const initialHash=' + json.dumps(initial_hash) + '; const failHistory=' + str(fail_history).lower() + ';')
        ctx.eval(MOCK_DOM)
        ctx.eval((ROOT / 'deck.js').read_text())
        return ctx

    def test_navigation_and_boundaries(self):
        self.context().eval('''
          check(elements.counter.textContent===`1 / ${slides.length}`,'initial counter');
          check(elements.prev.disabled,'first slide boundary');
          key('ArrowRight'); check(!slides[1].hidden && slides[0].hidden,'next');
          check(!document.title.includes(String.fromCharCode(10)),'multiline title flattened in browser tab');
          key('constructor',{preventDefault(){throw Error('not a shortcut');}});
          key('End'); check(elements.next.disabled && !slides[slides.length-1].hidden,'last');
          key('ArrowRight'); check(!slides[slides.length-1].hidden,'clamp last');
          key('Home'); key('ArrowLeft'); check(!slides[0].hidden,'clamp first');
          check(slides.filter(s=>!s.hidden).length===1,'one visible');
        ''')

    def test_fullscreen_change_updates_button_and_refits_stage(self):
        self.context().eval('''
          document.fullscreenElement=document.documentElement;
          document.activeElement=elements.fullscreen;
          elements.deck.clientWidth=1280; elements.deck.clientHeight=720;
          docHandlers.fullscreenchange();
          check(elements.fullscreen.attrs['aria-pressed']==='true','fullscreen active');
          check(focused==='deck','focus leaves toolbar');
          check(lastScale==='0.8','fullscreen fits 1280x720');
          document.fullscreenElement=null;
          elements.deck.clientHeight=640;
          docHandlers.fullscreenchange();
          check(elements.fullscreen.attrs['aria-pressed']==='false','fullscreen exited');
          check(Number(lastScale)===640/900,'stage refits with toolbar');
        ''')

    def test_hash_and_file_history_fallback(self):
        ctx = self.context('#live-demo', True)
        ctx.eval("check(!slides.find(s=>s.id==='live-demo').hidden,'deep link'); key('ArrowRight'); check(location.hash==='demo-fallback','history fallback');")
        self.context('#%invalid').eval("check(!slides[0].hidden,'malformed hash');")
        self.context('#unknown').eval("check(!slides[0].hidden,'unknown hash');")

    def test_notes_overview_print(self):
        self.context().eval('''
          key('n'); check(!elements['notes-panel'].hidden,'notes open');
          check(focused==='close-notes','notes focus');
          key('Escape'); check(elements['notes-panel'].hidden,'notes close');
          check(focused==='notes','focus return');
          key('o'); check(elements['overview-dialog'].open,'overview');
          key('ArrowRight'); check(!slides[0].hidden,'modal blocks navigation');
          buttons[5].handlers.click(); check(!slides[5].hidden,'overview jump');
          check(!elements['overview-dialog'].open,'overview close');
          elements.print.handlers.click(); check(printed,'print invoked');
        ''')

    def test_modifiers_resize_and_touch(self):
        self.context().eval('''
          key('ArrowRight',{ctrlKey:true}); check(!slides[0].hidden,'modified ignored');
          elements.deck.clientWidth=800; elements.deck.clientHeight=450;
          winHandlers.resize(); check(lastScale==='0.5','fit');
          elements.deck.handlers.touchstart({touches:[{clientX:200,clientY:100}],target:{closest:()=>null}});
          elements.deck.handlers.touchend({changedTouches:[{clientX:100,clientY:110}]});
          check(!slides[1].hidden,'swipe next');
          elements.deck.handlers.touchstart({touches:[{clientX:100,clientY:100}],target:{closest:()=>null}});
          elements.deck.handlers.touchcancel();
          elements.deck.handlers.touchend({changedTouches:[{clientX:200,clientY:100}]});
          check(!slides[1].hidden,'cancelled touch');
        ''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
