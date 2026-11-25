---
id: backup-grenzen
chapter: Backup
layout: cards
minutes: 0
sources: [S13]
backup: true
---

# Bewusste Grenzen
der Prozess-Sandbox

## Karten

### Kein Docker-Socket

Ein externer Daemon könnte die Grenzen des Agentenprozesses umgehen.

### Nicht jeder Test läuft darin

Testcontainers benötigen einen anderen Testweg; externe Infrastruktur gezielt vorbereiten.

### Kein Freigabeersatz

Read-only-Prompts und lokale Guards reduzieren nicht automatisch die Rechte eines Dienst-Tokens.

## Kernaussage

Ein engerer Aktionsraum hat praktische Kosten. Diese müssen verständlich bleiben.

## Sprechernotizen

Backup zur technischen Diskussion. README beschreibt feste lokale Ports und externe Infrastruktur als Muster, nicht den Agentenstart von Docker. Profilgrenzen und aktuelle Plattformunterstützung vor der Demo prüfen. Kein pauschales Schutzversprechen gegen Prompt Injection, Datenabfluss oder alle Hostrisiken.
