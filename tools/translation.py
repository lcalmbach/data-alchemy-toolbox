
import streamlit as st
import time
import pandas as pd
import iso639
import os

from tools.tool_base import ToolBase
class Translation(ToolBase):
    def __init__(self, logger):
        self.logger = logger
        self.title = "Übersetzung"
        self.lang_source = 'de'
        self.lang_target = 'en'
        self.texts_df = pd.DataFrame()
        self.language_dict = self.get_language_dict()
        self.translation_input_options = ['Dokumentensammlung (gezippt)', 'Texte aus csv-Datei', 'json-Datei']
        self.translation_input_type = self.translation_input_options[0]
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()

    def show_settings(self):
        index_source = list(self.language_dict.keys()).index(self.lang_source)
        index_target = list(self.language_dict.keys()).index(self.lang_target)
        self.lang_source = st.selectbox(label='Übersetze von',
                                        options=self.language_dict.keys(),
                                        format_func=lambda x: self.language_dict[x],
                                        index=index_source)
        self.lang_target = st.selectbox(label='Übersetze nach',
                                        options=self.language_dict.keys(),
                                        format_func=lambda x: self.language_dict[x],
                                        index=index_target)
        self.translation_input_type = st.radio("Format deines Input für die Übersetzung",
                                               options=self.translation_input_options)
        file = st.file_uploader('Datei hochladen')
        if file:
            st.success('Datei erfolgreich hochgeladen!')

    def get_language_dict(self):
        keys = [lang["iso639_1"] for lang in iso639.data if lang["iso639_1"] != ""]
        values = [lang["name"] for lang in iso639.data if lang["iso639_1"] != ""]
        return dict(zip(keys, values))
    
    def run(self):
        st.info("Diese Option wird noch nicht unterstützt.")
