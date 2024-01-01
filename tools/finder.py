import streamlit as st
import os
import pandas as pd
import zipfile
import shutil
from helper import (
    init_logging,
    extract_text_from_uploaded_file,
    extract_text_from_url,
    empty_folder,
    url_exists,
    get_original_url
)
from whoosh.index import create_in
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh.query import Every, Term
from pathlib import Path
import time

from tools.tool_base import (
    ToolBase,
    INDEX_PATH,
    DOCS_PATH,
    LOGFILE,
)

MAX_DOCS = 1000  # max number of docs to index
MAX_WAIT_SECS = (
    100  # max number of seconds to wait between requests to avoid server overload
)

logger = init_logging(__name__, LOGFILE)
INDEX_SOURCES = {
    "local": {
        "label": "Lokale Dokumentensammlung",
        "help": "Lade eine oder mehrere Dokumente hoch, die du durchsuchen möchtest. die dokumente werden lokal gespeichert.",
        "docs_path": DOCS_PATH,
        "indexdir": INDEX_PATH + "indexdir_local",
    },
    "remote": {
        "label": "Eine Linksammlung",
        "help": "Lade eine Linksammlung hoch, welche Links zu Dokumenten enthält, die du durchsuchen möchtest.",
        "docs_path": None,
        "indexdir": INDEX_PATH + "indexdir_remote",
    },
    "s3": {
        "label": "Ein S3 bucket",
        "help": "gib eine ARN zu einem S3 bucket ein, der Dokumente enthält, die du durchsuchen möchtest.",
        "docs_path": None,
        "indexdir": INDEX_PATH + "indexdir_s3",
    },
}

FILE_FORMAT_OPTIONS = ["pdf", "txt"]
INPUT_FORMAT_OPTIONS = {key: value["label"] for key, value in INDEX_SOURCES.items()}


class Document:
    def __init__(self, title, path, content):
        self.title = title
        self.path = path
        self.content = content

    def __repr__(self) -> str:
        return f"{self.title} - {self.path}"


