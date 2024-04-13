**Klassifizierung**: Dieses Tool ermöglicht es, eine Liste von Texten bestimmten, vordefinierten Kategorien zuzuordnen. Jeder Text kann dabei mehreren Kategorien zugeordnet werden. Folgende Inputformate werden unterstützt:

1. **Demo-Modus**: Hierbei ist keine Eingabe erforderlich, da der Input vordefiniert ist. Der Demo-Datensatz umfasst 20 Antworten von Schülern auf die Frage: "Was gefällt dir besonders gut an Basel?" Bei einer Befragung solchen offenen Fragen, das heisst Fragen, die eine Freitextantwort erlauben, können auf diese Weise tausende von Antworten kategorisiert werden und die Antworten z.B. grafisch ausgewertet werden.

2. **csv/xlsx Datei hochladen**: Bei dieser Option können die Text wie auch die Kategorien als Dateien im Excel oder Komma-separierten (csv) Format hochgeladen werden. Die Texte müssen im folgendem Format vorliegen:
    ```
    Texte:
    text_id; text
    1; Mir gefällt das Münster und das Baden im Rhein.
    2; Ich finde toll, dass man mit dem Tram überall hinkommt.

    Kategorien:
    cat_id; Kategorie
    1; Verkehr
    2; Kultur, Fasnacht
    3; Sport, FCB
    4; Restaurants
    ```

    Überprüfe zunächst die Einstellungen unter dem Menüpunkt **⚙️ Einstellungen**. Anschliessend kannst eine oder mehrere Dateien hochladen. Es ist auch möglich, mehrere Dateien in einem Zip-Archiv zu verpacken. Beachte, dass das Archiv eine maximale Grösse von 100 MB nicht überschreiten darf.

    Das Zip-Archiv kann über den Download-Button heruntergeladen werden. Die Ergebnisse der Klassifizierung werden in einem Zip-Archiv als eine oder mehrere Textdateien zurückgegeben. Diese Dateien tragen den gleichen Namen wie die ursprünglichen CSV- oder XLSX-Dateien.

3. **Interaktive Eingabe**: Bei dieser Option können die Texte und Kategorien direkt im Eingabefeld eingegeben werden. Dieser Modus eignet sich zum Beispiel um die Sensitivität des Modells zu testen oder um die Funktionsweise des Tools zu demonstrieren.

**Anwendungsmöglichkeiten**:

- **Klassifizierung von Texten und Dokumenten**: Beliebige Texte und Dokumente können nach vorgegebenen Kategorien klassifiziert werden.

- **Sentimentanalyse**: Texte oder Dokumentinhalte werden in die festen Kategorien positiv, negativ oder neutral eingeordnet. Dies könnte beispielsweise für die Analyse von Tweets mit dem Hashtag #Basel oder anderen umfangreichen Textsammlungen, wie Kundenfeedback, verwendet werden.