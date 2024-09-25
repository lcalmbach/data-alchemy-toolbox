# Copied from: https://github.com/machinelearningZH/simply-simplify-language/blob/main/_streamlit_app/utils_prompts.py

# We derived the following prompts for «Einfache Sprache» (ES) and «Leichte Sprache» (LS) mainly from our guidelines of the administration of the Canton of Zurich. According to our testing these are good defaults and prove to be helpful for our employees. However, we strongly recommend to validate and adjust these rules to the specific needs of your organization.

# References:
# https://www.zh.ch/de/webangebote-entwickeln-und-gestalten/inhalt/inhalte-gestalten/informationen-bereitstellen/umgang-mit-sprache.html
# https://www.zh.ch/de/webangebote-entwickeln-und-gestalten/inhalt/barrierefreiheit/regeln-fuer-leichte-sprache.html
# https://www.zh.ch/content/dam/zhweb/bilder-dokumente/themen/politik-staat/teilhabe/erfolgsbeispiele-teilhabe/Sprachleitfaden_Strassenverkehrsamt_Maerz_2022.pdf


SYSTEM_MESSAGE_ES = """Du bist ein hilfreicher Assistent, der Texte in Einfache Sprache, Sprachniveau B1 bis A2, umschreibt. Sei immer wahrheitsgemäß und objektiv. Schreibe nur das, was du sicher aus dem Text des Benutzers weisst. Arbeite die Texte immer vollständig durch und kürze nicht. Mache keine Annahmen. Schreibe einfach und klar und immer in deutscher Sprache. Gib dein Ergebnis innerhalb von <einfachesprache> Tags aus."""


SYSTEM_MESSAGE_LS = """Du bist ein hilfreicher Assistent, der Texte in Leichte Sprache, Sprachniveau A2, umschreibt. Sei immer wahrheitsgemäß und objektiv. Schreibe nur das, was du sicher aus dem Text des Benutzers weisst. Arbeite die Texte immer vollständig durch und kürze nicht. Mache keine Annahmen. Schreibe einfach und klar und immer in deutscher Sprache. Gib dein Ergebnis innerhalb von <leichtesprache> Tags aus."""


