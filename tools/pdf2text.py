
import streamlit as st
import os
from tools.tool_base import ToolBase
import fitz
import requests
import pyperclip
from moviepy.editor import *

class Pdf2Text(ToolBase):
    def __init__(self, logger):
        self.logger = logger
        self.title = "Pdf zu Text"
        self.formats = ['PDF Datei', 'Sammlung von PDF-Dateien (zip)']
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.text = ""
        self.encoding_source = "utf-8"
        self.encoding_target = "utf-8"

    def show_settings(self):
        self.input_type = st.radio(
            "Input für PDF2Text",
            options=self.formats
        )
        self.remove_crlf = st.checkbox("Zeilenendezeichen entfernen")
        self.remove_sep = st.checkbox(";-Zeichen entfernen")
        encoding_options = ['utf-8', 'latin1', 'cp1252']
        self.encoding_source = st.selectbox(
            label='Quellen-Encoding',
            options=encoding_options
        )
        self.encoding_target = st.selectbox(
            label='Ziel-Encoding',
            options=encoding_options
        )
        if self.formats.index(self.input_type) == 0:
            self.file = st.file_uploader('Datei hochladen')
        elif self.formats.index(self.input_type) == 1:
            ...
        elif self.formats.index(self.input_type) == 2:
            ...

    def extract_text_from_pdf(self, file):
        """
        Extracts text from a PDF file.

        Args:
            file: A file object representing the PDF file.

        Returns:
            A string containing the extracted text.
        """
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        pdf_text = ""
        for page in pdf_document:
            pdf_text += page.get_text()
            page_text_unicode = pdf_text.encode(self.encoding_source).decode(self.encoding_target)
            pdf_text += page_text_unicode
        return pdf_text

    def read_pdf_from_url(url: str):
        # Step 1: Download the PDF
        response = requests.get(url)
        if response.status_code == 200:
            with open("temp.pdf", "wb") as f:
                pdf = fitz.open("temp.pdf")
                text = ""
                for page_num in range(len(pdf)):
                    page = pdf.load_page(page_num)
                    text += page.get_text()
                return text
        else:
            st.error(f"Failed to download PDF. Status code: {response.status_code}")

    def run(self):
        if st.button("Starten"):
            if self.formats.index(self.input_type) == 0:
                if self.file:
                    self.text = self.extract_text_from_pdf(self.file)
                    dummy = st.text_area("Text", value=self.text, height=400)
                    
        if self.formats.index(self.input_type) == 0 and self.text != "":
            cols = st.columns(2, gap='small')
            with cols[0]:
                if st.button("Text in Zwischenablage kopieren"):
                    pyperclip.copy(self.text,)
                    st.success("Text wurde in die Zwischenablage kopiert.")
            with cols[1]:
                btn = st.download_button(
                    label="Text als txt-Datei herunterladen",
                    data=self.text,
                    file_name="pdf2text.txt",
                    mime="text/plain"
                )
