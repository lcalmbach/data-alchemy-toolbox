**Sprache vereinfachen**: 

Dieses Tool ermöglicht es automatisch Texte in einfache Sprache zu übersetzen. Einfache Sprache macht Innhalte für ein breites Publikum zugänglich.

Zudem ist es möglich die komplexität eines Textes auf einer Skala von -10 bis 10 (von -10 = extrem schwer verständlich bis 10 = sehr gut verständlich) zu bewerten. Texte in Einfacher Sprache haben meist einen Wert von 0 bis 4 oder höher, Texte in Leichter Sprache 2 bis 6 oder höher.

Credits: Amt für Statistik Zürich [simply-simplify-language](https://github.com/machinelearningZH/simply-simplify-language?tab=readme-ov-file)

## Was macht diese App?

**Diese App übersetzt einen Text in Entwürfe für Einfache Sprache oder Leichte Sprache.**

Dein Text wird dazu in der App aufbereitet und an ein sogenanntes grosses Sprachmodell (LLM, Large Language Model) eines kommerziellen Anbieters geschickt. Diese Sprachmodelle sind in der Lage, Texte nach Anweisungen umzuformulieren und dabei zu vereinfachen.

**Die Texte werden teils in sehr guter Qualität vereinfacht. Sie sind aber nie 100% korrekt. Die App liefert lediglich einen Entwurf. Die Texte müssen immer von dir überprüft und angepasst werden. Insbesondere bei Leichter Sprache ist [die Überprüfung der Ergebnisse durch Prüferinnen und Prüfer aus dem Zielpublikum essentiell](https://www.leichte-sprache.org/leichte-sprache/das-pruefen/).**

### Was ist der Modus «Leichte Sprache»?
Mit dem Schalter «Leichte Sprache» kannst du das Modell anweisen, einen ***Entwurf*** in Leichter Sprache zu schreiben. Wenn Leichte Sprache aktiviert ist, kannst du zusätzlich wählen, ob das Modell alle Informationen übernehmen oder versuchen soll, sinnvoll zu verdichten. 


### Welches Sprachmodell wird verwendet?
In dieser App-Variante wird das Sprachmodell GPT-4o von [OpenAI](https://openai.com/) verwendet.
GPT-4o arbeitet schnell und gut. 100 einzelne [Normseiten](https://de.wikipedia.org/wiki/Normseite) kosten grob gerechnet 5.5 CHF an Tokenkosten (Stand Juni 2024, ohne Gewähr).


### Wie funktioniert die Bewertung der Verständlichkeit?
Wir haben einen Algorithmus entwickelt, der die Verständlichkeit von Texten auf einer Skala von -10 bis 10 bewertet. Dieser Algorithmus basiert auf diversen Textmerkmalen: Den Wort- und Satzlängen, dem [Lesbarkeitsindex RIX](https://www.jstor.org/stable/40031755), der Häufigkeit von einfachen, verständlichen, viel genutzten Worten, sowie dem Anteil an Worten aus dem Standardvokabular A1, A2 und B1. Wir haben dies systematisch ermittelt, indem wir geschaut haben, welche Merkmale am aussagekräftigsten für Verwaltungs- und Rechtssprache und deren Vereinfachung sind.

Die Bewertung kannst du so interpretieren:

- **Sehr schwer verständliche Texte** wie Rechts- oder Verwaltungstexte haben meist Werte von **-10 bis -2**.
- **Durchschnittlich verständliche Texte** wie Nachrichtentexte, Wikipediaartikel oder Bücher haben meist Werte von **-2 bis 0**.
- **Gut verständliche Texte im Bereich Einfacher Sprache und Leichter Sprache** haben meist Werte von **0 oder grösser.**.

Wir zeigen dir zusätzlich eine **grobe** Schätzung des Sprachniveaus gemäss [CEFR (Common European Framework of Reference for Languages)](https://www.coe.int/en/web/common-european-framework-reference-languages/level-descriptions) von A1 bis C2 an.  


**Anwendungsmöglichkeiten**:

- Behördendeutsch in einfache Sprache übersetzen
- Komplexität eines Textes berechnen