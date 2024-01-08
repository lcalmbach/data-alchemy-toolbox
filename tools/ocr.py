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
FEATURE_TYPES_OPTIONS = ["FORMS", "TABLES", "DOCUMENT"]


class InputFormat(Enum):
    DEMO = 0


class Ocr(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Texterkennung"
        self.formats = ["Demo"]
        self.input_type = FEATURE_TYPES_OPTIONS[0]
        self.text = None
        self.input_file = None
        self.image_dict = {}
        self.text_dict = {}

        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()

    def show_settings(self):
        self.input_type = st.selectbox("Quelle", options=FEATURE_TYPES_OPTIONS)
        st.image(DEMO_FILE)

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
            region_name='eu-central-1',
        )
        with open(DEMO_FILE, "rb") as image:
            f = image.read()
            image_data = bytearray(f)
            response = textract.analyze_document(
                Document={"Bytes": image_data}, FeatureTypes=[self.input_type]
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
                for item in response:
                    if item["BlockType"] == "LINE":
                        st.write(item["Text"])
                        # st.write(item['Geometry']['BoundingBox']['Top'])
