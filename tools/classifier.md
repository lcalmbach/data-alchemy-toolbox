**Klassifizierung**: Dieses Tool ermöglicht es, eine Liste von Texten bestimmten, vordefinierten Kategorien zuzuordnen. Jeder Text kann dabei mehreren Kategorien zugeordnet werden. Folgende Inputformate werden unterstützt:

1. **Demo-Modus**: Hierbei ist kein weiterer Input erforderlich, da der Input vordefiniert ist. Der Demodatensatz umfasst 20 Antworten von Schülern auf die Frage: "Was gefällt dir besonders gut an Basel?"

2. **Text-Input-Datei**: Diese sollte im folgenden Format vorliegen:
    ```
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

Überprüfe zunächst die Einstellungen unter dem Menüpunkt **⚙️ Einstellungen**. Anschliessend kannst eine oder mehrere Dateien hochladen. Es ist auch möglich, mehrere Dateien in einem Zip-Archiv zu verpacken. Beachten Sie jedoch, dass das Archiv eine maximale Größe von 100 MB nicht überschreiten darf.

Das Zip-Archiv kann über den Download-Button heruntergeladen werden. Die Ergebnisse der Klassifizierung werden in einem Zip-Archiv als eine oder mehrere Textdateien zurückgegeben. Diese Dateien tragen den gleichen Namen wie die ursprünglichen CSV- oder XLSX-Dateien.

**Anwendungsmöglichkeiten**:

- **Klassifizierung von Texten und Dokumenten**: Beliebige Texte und Dokumente können nach vorgegebenen Kategorien klassifiziert werden.

- **Sentimentanalyse**: Texte oder Dokumentinhalte werden in die festen Kategorien positiv, negativ oder neutral eingeordnet. Dies könnte beispielsweise für die Analyse von Tweets mit dem Hashtag #Basel oder anderen umfangreichen Textsammlungen, wie Kundenfeedback, verwendet werden.