**pdf2text**: Umwandlung von PDF-Dokumenten in Text-Dateien

Die Funktion **pdf2text** ermöglicht die Umwandlung von PDF-Dokumenten in Textdateien. Dies gilt sowohl für einzelne PDF-Dokumente als auch für Sammlungen von PDFs. Die extrahierten Texte werden in einer ZIP-Datei zur Verfügung gestellt. Bitte überprüfe zuerst die erforderlichen Einstellungen unter dem Menüpunkt **⚙️ Einstellungen**. Anschließend kannst du eine oder mehrere PDF-Dateien hochladen. Es ist auch möglich, mehrere Dateien in eine einzige ZIP-Datei zu komprimieren und so hochzuladen. Beachte jedoch, dass die Grösse der ZIP-Datei 200 MB nicht überschreiten darf.

Input Formate
- PDF Datei hochladen: ein eigenes PDF-Dokument kann hochgeladen werden. Die Datei darf maximal 200 MB gross sein.
- URL: es kann eine URL angegeben werden, deren Inhalt in Text umgewandelt werden soll. Die Datei muss im PDF-Format vorliegen.
- ZIP-Datei hochladen: es können mehrere PDF-Dateien in eine ZIP-Datei komprimiert und hochgeladen werden. Die ZIP-Datei darf maximal 200 MB gross sein.
- S3 Bucket: es können mehrere PDF-Dateien aus einem S3 Bucket geladen werden. Die Dateien müssen im PDF-Format vorliegen. die Applikation braucht Zugriff auf den S3 Bucket oder der entsprechend Bucket is öffentlich.

Weitere Einstellungen:
- Zeilenendezeichen entfernen: wenn diese Option aktiviert ist, werden alle Zeilenumbrüche entfernt. Dies ist nützlich, wenn die Texte in einem Programm weiterverarbeitet werden sollen.
- Quell- und Ziel-Encoding. Default ist UTF-8. Wenn die PDF-Datei in einem anderen Encoding vorliegt oder der extrahierte Text in anderes encoding überführt werden soll, kann dieses hier angegeben werden.

Nach der Verarbeitung kannst du die resultierende ZIP-Datei mit dem Download-Button herunterladen. Die darin enthaltenen Textdateien tragen die gleichen Namen wie die ursprünglichen PDF-Dokumente, jedoch mit der Endung .txt.

Anwendungsmöglichkeiten:
- Integration in Prozessketten zur Verarbeitung von PDF-Dokumenten, beispielsweise als Vorstufe für die Indexierung von Dokumentensammlungen die anschliessend über den Index durchsucht werden können.
- Unterstützung bei der Erstellung bei allen Aufgaben, bei denen die Quelle im pdf Format vorliegt und deren Text an ein Large Language Model übergeben werden sollen.