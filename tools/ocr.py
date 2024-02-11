import streamlit as st
import os
from enum import Enum
import boto3

from helper import (
    get_var,
    init_logging,
    save_uploadedfile,
)
from tools.tool_base import ToolBase, TEMP_PATH, OUTPUT_PATH, DEMO_PATH

DEMO_FILE = DEMO_PATH + "formular55plus.png"
FILE_FORMAT_OPTIONS = ["jpg", "jpeg", "png", "gif"]
FEATURE_TYPES_OPTIONS = {
    "DOCUMENT": "Raw Text",
    "FORMS": "Schlüssel/Werte Paare",
    "TABLES": "Tabellen",
}


class InputFormat(Enum):
    DEMO = 0
    FILE = 1
    S3 = 2


INPUT_TYPE_OPTIONS = {
    InputFormat.DEMO.value: "Demo",
    InputFormat.FILE.value: "Bild hochladen",
    InputFormat.S3.value: "S3 Bucket",
}


class Ocr(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Texterkennung"
        self.input_type = InputFormat.DEMO.value
        self.feature_type = "DOCUMENT"
        self.text = None
        self.input_file = None
        self.image_dict = {}
        self.text_dict = {}

        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()

    def show_settings(self):
        self.input_type = st.selectbox(
            label="Quelle",
            options=INPUT_TYPE_OPTIONS.keys(),
            format_func=lambda x: INPUT_TYPE_OPTIONS[x],
        )
        self.feature_type = st.selectbox(
            "Analyse",
            options=FEATURE_TYPES_OPTIONS.keys(),
            format_func=lambda x: FEATURE_TYPES_OPTIONS[x],
        )
        if self.input_type == InputFormat.DEMO.value:
            self.input_file = DEMO_FILE
        elif self.input_type == InputFormat.FILE.value:
            self.input_file = None
            uploaded_file = st.file_uploader(
                "Datei hochladen", type=FILE_FORMAT_OPTIONS
            )
            if uploaded_file is not None:
                self.input_file = uploaded_file

        if self.input_file is not None:
            st.image(self.input_file)

    def extract_text(self):
        """
        Extracts text from an image using Amazon Textract.

        Returns:
            list: A list of Textract blocks containing the extracted text.
        """
        textract = boto3.client(
            "textract",
            aws_access_key_id=get_var("aws_access_key_id"),
            aws_secret_access_key=get_var("aws_secret_access_key"),
            region_name="eu-central-1",
        )
        if self.input_type == InputFormat.DEMO.value:
            with open(self.input_file, "rb") as image:
                f = image.read()
                image_data = bytearray(f)
        elif self.input_type == InputFormat.FILE.value:
            image_data = bytearray(self.input_file.getvalue())

        if self.feature_type == "DOCUMENT":
            response = textract.detect_document_text(
                Document={"Bytes": image_data},
            )
        else:
            image_data = bytearray(self.input_file.getvalue())
            response = textract.analyze_document(
                Document={"Bytes": image_data}, FeatureTypes=[self.feature_type]
            )
        return response["Blocks"]

    def run(self):
        with st.expander("Vorschau Dokument", expanded=False):
            st.image(DEMO_FILE)
        if st.button("Text extrahieren"):
            response = self.extract_text()
            with st.expander("Ergebnis mit Details", expanded=True):
                st.write(response)
            with st.expander("Extrahierte Text Elemente", expanded=True):
                texts = []
                elements = []
                for item in response:
                    if item["BlockType"] == "LINE":
                        texts.append(item["Text"])
                        elements.append(item["Geometry"]["BoundingBox"])
                st.write(texts)
                # st.write(elements)
                # self.mark_elements_on_image(self.input_file, elements)
