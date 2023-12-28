import streamlit as st
import json
import io
import os
from io import StringIO
import socket
import string
import csv
import zipfile
import random
import logging
import fitz
import tiktoken
import base64
import requests

LOCAL_HOST = "liestal"
LOGFILE = "./data-alchemy-toolbox.log"


def download_file_button(file_path: str, button_text: str = "Download"):
    """
    Creates a Streamlit download button that allows users to download a file.

    Parameters:
        button_text (str): The text to display on the download button. Default is "Download".
        file_path (str): The path to the file to be downloaded.

    Returns:
        None
    """
    if st.button(button_text):
        with open(file_path, "rb") as file:
            file_data = file.read()
        st.download_button(
            label="Click here to download",
            data=file_data,
            key="file_download",
            file_name=file_path,
        )


def download_button(data, download_filename, button_text):
    """
    Generates a download button for a given data object.

    Parameters:
    - data: The data object to be downloaded.
    - download_filename: The name of the file to be downloaded.
    - button_text: The text to be displayed on the download button.

    Returns:
    None
    """

    # Create a BytesIO buffer
    json_bytes = json.dumps(data).encode("utf-8")
    buffer = io.BytesIO(json_bytes)

    # Set the appropriate headers for the browser to recognize the download
    st.set_option("deprecation.showfileUploaderEncoding", False)
    st.download_button(
        label=button_text,
        data=buffer,
        file_name=download_filename,
        mime="application/json",
    )


def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except ValueError:
        return False


def get_hostname():
    return socket.gethostname().lower()


def get_var(varname: str) -> str:
    """
    Retrieves the value of a given environment variable or secret from the Streamlit configuration.

    If the current host is the local machine (according to the hostname), the environment variable is looked up in the system's environment variables.
    Otherwise, the secret value is fetched from Streamlit's secrets dictionary.

    Args:
        varname (str): The name of the environment variable or secret to retrieve.

    Returns:
        The value of the environment variable or secret, as a string.

    Raises:
        KeyError: If the environment variable or secret is not defined.
    """
    if socket.gethostname().lower() == LOCAL_HOST:
        return os.environ[varname]
    else:
        return st.secrets[varname]


def get_random_word(length=5) -> str:
    """
    Generate a random word of a given length.

    This function generates a random word by choosing `length` number of random letters from ASCII letters.

    Parameters:
    length (int): The length of the random word to generate. Default is 5.

    Returns:
    str: The generated random word.
    """
    # Choose `length` random letters from ascii_letters
    letters = string.ascii_letters
    return "".join(random.choice(letters) for _ in range(length))


