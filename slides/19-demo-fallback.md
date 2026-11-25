---
id: demo-fallback
chapter: Demo
layout: terminal
minutes: 1
sources: [D01]
---

# Woran wir die Änderung prüfen

Geplante Prüffälle für createTask – keine Testergebnisse.

## Code

```text
null             → IllegalArgumentException
""               → IllegalArgumentException
"   "            → IllegalArgumentException
"Bericht senden" → Verhalten unverändert
```

## Kernaussage

Im Review zählen der Diff und das tatsächliche Testergebnis. Ohne Testlauf bleibt die Prüfung offen.

## Sprechernotizen

Bei funktionierender Live-Demo die sichtbaren Ergebnisse mit diesen Prüffällen abgleichen. Im Fallback die erwartete Änderung und die noch offenen Prüfungen erklären. Kein Testergebnis vortäuschen. Ein späterer aufgezeichneter Demo-Lauf muss separat als solcher datiert und freigegeben werden.
