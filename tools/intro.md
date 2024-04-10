## Willkommen in der DataAlchemy-Toolbox

{}

Die DataAlchemy Toolbox (DATx) ist eine Sammlung von Werkzeugen zur Verarbeitung unstrukturierter Daten (Text, Audio, Bilder, Video). Sie umfasst Methoden, die für die Aufbereitung dieser Daten notwendig sind. Die Verfügbarkeit und die Eigenschaften der einzelnen Werkzeuge sind in der nachstehenden Tabelle aufgelistet. Die Toolbox wird kontinuierlich erweitert und verbessert.

Bitte beachte, dass diese Applikation darauf abzielt, die Möglichkeiten verschiedener Large Language Model (LLM) -Technologien zu demonstrieren. Jedes Werkzeug ist so konzipiert, dass es sowohl in dieser Applikation, als auch eigenständig in einen bestehenden Prozess, integriert verwendet werden kann.

| Funktionen | Verfügbarkeit |
|------------|---------------|
| **Anonymisierung** von Texten, z.B. zur Vorbereitung für die Bearbeitung in der Cloud mit LLM-Technologien. diese Option wurde entfernt, da sie das Herunterladen eines lokalen Sprachmodells erfordert, was auf der für die Kapazität der Umgebung, auf welcher DataAlchemyToolbox zur Zeit läuft, leider sprengt. | ✅ |
| **Klassifizierung** von Texten nach vorgegebenen Kategorien | ✅ |
| **Speech2Text**: Umwandlung von Audio-Dateien in Text | ✅ |
| **Bild zu Text** erstellt Bildbeschreibungen | ✅ |
| **Zusammenfassung** von Texten aus Text- oder PDF-Dateien | ✅ |
| Übersetzung von Texten | ✅ |
| **PDF2TXT**: Umwandlung von PDF-Dateien in Text | ✅ |
| **PDF Chatbot** beantwortet Fragen zu einem geladenen Dokument | ✅ |
| **Tokenizer** gibt die Anzahl Sätze, Wörter und Tokens in Texten und Dokumenten an | ✅ |
| **Finder** erlaubt es, eine Sammlung von Dokumenten zu laden oder per csv Datei zu referenzieren und die Dokumente zu durchsuchen | ✅ |
| **Unangemessene Inhalte** verwendet das Moderation-API um Text auf problematische Inhalte zu untersuchen. | 🚧 | 
| **Text zu Audio** wandelt Texte in gesprochene Sprache um. | 🚧 | 
| **Bildgenerator** erlaubt es, Bilder in verschiedenen Formaten zu generieren. Es wird das [DALLE-3](https://openai.com/dall-e-3) API verwendet. | 🚧 |
| **Texterkennung** Erlaubt es, Texte aus Bilddateien zu extrahieren. Es wird Amazon-Textract verwendet| 🚧 |
</br>

| **Legende zur Verfügbarkeit:** | |
|----------------------------|---|
| 💡 | Idee |
| 🚧 | Im Aufbau, eingeschränkt funktionsfähig |
| 🚧✅ | Verfügbar nur im Demo-Modus |
| ✅ | Alle Funktionen implementiert |
| ✅✅ | Implementiert und umfassend getestet |
