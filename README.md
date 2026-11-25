# Shift Happens · IT-Tage 2026

Browserbasierter Vortragsdraft im DEVK-Stil für Dr. Lofi Dewanto und Patrick van Issem.
**Draft 0.7 · Stand 24.11.2026 · nicht extern freigegeben.**

Für die Wiederaufnahme und Auslagerung des Ordners zuerst [`PLAN.MD`](PLAN.MD)
lesen: dort stehen Auftrag, Entscheidungen, Quellenkontext und eigenständige Startbefehle.

## Ansehen

[`index.html`](index.html) direkt im Browser öffnen. Keine Installation, kein CDN,
kein Login und kein Internet für den Foliensatz erforderlich.

Alternativ aus diesem Präsentationsordner:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory .
```

Dann **http://localhost:8765** aufrufen. Der lokale Server stellt auch die
Review-Dateien bereit: nur an Loopback binden, nicht öffentlich betreiben.

### Bedienung

| Funktion | Bedienung |
|---|---|
| Nächste / vorherige Folie | Pfeiltasten, Bild auf/ab oder Buttons |
| Erste / letzte Folie | Pos1 / Ende |
| Sprechernotizen | `N` oder „Notizen“; `Esc` schließt |
| Übersicht | `O` oder „Übersicht“ |
| Vollbild | `F` oder „Vollbild“, sofern vom Browser unterstützt; Steuerung unten bei Mauszeiger oder Tastaturfokus |
| Direktlink | URL mit Folien-ID, z. B. `index.html#live-demo` |
| Mobil | Horizontal wischen oder Buttons; 16:9 wird passend skaliert |
| PDF | „PDF / Druck“ oder Browser-Druckfunktion |

PDF-Druck: Hintergrundgrafiken aktivieren, Kopf-/Fußzeilen deaktivieren,
keine Ränder. Das CSS gibt ein 16:9-Seitenformat vor. Gedruckt werden **alle
30 Folien**, einschließlich der drei Backups, ohne Sprechernotizen.
Das tatsächliche Druckergebnis muss im Zielbrowser geprüft werden.

**Notizen sind keine private Presenter-Ansicht:** Sie sind im HTML enthalten und
nach einer Veröffentlichung von jedem lesbar. Interne Quellenlinks liegen daher
nur in `SOURCES.md`, nicht im Hosting-Paket. Auch Notizen vor Veröffentlichung reviewen.

## Inhalt und Timing

**27 Hauptfolien + 3 Backups.** Vorläufiger 45-Minuten-Slot:
43 Minuten verteiltes Timing, davon zwei Minuten Vorstellung, acht Minuten Demo
und fünf Minuten Fragen; zwei Minuten Puffer. Slotdauer noch bestätigen.

Der rote Faden:

1. Was Developer Relations ist, warum Cloud-Enablement dazugehört und wo das DEVK-Team in der Plattform sitzt
2. Needs verstehen: Arbeitsumgebung, Wissen, Prozesse
3. Die Reise: Cloud-Auftrag im Januar, KI-Schwerpunkt ab Februar, parallele Cloud-Needs und Toolarbeit im Juli
4. Warum devkcode entstand; OpenCode als Basis und devkcode als Ausführungsrahmen
5. Developer Journey und eine kleine, prüfbare Demo
6. Belegte Aktivitäten, Lehren und der nächste Abschnitt

Keine behaupteten Produktivitätsprozente, realisierten Budgeteinsparungen oder
abgeschlossenen Migrationen. Zukunft, Konzept und Prototyp sind gekennzeichnet.

Die Ergänzung vom 12.11. nutzt eine aufbereitete interne Zeitleiste bis 11.11.
für ausgewählte Meilensteine, nicht als vollständige Jahreschronik oder aktuellen
Produkt-/Freigabenachweis. Teamwachstum, devkcode-Entstehung und Lehren zu Wartbarkeit
und Feedback sind ergänzt; für den Kickoff-Ausblick gilt der neuere Workshopstand
unten. Die Workshop-Primärquelle wurde am 12.11. erneut
geprüft: weiterhin acht datierte durchgeführte Termine. Quellen und Aussagegrenzen
stehen in `SOURCES.md`; personenbezogene Chat-Auswertungen sind nicht im Deck.

Am 19.11. wurden Auftrag, Bedarfsanalyse, Einstiegshilfen und Developer Journey
anhand der Vorstandspräsentation vom Juli geschärft. Cloud-Begleitung und
Wissensaustausch sind die zwei Leitmotive; der „Golden Path“ ist ein Zielbild,
kein Nachweis eines ausgerollten Standards. Kickoff-Ergebnisse wurden dabei
nicht recherchiert oder vorweggenommen.

