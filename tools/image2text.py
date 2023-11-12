from openai import OpenAI
import streamlit as st
import os
import pandas as pd
from tools.tool_base import ToolBase

URL_ROOT = "https://images-datbx.s3.eu-central-1.amazonaws.com/"


class Image2Text(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Image zu Text"
        self.formats = ["Demo"]
        self.model = "gpt-4-vision-preview"
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()

    def show_settings(self):
        self.input_type = st.radio("Input für Speech2Text", options=self.formats)
        if self.formats.index(self.input_type) == 0:
            ...

    def image2text(self, url: str) -> str:
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Beschreibe den Inhalt des Bildes"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content

    def run(self):
        images_df = pd.read_csv("./data/demo/images.csv")
        images_df.columns = ["url"]
        sel_image = st.selectbox("Wähle ein Bild aus", images_df["url"])
        url = f"{URL_ROOT}{sel_image}"
        st.image(url)
        if st.button("Bild zu Text"):
            with st.spinner("Bilderkennung läuft..."):
                response = self.image2text(url)
                st.text_area("Beschreibung des Bilds", response)
