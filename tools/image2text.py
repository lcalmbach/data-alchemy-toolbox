from openai import OpenAI
import streamlit as st
import os
import pandas as pd
from enum import Enum
from PIL import Image
from PIL.ExifTags import TAGS
import requests
from io import BytesIO
import base64
import zipfile

from helper import (
    init_logging,
    save_uploadedfile,
    encode_image,
    convert_df_to_csv,
    url_exists,
    encode_image,
)
from tools.tool_base import ToolBase, TEMP_PATH, IMAGE_PATH, UPLOAD_PATH


FILE_FORMAT_OPTIONS = ["jpg", "jpeg", "png", "gif"]

class InputFormat(Enum):
    DEMO = 0
    FILE = 1
    URL = 2
    ZIPPED_FILE = 3


class Image2Text(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Image zu Text"
        self.formats = ["Demo", "Image File", "Image URL", "Zip File"]
        self.MODEL_OPTIONS = ["gpt-4o-mini", "gpt-4o"]
        self.model = self.MODEL_OPTIONS[0]
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.text = None
        self.input_file = None
        self.image_dict = {}
        self.text_dict = {}
        self.demo_images = self.get_demo_images()
        self.input_file_url = ''

    def get_demo_images(self):
        # generates a list of image_file_names: imag_file_path objects from the impaage_path directory
        image_files = os.listdir(IMAGE_PATH)
        image_files = {IMAGE_PATH + file:file for file in image_files}
        return image_files
    
    def extract_metadata(self, source_path: str) -> dict:
        """
        Extracts metadata from an image.

        Args:
            source_path (str): The path to the image file or URL.

        Returns:
            dict: A dictionary containing the extracted metadata, or an error message if the metadata is not found.
        """
        # Check if the source is a URL
        if source_path.lower().startswith("http"):
            # Handle URL
            response = requests.get(source_path)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
            else:
                return "Failed to retrieve the image from the URL."
        else:
            # Handle local file
            img = Image.open(source_path)
        with img:
            exif_data = img._getexif()
            if exif_data is not None:
                return {TAGS.get(key): value for key, value in exif_data.items()}
            else:
                return "Das Bild enthält keine EXIF Metadaten."

    def show_settings(self):
        self.input_type = st.radio("Input für Image2Text", options=self.formats)
        self.model = st.selectbox(
            label="Modell",
            options=self.MODEL_OPTIONS,
            help="Zur Zeit wird nur das Modell gpt-4o-mini unterstützt.",
        )
        if self.formats.index(self.input_type) == InputFormat.FILE.value:
            self.input_file = st.file_uploader(
                "Bild Datei hochladen",
                type=FILE_FORMAT_OPTIONS,
                help="Lade das Bild hoch, das du beschreiben möchtest.",
            )
            if self.input_file is not None:
                ok, err_msg = save_uploadedfile(self.input_file, TEMP_PATH)
                if ok:
                    image = Image.open(self.input_file)
                    st.image(
                        image, caption="Hochgeladenes Bild.", use_column_width=True
                    )
                else:
                    st.error(err_msg)
        elif self.formats.index(self.input_type) == InputFormat.URL.value:
            image_url = st.text_input(
                "Bild URL eingeben",
                help="Gebe die URL ein für das Bild, das du beschreiben möchtest.",
            )
            ok, err_msg = url_exists(image_url)
            if ok and image_url != self.input_file_url:
                self.input_file_url = image_url
                self.text = None
                try:    
                    response = requests.get(self.input_file_url)
                    response.raise_for_status()  # Stellt sicher, dass die Anfrage erfolgreich war
                    image = Image.open(BytesIO(response.content))
                    st.image(
                        image,
                        caption=f"Geladenes Bild ({self.input_file_url}).",
                        use_column_width=True,
                    )
                    self.input_file = UPLOAD_PATH + "temp_image.jpg"
                    image.save(self.input_file)
                except Exception as e:
                    # only report error if the user has entered a URL
                    if self.input_file.startswith("http"):
                        st.error(f"Ein Fehler ist aufgetreten: {e}")
        elif self.formats.index(self.input_type) == InputFormat.ZIPPED_FILE.value:
            self.input_file = st.file_uploader(
                "ZIP Datei hochladen",
                type=["zip"],
                help="Lade die Zip Datei hoch, welche die zu beschreibenden Bilder enthält.",
            )
            if self.input_file is not None:
                files = []
                images = []
                with zipfile.ZipFile(self.input_file, "r") as z:
                    # List of file names in the zip
                    for file_name in z.namelist():
                        if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                            byte_data = z.read(file_name)
                            image = Image.open(BytesIO(byte_data))
                            images.append(image)
                            files.append(file_name)
                self.image_dict = dict(zip(files, images))
                file = st.selectbox(
                    "Vorschau der Bilder",
                    options=files,
                )
                st.image(
                    self.image_dict[file], caption=file_name, use_column_width=True
                )

    def image2text(self, file_path: str) -> str:
        client = OpenAI()
        base64_image = encode_image(file_path)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Descscribe the picture in german. The location is Basel, Switzerland",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url":  f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            },
                        },
                    ],
                }
            ],
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content

    def run_demo(self):
        sel_image = st.selectbox(
            "Wähle ein Bild aus", 
            options=list(self.demo_images.keys()),
            format_func=lambda x: self.demo_images[x]
        )
        st.image(sel_image)
        metadata = self.extract_metadata(sel_image)
        with st.expander("EXIF Metadaten"):
            st.write(metadata)
        # make sure the text does not appear if the user selects a new image
        if self.input_file != sel_image:
            self.text = None
        if st.button("Bild zu Text", disabled=self.input_file == sel_image):
            self.input_file = sel_image
            with st.spinner("Bilderkennung läuft..."):
                self.text = self.image2text(self.input_file)
        if self.text:
            st.text_area("Beschreibung des Bilds", self.text, height=500)

    def run_uploaded_file(self):
        if self.input_file is not None:
            image = Image.open(self.input_file)
            st.image(image, caption="Hochgeladenes Bild", use_column_width=True)
            metadata = self.extract_metadata(TEMP_PATH + self.input_file)
            with st.expander("EXIF Metadaten"):
                st.write(metadata)
        if st.button("Bild zu Text", disabled=self.input_file is None):
            base64_image = encode_image(TEMP_PATH + self.input_file.name)
            with st.spinner("Bilderkennung läuft..."):
                self.text = self.image2text(f"data:image/jpeg;base64,{base64_image}")
        if self.text:
            st.text_area("Beschreibung des Bilds", self.text, height=500)

    def run_url(self):
        ok = os.path.isfile(self.input_file)
        if ok:
            st.image(self.input_file)
            metadata = self.extract_metadata(self.input_file)
            with st.expander("EXIF Metadaten"):
                st.write(metadata)
        if st.button("Bild zu Text", disabled=not ok):
            self.text = None
            with st.spinner("Bilderkennung läuft..."):
                self.text = self.image2text(self.input_file)
        if self.text is not None:
            st.text_area("Beschreibung des Bilds", self.text, height=500)

    def run_zipped_file(self):
        if st.button("Bild zu Text", disabled=self.input_file is None):
            placeholder = st.empty()
            with st.spinner("Bilderkennung läuft..."):
                self.text = None
                for file, image in self.image_dict.items():
                    placeholder.markdown(f"Erkennung Bild {file}")
                    buffer = BytesIO()
                    image.save(buffer, format="PNG")
                    byte_data = buffer.getvalue()
                    # Encode the bytes to Base64
                    base64_image = base64.b64encode(byte_data).decode()
                    text = self.image2text(f"data:image/jpeg;base64,{base64_image}")
                    self.text_dict[file] = text
            st.success("Bildbeschreibung abgeschlossen.")

        if self.text_dict:
            file = st.selectbox(
                "Texte",
                options=self.text_dict.keys(),
            )
            st.text_area("Beschreibung des Bilds", self.text_dict[file], height=500)
            df_texts = pd.DataFrame.from_dict(
                self.text_dict, orient="index", columns=["Datei", "Text"]
            )
            csv_data = convert_df_to_csv(df_texts)
            st.download_button(
                label="Texte im CSV format herunterladen",
                data=csv_data,
                file_name="df_texts.csv",
                mime="text/csv",
            )

    def run(self):
        if self.formats.index(self.input_type) == InputFormat.DEMO.value:
            self.run_demo()
        elif self.formats.index(self.input_type) == InputFormat.FILE.value:
            self.run_uploaded_file()
        elif self.formats.index(self.input_type) == InputFormat.URL.value:
            self.run_url()
        elif self.formats.index(self.input_type) == InputFormat.ZIPPED_FILE.value:
            self.run_zipped_file()