Am 24.11. wurde der Kickoff-Ergebnisentwurf vom 19.11. ausgewertet. Der Auftrag
beschreibt nun ausdrücklich die praktische Mitarbeit ohne Übernahme der Verantwortung
des Produktteams. Der Ausblick trennt die Vorbereitung einer ersten Cloud-Begleitung,
den Planning Day als Experiment und offene Fragen zu devkcode und Wirkungsmessung.
Ein fester Pilotstart im Januar oder neue Teamstandards werden nicht behauptet.

## Bearbeiten

- `slides/*.md`: **eine editierbare Markdown-Datei pro Folie**, inklusive Notizen.
- `deck.json`: übergreifende Deck-Metadaten.
- `deck.css`: Gestaltung, Hausschriften, Layouts und Druckansicht.
- `deck.js`: Navigation, Übersicht, Notizen, Touch und Vollbild.
- `slide_source.py`: liest und validiert das Folienformat.
- `build.py`: generiert das fertige `index.html`, nur Python-Standardbibliothek.

```bash
python3 -B build.py
python3 -B test_deck.py
```

Nach Änderungen an den Markdown-Dateien das HTML mit diesen Befehlen neu erstellen
und prüfen. **`index.html` nicht direkt bearbeiten**: Änderungen darin werden beim
nächsten Build überschrieben. `slides.json` wurde vollständig durch die einzelnen
Folien ersetzt; es gibt keine zweite Inhaltsquelle.

### Eine Folie bearbeiten

Beispiel: [`slides/02-die-eigentliche-frage.md`](slides/02-die-eigentliche-frage.md).

```markdown
---
id: die-eigentliche-frage
chapter: Auftakt
layout: statement
minutes: 1
sources: [S01, S02, S03]
---

# Wie wird aus einer Cloud-Plattform
ein gangbarer Weg für Teams?

Ein Team braucht mehr als Infrastruktur: eine funktionierende Arbeitsumgebung, Orientierung und einen klaren Weg bis zum Betrieb.

## Kernaussage

Unser Ausgangspunkt war der Arbeitsalltag der Teams – nicht die Suche nach einem KI-Anwendungsfall.

## Sprechernotizen

Hier stehen Hinweise für den Vortrag.
```

- `#` beginnt den Titel. Direkt folgende Zeilen gehören bis zur ersten Leerzeile
  zum Titel und erzeugen sichtbare Zeilenumbrüche.
- Der Text zwischen Titel und erstem `##`-Abschnitt ist die optionale Einleitung.
- `## Kernaussage` und `## Sprechernotizen` sind Pflichtabschnitte.
- Die Kopfzeilen sind ein bewusst kleines **YAML-kompatibles Metadatenformat**,
  kein allgemeiner YAML-Parser: eine Zeile pro Feld, keine verschachtelten Werte,
  Kommentare, YAML-Aliase oder mehrzeiligen YAML-Blöcke. Textwerte können unquotiert,
  mit JSON-Doppelanführungszeichen oder einfachen YAML-Anführungszeichen stehen.
- `minutes` ist eine nichtnegative ganze Zahl, `sources` eine Liste von IDs aus
  `SOURCES.md`. Für Backup-Folien zusätzlich `backup: true` setzen.
- Unterstützt wird **strukturelles Markdown** mit den hier beschriebenen
  Überschriften, Karten und Codeblöcken. Fließtext ist Klartext: `**fett**`, Listen,
  Inline-Links und HTML werden nicht als zusätzliche Formatierung interpretiert.
  Zeilenumbrüche in Titel, Einleitung und Kartentext sind bewusst gesetzt;
  beim Bearbeiten besser den automatischen Zeilenumbruch des Editors nutzen.
- Notizen sind weiterhin Teil des fertigen HTML, kein privater Presenter-Bereich.

### Karten, Links und Spezialfolien

Für `cards`, `split`, `journey` und die anderen Kartenlayouts:

```markdown
## Karten

### Erste Karte
> number: 01

Text der ersten Karte.

### Zweite Karte
> url: https://example.com/

Anzeigetext des Links
```

`number` und `url` sind optional und stehen direkt unter dem Kartentitel;
Links müssen absolute HTTP(S)-URLs sein. Verfügbare Layouts:
`hero`, `statement`, `cards`, `timeline`, `split`, `journey`, `pairs`,
`platform`, `architecture`, `demo`, `terminal`, `evidence`, `closing`, `speaker`.
Die bestehenden Dateien dienen als Beispiele für passende Kartenzahlen.

- Terminaltext: `## Code`, darunter genau ein eingezäunter `text`-Codeblock;
  siehe [`slides/19-demo-fallback.md`](slides/19-demo-fallback.md).
- Plattformdiagramm: `layout: platform` und `## Diagramm` mit genau einem
  `json`-Codeblock; siehe [`slides/05-plattform-kontext.md`](slides/05-plattform-kontext.md).
  Karten und zusätzlicher Terminaltext sind auf dieser Spezialfolie nicht vorgesehen.
- Vorstellung: `layout: speaker` und optional `portrait: portraits/name.png` in
  den Metadaten. Ohne Bilddatei zeigt die Folie „Foto folgt“. Neue Porträts auch
  in die Pages-Whitelist und die Tests aufnehmen.

