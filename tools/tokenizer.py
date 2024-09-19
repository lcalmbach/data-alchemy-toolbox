import streamlit as st
import os
import pandas as pd
import tiktoken
import nltk
import zipfile
from nltk.tokenize import sent_tokenize
from helper import init_logging, extract_text_from_uploaded_file, get_text_from_binary
from enum import Enum

from tools.tool_base import (
    ToolBase,
    MODEL_OPTIONS,
    MODEL_TOKEN_PRICING,
    DEMO_PATH,
    LOGFILE,
    DEFAULT_MODEL
)

nltk.download("punkt")
logger = init_logging(__name__, LOGFILE)


DEMO_FILE = DEMO_PATH + "demo_summary.txt"
FILE_FORMAT_OPTIONS = ["pdf", "txt"]
INPUT_FORMAT_OPTIONS = [
    "Demo",
    "Eine Datei (txt, pdf)",
    "Mehrere Dateien gezippt",
]


class limitType(Enum):
    CHARACTERS = 0
    TOKENS = 1
    SENTENCES = 2


class InputFormat(Enum):
    DEMO = 0
    FILE = 1
    ZIPPED_FILE = 2


class OutputFormat(Enum):
    DEMO = 0
    CSV = 1
    ZIP = 2


def calc_tokens(text: str, model_name=DEFAULT_MODEL):
    """
    Calculates the number of tokens in a given text.

    Args:
        text (str): The text to be tokenized.
        model_name (str, optional): The name of the model to be used for tokenization. Defaults to "gpt-3.5".

    Returns:
        int: The number of tokens in the text.
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    return tokens


def split_text(
    text: str,
    system_prompt: str = "",
    model_name=DEFAULT_MODEL,
    max_tokens_per_chunk: int = 4097,
    expected_completion_tokens: int = 1000,
):
    """
    Splits a given text into chunks of sentences, where each chunk has a maximum size of chunk_size.

    Args:
        text (str): The text to be split.
        chunk_size (int, optional): The maximum size of each chunk. Defaults to 2048.

    Returns:
        list: A list of chunks, where each chunk is a string of sentences.
    """
    chunks = []
    current_chunk = ""
    current_token_count = 0
    system_prompt_tokens = len(calc_tokens(system_prompt, model_name))
    max_tokens_per_chunk = (
        max_tokens_per_chunk - system_prompt_tokens - expected_completion_tokens
    )
    for line in text.split("\n"):
        line_token_count = len(calc_tokens(line, model_name))
        if current_token_count + line_token_count > max_tokens_per_chunk:
            chunks.append(current_chunk)
            current_chunk = line + "\n"
            current_token_count = line_token_count
        else:
            current_chunk += line + "\n"
            current_token_count += line_token_count

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


class Tokenizer(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.logger = logger
        self.title = "Tokenizer"
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.input_format = INPUT_FORMAT_OPTIONS[0]
        self.model = MODEL_OPTIONS[0]
        self.input_file = None
        self.output_file = None
        self.html = None
        self.text = self.read_file(DEMO_FILE)

    def read_file(self, filename):
        with open(filename, "r", encoding="utf8") as file:
            return file.read()

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
                "Demo Text für den Tokenizer",
                value=self.text,
                height=400,
                help="Geben Sie den Text ein, für den die Token berechnet werden sollen.",
            )
        elif INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.FILE.value:
            self.input_file = st.file_uploader(
                "PDF oder Text Datei",
                type=["pdf", "txt"],
                help="Laden Sie die Datei hoch, für die du Tokens berechnen möchtest.",
            )
        elif (
            INPUT_FORMAT_OPTIONS.index(self.input_format)
            == InputFormat.ZIPPED_FILE.value
        ):
            self.input_file = st.file_uploader(
                "ZIP Datei",
                type=["zip"],
                help="Lade die ZIP Datei hoch mit Dateien, für die du tokens berechnen möchten. Die Datei muss Dateien im Format zip, txt und pdf enthalten.",
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
            len(openai_tokens) / 1000 * MODEL_TOKEN_PRICING[MODEL_OPTIONS[0]]["in"]
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
                self.text = extract_text_from_uploaded_file(
                    self.input_file, placeholder
                )
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
                                self.text = extract_text_from_uploaded_file(
                                    pdf_file, placeholder
                                )
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
            
        if self.html is not None and INPUT_FORMAT_OPTIONS.index(self.input_format) in (
            0,
            1,
        ):
            st.markdown(self.html, unsafe_allow_html=True)
