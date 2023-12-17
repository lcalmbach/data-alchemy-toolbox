import streamlit as st
import zipfile
import os
from enum import Enum
import boto3
from io import BytesIO
from helper import (
    init_logging,
    split_text,
    check_file_type,
    extract_text_from_pdf,
    show_download_button,
    zip_texts,
    get_text_from_binary,
    download_file_button,
    get_var,
    get_token_size
)
from const import LOGFILE, OUTPUT_PATH
from tools.tool_base import ToolBase, MODEL_OPTIONS

logger = init_logging(__name__, LOGFILE)

DEMO_FILE = "./data/demo/demo_summary.txt"
SYSTEM_PROMPT_TEMPLATE = "You will be provided with a text. Your task is to summarize the text in german. The summary should contain a maximum of {}"
LIMIT_OPTIONS = ["Zeichen", "Tokens", "Sätze"]
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


class Summary(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.logger = logger
        self.title = "Zusammenfassung"
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.input_format = INPUT_FORMAT_OPTIONS[0]

        self.limit_type = LIMIT_OPTIONS[0]
        self.limit_number = 500
        self.model = MODEL_OPTIONS[1]
        self.input_file = None
        self.output_file = None
        self.bucket_name = "data-alchemy-bucket-01"
        self.input_prefix = "input/"
        self.output_prefix = "output/"
        with open(DEMO_FILE, "r", encoding="utf8") as file:
            self.text = file.read()

    @property
    def system_prompt(self):
        limit_expression = f"{self.limit_number} {self.limit_type}"
        return SYSTEM_PROMPT_TEMPLATE.format(limit_expression)

    def show_settings(self):
        self.input_format = st.selectbox(
            label="Input Format", options=INPUT_FORMAT_OPTIONS
        )
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
                value=self.bucket_name,
                help="Geben Sie die ARN des S3-Buckets ein, der die Dateien enthält, die Sie zusammenfassen möchten.",
            )

    def run(self):
        def show_summary_text_field():
            st.markdown(self.token_use_expression())
            st.text_area("Zusammenfassung", value=self.output, height=400)
            show_download_button(text_data=self.output)

        def generate_summary(text: str, placeholder) -> str:
            """
            Generate a summary of the given text. if the text does not fit into the max_tokens limit,
            it is split into chunks and a summary is generated for each chunk.

            Args:
                text (str): The input text to be summarized.
                placeholder: The placeholder object to write progress updates.

            Returns:
                str: The generated summary of the text.
            """
            self.tokens_in, self.tokens_out = 0, 0
            buffer_number = self.limit_number
            buffer_type = self.limit_type
            self.limit_number = 1
            self.limit_type = "sentence"
            input_chunks = split_text(text, chunk_size=self.chunk_size())
            output_chunks = []
            for chunk in input_chunks:
                response, tokens = self.get_completion(text=chunk, index=0)
                output_chunks.append(response)
                placeholder.write(
                    f"Chunk {input_chunks.index(chunk) + 1} / {len(input_chunks)} completed"
                )
                self.tokens_in += tokens[0]
                self.tokens_out += tokens[1]
            self.limit_number = buffer_number
            self.limit_type = buffer_type
            
            # generate a summary for all chunks
            text = " ".join(output_chunks)
            # make sure the summary is not longer than the limit
            input_chunks = split_text(text, chunk_size=self.chunk_size())
            if len(input_chunks) > 1:
                logger.info(f"Summary too long after summarizing the document in chunks. Only the first {self.chunk_size()} of {get_token_size(text)} tokens were used for summary.")
            self.output, tokens = self.get_completion(text=input_chunks[0], index=0)
            self.tokens_in += tokens[0]
            self.tokens_out += tokens[1]

        if st.button("Zusammenfassung"):
            with st.spinner("Generiere Zusammenfassung..."):
                self.errors = []
                placeholder = st.empty()
                if (
                    INPUT_FORMAT_OPTIONS.index(self.input_format)
                    == InputFormat.DEMO.value
                ):
                    self.output, tokens = self.get_completion(text=self.text, index=0)
                    self.tokens_in, self.tokens_out = tokens
                    show_summary_text_field()

                elif (
                    INPUT_FORMAT_OPTIONS.index(self.input_format)
                    == InputFormat.FILE.value
                ):
                    if self.input_file:
                        if check_file_type(self.input_file) == "pdf":
                            text = extract_text_from_pdf(self.input_file)
                            generate_summary(text, placeholder)
                            show_summary_text_field()
                elif (
                    INPUT_FORMAT_OPTIONS.index(self.input_format)
                    == InputFormat.ZIPPED_FILE.value
                ):
                    if self.input_file:
                        if check_file_type(self.input_file) == "zip":
                            summaries = []
                            file_names = []
                            with zipfile.ZipFile(self.input_file, "r") as zip_ref:
                                for file in zip_ref.infolist():
                                    text, out_filename = "", ""
                                    placeholder.markdown(
                                        f"{file.filename} wird zusammengefasst."
                                    )
                                    if file.filename.endswith(".pdf"):
                                        with zip_ref.open(file) as pdf_file:
                                            text = extract_text_from_pdf(
                                                pdf_file, placeholder
                                            )
                                            out_filename = file.filename.replace(
                                                ".pdf", ".txt"
                                            )
                                    elif file.filename.endswith(".txt"):
                                        with zip_ref.open(file) as text_file:
                                            binary_content = text_file.read()
                                            text = get_text_from_binary(binary_content)
                                            out_filename = file.filename
                                    if text > "":
                                        generate_summary(text, placeholder)
                                        summaries.append(self.output)
                                        file_names.append(out_filename)
                                    else:
                                        st.warning(
                                            f"Die Datei {file.filename} hat nicht das richtige Format und ist leer oder konnte nicht gelesen werden."
                                        )
                            self.output_file = (
                                OUTPUT_PATH
                                + self.input_file.name.replace(".zip", "_output.zip")
                            )
                            placeholder.markdown(
                                f"Alle Dateien in wurden zusammengefasst und können als ZIP-Datei heruntergeladen werden."
                            )
                            zip_texts(summaries, file_names, self.output_file)
                    if self.output_file:
                        download_file_button(self.output_file, "Datei herunterladen")

                elif (
                    INPUT_FORMAT_OPTIONS.index(self.input_format)
                    == InputFormat.S3.value
                ) and (self.s3_input_bucket > ""):
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=get_var('aws_access_key_id'),
                        aws_secret_access_key=get_var('aws_secret_access_key'),
                        region_name=get_var('aws_region')
                    )
                    response = s3_client.list_objects_v2(
                        Bucket=self.bucket_name,
                        Prefix=self.input_prefix
                    )
                    if 'Contents' in response:
                        for item in response['Contents']:
                            file_key = item['Key']
                            # skip folders
                            if file_key.endswith('/'):
                                continue
                            try:
                                file_obj = s3_client.get_object(
                                    Bucket=self.bucket_name,
                                    Key=file_key
                                )
                                text = ""
                                output_file_key = file_key.replace(
                                    self.input_prefix,
                                    self.output_prefix
                                )
                                if file_key.endswith(".txt"):
                                    text = file_obj['Body'].read().decode('utf-8')
                                elif file_key.endswith(".pdf"):
                                    pdf_stream = BytesIO(file_obj['Body'].read())
                                    text = extract_text_from_pdf(pdf_stream, placeholder)
                                    output_file_key = output_file_key.replace('.pdf', '.txt')
                                if text > "":
                                    token_number = get_token_size(text)
                                    logger.info(f"Summarizing {file_key} ({token_number} tokens)")
                                    generate_summary(text, placeholder)
                                    s3_client.put_object(
                                        Bucket=self.bucket_name,
                                        Key=output_file_key,
                                        Body=self.output
                                    )
                                else:
                                    st.warning(
                                        f"Die Datei {file.filename} hat nicht das richtige Format und ist leer oder konnte nicht gelesen werden."
                                    )
                            except Exception as e:
                                st.warning(str(e))
                        st.success(f"Alle Dateien wurden zusammengefasst und im Bucket {self.bucket_name}{self.output_prefix} abgelegt.")
                        st.markdown(self.token_use_expression())
                    else:
                        st.write("No files in the bucket.")            