### Reihenfolge und neue Folien

Die **Nummer am Anfang des Dateinamens** bestimmt die Reihenfolge, bei gleicher
Nummer entscheidet der Dateiname alphabetisch. Dateien umbenennen, um Folien
umzusortieren; die `id` dabei unverändert lassen, damit Direktlinks stabil bleiben.
Jede ID muss eindeutig sein. Alle `.md`-Dateien direkt in `slides/` werden eingelesen.

Für eine neue Folie [`SLIDE_TEMPLATE.md`](SLIDE_TEMPLATE.md) nach beispielsweise
`slides/27-neue-folie.md` kopieren. ID, Kapitel, Quellen, Layout und Timing anpassen,
danach bauen und testen. Die bestehenden Timingtests erwarten 43 Minuten
und acht Minuten Demo; bei bewusst geändertem Zeitplan Tests und Dokumentation
mit aktualisieren. Der Build meldet Formatfehler mit dem betreffenden Dateinamen.

Unterschiedliche Layouttypen sind bewusst knapp gehalten; längere Texte besser
in Notizen verschieben als die Folien zu überladen. Das Browserdeck benötigt
`index.html`, `deck.css`, `deck.js` und die eingebundenen lokalen Porträts,
nicht die Markdown-Quellen.

## DEVK-Gestaltung

Logo-SVG und Farbwerte stammen aus der neueren internen KI-Community-Vorlage:
DEVK-Grün `#008746`, Dunkelgrün `#005437`, Hellgrün `#8bc379`, Gelb `#fdc75f`
und ergänzend Petrol. Ahkio für Überschriften und Univers Next Pro für Text
werden ausschließlich über lokal installierte Fonts verwendet.

**Ohne Hausschriften greifen System-Fallbacks.** Keine Fontdateien wurden kopiert
oder veröffentlicht. Für finale CI-Konformität Fonts, Logo-Verwendung und Layout
mit dem DEVK-Markenteam prüfen; der Draft ist keine abgenommene Corporate-Vorlage.

## GitLab Pages · geschützte Vorschau

Das vollständige Arbeitsprojekt liegt in GitLab unter
[devrel/presentations/it-tage-2026](https://git.hv.devk.de/devrel/presentations/it-tage-2026).
Untergruppe und Projekt sind **intern** sichtbar, nicht nur für das DevRel-Team.
Die Dateien liegen direkt im Repository-Root; interne Quellen- und Review-Dateien
sind bewusst Teil dieses internen Repositories. `IDP DEVK.png` ist die Originalgrafik
der Plattform-Kontextfolie und keine Laufzeitabhängigkeit des Decks.

Die aktive [`.gitlab-ci.yml`](.gitlab-ci.yml) baut und testet das Deck bei Änderungen
auf dem Default-Branch `main` und veröffentlicht anschließend automatisch
**ausschließlich `index.html`, `deck.css`, `deck.js` und die explizit benannten
Porträts** über GitLab Pages.
Schlägt Build oder Test fehl, wird kein neues Pages-Artefakt bereitgestellt.
Die optionalen JavaScript-Tests bleiben im schlanken Python-Image übersprungen.
[`gitlab-pages.example.yml`](gitlab-pages.example.yml) ist nur noch eine Referenzkopie.

**Pages-Zugriff: nur berechtigte Projektmitglieder nach GitLab-Anmeldung**
(`pages_access_level=private`), nicht öffentlich. Die Pages-Adresse erscheint nach
erfolgreicher Bereitstellung im Projekt unter **Deploy → Pages**. Die interne
Repository-Sichtbarkeit und die strengere Pages-Zugriffsregel sind getrennte
Einstellungen. CI-Artefakt-Downloads sind zusätzlich auf Developer und höhere
Projektrollen beschränkt.

Quellenverzeichnis, Markdown-Folien, Review-Dateien und Originalgrafik werden nicht
auf Pages veröffentlicht. **Sprechernotizen stehen dagegen im HTML und sind für
Pages-Berechtigte lesbar.** Das geschützte Hosting ist keine externe Inhaltsfreigabe;
eine öffentliche Freischaltung bleibt ein gesonderter Auftrag nach Inhaltsreview.
`noindex` ist lediglich ein Suchmaschinenhinweis, kein Zugriffsschutz.

## Prüfung und offene Punkte

Siehe [`REVIEW.md`](REVIEW.md), [`SOURCES.md`](SOURCES.md) und [`DEMO.md`](DEMO.md).
Struktur- und JavaScript-Logiktests ersetzen keine visuelle Browserprüfung.
Vor dem Vortrag insbesondere Layout mit den tatsächlichen Hausschriften,
Beamerauflösung, Vollbild und PDF-Ausgabe überprüfen.

KI-unterstützt erstellt mit devkcode/opencode; fachliche und externe Freigabe ausstehend.
