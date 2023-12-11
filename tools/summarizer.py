import streamlit as st
import fitz
import os
import io
from enum import Enum
import logging
from helper import create_file, append_row, zip_files, get_var, init_logging, split_text
from tools.tool_base import ToolBase, MODEL_OPTIONS

logger = init_logging(__name__, "messages.log")

DEMO_FILE = "./data/demo/demo_summary.txt"
SYSTEM_PROMPT_TEMPLATE = "You will be provided with a text. Your task is to summarize the text in german. The summary should contain a maximum of {}"
LIMIT_OPTIONS = ["Zeichen", "Tokens", "Sätze"]
INPUT_FORMAT_OPTIONS = ["Demo", "pdf-Datei", "zip Datei", "S3-Bucket"]
OUTPUT_FORMAT_OPTIONS = ["Textfeld auf Maske", "Eine csv-Datei", "Text Dateien gezippt", "Text Dateien in S3-Bucket"]


class limitType(Enum):
    CHARACTERS = 0
    TOKENS = 1
    SENTENCES = 2


class InputFormat(Enum):
    DEMO = 0
    PDF = 1
    ZIP = 2
    S3 = 3


class OutputFormat(Enum):
    DEMO = 0
    CSV = 1
    ZIP = 2
    S3 = 3


class Summary(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.logger = logger
        self.title = "Zusammenfassung"
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.input_format = INPUT_FORMAT_OPTIONS[0]
        self.output_format = OUTPUT_FORMAT_OPTIONS[0]
        self.limit_type = LIMIT_OPTIONS[0]
        self.limit_number = 500
        self.model = MODEL_OPTIONS[1]
        self.input_file = None
        self.output_file = None
        self.s3_input_bucket = ""
        self.s3_output_bucket = ""
        with open(DEMO_FILE, "r", encoding="utf8") as file:
            self.text = file.read()

    @property
    def system_prompt(self):
        limit_expression = f"{self.limit_number} {self.limit_type}"
        return SYSTEM_PROMPT_TEMPLATE.format(limit_expression)

    def show_settings(self):
        self.model = self.get_model()
        st.markdown("Begrenze die Zusammenfassung auf")
        cols = st.columns([1, 1, 2])
        with cols[0]:
            self.limit_number = st.number_input(
                "Anzahl",
                min_value=1,
                max_value=10000,
                value=self.limit_number,
                step=1,
            )
        with cols[1]:
            self.limit_type = st.selectbox(
                "Typ",
                options=LIMIT_OPTIONS,
                index=0,
                help="Wähle die Einheit der Limite, die du verwenden möchtest.",
            )
        self.input_format = st.selectbox(
            label="Input Format",
            options=INPUT_FORMAT_OPTIONS
        )
        if INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.DEMO.value:
            self.text = st.text_area(
                "Text",
                value=self.text,
                height=400,
                help="Geben Sie den Text ein, den Sie zusammenfassen möchten.",
            )
        elif INPUT_FORMAT_OPTIONS.index(self.input_format) in (InputFormat.PDF.value, InputFormat.ZIP.value):
            text = "pdf Datei" if INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.PDF.value else "zip Datei"
            formats = ['pdf'] if INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.PDF.value else ['zip']
            self.input_file = st.file_uploader(
                text,
                type=formats,
                help="Laden Sie die Datei hoch, die Sie zusammenfassen möchten.",
            )
        
        if INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.S3.value:
            self.s3_input_bucket = st.text_input(
                "S3-Bucket",
                value=self.s3_input_bucket,
                help="Geben Sie die ARN des S3-Buckets ein, der die Dateien enthält, die Sie zusammenfassen möchten.",
            )
        # output format
        if INPUT_FORMAT_OPTIONS.index(self.input_format) > InputFormat.DEMO.value:
            self.output_format = st.selectbox(
                label="Ausgabe Format",
                options=OUTPUT_FORMAT_OPTIONS[1:]
            )
        if OUTPUT_FORMAT_OPTIONS.index(self.output_format) == OutputFormat.S3.value:
            self.s3_output_bucket = st.text_input(
                "S3-Ausgabe-Bucket",
                value=self.s3_output_bucket,
                help="Geben Sie die ARN des S3-Buckets ein, in dem die Zusammenfassungs-Dateien gespeichert werden sollen.",
            )

    def run(self):
        def generate_summary(text, placeholder):
            buffer_number = self.limit_number
            buffer_type = self.limit_type
            self.limit_number = 1 
            self.limit_type = 'sentence'
            st.write(self.chunk_size())
            input_chunks = split_text(text, chunk_size=self.chunk_size())
            output_chunks = []
            for chunk in input_chunks:
                response, tokens = self.get_completion(text=chunk, index=0)
                output_chunks.append(response)
                print(response)
                placeholder.write(f"Chunk {input_chunks.index(chunk)} / {len(input_chunks)} completed")
            self.limit_number = buffer_number
            self.limit_type = buffer_type
            return " ".join(output_chunks)

        if st.button("Zusammenfassung"):
            with st.spinner("Generiere Zusammenfassung..."):
                self.errors = []
                if INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.DEMO.value:
                    self.output, tokens = self.get_completion(text=self.text, index=0)
                    st.markdown(self.token_use_expression(tokens))
                    st.markdown(self.output)
                elif INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.PDF.value: 
                    placeholder = st.empty()
                    if self.input_file:
                        if self.input_file.type == "application/pdf":
                            pdf_document = fitz.open(stream=self.input_file.read(), filetype="pdf")
                            text = ""
                            for page_number in range(pdf_document.page_count):
                                page = pdf_document[page_number]
                                placeholder.write(f"Page {page_number} extracted")
                                text += page.get_text()

                            # generate a summary for each chunk
                            text = generate_summary(text, placeholder)
                            self.output, tokens = self.get_completion(text=text, index=0)
                            st.text_area("Zusammenfassung", value=self.output, height=400)
                            text_buffer = io.StringIO()
                            text_buffer.write(self.output)
                            # Provide a download link for the extracted text
                            st.download_button(
                                "Text herunterladen",
                                text_buffer.getvalue(),
                                file_name="extracted_text.txt",
                                key="text-download",
                            )
                else:
                    st.warning("Diese Option wird noch nicht unterstützt.")
