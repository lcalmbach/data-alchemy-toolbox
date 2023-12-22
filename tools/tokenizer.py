import streamlit as st
import os
import pandas as pd
import tiktoken
import nltk
from io import BytesIO
import zipfile
from nltk.tokenize import word_tokenize, sent_tokenize
from helper import init_logging, extract_text_from_pdf, get_text_from_binary
from enum import Enum
from const import LOGFILE, OUTPUT_PATH
from tools.tool_base import ToolBase, MODEL_OPTIONS, MODEL_TOKEN_PRICING

nltk.download("punkt")
logger = init_logging(__name__, LOGFILE)

DEMO_FILE = "./data/demo/demo_summary.txt"
FILE_FORMAT_OPTIONS = ["pdf", "txt"]
INPUT_FORMAT_OPTIONS = [
    "Demo",
    "Eine Datei (txt, pdf)",
    "Mehrere Dateien gezippt",
    "S3-Bucket",
]


class limitType(Enum):
    CHARACTERS = 0
    TOKENS = 1
    SENTENCES = 2


class InputFormat(Enum):
    DEMO = 0
    FILE = 1
    ZIPPED_FILE = 2
    S3 = 3


class OutputFormat(Enum):
    DEMO = 0
    CSV = 1
    ZIP = 2
    S3 = 3


class Tokenizer(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.logger = logger
        self.title = "Tokenizer"
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.input_format = INPUT_FORMAT_OPTIONS[0]
        self.model = MODEL_OPTIONS[1]
        self.input_file = None
        self.output_file = None
        self.s3_input_bucket = ""
        self.html = None
        with open(DEMO_FILE, "r", encoding="utf8") as file:
            self.text = file.read()

    def show_settings(self):
        """
        Displays the settings options for the tokenizer tool based on the selected input format.

        The method prompts the user to select an input format and then presents the appropriate input options based on the selected format.
        The available input formats include DEMO, FILE, ZIPPED_FILE, and S3.

        Returns:
            None
        """
        self.model = self.get_model()
        self.input_format = st.selectbox(
            label="Input Format", options=INPUT_FORMAT_OPTIONS
        )
        if INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.DEMO.value:
            self.text = st.text_area(
                "Demo Text für die Zusammenfassung",
                value=self.text,
                height=400,
                help="Geben Sie den Text ein, den Sie zusammenfassen möchten.",
            )
        elif INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.FILE.value:
            self.input_file = st.file_uploader(
                "PDF oder Text Datei",
                type=["pdf", "txt"],
                help="Laden Sie die Datei hoch, die Sie zusammenfassen möchten.",
            )
        elif (
            INPUT_FORMAT_OPTIONS.index(self.input_format)
            == InputFormat.ZIPPED_FILE.value
        ):
            self.input_file = st.file_uploader(
                "ZIP Datei",
                type=["zip"],
                help="Laden Sie die ZIP Datei hoch mit Dateien, die Sie zusammenfassen möchten. Die Datei muss Dateien im Format zip, txt und pdf enthalten.",
            )
        elif INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.S3.value:
            self.s3_input_bucket = st.text_input(
                "S3-Bucket",
                value=self.s3_input_bucket,
                help="Geben Sie die ARN des S3-Buckets ein, der die Dateien enthält, die Sie zusammenfassen möchten.",
            )

    def analyse_text(self):
        """
        Analyzes the text by performing tokenization and calculating costs.

        Returns:
            None
        """
        enc = tiktoken.get_encoding("cl100k_base")
        openai_tokens = enc.encode(self.text)
        preis_4k = "{:.3f} USD".format(
            len(openai_tokens) / 1000 * MODEL_TOKEN_PRICING[MODEL_OPTIONS[0]]["in"]
        )
        preis_16k = "{:.3f} USD".format(
            len(openai_tokens) / 1000 * MODEL_TOKEN_PRICING[MODEL_OPTIONS[1]]["in"]
        )
        df = pd.DataFrame(
            {
                "key": [
                    "Anzahl Sätze",
                    "Anzahl Wörter",
                    "Anzahl Tokens (OpenAi)",
                    "Kosten (gpt-3.5-turbo 4K)",
                    "Kosten (gpt-3.5-turbo 16K)",
                ],
                "value": [
                    len(sent_tokenize(self.text)),
                    len(self.text.split()),
                    len(openai_tokens),
                    preis_4k,
                    preis_16k,
                ],
            }
        )
        self.html = df.to_html(index=False, header=False) + "<br>"

    def run(self):
        """
        Executes the tokenization process based on the selected input format.

        Returns:
            None
        """
        if st.button("Analyse"):
            placeholder = st.empty()
            self.errors = []
            if INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.DEMO.value:
                self.analyse_text()
            elif (
                INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.FILE.value
            ):
                self.text = extract_text_from_pdf(self.input_file, placeholder)
                self.analyse_text()
            elif (
                INPUT_FORMAT_OPTIONS.index(self.input_format)
                == InputFormat.ZIPPED_FILE.value
            ):
                with zipfile.ZipFile(self.input_file, "r") as zip_ref:
                    for file in zip_ref.infolist():
                        self.text = ""
                        st.markdown(file.filename)
                        if file.filename.endswith(".pdf"):
                            with zip_ref.open(file) as pdf_file:
                                self.text = extract_text_from_pdf(pdf_file, placeholder)
                        elif file.filename.endswith(".txt"):
                            with zip_ref.open(file) as text_file:
                                binary_content = text_file.read()
                                self.text = get_text_from_binary(binary_content)
                        if self.text > "":
                            self.analyse_text()
                            st.markdown(self.html, unsafe_allow_html=True)
                        else:
                            st.warning(
                                f"Die Datei {file.filename} hat nicht das richtige Format und ist leer oder konnte nicht gelesen werden."
                            )
                st.success("Alle Dateien in wurden analysiert.")
            elif (
                INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.S3.value
            ) and (self.s3_input_bucket > ""):
                pass
        if self.html is not None and INPUT_FORMAT_OPTIONS.index(self.input_format) in (
            0,
            1,
        ):
            st.markdown(self.html, unsafe_allow_html=True)
