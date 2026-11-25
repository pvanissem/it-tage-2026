---
id: drei-schutzschichten
chapter: devkcode
layout: cards
minutes: 2
sources: [S13, S14]
---

# Zugriff begrenzen.
Änderungen nachvollziehbar machen.

## Karten

### Zugriff begrenzen
> number: 01

Datei- und Netzwerkfreigaben begrenzen, was der Agent erreichen kann.

### Zugangsdaten abschirmen
> number: 02

Beim GitLab-HTTP-Proxy verbleibt der echte Token auf dem Host. Der Agent sieht einen Sitzungstoken.

### Änderungen sichtbar machen
> number: 03

KI-Kennzeichnung von Commits und Merge Requests unterstützt menschlichen Review.

## Kernaussage

Kennzeichnung hilft beim Review. Sie ist keine technische Zugriffsgrenze.

## Sprechernotizen

Die Credential-Aussage gilt ausdrücklich für HTTP-Proxy-Routen, nicht für beliebige Environment-Credentials. Letztere können reale Secrets im Agentenprozess sichtbar machen. Git-Hooks und Tool-Guards helfen gegen versehentliche Verstöße, sind nicht lückenlos durchsetzbar. Menschlichen Review im bestehenden Softwareentwicklungsprozess verankern.
