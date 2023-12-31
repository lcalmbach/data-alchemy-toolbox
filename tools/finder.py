import streamlit as st
import os
import pandas as pd
import zipfile
from helper import init_logging, extract_text_from_uploaded_file, empty_folder
from enum import Enum
from whoosh.index import create_in
from whoosh import index
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.qparser import QueryParser
from whoosh.query import Every, Term
from pathlib import Path

from tools.tool_base import (
    ToolBase,
    INDEX_PATH,
    DOCS_PATH,
    LOGFILE,
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
            return create_in(INDEX_PATH, schema)
        else:
            return index.open_dir(INDEX_PATH)

    def add_document(self, doc: Document):
        writer = self.ix.writer()
        writer.add_document(title=doc.title, path=doc.path, content=doc.content)
        writer.commit()

    def document_exists_in_index(self, filename):
        """
        Check if a document with the given filename exists in the Whoosh index.

        Args:
            filename (str): The filename or unique identifier of the document to check.
            index_directory (str): The path to the directory containing the Whoosh index.

        Returns:
            bool: True if the document exists in the index, False otherwise.
        """

        # Create a searcher
        with self.ix.searcher() as searcher:
            query = Term("title", filename)
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
            writer = self.ix.writer()
            writer.delete_by_query(Every())
            writer.commit()
            ok, files_removed = empty_folder()
            if ok:
                logger.info(f"Removed {files_removed} files from {self.docs_path}")
            else:
                logger.warning(f"Could not remove files from {self.docs_path}")
            return True
        except Exception as e:
            return False

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
                    if not self.document_exists_in_index(file.name):
                        text = extract_text_from_uploaded_file(file)
                        doc = Document(file.name, file.name, text)
                        self.add_document(doc)
                        save_path = os.path.join(
                            INDEX_SOURCES[self.index_source]["docs_path"], file.name
                        )
                        with open(save_path, "wb") as f:
                            f.write(file.getbuffer())
            with st.expander(f"{self.ix.doc_count()} Dokumente im Index"):
                with self.ix.searcher() as searcher:
                    docnums = searcher.reader().all_doc_ids()
                    for docnum in docnums:
                        document = searcher.reader().stored_fields(docnum)
                        st.write(document["path"])
            if st.button("Index löschen"):
                self.purge_index()
        elif self.index_source == "remote":
            ...
        elif self.index_source == "s3":
            ...

    def run(self):
        """
        Executes the tokenization process based on the selected input format.

        Returns:
            None
        """

        st.write(f"{self.ix.doc_count()} Dokumente im Index")
        text = st.text_input("🔎Suchen", help="Gib einen Suchbegriff ein")

        if st.button("Suche starten"):
            qp = QueryParser("content", schema=self.ix.schema)
            q = qp.parse(text)

            with self.ix.searcher() as s:
                results = s.search(q, limit=None)
                for hit in results:
                    cols = st.columns(2)
                    with cols[0]:
                        st.write(hit["title"])
                    with cols[1]:
                        st.download_button(
                            "Laden",
                            Path(self.docs_path + hit["path"]).read_bytes(),
                            hit["title"],
                        )
                    st.markdown(hit.highlights("content"), unsafe_allow_html=True)
                    st.markdown("----")
