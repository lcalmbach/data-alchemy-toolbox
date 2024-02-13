**Übersetzung** ermöglicht die Übersetzung von Texten und Dokumenten in eine Vielzahl von Zielsprachen. Ein wesentlicher Vorteil gegenüber bekannten kommerziellen Übersetzungsdiensten ist die Möglichkeit, durch die Wahl eines geeigneten und idealerweise local installierten Sprachmodells Datenschutz- und Sicherheitsanforderungen für sensible Inhalte zu erfüllen. Die derzeitige Version nutzt allerdings noch die OpenAI API, welche diese spezifischen Schutzbedingungen noch nicht vollständig erfüllt. Mit vollständiger Kontrolle über den Übersetzungsprozess lassen sich sowohl Eingabe- als auch Ausgabedaten gemäß den spezifischen Anforderungen der Anwendung anpassen. So können beispielsweise JSON-Dateien direkt als Input und Output verwendet werden.

Eingabeformate
- **Demo**: Ein Demotext wird genutzt, um die Funktionsweise des Tools zu veranschaulichen. Zusätzlicher Input ist nicht erforderlich. Du kannst jedoch den Demotext in der Textbox durch deinen eigenen ersetzen und diesen dann übersetzen lassen.
- **Eine Date**i: Du hast die Möglichkeit, eine Text- oder PDF-Datei, die übersetzt werden soll, hochzuladen. Die Datei muss im Text- oder PDF-Format vorliegen.
- **Eine URL**: Es ist möglich, eine URL anzugeben, deren Inhalt übersetzt werden soll. Auch hier muss die Datei im Text- oder PDF-Format vorliegen.
- **Schlüssel-Wert-Paare**: Du kannst eine Liste von Schlüssel-Wert-Paaren hochladen, die übersetzt werden sollen. Diese Art der Übersetzung eignet sich besonders für Codelisten oder kurzen Texten von Webseitentexte. Die Datei sollte im CSV-Format vorliegen und folgende Struktur aufweisen:
    ```vbnet
    key; value
    welcome; Willkommen
    tab; Tabelle
    ```	
    Dabei ist `key` der im Programmcode verwendete Schlüssel, welcher eindeutig sein muss. `value` ist der zu übersetzende Text. Die App fügt eine Spalte "translation" hinzu, in der die Übersetzung eingetragen wird. Der Schlüssel wird für die Übersetzung von Weboberflächen verwendet, beispielsweise wird statt `print("Willkommen")` dann `print(translate("welcome"))` genutzt. Soll lediglich eine Codeliste übersetzt werden, wäre der Schlüssel nicht erforderlich; dennoch muss die Spalte in der Eingabedatei vorhanden sein. In diesem Fall kann eine fortlaufende Nummerierung (1, 2, 3, 4) verwendet werden, wobei auf Eindeutigkeit zu achten ist.
- **Multilang JSON-Format**: Die meisten Bibliotheken zur Internationalisierung nutzen das JSON-Format für die Datenspeicherung. Dieses Format hat den Vorteil, dass übersetzte Texte einfach in die Wörterbücher des Programmiercodes integriert werden können. Das von dieser App unterstützte Format ist wie folgt strukturiert:
    ```json
    {
        "source": {
            "welcome": "Willkommen",
            "tab": "Tabelle"
        },
        "de": {
            "welcome": "Willkommen",
            "tab": "Tabelle"
        },
        "en": {
            "welcome": "Welcome",
            "tab": "Table"
        }
    }
    ```
    Der Originalinhalt wird im source-Abschnitt gespeichert. Dieser Abschnitt wird direkt von einem Abschnitt mit identischem Inhalt gefolgt, der die Sprachkennung der Zielsprache trägt, im gegebenen Beispiel 'de'. Der source-Abschnitt dient der Erfassung neuer Schlüssel und der Änderung bestehender Texte. Der zweite Abschnitt wird bei jeder Übersetzung mit den Einträgen aus source überschrieben. Fehlende Einträge in der Zielsprache bedeuten, dass der Eintrag neu ist; existiert der Eintrag, aber mit Änderungen, so ist er als geändert gekennzeichnet. Das Übersetzungstool muss daher nur Einträge übersetzen, die seit dem letzten Durchlauf Änderungen erfahren haben. Die übrigen Abschnitte enthalten die Übersetzungen in den jeweiligen Sprachen. Diese Struktur kann in einer Programmiersprache wie folgt genutzt werden:
    Ein Nutzer wählt die Sprache aus, und das Programm lädt das entsprechende Wörterbuch aus dem JSON-Format. Die Übersetzung erfolgt dann wie folgt:
    ```python
    def translate(key, lang):
        return wörterbuch[lang][key]
    print(translate("welcome", "de")
    ```
    
Anwendungsmöglichkeiten
- Übersetzung von Texten für Codelisten, Programme oder Websites mit Unterstützung spezieller Ausgabeformate wie JSON.