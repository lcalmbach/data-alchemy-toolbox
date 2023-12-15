import streamlit as st
import zipfile
import os
import pandas as pd
import io
import tiktoken
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from enum import Enum
import boto3
from helper import (
    init_logging,
    split_text,
    check_file_type,
    extract_text_from_pdf,
    show_download_button,
    zip_texts,
    get_text_from_binary,
    download_file_button,
)
import concurrent.futures
from const import LOGFILE, OUTPUT_PATH
from tools.tool_base import ToolBase, MODEL_OPTIONS, MODEL_TOKEN_PRICING

nltk.download("punkt")
logger = init_logging(__name__, LOGFILE)

DEMO_FILE = "./data/demo/demo_summary.txt"
# SYSTEM_PROMPT_TEMPLATE = "You will be provided with a text. Your task is to summarize the text in german. The summary should contain a maximum of {}"
# LIMIT_OPTIONS = ["Zeichen", "Tokens", "Sätze"]
FILE_FORMAT_OPTIONS = ["pdf", "txt"]
INPUT_FORMAT_OPTIONS = ["Demo", "Eine Datei", "Mehrere Dateien gezippt", "S3-Bucket"]


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
            formats = ",".join(FILE_FORMAT_OPTIONS)
            self.input_file = st.file_uploader(
                "PDF oder Text Datei",
                type=formats,
                help="Laden Sie die Datei hoch, die Sie zusammenfassen möchten.",
            )
        elif (
            INPUT_FORMAT_OPTIONS.index(self.input_format)
            == InputFormat.ZIPPED_FILE.value
        ):
            self.input_file = st.file_uploader(
                "ZIP Datei",
                type=["zip"],
                help="Laden Sie die Datei hoch, die Sie zusammenfassen möchten. Die ZIP Datei darf Dateien im Format txt und pdf enthalten.",
            )
        elif INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.S3.value:
            self.s3_input_bucket = st.text_input(
                "S3-Bucket",
                value=self.s3_input_bucket,
                help="Geben Sie die ARN des S3-Buckets ein, der die Dateien enthält, die Sie zusammenfassen möchten.",
            )

    def run(self):
        if st.button("Analyse"):
            self.errors = []
            if (
                INPUT_FORMAT_OPTIONS.index(self.input_format)
                == InputFormat.DEMO.value
            ):
                enc = tiktoken.get_encoding("cl100k_base")
                openai_tokens = enc.encode(self.text)
                preis_4k = "{:.3f} USD".format(len(openai_tokens) / 1000 * MODEL_TOKEN_PRICING[MODEL_OPTIONS[0]]["in"])
                preis_16k = "{:.3f} USD".format(len(openai_tokens) / 1000 * MODEL_TOKEN_PRICING[MODEL_OPTIONS[1]]["in"])
                df = pd.DataFrame(
                    {
                        "key": [
                            "Anzahl Sätze",
                            "Anzahl Wörter",
                            "Anzahl Tokens (OpenAi)",
                            "Kosten (gpt-3.5-turbo 4K)",
                            "Kosten (gpt-3.5-turbo 16K)"
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
                self.html = df.to_html(index=False, header=False)
            elif (
                INPUT_FORMAT_OPTIONS.index(self.input_format)
                == InputFormat.FILE.value
            ):
                pass
            elif (
                INPUT_FORMAT_OPTIONS.index(self.input_format)
                == InputFormat.ZIPPED_FILE.value
            ):
                pass
            elif (
                INPUT_FORMAT_OPTIONS.index(self.input_format)
                == InputFormat.S3.value
            ) and (self.s3_input_bucket > ""):
                pass
        if self.html is not None:
            st.markdown(self.html, unsafe_allow_html=True)