class Finder(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.logger = logger
        self.title = "Finder"
        self.input_file = None
        self.ix = None
        self._index_source = "local"

        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()

    @property
    def index_source(self):
        return self._index_source

    @index_source.setter
    def index_source(self, value):
        self._index_source = value
        self.ix = self.get_index()
        self.docs_path = INDEX_SOURCES[value]["docs_path"]

    def get_index(self):
        source = INDEX_SOURCES[self.index_source]
        if not os.path.exists(source["indexdir"]):
            os.mkdir(source["indexdir"])
            schema = Schema(
                title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True)
            )
            return create_in(source["indexdir"], schema)
        else:
            return index.open_dir(source["indexdir"])

    def add_document(self, doc: Document):
            """
            Adds a document to the index.

            Args:
                doc (Document): The document to be added.

            Returns:
                None
            """
            writer = self.ix.writer()
            writer.add_document(title=doc.title, path=doc.path, content=doc.content)
            writer.commit()

    def document_exists_in_index(self, field: str, value: str):
        """
        Check if a document exists in the index based on the given field and value.

        Args:
            field (str): The field to search in.
            value (str): The value to search for.

        Returns:
            bool: True if a matching document is found, False otherwise.
        """

        # Create a searcher
        with self.ix.searcher() as searcher:
            query = Term(field,  value)
            results = searcher.search(query)
            return not results.is_empty()

    def purge_index(self):
        """
        Purges the index by deleting all document info from the index and all
        documents in the local document store.

        Returns:
            bool: True if the index was successfully purged, False otherwise.
        """
        try:
            source = INDEX_SOURCES[self.index_source]
            shutil.rmtree(source["indexdir"])
            # trigger regeneration of empty index
            self.index_source = self._index_source
        except Exception as e:
            logger.warning(f"Error while purging index: {e}")

    def index_documents(self, df, placeholder, max_docs, sleep_time):
        df.columns = ["title", "url"]
        cnt = 1
        for _, row in df.iterrows():
            if " " in row["url"]:
                logger.warning(f"Removed space from URL: {row['url']}")
                row["url"] = row["url"].split(" ")[0]
            # find original url if url is a redirect
            url = get_original_url(row["url"])
            exists, status_code = url_exists(url)
            if exists and not self.document_exists_in_index("path", url):
                text = extract_text_from_url(url)
                doc = Document(row["title"], url, text)
                self.add_document(doc)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                placeholder.markdown(f"Indexiere ({cnt}/{len(df)}) {row['title']}")
            elif not exists:
                st.warning(f"({cnt}/{len(df)}) Status {status_code} für Dokument {row['title']} existiert nicht ({row['url']})")
            else:
                placeholder.markdown(f"({cnt}/{len(df)}) {row['title']} existiert bereits in index")
            cnt += 1
            if cnt > max_docs:
                placeholder.warning(f"Maximale Anzahl Dokumente erreicht ({max_docs})")
                break

    def show_index_content(self):
        if self.ix.doc_count() > 0:
            with st.expander(f"{self.ix.doc_count()} Dokumente im Index"):
                with self.ix.searcher() as searcher:
                    docnums = searcher.reader().all_doc_ids()
                    cnt = 0
                    if self.ix.doc_count() > 100:
                        st.markdown("Es werden nur die ersten 100 Dokumente angezeigt.")
                    for docnum in docnums:
                        document = searcher.reader().stored_fields(docnum)
                        st.markdown(document["path"])
                        cnt += 1
                        if cnt > 100:
                            break
            if st.button("Index initialisieren"):
                self.purge_index()
        else:
            st.markdown("Der Index ist leer.")

    def show_settings(self):
        """
        Displays the settings options for the tokenizer tool based on the selected input format.

        The method prompts the user to select an input format and then presents the appropriate input options based on the selected format.
        The available input formats include DEMO, FILE, ZIPPED_FILE, and S3.

        Returns:
            None
        """

        self.index_source = st.selectbox(
            label="Input Format",
            options=INPUT_FORMAT_OPTIONS.keys(),
            format_func=lambda x: INPUT_FORMAT_OPTIONS[x],
        )
        if self.index_source == "local":
            uploaded_files = st.file_uploader(
                "PDF oder Text Datei",
                type=["pdf", "txt"],
                help="Lade eine oder mehrere Dateien hoch, die du durchsuchen möchtest.",
                accept_multiple_files=True,
            )
            if uploaded_files:
                for file in uploaded_files:
                    if not self.document_exists_in_index("title", file.name):
                        text = extract_text_from_uploaded_file(file)
                        doc = Document(file.name, file.name, text)
                        self.add_document(doc)
                        save_path = os.path.join(
                            INDEX_SOURCES[self.index_source]["docs_path"], file.name
                        )
                        try:
                            with open(save_path, "wb") as f:
                                f.write(file.getbuffer())
                        except Exception as e:
                            st.error(f"Error: {e}")
            self.show_index_content()

        elif self.index_source == "remote":
            self.show_index_content()
            uploaded_file = st.file_uploader(
                "CSV Datei mit Links",
                type=["csv"],
                help="Lade eine Datei hoch, welche die Felder: [title, url] enthält",
                accept_multiple_files=False,
            )
            if uploaded_file:
                df = pd.DataFrame()
                df = df.iloc[324:]
                try:
                    df = pd.read_csv(uploaded_file, sep=";")
                    st.markdown(f"{len(df)} Dokumente in der Datei gefunden")
                    # todo validate content of file
                    # ok = (len(df.columns) = 2)
                    max_docs = st.number_input(
                        "Maximale Anzahl Dokumente",
                        min_value=1,
                        max_value=MAX_DOCS,
                        value=MAX_DOCS,
                        help="Die Anzahl der indexierbaren Dokumente ist in dieser App begrenzt, um den Server nicht zu überlasten."
                    )
                    sleep_time = st.number_input(
                        "Wartezeit zwischen den Anfragen (in Sekunden)",
                        min_value=0,
                        max_value=MAX_WAIT_SECS,
                        value=0,
                        help="Manche Server blockieren Anfragen, wenn zu viele Anfragen in zu kurzer Zeit gestellt werden."
                    )
                    st.markdown("Damit der Inhalt dieser Dokumente für eine Suche bereitsteht, müssen sie zuerst indexiert werden. Klicke auf die Schaltfläche unten um den Prozess zu starten.")
                    if st.button("Dokumente indexierenmm"):
                        placeholder = st.empty()
                        self.index_documents(df, placeholder, max_docs, sleep_time)
                except Exception as e:
                    st.error(f"Error: {e}")
        elif self.index_source == "s3":
            st.info("Diese Option steht noch nicht zur Verfügung, stay tuned!")

    def run(self):
        """
        Executes the tokenization process based on the selected input format.

        Returns:
            None
        """

        st.markdown(f"{self.ix.doc_count()} Dokumente im Index")
        text = st.text_input("🔎Suchen", help="Gib einen Suchbegriff ein")

        if st.button("Suche starten"):
            qp = QueryParser("content", schema=self.ix.schema)
            q = qp.parse(text)

            with self.ix.searcher() as s:
                results = s.search(q, limit=None)
                results.fragmenter.surround = 50
                for hit in results:
                    st.markdown(hit.highlights("content"), unsafe_allow_html=True)
                    st.markdown(hit["path"])
                    st.markdown("----")
