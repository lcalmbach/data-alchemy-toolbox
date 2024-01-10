import streamlit as st
import json
from datetime import datetime
import os
import pandas as pd
import altair as alt
from enum import Enum

from helper import init_logging, extract_text_from_file
from tools.tool_base import (
    ToolBase,
    MODEL_OPTIONS,
    MAX_ERRORS,
    LOGFILE,
    DEMO_PATH,
    OUTPUT_PATH,
)


DEFAULT_MODEL = "gpt-3.5-turbo"
DEMO_TEXTS_FILES = [DEMO_PATH + "000000406047.pdf", DEMO_PATH + "drohbrief.txt"]


class InputFormat(Enum):
    DEMO = 0
    FILE = 1


logger = init_logging(__name__, LOGFILE)


class Moderator(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Moderator"
        self._settings = {}
        self.results_df = pd.DataFrame()
        self.stats_df = pd.DataFrame()
        self.errors = []
        self.category_list_expression = ""

        self.texts_input = None
        self.categories_input = None
        self.categories_df = pd.DataFrame()
        self.texts_df = pd.DataFrame()

        self.formats = ["Demo", "pdf/txt Datei hochladen"]
        self.input_type = self.formats[0]
        self.model = MODEL_OPTIONS[0]

        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()

    def show_settings(self):
        def manage_demo():
            ...

        def manage_file_upload():
            st.info("Noch nicht implementiert.")

        self.input_type = st.radio("Input", options=self.formats)
        if self.formats.index(self.input_type) == InputFormat.DEMO.value:
            manage_demo()
        elif self.formats.index(self.input_type) == InputFormat.FILE.value:
            manage_file_upload()
        else:
            st.warning("Diese Option wird noch nicht unterstützt.")

    def run(self):
        """
        Runs the GPT-3 API on each row of the input DataFrame and categorizes
        the text according to the user's instructions.

        Returns:
            pandas.DataFrame: A copy of the input DataFrame with an additional
            'result' column containing the API's categorized output.

        Raises:
            OpenAIError: If there is a problem with the OpenAI API request.
            ValueError: If the 'OPENAI_API_KEY' environment variable is not
            set.
        """
        file = self.texts_input = st.selectbox(
            "Texte",
            options=DEMO_TEXTS_FILES,
        )
        if file.endswith(".pdf"):
            self.texts_input = extract_text_from_file(file)
        else:
            with open(file, "r", encoding="utf-8") as file:
                self.texts_input = file.read()
        self.texts_input = st.text_area(
            "Text",
            value=self.texts_input,
            height=300,
            help="Du kannst diesen Text manuell anpassen um die Sensitivität der Analyse für verschiedene Kategorien zu testen.",
        )
        if st.button("Text überprüfen"):
            sentences = self.texts_input.split(".")
            results = []
            for sentence in sentences:
                output = self.usage_compliance_check(sentence)
                flagged = output["results"][0]["flagged"]
                results.append(flagged)
                flag = '❌' if flagged else '✅'
                with st.expander(f"{sentence}: {flag}"):
                    st.write(output["results"][0])
            st.markdown(f"Gesamtergebnis: {'❌' if any(results) else '✅'}")
