Die Suche nach Dokumenten, die einen bestimmten Text enthalten, ist die wohl häufigste Analyse von unstrukturierten Daten. Damit die Suche performant bleibt, wird nicht in den Dokumenten selbst gesucht, sondern die Dokumente werden indiziert, sodass über diesen Index gesucht werden kann. Die App **Finder** erlaubt es, lokal gespeicherte Dateien sowie Dokumentensammlungen in der Cloud zu indexieren und zu durchsuchen. Die Suche basiert auf der Python-Bibliothek [Whoosh](https://whoosh.readthedocs.io/en/latest/index.html).

Es stehen folgende Optionen zur Verfügung:

- **Lokale Dokumentensammlung**: Es lassen sich Dokumente auf den Server hochladen und anschließend durchsuchen. Diese Option demonstriert, wie die Suche lokal implementiert werden kann. Jedoch müsste im Falle eines produktiven Einsatzes der App **Finder** die Suche auf lokalen Dateien des Servers auf einen Knoten auf File-Basis aufsetzen.

- **Linksammlung**: Hier muss eine Liste von URLs als Datei hochgeladen werden. Die App indiziert die in der Liste enthaltenen Dokumente, lässt jedoch das Original in der Cloud, ohne eine lokale Kopie zu erstellen.

- **S3 Bucket**: Hier liegen die Dokumente in einem AWS S3 Bucket. S3-Buckets haben den Vorteil, dass sie wie ein lokales Dateisystem das Schreiben von Dateien ermöglichen. Jede Datei hat gleichzeitig eine URL, über die die Datei verlinkt und als Datei in der Cloud geöffnet werden kann. 