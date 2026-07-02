# Pirates of the Pythonean

## Was ist das?
Pirates of the Pythonean ist ein Programmier-Lernspiel. Schülerinnen und Schüler schreiben echten Python-Code in einem Code-Editor, um ein Schiff zu steuern.

Das Ziel ist:
- alle Schätze einzusammeln
- nicht von gegnerischen Schiffen zerstört zu werden
- nicht mit einer Insel zu kollidieren

## Kommandos

Es gibt folgende Funktionen (Kommandos) um das Schiff zu steuern und das Spielziel zu erreichen.


| Kommando | Beschreibung | Beispiel |
| --- | --- | --- |
| `fd(distance)` | Bewegt dein Schiff um die angegebene Strecke nach vorne. | `fd(120)` |
| `lt(angle)` | Dreht dein Schiff um den angegebenen Winkel nach links (gegen den Uhrzeigersinn). | `lt(90)` |
| `rt(angle)` | Dreht dein Schiff um den angegebenen Winkel nach rechts (im Uhrzeigersinn). | `rt(45)` |
| `shoot()` | Feuert eine Kanonenkugel in die aktuelle Blickrichtung deines Schiffs. | `shoot()` |
| `collect()` | Sammelt einen Schatz ein, wenn dein Schiff nah genug am Schatz ist. | `collect()` |


## Tilemap-Layer
Die Karte basiert auf einer Tilemap mit mehreren Layern:
- `Water`
- `Island`
- `Decor1`
- `Decor2`
- weitere Deko-Layer nach demselben Muster
- `Entities` (Object Layer)

## Entity-Typen
Im Object Layer `Entities` werden diese Typen verwendet:
- `player`
- `enemy`
- `goal`

## Neue Karte mit Tiled erstellen
So legst du eine neue Karte an:

1. Öffne den Ordner `assets/levels/`.
2. Kopiere die Datei `level_template.tmx`.
3. Benenne die Kopie um, zum Beispiel in `level2.tmx`.
4. Öffne die neue Datei im Tiled Editor.
5. Bearbeite Tiles und Entities (z. B. `player`, `enemy`, `goal`) und speichere die Datei.

Damit bleibt die Layer-Struktur konsistent und neue Level lassen sich direkt im Spiel verwenden.
