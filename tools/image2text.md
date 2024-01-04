**image2text** liefert eine Textbeschreibung von Bildern. Es nutzt die OpenAI Vision API und basiert auf dem Modell `gpt-4-vision-preview`. Voraussetzung ist, dass die Bilddatei als URL im jpg- oder png-Format vorliegt. Nachdem die Bildbeschreibung in Textform generiert wurde, bietet sie dieselben Verarbeitungsmöglichkeiten wie Textdokumente: Die Beschreibungen können indexiert, durchsucht, kategorisiert usw. werden. JPG Bilder können Metadaten im Exchangeable Image File Format (EXIF) enthalten. Diese werden von **image2text** zwar angezeigt aber nicht an das LLM weitergegeben. Insbesondere die Koordinaten der Aufnahme sind eien wichtige Information, die für die Bildbeschreibung verwendet werden könnte.

**Anwendungsmöglichkeiten**:

**Kategorisierung**: Bilder lassen sich anhand ihrer Beschreibungen in Kategorien einteilen. Nach der initialen Kategorisierung der Bildsammlung können die Bilder in den jeweiligen Kategorien effizient durchsucht werden.

**Bildsuche**: Anhand der generierten Beschreibungen können Bilder gezielt gesucht werden. Wie bei der Kategorisierung muss die Bildsammlung zunächst durchlaufen werden, um die Beschreibungen zu generieren. Anschließend ist eine durchsuchbare Kategorisierung verfügbar.

**Quantitative Analysen**: Anstelle einer allgemeinen Beschreibung können spezifische Fragen an das Bild gestellt werden, wie z.B. "Wie viele Personen sind auf diesem Bild zu sehen?" oder "Wie viele Fahrzeuge sind auf dem Bild erkennbar?". Dies ermöglicht eine detailliertere und zielgerichtete Analyse der Bildinhalte.

**EXIF Metadaten**: Die Kordinaten der EXIF Metadaten können über eine einfache Abfrage auf eine georeferenzierte Adressdatenbank in Adressen umgewandelt werden. Neben der Adresse können auch weitere Informationen wie das quartier, die Postleitzahl, oder die Gemeindeextrahiert werden. Dies ermöglicht eine geografische Suche von Bildinhalten mit sehr geringem Aufwand. 

