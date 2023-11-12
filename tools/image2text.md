**image2text** liefert eine Textbeschreibung von Bildern. Es nutzt die OpenAI Vision API und basiert auf dem Modell `gpt-4-vision-preview`. Voraussetzung ist, dass die Bilddatei als URL im jpg- oder png-Format vorliegt. Nachdem die Bildbeschreibung in Textform generiert wurde, bietet sie dieselben Verarbeitungsmöglichkeiten wie anderer Text: Die Beschreibungen können indexiert, durchsucht, kategorisiert usw. werden.

**Anwendungsmöglichkeiten**:

**Kategorisierung**: Bilder lassen sich anhand ihrer Beschreibungen in Kategorien einteilen. Nach der initialen Kategorisierung der Bildsammlung können die Bilder in den jeweiligen Kategorien effizient durchsucht werden.

**Bildsuche**: Anhand der generierten Beschreibungen können Bilder gezielt gesucht werden. Wie bei der Kategorisierung muss die Bildsammlung zunächst durchlaufen werden, um die Beschreibungen zu generieren. Anschließend ist eine durchsuchbare Kategorisierung verfügbar.

**Quantitative Analysen**: Anstelle einer allgemeinen Beschreibung können spezifische Fragen an das Bild gestellt werden, wie z.B. "Wie viele Personen sind auf diesem Bild zu sehen?" oder "Wie viele Fahrzeuge sind auf dem Bild erkennbar?". Dies ermöglicht eine detailliertere und zielgerichtete Analyse der Bildinhalte.

