import streamlit as st
import os
import pandas as pd
from enum import Enum

from helper import init_logging, extract_text_from_file
from tools.tool_base import (
    ToolBase,
    DEFAULT_MODEL,
    LOGFILE,
    DEMO_PATH,
    DEFAULT_MODEL
)


DEMO_TEXTS_FILES = [DEMO_PATH + "000000406047.pdf", DEMO_PATH + "drohbrief.txt"]
SYSTEM_PROMPT_TEMPLATE = """You will be provided with a text. Your task is to perform a sentiment analysis on the text you respond with a list of two results:
1. the sentiment from the followoing list of sentiments[{}].
2. a probability score between 0 and 1 that the sentiment is correct.

example input: "ich fand ihren Service wirklich sehr gut, das Geschenk hat meiner Frau sehr gefallen
example output (where sentiments: ['positiv', 'negativ', 'neutral']): [positiv, 0.8]
"""

class InputFormat(Enum):
    DEMO = 0


logger = init_logging(__name__, LOGFILE)


class SentientAnalysis(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Sentiment Analysis"
        self._settings = {}
        self.results_df = pd.DataFrame()
        self.stats_df = pd.DataFrame()
        self.errors = []
        self.category_list_expression = ""

        self.texts_input = None
        self.categories_input = None
        self.categories_df = pd.DataFrame()
        self.texts_df = pd.DataFrame()
        self.sentiments = ["positiv", "negativ", "neutral"]

        self.formats = ["Demo"]
        self.input_type = self.formats[0]
        self.model = DEFAULT_MODEL
        self.results = []

        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()

    def show_settings(self):
        def manage_demo():
            ...

        def manage_file_upload():
            st.info("Noch nicht implementiert.")

        if self.formats.index(self.input_type) == InputFormat.DEMO.value:
            manage_demo()
        else:
            st.warning("Diese Option wird noch nicht unterstützt.")
        
        _ = st.text_area("Gefühle, auf die der Text geprüft werden soll", ", ".join(self.sentiments))
        self.sentiments = _.split(", ")
        self.input_type = st.radio("Input", options=self.formats)
        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(', '.join(self.sentiments))

    def transform_to_list(self, text):
        if text.startswith('[') and text.endswith(']'):
            # Removing the square brackets
            cleaned_string = text[1:-1]
            # Splitting by comma and converting to a list
            result = cleaned_string.split(", ")
            # Converting the second element to float, assuming it's always a valid number
            result[1] = float(result[1])
            return result
        else:
            return []
    
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
            help="Du kannst diesen Text manuell anpassen um die Sensitivität der Analyse zu testen.",
        )
        if st.button("Starte Sentiment-Analyse"):
            if len(self.results) == 0:
                self.results.append([])
            _, tokens = self.get_completion(text=self.texts_input, index=0)
            self.results[0] = self.transform_to_list(_)

        if len(self.results) > 0:
            st.markdown(f"Ergebnis: {self.results[0][0]} (Wahrscheinlichkeit: {self.results[0][1]})")