def create_file(file_name: str, columns: list) -> None:
    """
    Creates a new file and writes the columns list to the file.

    Parameters:
    file_name (str): The name of the file to be created.
    columns (list): The list of columns to be written to the file.

    Returns:
    None
    """
    with open(file_name, "w", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(columns)
        print(f"File {file_name} created.")


def append_row(file_name: str, row: list) -> None:
    """
    Appends a row to a CSV file.

    Args:
        file_name (str): The name of the CSV file to append to.
        row (list): The row to append to the CSV file.

    Returns:
        None
    """
    with open(file_name, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerows(row)


def zip_texts(texts: list, filenames: list, zip_filename: str = "summaries.zip"):
    """
    Zips a list of texts into a zip file.

    Args:
        texts (list): A list of texts to be zipped.
        filenames (list): A list of filenames corresponding to each text.
        zip_filename: filename of zipfile

    Returns:
        None
    """

    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for text, file_name in zip(texts, filenames):
            zipf.writestr(file_name, text)


def zip_files(file_names: list, target_file: str):
    """
    Compresses a list of files into a zip file. The zip file will be
    downloaded to the user's computer if download button is clicked.

    :return: None
    """

    # Create a new zip file and add files to it
    with zipfile.ZipFile(target_file, "w") as zipf:
        for file in file_names:
            # Add file to the zip file
            # The arcname parameter avoids storing the full path in the zip file
            zipf.write(file, arcname=os.path.basename(file))


def init_logging(name, filename, console_level=logging.DEBUG, file_level=logging.ERROR):
    """
    Initialize logging configuration.

    Args:
        name (str): The name of the logger.
        filename (str): The name of the log file.
        console_level (int, optional): The logging level for console output. Defaults to logging.DEBUG.
        file_level (int, optional): The logging level for file output. Defaults to logging.ERROR.

    Returns:
        logging.Logger: The configured logger object.
    """
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(
        min(console_level, file_level)
    )  # Set to the lower of the two levels

    # Create a file handler and set level
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(file_level)

    # Create a console handler and set level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)

    # Create a formatter with a custom time format (excluding milliseconds)
    time_format = "%Y-%m-%d %H:%M:%S"  # Custom time format
    formatter = logging.Formatter(
        f"%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt=time_format
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def split_text(text: str, chunk_size: int = 2048):
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
    for sentence in text.split("."):
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + "."
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + "."
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def check_file_type(uploaded_file):
    """
    Check the type of the uploaded file based on its content.

    Parameters:
    uploaded_file (file): The file object representing the uploaded file.

    Returns:
    str: The type of the file. Possible values are 'pdf', 'txt', 'docx',
    'xlsx', 'pptx', 'zip', 'Bad ZIP File', or 'Unknown'.
    """

    def check_msoffice_format():
        """
        Check if the uploaded file is in Microsoft Office format (docx, xlsx, pptx).

        Returns:
        str: The file format if it is a Microsoft Office file, otherwise 'zip' if it is a ZIP file, 'Bad ZIP File' if it is a corrupted ZIP file, or 'Unknown' if it is neither.
        """
        # Read the start of the file
        header = uploaded_file.read(4)  # Read first 4 bytes for ZIP signature
        uploaded_file.seek(0)  # Reset file read position

        # Check for ZIP signature (common for both DOCX and XLSX)
        if header == b"PK\x03\x04":
            # Further check internal structure if needed
            try:
                with zipfile.ZipFile(uploaded_file, "r") as zipped_file:
                    if any("word/" in item.filename for item in zipped_file.infolist()):
                        return "docx"
                    elif any("xl/" in item.filename for item in zipped_file.infolist()):
                        return "xlsx"
                    elif any(
                        "ppt/" in item.filename for item in zipped_file.infolist()
                    ):
                        return "pptx"
                    else:
                        return "zip"
            except zipfile.BadZipFile:
                return "Bad ZIP File"
        else:
            return "Unknown"

    def check_text_or_pdf() -> str:
        """
        Check if the uploaded file is a PDF or a text file.

        Returns:
        str: 'PDF' if the file is a PDF, 'Text' if the file is a text file, or 'unknown' if it is neither.
        """
        header = uploaded_file.read(1024)  # Read first 1024 bytes
        uploaded_file.seek(0)  # Reset file read position
        if header.startswith(b"%PDF-"):
            return "PDF"
        else:
            try:
                # Try reading as text
                text = header.decode("utf-8")
                return "Text"
            except UnicodeDecodeError:
                return "unknown"

    type = check_text_or_pdf()
    if type == "unknown":
        type = check_msoffice_format()
    return type


def extract_text_from_url(url: str):
    """
    Extracts text from a PDF file given its URL. The file must have a PDF or text
    content type.

    Args:
        url (str): The URL of the PDF file.

    Returns:
        str: The extracted text from the PDF file.
            If the file type is unsupported or not a PDF, returns "Unsupported file
            type or not a PDF".
    """
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful

    content_type = response.headers["Content-Type"]
    if "text/plain" in content_type:
        return response.text
    elif "application/pdf" in content_type:
        with fitz.open("pdf", response.content) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text
    else:
        return "Unsupported file type or not a PDF"


def extract_text_from_file(file_path: str) -> str:
    """
    Extracts text from a file. The file can be of type pdf of text.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The extracted text from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file extension is not supported.
    """
    _, file_extension = os.path.splitext(file_path)

    if file_extension.lower() == ".pdf":
        # Process PDF file
        with fitz.open(file_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text
    elif file_extension.lower() in [".txt", ".text"]:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    else:
        raise ValueError("Unsupported file type")


def extract_text_from_uploaded_file(uploaded_file: io.BytesIO) -> str:
    # Check the file type
    if uploaded_file.type == "application/pdf":
        # Process PDF file
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text

    elif uploaded_file.type in ["text/plain", "text/csv"]:
        # Process text file
        # Assuming the text file is encoded in 'utf-8'
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        text = stringio.read()
        return text

    else:
        return "Unsupported file type"


def show_download_button(
    text_data: str,
    download_filename: str = "download.txt",
    button_text: str = "Datei Herunterladen",
):
    """
    Function to create a download button for a given object.

    Parameters:
    - object_to_download: The object to be downloaded.
    - download_filename: The name of the file to be downloaded.
    - button_text: The text to be displayed on the download button.
    """

    # Convert the text data to a bytes stream
    text_bytes = io.BytesIO(text_data.encode("utf-8"))

    # Create a download button and offer the text data for download
    st.download_button(
        label=button_text,
        data=text_bytes,
        file_name=download_filename,
        mime="text/plain",
    )


def get_text_from_binary(binary_content: io.BytesIO):
    try:
        return binary_content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return binary_content.decode("cp1252")
        except UnicodeDecodeError:
            return binary_content.decode("latin1")
        except Exception as e:
            logger.error(str(e))
            return ""


def get_token_size(text: str, base: str = "cl100k_base") -> int:
    """
    Calculates the number of tokens in the given text using the specified base encoding.

    Args:
        text (str): The input text.
        base (str, optional): The base encoding to use. Defaults to "cl100k_base".

    Returns:
        int: The number of tokens in the text.
    """
    enc = tiktoken.get_encoding(base)
    openai_tokens = enc.encode(text)
    return len(openai_tokens)


def save_uploaded_image(uploaded_file, path: str):
    with open(os.path.join(path, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getvalue())


def save_uploadedfile(uploadedfile, path: str):
    ok, err_msg = True, ""
    try:
        with open(os.path.join(path, uploadedfile.name), "wb") as f:
            f.write(uploadedfile.getbuffer())
    except Exception as e:
        ok = False
        err_msg = str(e)
        logger.error(err_msg)
    return ok, err_msg


def encode_image(image_path: str):
    """
    Encodes an image file to base64.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64 encoded image.

    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def convert_df_to_csv(df):
    # Convert DataFrame to CSV
    output = StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()


logger = init_logging(__name__, LOGFILE)
