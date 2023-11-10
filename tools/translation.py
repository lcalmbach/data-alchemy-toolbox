
import streamlit as st
import pandas as pd
import iso639
import os

from tools.tool_base import ToolBase

SYSTEM_PROMPT_TEMPLATE = "You are a professional translator translating from {} to {}"
USER_PROMPT = "Translate the following text: {}"
DEMO_FILE = './data/demo/demo_summary.txt'


class Translation(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Übersetzung"
        self.lang_source = 'de'
        self.lang_target = 'en'
        self.texts_df = pd.DataFrame()
        self.language_dict = self.get_language_dict()
        self.formats = ['Demo', 'Dokumentensammlung (gezippt)', 'Texte aus csv-Datei', 'json-Datei']
        self.input_type = self.formats[0]
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()

    @property
    def system_prompt(self):
        return SYSTEM_PROMPT_TEMPLATE.format(
            iso639.to_name(self.lang_source),
            iso639.to_name(self.lang_target)
        )

    def show_settings(self):
        index_source = list(self.language_dict.keys()).index(self.lang_source)
        index_target = list(self.language_dict.keys()).index(self.lang_target)
        self.lang_source = st.selectbox(
            label='Übersetze von',
            options=self.language_dict.keys(),
            format_func=lambda x: self.language_dict[x],
            index=index_source)
        self.lang_target = st.selectbox(
            label='Übersetze nach',
            options=self.language_dict.keys(),
            format_func=lambda x: self.language_dict[x],
            index=index_target)
        self.input_type = st.radio(
            "Format deines Input für die Übersetzung",
            options=self.formats
            )
        if self.input_type == self.formats[0]:
            with open(DEMO_FILE, 'r', encoding='utf8') as file:
                text = file.read()
            self.text = st.text_area(
                label='Text',
                value=text,
                height=400,
                help="Geben Sie den Text ein, den Sie übersetzen möchten.")
        elif self.input_type == self.formats[1]:
            file = st.file_uploader('Datei hochladen')
            if file:
                st.success('Datei erfolgreich hochgeladen!')
        else:
            st.warning("Diese Option wird noch nicht unterstützt.")
        st.markdown('**System Prompt**')
        st.markdown(self.system_prompt)

    def get_language_dict(self):
        keys = [lang["iso639_1"] for lang in iso639.data if lang["iso639_1"] != ""]
        values = [lang["name"] for lang in iso639.data if lang["iso639_1"] != ""]
        return dict(zip(keys, values))

    def run(self):
        if st.button("Zusammenfassung"):
            with st.spinner("Übersetzung läuft..."):
                if self.input_type == self.formats[0]:
                    text = USER_PROMPT.format(self.text)
                    self.output, tokens = self.get_completion(text=text, index=0)
                    st.markdown(self.token_use_expression(tokens))
                else:
                    st.warning("Diese Option wird noch nicht unterstützt.")

        if self.input_type == self.formats[0]:
            st.markdown(self.output)

