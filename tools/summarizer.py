import streamlit as st
import time
import openai
import os
from helper import create_file, append_row, zip_files, get_var
from tools.tool_base import ToolBase, MODEL_OPTIONS


DEMO_FILE = "./data/demo/demo_summary.txt"
SYSTEM_PROMPT_TEMPLATE = "You will be provided with a text. Your task is to summarize the text. The summary should contain a maximum of {}"
LIMIT_OPTIONS = ["Zeichen", "Tokens", "Sätze"]


class Summary(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.logger = logger
        self.title = "Zusammenfassung"
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.formats = ["Demo", "zip Datei"]
        self.limit_type = LIMIT_OPTIONS[0]
        self.limit_number = 500
        with open(DEMO_FILE, "r", encoding="utf8") as file:
            self.text = file.read()

    @property
    def system_prompt(self):
        limit_expression = f"{self.limit_number} {self.limit_type}"
        return SYSTEM_PROMPT_TEMPLATE.format(limit_expression)

    def show_settings(self):
        self.model = self.get_model()
        st.markdown("Begrenze die Zusammenfassung auf")
        cols = st.columns([1, 1, 4])
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
        self.input_type = st.selectbox("Input Format", options=self.formats)

        if self.formats.index(self.input_type) == 0:
            self.text = st.text_area(
                "Text",
                value=self.text,
                height=400,
                help="Geben Sie den Text ein, den Sie zusammenfassen möchten.",
            )

        else:
            st.warning("Diese Option wird noch nicht unterstützt.")

    def run(self):
        if st.button("Zusammenfassung"):
            with st.spinner("Generiere Zusammenfassung..."):
                cnt = 1
                self.errors = []

                if self.formats.index(self.input_type) == 0:
                    self.output, tokens = self.get_completion(text=self.text, index=0)
                    st.markdown(self.token_use_expression(tokens))
                    st.markdown(self.output)
                else:
                    st.warning("Diese Option wird noch nicht unterstützt.")