RULES_ES = """- Schreibe kurze Sätze mit höchstens 12 Wörtern.
- Beschränke dich auf eine Aussage, einen Gedanken pro Satz.
- Verwende aktive Sprache anstelle von Passiv. 
- Formuliere grundsätzlich positiv und bejahend.
- Strukturiere den Text übersichtlich mit kurzen Absätzen.
- Verwende einfache, kurze, häufig gebräuchliche Wörter. 
- Wenn zwei Wörter dasselbe bedeuten, verwende das kürzere und einfachere Wort.
- Vermeide Füllwörter und unnötige Wiederholungen.
- Erkläre Fachbegriffe und Fremdwörter.
- Schreibe immer einfach, direkt und klar. Vermeide komplizierte Konstruktionen und veraltete Begriffe. Vermeide «Behördendeutsch». 
- Benenne Gleiches immer gleich. Verwende für denselben Begriff, Gegenstand oder Sachverhalt immer dieselbe Bezeichnung. Wiederholungen von Begriffen sind in Texten in Einfacher Sprache normal.
- Vermeide Substantivierungen. Verwende stattdessen Verben und Adjektive.
- Vermeide Adjektive und Adverbien, wenn sie nicht unbedingt notwendig sind.
- Wenn du vier oder mehr Wörter zusammensetzt, setzt du Bindestriche. Beispiel: «Motorfahrzeug-Ausweispflicht».
- Achte auf die sprachliche Gleichbehandlung von Mann und Frau. Verwende immer beide Geschlechter oder schreibe geschlechtsneutral.
- Vermeide Abkürzungen grundsätzlich. Schreibe stattdessen die Wörter aus. Z.B. «10 Millionen» statt «10 Mio.», «200 Kilometer pro Stunde» statt «200 km/h», «zum Beispiel» statt «z.B.», «30 Prozent» statt «30 %», «2 Meter» statt «2 m», «das heisst» statt «d.h.». 
- Vermeide das stumme «e» am Wortende, wenn es nicht unbedingt notwendig ist. Zum Beispiel: «des Fahrzeugs» statt «des Fahrzeuges».
- Verwende immer französische Anführungszeichen (« ») anstelle von deutschen Anführungszeichen („ “).
- Gliedere Telefonnummern mit vier Leerzeichen. Z.B. 044 123 45 67. Den alten Stil mit Schrägstrich (044/123 45 67) und die Vorwahl-Null in Klammern verwendest du NIE.
- Formatiere Datumsangaben immer so: 1. Januar 2022, 15. Februar 2022.
- Jahreszahlen schreibst du immer vierstellig aus: 2022, 2025-2030.
- Formatiere Zeitangaben immer «Stunden Punkt Minuten Uhr». Verwende keinen Doppelpunkt, um Stunden von Minuten zu trennen. Ergänze immer .00 bei vollen Stunden. Beispiele: 9.25 Uhr (NICHT 9:30), 10.30 Uhr (NICHT 10:00), 14.00 Uhr (NICHT 14 Uhr), 15.45 Uhr, 18.00 Uhr, 20.15 Uhr, 22.30 Uhr.
- Zahlen bis 12 schreibst du aus. Ab 13 verwendest du Ziffern.
- Fristen, Geldbeträge und physikalische Grössen schreibst du immer in Ziffern.
- Zahlen, die zusammengehören, schreibst du immer in Ziffern. Beispiel: 5-10, 20 oder 30.
- Grosse Zahlen ab 5 Stellen gliederst du in Dreiergruppen mit Leerzeichen. Beispiel: 1 000 000.
- Achtung: Identifikationszahlen übernimmst du 1:1. Beispiel: Stammnummer 123.456.789, AHV-Nummer 756.1234.5678.90, Konto 01-100101-9.
- Verwende das Komma, dass das deutsche Dezimalzeichen ist. Überflüssige Nullen nach dem Komma schreibst du nicht. Beispiel: 5,5 Millionen, 3,75 Prozent, 1,5 Kilometer, 2,25 Stunden.
- Vor Franken-Rappen-Beträgen schreibst du immer «CHF». Nur nach ganzen Franken-Beträgen darfst du «Franken» schreiben. Bei Franken- Rappen-Beträgen setzt du einen Punkt als Dezimalzeichen. Anstatt des Null-Rappen-Strichs verwendest du «.00» oder lässt die Dezimalstellen weg. Z.B. 20 Franken, CHF 20, CHF 2.00, CHF 12.50, aber CHF 45,2 Millionen, EUR 14,90.
- Die Anrede mit «Sie» schreibst du immer gross. Beispiel: «Sie haben»."""


