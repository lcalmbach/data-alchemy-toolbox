**Interantionalisierung (i18n)** ermöglicht die Übersetzung von Texten und Dokumenten in eine Vielzahl von Zielsprachen. Ein wesentlicher Vorteil gegenüber bekannten kommerziellen Übersetzungsdiensten ist die Möglichkeit, durch die Wahl eines geeigneten Sprachmodells Datenschutz- und Sicherheitsanforderungen für sensible Inhalte zu erfüllen. Die derzeitige Version nutzt allerdings noch die OpenAI API, welche diese spezifischen Schutzbedingungen noch nicht vollständig erfüllt. Mit vollständiger Kontrolle über den Übersetzungsprozess lassen sich sowohl Eingabe- als auch Ausgabedaten gemäß den spezifischen Anforderungen der Anwendung anpassen. So können beispielsweise i18n JSON-Dateien direkt als Input und Output verwendet werden, etwa im [i18next](https://www.i18next.com/) JSON-Format.

Eingabeformate
- **Demo**: Ein Demotext wird genutzt, um die Funktionsweise des Tools zu veranschaulichen. Zusätzlicher Input ist nicht erforderlich. Du kannst jedoch den Demotext durch deinen eigenen ersetzen und diesen dann übersetzen lassen.
- **Eine Date**i: Du hast die Möglichkeit, eine Text- oder PDF-Datei hochzuladen, die übersetzt werden soll. Die Datei sollte im Text- oder PDF-Format vorliegen.
- **Eine URL**: Es ist möglich, eine URL anzugeben, deren Inhalt übersetzt werden soll. Auch hier muss die Datei im Text- oder PDF-Format vorliegen.
- **Schlüssel-Wert-Paare**: Du kannst eine Liste von Schlüssel-Wert-Paaren hochladen, die übersetzt werden sollen. Diese Art der Übersetzung eignet sich besonders für Codelisten oder Webseitentexte. Die Datei sollte im CSV-Format vorliegen und folgende Struktur aufweisen:
    ```vbnet
    Copy code
    key; value
    welcome; Willkommen
    tab; Tabelle
    ```	
    Dabei ist `key` der im Programmcode verwendete Schlüssel, welcher eindeutig sein muss. `value` ist der zu übersetzende Text. Die App fügt eine Spalte "translation" hinzu, in der die Übersetzung eingetragen wird. Der Schlüssel wird für die Übersetzung von Weboberflächen verwendet, beispielsweise wird statt `print("Willkommen")` dann `print(translate("welcome"))` genutzt. Soll lediglich eine Codeliste übersetzt werden, ist der Schlüssel nicht erforderlich; dennoch muss die Spalte in der Eingabedatei vorhanden sein. In diesem Fall kann eine fortlaufende Nummerierung (1, 2, 3, 4) verwendet werden, wobei auf Eindeutigkeit zu achten ist.
- **Multilang JSON-Format**: Viele Internationalisierungs-Bibliotheken nutzen das JSON-Format zur Datenspeicherung. Dieses Format bietet den Vorteil, dass die übersetzten Texte sehr einfach in Programmcode-Wörterbücher integriert werden können.

Anwendungsmöglichkeiten
- Übersetzung von Texten für Codelisten, Programme oder Websites mit Unterstützung spezieller Ausgabeformate wie JSON.