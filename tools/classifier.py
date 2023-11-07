
import streamlit as st
import time
from tools.tool_base import ToolBase
import os
import pandas as pd

class Classifier(ToolBase):
    def __init__(self, logger):
        self.title = "Klassifizerung"
        self.formats = ['Demo', 'csv Datei', 'Interaktive Eingabe']
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.text = ""
        self.encoding_source = "utf-8"

    def show_settings(self):
        self.input_type = st.selectbox(
            "Input",
            options=self.formats
        )
        
        if self.formats.index(self.input_type) == 0:
            self.texts_df = pd.read_excel('./data/demo/demo_texts.xlsx')
            self.texts_df.columns = ['text_id', 'text']
            categories_df = pd.read_excel('./data/demo/demo_categories.xlsx')
            categories_df.columns = ['cat_id', 'text']
            self.categories_dic = dict(zip(categories_df['cat_id'], categories_df['text']))
            with st.expander("Demo-Texte", expanded=False):
                st.table(self.texts_df)
            with st.expander("Kategorien", expanded=False):
                st.table(self.categories_dic)
        else:
            st.warning("Diese Option wird noch nicht unterstützt.")

    def run(self):
        if st.button("Klassifizieren"):
            with st.spinner("Klassifizierung läuft..."):
                time.sleep(10)
            st.success("Klassifizierung erfolgreich!")