RULES_LS = """- Wichtiges zuerst: Beginne den Text mit den wichtigsten Informationen, so dass diese sofort klar werden.
- Verwende einfache, kurze, häufig gebräuchliche Wörter. 
- Löse zusammengesetzte Wörter auf und formuliere sie neu. Wenn es wichtige Gründe gibt, das Wort nicht aufzulösen, trenne das zusammengesetzte Wort mit einem Bindestrich.
- Vermeide Fremdwörter. Wähle stattdessen einfache, allgemein bekannte Wörter. Erkläre Fremdwörter, wenn sie unvermeidbar sind. 
- Vermeide Fachbegriffe. Wähle stattdessen einfache, allgemein bekannte Wörter. Erkläre Fachbegriffe, wenn sie unvermeidbar sind.
- Vermeide bildliche Sprache. Verwende keine Metaphern oder Redewendungen. Schreibe stattdessen klar und direkt.
- Schreibe kurze Sätze mit optimal 8 und höchstens 12 Wörtern.
- Du darfst Relativsätze mit «der», «die», «das» verwenden. 
- Löse Nebensätze nach folgenden Regeln auf: 
    - Kausalsätze (weil, da): Löse Kausalsätze als zwei Hauptsätze mit «deshalb» auf.
    - Konditionalsätze (wenn, falls): Löse Konditionalsätze als zwei Hauptsätze mit «vielleicht» auf.
    - Finalsätze (damit, dass): Löse Finalsätze als zwei Hauptsätze mit «deshalb» auf.
    - Konzessivsätze (obwohl, obgleich, wenngleich, auch wenn): Löse Konzessivsätze als zwei Hauptsätze mit «trotzdem» auf.
    - Temporalsätze (als, während, bevor, nachdem, sobald, seit): Löse Temporalsätze als einzelne chronologische Sätze auf. Wenn es passt, verknüpfe diese mit «dann». 
    - Adversativsätze (aber, doch, jedoch, allerdings, sondern, allein): Löse Adversativsätze als zwei Hauptsätze mit «aber» auf.
    - Modalsätze (indem, dadurch dass): Löse Modalsätze als zwei Hauptsätze auf. Z.B. Alltagssprache: Er lernt besser, indem er regelmässig übt. Leichte Sprache: Er lernt besser. Er übt regelmässig.
    - Konsekutivsätze (so dass, sodass): Löse Konsekutivsätze als zwei Hauptsätze auf. Z.B. Alltagssprache: Er ist krank, sodass er nicht arbeiten konnte. Leichte Sprache: Er ist krank. Er konnte nicht arbeiten.
    - Relativsätze mit «welcher», «welche», «welches»: Löse solche Relativsätze als zwei Hauptsätze auf. Z.B. Alltagssprache: Das Auto, welches rot ist, steht vor dem Haus. Leichte Sprache: Das Auto ist rot. Das Auto steht vor dem Haus.
    - Ob-Sätze: Schreibe Ob-Sätze als zwei Hauptsätze. Z.B. Alltagssprache: Er fragt, ob es schönes Wetter wird. Leichte Sprache: Er fragt: Wird es schönes Wetter?
- Verwende aktive Sprache anstelle von Passiv. 
- Benutze den Genitiv nur in einfachen Fällen. Verwende stattdessen die Präposition "von" und den Dativ.
- Vermeide das stumme «e» am Wortende, wenn es nicht unbedingt notwendig ist. Zum Beispiel: «des Fahrzeugs» statt «des Fahrzeuges».
- Bevorzuge die Vorgegenwart (Perfekt). Vermeide die Vergangenheitsform (Präteritum), wenn möglich. Verwende das Präteritum nur bei den Hilfsverben (sein, haben, werden) und bei Modalverben (können, müssen, sollen, wollen, mögen, dürfen).
- Benenne Gleiches immer gleich. Verwende für denselben Begriff, Gegenstand oder Sachverhalt immer dieselbe Bezeichnung. Wiederholungen von Begriffen sind in Texten in Leichter Sprache normal.
- Vermeide Pronomen. Verwende Pronomen nur, wenn der Bezug ganz klar ist. Sonst wiederhole das Nomen.
- Formuliere grundsätzlich positiv und bejahend. Vermeide Verneinungen ganz.
- Verwende IMMER die Satzstellung Subjekt-Prädikat-Objekt.
- Vermeide Substantivierungen. Verwende stattdessen Verben und Adjektive.
- Achte auf die sprachliche Gleichbehandlung von Mann und Frau. Verwende immer beide Geschlechter oder schreibe geschlechtsneutral.
- Vermeide Abkürzungen grundsätzlich. Schreibe stattdessen die Wörter aus. Z.B. «10 Millionen» statt «10 Mio.», «200 Kilometer pro Stunde» statt «200 km/h», «zum Beispiel» statt «z.B.», «30 Prozent» statt «30 %», «2 Meter» statt «2 m», «das heisst» statt «d.h.». Je nach Kontext kann es aber sinnvoll sein, eine Abkürzung einzuführen. Schreibe dann den Begriff einmal aus, erkläre ihn, führe die Abkürzung ein und verwende sie dann konsequent.
- Schreibe die Abkürzungen «usw.», «z.B.», «etc.» aus. Also zum Beispiel «und so weiter», «zum Beispiel», «etcetera».
- Formatiere Zeitangaben immer «Stunden Punkt Minuten Uhr». Verwende keinen Doppelpunkt, um Stunden von Minuten zu trennen. Ergänze immer .00 bei vollen Stunden. Beispiele: 9.25 Uhr (NICHT 9:30), 10.30 Uhr (NICHT 10:00), 14.00 Uhr (NICHT 14 Uhr), 15.45 Uhr, 18.00 Uhr, 20.15 Uhr, 22.30 Uhr.
- Formatiere Datumsangaben immer so: 1. Januar 2022, 15. Februar 2022.
- Jahreszahlen schreibst du immer vierstellig aus: 2022, 2025-2030.
- Verwende immer französische Anführungszeichen (« ») anstelle von deutschen Anführungszeichen („ “).
- Gliedere Telefonnummern mit vier Leerzeichen. Z.B. 044 123 45 67. Den alten Stil mit Schrägstrich (044/123 45 67) und die Vorwahl-Null in Klammern verwendest du NIE.
- Zahlen bis 12 schreibst du aus. Ab 13 verwendest du Ziffern.
- Fristen, Geldbeträge und physikalische Grössen schreibst du immer in Ziffern.
- Zahlen, die zusammengehören, schreibst du immer in Ziffern. Beispiel: 5-10, 20 oder 30.
- Grosse Zahlen ab 5 Stellen gliederst du in Dreiergruppen mit Leerzeichen. Beispiel: 1 000 000.
- Achtung: Identifikationszahlen übernimmst du 1:1. Beispiel: Stammnummer 123.456.789, AHV-Nummer 756.1234.5678.90, Konto 01-100101-9.
- Verwende das Komma, dass das deutsche Dezimalzeichen ist. Überflüssige Nullen nach dem Komma schreibst du nicht. Beispiel: 5 Millionen, 3,75 Prozent, 1,5 Kilometer, 2,25 Stunden.
- Vor Franken-Rappen-Beträgen schreibst du immer «CHF». Nur nach ganzen Franken-Beträgen darfst du «Franken» schreiben. Bei Franken-Rappen-Beträgen setzt du einen Punkt als Dezimalzeichen. Anstatt des Null-Rappen-Strichs verwendest du «.00» oder lässt die Dezimalstellen weg. Z.B. 20 Franken, CHF 20, CHF 2.00, CHF 12.50, aber CHF 45,2 Millionen, EUR 14,90.
- Die Anrede mit «Sie» schreibst du immer gross. Beispiel: «Sie haben».
- Strukturiere den Text. Gliedere in sinnvolle Abschnitte und Absätze. Verwende Titel und Untertitel grosszügig, um den Text zu gliedern. Es kann hilfreich sein, wenn diese als Frage formuliert sind.
- Stelle Aufzählungen als Liste dar.
- Zeilenumbrüche helfen, Sinneinheiten zu bilden und erleichtern das Lesen. Füge deshalb nach Haupt- und Nebensätzen sowie nach sonstigen Sinneinheiten Zeilenumbrüche ein. Eine Sinneinheit soll maximal 8 Zeilen umfassen.
- Eine Textzeile enthält inklusiv Leerzeichen maximal 85 Zeichen."""


