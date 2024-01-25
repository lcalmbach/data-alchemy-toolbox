import streamlit as st
import os
import pyperclip
from moviepy.editor import *
from enum import Enum
import re

from tools.tool_base import ToolBase
from helper import extract_text_from_uploaded_file, extract_text_from_url


ENCODING_OPTIONS = ["utf-8", "latin1", "cp1252"]
FILE_FORMAT_OPTIONS = ["pdf"]


class InputFormat(Enum):
    FILE = 0
    URL = 1
    ZIPPED_FILE = 2
    S3 = 3


class Pdf2Text(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "PDF zu Text"
        self.formats = [
            "PDF Datei hochladen",
            "URL",
            "ZIP-Datei",
            "S3 Bucket",
        ]
        self.text = None
        self.encoding_source = "utf-8"
        self.encoding_target = "utf-8"
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()

    def show_settings(self):
        self.input_type = st.radio("Input Format", options=self.formats)
        self.remove_crlf = st.checkbox("Zeilenendezeichen entfernen")

        self.encoding_source = st.selectbox(
            label="Quellen-Encoding", options=ENCODING_OPTIONS
        )
        self.encoding_target = st.selectbox(
            label="Ziel-Encoding", options=ENCODING_OPTIONS
        )
        if self.formats.index(self.input_type) == InputFormat.FILE.value:
            self.input_file = st.file_uploader(
                "PDF Datei",
                type=FILE_FORMAT_OPTIONS,
                help="Lade die Datei hoch, deren Text du extrahieren möchtest.",
            )
            if self.input_file:
                self.text = extract_text_from_uploaded_file(self.input_file)
                self.text = self.clean_text(self.text)
        elif self.formats.index(self.input_type) == InputFormat.URL.value:
            self.input_file = st.text_input(
                "URL",
                help="Bitte gib den Link zur Datei ein, aus der du den Text extrahieren möchtest.",
            )
            if self.input_file:
                self.text = extract_text_from_url(self.input_file)
                self.text = self.clean_text(self.text)
        elif self.formats.index(self.input_type) == InputFormat.ZIPPED_FILE.value:
            ...

    def clean_text(self, text):
        text = text.replace("-\n", "")
        if self.remove_crlf:
            text = text.replace("\n", " ")
        # pattern = r'(?<!\.\s)(?<!\!\s)(?<!\?\s)\n'
        # text = re.sub(pattern, ' ', text)
        return text

    def run(self):
        """
        Runs the PDF2Text tool.

        If the 'Starten' button is clicked and the input type is PDF, extracts
        text from the selected PDF file and displays it in a text area.
        If the 'Text in Zwischenablage kopieren' button is clicked, copies the
        extracted text to the clipboard.
        If the 'Text als txt-Datei herunterladen' button is clicked, downloads
        the extracted text as a txt file.
        """
        if st.button("Starten"):
            if self.formats.index(self.input_type) in (
                InputFormat.FILE.value,
                InputFormat.URL.value,
            ):
                if self.text:
                    st.markdown("## Extrahierter Text")
                    st.markdown(self.text)

        if self.formats.index(self.input_type) == 0 and self.text != None:
            cols = st.columns(2, gap="small")
            with cols[0]:
                if st.button("Text in Zwischenablage kopieren"):
                    pyperclip.copy(self.text)
            with cols[1]:
                st.download_button(
                    label="Text als txt-Datei herunterladen",
                    data=self.text,
                    file_name="pdf2text.txt",
                    mime="text/plain",
                )
