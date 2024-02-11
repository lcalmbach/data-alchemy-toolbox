import streamlit as st
import pandas as pd
import zipfile
import os
from enum import Enum
import boto3
import json
from io import BytesIO
from helper import (
    init_logging,
    check_file_type,
    extract_text_from_uploaded_file,
    show_download_button,
    zip_texts,
    get_text_from_binary,
    download_file_button,
    get_var,
    get_token_size,
    display_pdf,
    extract_text_from_file,
    save_json_object,
)
from tools.tokenizer import split_text, calc_token_size
from tools.tool_base import ToolBase, MODEL_OPTIONS, LOGFILE, OUTPUT_PATH

logger = init_logging(__name__, LOGFILE)

DEMO_FILES = "./data/demo/summary_folder/"
SYSTEM_PROMPT_TEMPLATE = "You will be provided with a text. Your task is to summarize the text in German. The summary should contain a maximum of {}. Focus on the main results."
LIMIT_OPTIONS = ["Zeichen", "Tokens", "Sätze"]
FILE_FORMAT_OPTIONS = ["pdf", "txt"]
INPUT_FORMAT_OPTIONS = ["Demo", "Datei Hochladen", "ZIP hochladen", "S3-Bucket"]


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
        self.model = MODEL_OPTIONS[1]
        self.title = "Zusammenfassung"
        self.script_name, script_extension = os.path.splitext(__file__)

        self.limit_type = LIMIT_OPTIONS[0]
        self.limit_number = 500
        self.model = MODEL_OPTIONS[1]
        self.input_files = []
        self.output_file = None
        self.results = []
        self.bucket_name = "data-alchemy-bucket-01"
        self.input_prefix = "input/"
        self.output_prefix = "output/"
        self.text = ""

        self.intro = self.get_intro()
        self.input_format = INPUT_FORMAT_OPTIONS[0]
    @property
    def system_prompt(self):
        limit_expression = f"{self.limit_number} {self.limit_type}"
        return SYSTEM_PROMPT_TEMPLATE.format(limit_expression)

    def show_settings(self):
        self.input_format = st.radio(label="Input Format", options=INPUT_FORMAT_OPTIONS)
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
        st.markdown("---")
        if INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.DEMO.value:
            files = os.listdir(DEMO_FILES)
            selected = [True for x in files if x.endswith(".pdf")]
            df = pd.DataFrame({"datei": files, "auswahl": selected})
            st.markdown("Wähle die Dateien, die du zusammenfassen möchtest.")
            df = st.data_editor(df)
            self.input_files = df[df["auswahl"] == True]["datei"].tolist()
            sel_preview = st.selectbox("Vorschau", options=self.input_files)
            preview_type = st.radio(
            "Vorschau Format", options=["pdf", "text"], help = 'PDF Vorschau: nur für Dokumente < 2MB'
            )
            file_path = os.path.join(DEMO_FILES, sel_preview)
            if preview_type.startswith("pdf"):
                display_pdf(file_path)
            else:
                text = extract_text_from_file(file_path)
                self.text = st.text_area(
                    "Extrahierter Text aus Dokument {sel_preview}",
                    value=text,
                    height=400,
                )
        elif INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.FILE.value:
            self.input_file = st.file_uploader(
                "PDF oder Text Datei",
                type=FILE_FORMAT_OPTIONS,
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
            if self.input_file:
                with st.expander("ZIP Datei Inhalt"):
                    # Preview zip content
                    with zipfile.ZipFile(self.input_file, "r") as zip_ref:
                        for file in zip_ref.infolist():
                            st.markdown(f"- {file.filename}")
                self.output_file = OUTPUT_PATH + self.input_file.name.replace(
                    ".zip", "_output.zip"
                )
        elif INPUT_FORMAT_OPTIONS.index(self.input_format) == InputFormat.S3.value:
            self.s3_input_bucket = st.text_input(
                "S3-Bucket",
                value=self.bucket_name,
                help="Gib die ARN des S3-Buckets ein, der die Dateien enthält, die du zusammenfassen möchten. Beachte, dass die Applikation Leserecht auf dem bucket haben muss oder dass der Bucket öffentlich zugänglich ist.",
            )

    def extract_title(self, text: str):
        prompt = f"Extract the title for the following text:\n\n{text}"
        title, tokens = self.get_completion(text=prompt, index=0)
        return title, tokens

    def save_file(self, file: str, result: dict):
        file_path = os.path.join(OUTPUT_PATH, file.replace(".pdf", ".json"))
        save_json_object(result, file_path)

    def run(self):
        def show_summary_text_field(result):
            st.markdown(f"**Titel:** {result['title']}")
            st.text_area("Zusammenfassung", value=result['summary'], height=400)
            show_download_button(text_data=json.dumps(result, indent=4))

        def generate_summary(text: str, file: str, placeholder) -> str:
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
            input_chunks = split_text(
                text,
                system_prompt=self.system_prompt,
                model_name=self.model,
                max_tokens_per_chunk=self.chunk_size(),
            )
            output_chunks = []
            for chunk in input_chunks:
                response, tokens = self.get_completion(text=chunk, index=0)
                output_chunks.append(response)
                placeholder.write(
                    f"File: {file}: Chunk {input_chunks.index(chunk) + 1} / {len(input_chunks)} completed"
                )

            text = " ".join(output_chunks)
            # make sure the summary is not longer than the limit
            input_chunks = split_text(
                text,
                system_prompt=self.system_prompt,
                model_name=self.model,
                max_tokens_per_chunk=self.chunk_size(),
            )
            if len(input_chunks) > 1:
                logger.info(
                    f"Der Text ist für eine Zusammenfassung mit diesem Modell zu lang. Nur die ersten {self.chunk_size()} von {get_token_size(text)} token werden verwendet."
                )
            text, tokens = self.get_completion(text=input_chunks[0], index=0)
            return text, tokens

        self.display_selected_model()
        st.markdown(f"{len(self.input_files)} Dateien werden zusammengefasst.")
        if st.button("Zusammenfassung"):
            self.results = []
            with st.spinner("Generiere Zusammenfassung..."):
                self.errors = []
                placeholder = st.empty()
                if (
                    INPUT_FORMAT_OPTIONS.index(self.input_format)
                    == InputFormat.DEMO.value
                ):
                    for file in self.input_files:
                        text = extract_text_from_file(os.path.join(DEMO_FILES, file))
                        title, tokens = self.extract_title(text[:500])
                        self.add_tokens(tokens)
                        summary, tokens = generate_summary(text, file, placeholder)
                        self.add_tokens(tokens)
                        result = {'title': title, 'summary': summary, 'tokens_in': tokens[0], 'tokens_out': tokens[1]}
                        self.results.append(result)
                        self.save_file(file, result)

                elif (
                    INPUT_FORMAT_OPTIONS.index(self.input_format)
                    == InputFormat.FILE.value
                ):
                    if self.input_file:
                        if check_file_type(self.input_file) == "pdf":
                            text = extract_text_from_uploaded_file(self.input_file)
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
                                            text = extract_text_from_uploaded_file(
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
                        "s3",
                        aws_access_key_id=get_var("aws_access_key_id"),
                        aws_secret_access_key=get_var("aws_secret_access_key"),
                        region_name=get_var("aws_region"),
                    )
                    response = s3_client.list_objects_v2(
                        Bucket=self.bucket_name, Prefix=self.input_prefix
                    )
                    if "Contents" in response:
                        for item in response["Contents"]:
                            file_key = item["Key"]
                            # skip folders
                            if file_key.endswith("/"):
                                continue
                            try:
                                file_obj = s3_client.get_object(
                                    Bucket=self.bucket_name, Key=file_key
                                )
                                text = ""
                                output_file_key = file_key.replace(
                                    self.input_prefix, self.output_prefix
                                )
                                if file_key.endswith(".txt"):
                                    text = file_obj["Body"].read().decode("utf-8")
                                elif file_key.endswith(".pdf"):
                                    pdf_stream = BytesIO(file_obj["Body"].read())
                                    text = extract_text_from_uploaded_file(
                                        pdf_stream, placeholder
                                    )
                                    output_file_key = output_file_key.replace(
                                        ".pdf", ".txt"
                                    )
                                if text > "":
                                    token_number = get_token_size(text)
                                    logger.info(
                                        f"Summarizing {file_key} ({token_number} tokens)"
                                    )
                                    generate_summary(text, placeholder)
                                    s3_client.put_object(
                                        Bucket=self.bucket_name,
                                        Key=output_file_key,
                                        Body=self.output,
                                    )
                                else:
                                    st.warning(
                                        f"Die Datei {file.filename} hat nicht das richtige Format, ist leer oder konnte nicht gelesen werden."
                                    )
                            except Exception as e:
                                st.warning(str(e))
                        st.success(
                            f"Alle Dateien wurden zusammengefasst und im Bucket {self.bucket_name}{self.output_prefix} abgelegt."
                        )
                    else:
                        st.write("No files in the bucket.")
               
                if len(self.results) > 0:
                    st.markdown('---')
                    with st.expander('Verwendete Tokens'):
                        st.markdown(self.token_use_expression())
                    for result in self.results:
                        show_summary_text_field(result)