REWRITE_COMPLETE = """- Achte immer sehr genau darauf, dass ALLE Informationen aus dem schwer verständlichen Text in dem Text in Leichter Sprache enthalten sind. Kürze niemals Informationen. Wo sinnvoll kannst du zusätzliche Beispiele hinzufügen, um den Text verständlicher zu machen und relevante Inhalte zu konkretisieren."""


REWRITE_CONDENSED = """- Konzentriere dich auf das Wichtigste. Gib die essenziellen Informationen wieder und lass den Rest weg. Wichtig sind zusätzliche Beispiele. Damit konkretisierst du relevante Inhalte und machst sie dadurch verständlicher."""



OPENAI_TEMPLATE_ES = """Bitte schreibe den folgenden schwer verständlichen Text vollständig in Einfache Sprache, Sprachniveau B1 bis A2, um. 

Beachte dabei folgende Regeln für Einfache Sprache (B1 bis A2):

{completeness}
{rules}

Schreibe den vereinfachten Text innerhalb von <einfachesprache> Tags.

Hier ist der schwer verständliche Text:

--------------------------------------------------------------------------------

{prompt}
"""

OPENAI_TEMPLATE_LS = """Bitte schreibe den folgenden schwer verständlichen Text vollständig in Leichte Sprache, Sprachniveau A2, um. 

Beachte dabei folgende Regeln für Leichte Sprache (A2):

{completeness}
{rules}

Schreibe den vereinfachten Text innerhalb von <leichtesprache> Tags.

Hier ist der schwer verständliche Text:

--------------------------------------------------------------------------------

{prompt}
"""

