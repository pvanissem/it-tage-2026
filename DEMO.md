# Demo-Drehbuch · Vorschlag, noch nicht durchgeführt

**Ziel:** Die Developer Journey an einem kleinen, prüfbaren Änderungsvorschlag
zeigen. Acht Minuten, plus zusammenfassende Fallback-Folie.

## Vorbereiten

- Synthetisches Java-Repository mit einer kleinen, verständlichen Eingabevalidierung.
- Beispielsweise `TaskService.createTask(String title)` mit Tests, zunächst ohne
  Behandlung leerer Titel. Kein Fachsystem, keine DEVK-Kunden-/Produktionsdaten.
- Erwartetes Verhalten vorab festlegen: `null`, leerer oder nur aus Leerzeichen
  bestehender Titel wird mit `IllegalArgumentException` abgelehnt; gültige Titel
  behalten das bisherige Verhalten.
- Kein Docker/Testcontainers, keine echten Cloudzugriffe und kein Deployment.
- Abhängigkeiten vorab außerhalb der Sandbox bereitstellen; einen verifizierten
  lokalen Testbefehl, z. B. `mvn -o test`, dokumentieren.
- Freigegebene devkcode-Version und Profil testen. Repozugriff bewusst beschränken.
- Keine weiteren Projektverzeichnisse, Credentials oder MCP-Tools nur für Showeffekte.
- Sauberen, gesonderten Demo-Branch vorbereiten. Nicht im produktiven Arbeitsrepo testen.
- Bei Aufzeichnung: echte Ausgangslage, Diff und Testausgabe sichern und datieren.

## 00:00–02:00 · Einstieg und Orientierung

Patrick zeigt das vorbereitete Beispielrepo und startet `devkcode run`.
Lofi erklärt kurz Modell / Kontext / Tools / Ausführungsgrenze.

```text
Erkläre mir dieses Beispielprojekt und den lokalen Testweg.
Lies nur das Projekt; ändere noch nichts. Nenne Unsicherheiten ausdrücklich.
```

## 02:00–03:00 · Spezifikation und Plan

```text
Wir möchten createTask um eine Eingabevalidierung ergänzen.
null, leere und nur aus Leerzeichen bestehende Titel sollen mit
IllegalArgumentException abgelehnt werden. Gültige Titel behalten
das bisherige Verhalten.

Erstelle zunächst nur einen kurzen Plan mit Testfällen.
Kein Push, kein Deployment, kein Zugriff auf externe Systeme.
Warte vor Änderungen auf meine Bestätigung.
```

Plan kurz prüfen. Nicht nur „sieht gut aus“ sagen: Welche Datei, welche Grenze,
welche Testfälle? Patrick bestätigt die vereinbarte kleine Änderung.

## 03:00–06:30 · Umsetzen und prüfen

```text
Setze den abgestimmten Plan im Projekt um und ergänze die Tests.
Führe den vorbereiteten lokalen Testbefehl aus.
Falls die Umgebung den Lauf verhindert: nichts umgehen;
nenne den Blocker und markiere die Prüfung als nicht durchgeführt.
```

Lofi kommentiert sichtbare Toolaktionen. Nicht jede Wartezeit erklären;
die Entscheidungen und Grenzen sind der Inhalt der Demo.

## 06:30–08:00 · Übergabe und Review

```text
Zeige den relevanten Diff. Fasse geändertes Verhalten, Testbefehl,
tatsächliches Testergebnis und offene Punkte zusammen.
Kein Commit und kein Push. Ich prüfe und entscheide über die Übernahme.
```

Diff fachlich gegen die Spezifikation lesen. Ein Testlauf allein reicht nicht
als Review. Die sichtbaren Ergebnisse mit der Folie „Woran wir die Änderung prüfen“ abgleichen.

## Fallback

Wenn Verbindung, Modell oder Umgebung stockt: nicht länger als eine Minute
diagnostizieren und spätestens bei 06:30 auf die nächste Folie wechseln,
damit Zeit für den Review bleibt. `#demo-fallback` zeigt **geplante Prüffälle**,
keine Testergebnisse. Am Beispiel erläutern: Was müsste im Diff und im echten
Testlauf zu sehen sein? Klar benennen, was im Live-Lauf ungeprüft geblieben ist.

## Was diese Demo nicht beweist

Keine allgemeine Produktivitätssteigerung, keine fehlerfreie Agentenautonomie,
keine abgeschlossene Cloud-Migration, keine vollständige Security-/Compliance-Freigabe.
Das synthetische Beispiel zeigt lediglich den gewünschten Arbeits- und Prüfweg.
