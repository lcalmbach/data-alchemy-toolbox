**Klassifizierung** erlaubt es ein, eine Liste von Texten einer definierten Sammlung von Kategorien zuzuordnen. Jeder Text kann mehreren Kategorien zugeordnet werden. es werden folgende Input Formate unterstützt:
- Im Demomode ist der Input vordefiniert und keine weitere Spezifikation ist nötig. Das Demodatensatz beinhaltet 20 Antworten an Schüler auf die Frage: "Was gefällt dir besonders gut an Basel" 
- Eine Text Input Datei in folgendem Format: 
    ```
    text_id; text
    1; Mir gefällt das Münster und das Baden im Rhein
    2; Ich finde toll, dass man mit dem Tram überall hinkommt
    
    Kategorien:
    cat_id; text
    1; Verkehr
    2; Kultur, Fasnacht
    3; Sport, FCB
    4; Restaurants
```	

Überprüfe zuerst die Einstellungen unter dem Menüpunkt **⚙️Einstellungen**. Anschliessend lade eine oder mehrer Dateien hoch. Du kannst auch mehrere Dateien in ein zip file verpacken. Allerdings darf die Datei nicht grösser als 100 MB gross sein. 

Das Zipfile kann mit dem Download-button heruntergeladen werden. Die Textdateien mit dem REsultat der Klassifizierung werden anschliessend in einem zip-File als ein oder mehrere Textdateien zurückgegeben. Die Textdateien haben den gleichen Namen wie die csv oder xlsx Dateien.