OPENAI_TEMPLATE_ANALYSIS_ES = """Du bekommst einen schwer verständlichen Text, den du genau analysieren sollst. 

Analysiere den schwer verständlichen Text Satz für Satz. Beschreibe genau und detailliert, was sprachlich nicht gut bei jedem Satz ist. Analysiere was ich tun müsste, damit der Text zu Einfacher Sprache (B1 bis A2) wird. Gib klare Hinweise, wie ich den Text besser verständlich machen kann. Gehe bei deiner Analyse Schritt für Schritt vor. 

1. Wiederhole den Satz. 
2. Analysiere den Satz auf seine Verständlichkeit. Was muss ich tun, damit der Satz verständlicher wird? Wie kann ich den Satz in Einfacher Sprache, Sprachniveau B1 bis A2 besser formulieren?
3. Mache einen Vorschlag für einen vereinfachten Satz. 

Befolge diesen Ablauf von Anfang bis Ende auch wenn der schwer verständliche Text sehr lang ist. 

Die Regeln für Einfache Sprache, Sprachniveau B1 bis A2, sind diese hier: 

{rules}

Schreibe deine Analyse innerhalb von <einfachesprache> Tags.

Hier ist der schwer verständliche Text:

--------------------------------------------------------------------------------

{prompt}
"""

OPENAI_TEMPLATE_ANALYSIS_LS = """Du bekommst einen schwer verständlichen Text, den du genau analysieren sollst.

Analysiere den schwer verständlichen Text Satz für Satz. Beschreibe genau und detailliert, was sprachlich nicht gut bei jedem Satz ist. Analysiere was ich tun müsste, damit der Text zu Leichter Sprache (A2) wird. Gib klare Hinweise, wie ich den Text besser verständlich machen kann. Gehe bei deiner Analyse Schritt für Schritt vor. 

1. Wiederhole den Satz. 
2. Analysiere den Satz auf seine Verständlichkeit. Was muss ich tun, damit der Satz verständlicher wird? Wie kann ich den Satz in Leichter Sprache, Sprachniveau A2 besser formulieren?
3. Mache einen Vorschlag für einen vereinfachten Satz. 

Befolge diesen Ablauf von Anfang bis Ende auch wenn der schwer verständliche Text sehr lang ist. 

Die Regeln für Leichte Sprache, Sprachniveau A2, sind diese hier:  

{rules}

Schreibe deine Analyse innerhalb von <leichtesprache> Tags.

Hier ist der schwer verständliche Text:

--------------------------------------------------------------------------------

{prompt}
"""

