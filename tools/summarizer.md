**Zusammenfassung**: Kompakte Überblicke aus Texten und PDFs erstellen

**Zusammenfassung** ist ein leistungsfähiges Tool, das dir ermöglicht, Texte oder eine Liste von Text- oder PDF-Dateien effizient zu kürzen. Du hast die Möglichkeit, die Länge der Zusammenfassung individuell festzulegen, indem du bestimmst, wie viele Wörter oder Sätze diese enthalten soll.

**Einstellungen:**

**Modell**: Es stehen 2 Modele zur Verfügung: gpt-3.5-turbo und gpt-3.5-turbo-1106. Die beiden Modelle unterscheiden sich vor allem durch die Anzahl Tokens, welche als Prompt akzeptiert werden. gpt-3.5-turbo kann 4K Tokens entgegennehmen, während gpt-3.5-turbo-1106 16K Tokens akzeptiert. Bei sehr langen Texten wird der Text zuerst in sogenannte chunks aufgeteilt, welche dann einzeln verarbeitet werden. Für jeden Chunk wird eine Zusammefassung geschrieben, und die Summe der Zusammenfassungen am schluss nochmals in eine Zusammenfassung konsolidiert. Für das Modell gpt-3.5-turbo-1106 müssen somit weniger chunks erstellt werden, was die Qualität der Zusammenfassung verbessert. Bei kurzen Dokumenten bis 2 Seiten ist das Modell gpt-3.5-turbo ausreichend und günstiger.

**Input Format**: Folgende Foramte stehen zur Verfügung:
- Demo: Ein Demo-Text wird verwendet, um die Funktionsweise des Tools zu demonstrieren. Kein weiterer Input wird benötigt.
- Eine Datei: Du kannst eine Text- oder PDF-Datei hochladen, die zusammengefasst werden soll.
- Mehrere Dateien gezippt: Du kopierst alle Text oder pdf-Dateien in eine ZIP-DAtei und lädst diese hoch. Die Dateien werden dann einzeln zusammengefasst und die generierten Zusammenfassungen lassen sich wiederum als zip-Datei zum Herunterladen. Die Eingabe-Datei darf nicht grösser als 200 MB gross sein.
- S3-Bucket: bei grösseren Dokumentensammlungen oder in Workflows, bei denen Dateien regelmässig zusammengefasst werden sollen, kann es sinnvoll sein, die Dateien in einem S3-Bucket zu speichern. Die Resultate werden dann ebenfalls im gleichen S3-Bucket im Unterordner *output* gespeichert.


Anwendungsmöglichkeiten:
1. Dokumentensammlungen: Das Tool eignet sich hervorragend für den Einsatz in umfangreichen Dokumentensammlungen, die bisher keine manuellen Zusammenfassungen besitzen. Es kann schnell und präzise die Kerninhalte extrahieren und übersichtlich darstellen.
2. Executive Summaries: Bei der Erstellung von Executive Summaries für Berichte, Studien und ähnliche Dokumente leistet **Zusammenfassung** wertvolle Dienste. Es ermöglicht dir, schnell eine prägnante und aussagekräftige Übersicht über den Hauptinhalt eines Dokuments zu gewinnen, was insbesondere für Entscheidungsträger von Nutzen ist.

Durch seine Flexibilität und Anwendungsvielfalt ist **Zusammenfassung** ein unverzichtbares Werkzeug für Fachleute, die mit der Verwaltung, Analyse und Präsentation von Dokumenten befasst sind. Es erleichtert die Informationsaufnahme und fördert ein effizienteres Dokumentenmanagement.

