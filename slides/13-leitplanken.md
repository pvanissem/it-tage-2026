---
id: leitplanken
chapter: devkcode
layout: architecture
minutes: 2
sources: [S13]
---

# Was der Agent darf,
entscheidet nicht der Prompt allein.

## Karten

### Mensch

Setzt den Auftrag, prüft das Ergebnis und entscheidet über die Übernahme.

### Agentenprozess in der Sandbox

OpenCode und seine Werkzeuge laufen in dem von devkcode gesetzten Rahmen.

### Dateien

Nur gezielt freigegebene Projektpfade lesen oder beschreiben.

### Netzwerk

Profile und Regeln begrenzen, welche Dienste erreichbar sind.

## Kernaussage

nono begrenzt den laufenden Prozess: Landlock unter Linux, Seatbelt unter macOS.

## Sprechernotizen

Die Grafik ist eine vereinfachte Vertrauensgrenze: Der Mensch bleibt außerhalb des Agentenprozesses verantwortlich. nono beschränkt den laufenden Hostprozess; es gibt kein Container-Image und kein eigenes Root-Dateisystem. Netzfreigaben ergeben sich aus Profil, Presets, Gruppen und Credential-Routen. Nicht fälschlich behaupten, dass jede Integration automatisch sicher oder freigegeben ist.