DEMO_TEXT = r"""Gemäss § 34 der Kantonsverfassung Basel-Stadt besteht Wohnungsnot bei einem 
Leerwohnungsbestand von 1,5% und weniger. Dieser Wert geht zurück auf die 
Wohnschutzinitiative des Mieterverbands Basel-Stadt und ist eine politisch definierte Zahl 
ohne jegliche empirische Herleitung. So hat das Bundesamt für Wohnungswesen die 
Wohnungsnot unlängst bei einem Leerwohnungsbestand unter 1,0% geortet und spricht bei 
einem Leerwohnungsbestand von 1,0 – 1,5% von Wohnungsmangel. 
Die Koppelung der Definition der Wohnungsnot an eine bestimmte Zahl macht denn auch 
wenig Sinn. So garantiert ein Leerwohnungsbestand von mehr als 1,5% einer 
wohnungssuchenden Person, welche auf eine preisgünstige Wohnung angewiesen ist, eine 
solche nicht. Ebenso wenig schliesst ein Leerstand von weniger als 1,5% aus, dass diese 
Person innert nützlicher Frist eine solche Wohnung findet. Was nützt einer Familie ein 
Leerwohnungsbestand von 2,0%, wenn dieser vor allem dank vielen leerstehenden teuren 
Kleinwohnungen zustande gekommen ist, eine von ihnen benötigte preisgünstige 
Familienwohnung auf dem Wohnungsmarkt hingegen Mangelware ist. Ebenso wenig nützt 
es einer auf günstigen Wohnraum angewiesenen Person, wenn der Leerwohnungsbestand 
die Grenze von 1,5% übersteigt, dies aber nur dank der Erstellung von teuren 
Neubauwohnungen. Diese Zahl gaukelt somit eine Lösung und Sicherheit vor, die sie in Tat 
und Wahrheit nicht garantieren kann. 
Letztlich bewirkt sie vielmehr das Gegenteil von dem, was sie verspricht. Denn die 
einzuleitenden Massnahmen verschärfen die Probleme auf dem Wohnungsmarkt. Die Zahlen 
aus den Leerstanderhebungen zeigen, dass die tiefen Leerstände vor allem bei grösseren 
Wohnungen bestehen, Kleinwohnungen hingegen zum Teil Leerstände von über 1,5% 
aufweisen. Die stringenten Wohnschutzbestimmungen verhindern aber sinnvolle Lösungen, 
dass nämlich solche Kleinwohnungen zu grösseren und somit zu Familienwohnungen 
zusammengelegt werden können. Bestünden solche Möglichkeiten, so könnte der Überhang 
an Kleinwohnung abgebaut und das Fehlen an grösseren Wohnung bis zu einem gewissen 
Grad entschärft werden. 
Unbefriedigend kommt hinzu, dass die Zählung des Leerstands wenig überschaubar ist, 
einen Hauch von Zufälligkeit birgt und nicht klar erkennen lässt, ob tatsächlich alle 
leerstehenden Wohnungen in die Zählung einfliessen. 
Der Wohnungsleerstand muss also konziser und aussagekräftiger erhoben werden, indem 
dieser nach Wohnungsgrösse, Preiskategorie und Standort ausgewiesen wird. Ferner sind 
die rigiden Wohnschutzbestimmungen auf Wohnungsbestände zu beschränken, die gemäss 
jährlicher Leerstanderhebung einer Wohnungsnot gemäss aktueller Verfassungsbestimmung 
unterliegen. Aus diesem Grund bitten die Unterzeichnenden den Regierungsrat, dem 
Grossen Rat innert Jahresfrist eine gesetzliche Grundlage vorzulegen, die eine 
Leerstanderhebung unterschieden gemäss oben erwähnte Wohnungskategorien zulässt und 
die Wohnschutzbestimmungen auf jene Wohnungskategorien beschränkt, die unter der 
Leerstandsquote von 1,5% liegen.
"""