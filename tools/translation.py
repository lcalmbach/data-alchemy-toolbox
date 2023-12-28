import streamlit as st
import pandas as pd
import iso639
import os
from enum import Enum

from helper import (
    extract_text_from_url,
    extract_text_from_file,
    extract_text_from_uploaded_file,
)
from tools.tool_base import ToolBase, DEMO_PATH, OUTPUT_PATH

SYSTEM_PROMPT_TEMPLATE = "You are a professional translator translating from {} to {}"
USER_PROMPT = "Translate the following text: {}"
DEMO_FILE = DEMO_PATH + "demo_summary.txt"
FILE_FORMAT_OPTIONS = ["txt", "pdf"]


class InputFormat(Enum):
    DEMO = 0
    FILE = 1
    URL = 2
    KEY_VALUE_PAIRS = 3
    MULTI_LANG_JSON = 4


class Translation(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Übersetzung"
        self.lang_source = "de"
        self.lang_target = "en"
        self.texts_df = pd.DataFrame()
        self.language_dict = self.get_language_dict()
        self.formats = [
            "Demo",
            "Text oder PDF Datei hochladen",
            "URL von Text oder PDF Datei",
            "Schlüssel-Wert-Paare in einer CSV-Datei",
            "JSON-Datei (Multi-lang-Format)",
        ]
        self.input_type = self.formats[0]
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.output = None
        self.separator = ";"

    @property
    def system_prompt(self):
        return SYSTEM_PROMPT_TEMPLATE.format(
            iso639.to_name(self.lang_source), iso639.to_name(self.lang_target)
        )

    def show_settings(self):
        self.input_type = st.radio("Input Format", options=self.formats)
        index_source = list(self.language_dict.keys()).index(self.lang_source)
        index_target = list(self.language_dict.keys()).index(self.lang_target)
        self.lang_source = st.selectbox(
            label="Übersetze von",
            options=self.language_dict.keys(),
            format_func=lambda x: self.language_dict[x],
            index=index_source,
        )
        self.lang_target = st.selectbox(
            label="Übersetze nach",
            options=self.language_dict.keys(),
            format_func=lambda x: self.language_dict[x],
            index=index_target,
        )
        if self.formats.index(self.input_type) == InputFormat.DEMO.value:
            text = extract_text_from_file(DEMO_FILE)
            self.text = st.text_area(
                label="Text",
                value=text,
                height=400,
                help="Geben Sie den Text ein, den Sie übersetzen möchten.",
            )
        elif self.formats.index(self.input_type) == InputFormat.FILE.value:
            self.input_file = st.file_uploader(
                self.input_type,
                type=FILE_FORMAT_OPTIONS,
                help="Lade die Datei hoch, die du übersetzen möchtest.",
            )
            if self.input_file is not None:
                self.text = extract_text_from_uploaded_file(self.input_file)
        elif self.formats.index(self.input_type) == InputFormat.URL.value:
            self.input_file = st.text_input(
                label=self.input_type,
                help="Gib bitte die URL der Datei ein, den du übersetzen möchtest.",
            )
            if self.input_file is not None:
                self.text = extract_text_from_url(self.input_file)
        elif self.formats.index(self.input_type) == InputFormat.KEY_VALUE_PAIRS.value:
            self.separator = st.selectbox(
                label="Trennzeichen",
                options=[";", ",", "|", "\t"],
                help="Gib bitte das Trennzeichen ein, das du in der hochgeladenen Datei verwendest.",
            )
            self.input_file = st.file_uploader(
                self.input_type,
                type=["csv"],
                help="Lade die Datei hoch, die du übersetzen möchtest.",
            )
            if self.input_file is not None:
                self.data = pd.read_csv(self.input_file, sep=self.separator)
                self.data.columns = ["key", "value"]
                with st.expander("Schlüssel-Wert-Paare"):
                    st.dataframe(self.data)
        else:
            st.warning("Diese Option wird noch nicht unterstützt.")
        with st.expander("System Prompt"):
            st.markdown(self.system_prompt)

    def get_language_dict(self):
        keys = [lang["iso639_1"] for lang in iso639.data if lang["iso639_1"] != ""]
        values = [lang["name"] for lang in iso639.data if lang["iso639_1"] != ""]
        return dict(zip(keys, values))

    def run_csv_translation(self, placeholder):
        """
        Runs the translation process for a CSV file. Texts are translated line by line.
        the result is stored in a new column called "translation" and in the end, the
        dataframe is saved to a CSV file in the output folder and a download button is
        displayed.

        Args:
            placeholder: The placeholder object used for displaying progress.

        Returns:
            None
        """
        self.data["translation"] = ""
        i = 1
        for index, row in self.data.iterrows():
            placeholder.markdown(f"Übersetze ({i}/{len(self.data)}): {row['value']}...")
            prompt = USER_PROMPT.format(row["value"])
            self.output, tokens = self.get_completion(text=prompt, index=index)
            self.data.loc[index, "translation"] = self.output
            i += 1
        filename = OUTPUT_PATH + self.input_file.name.replace(
            ".csv", "_translation.csv"
        )
        self.data.to_csv(filename, sep=self.separator, index=False)
        with st.expander("Übersetzung"):
            st.dataframe(self.data)
        st.download_button(
            label="Übersetzung herunterladen",
            data=filename,
            file_name=filename,
        )

    def run(self):
        if st.button("Übersetzung"):
            with st.spinner("Übersetzung läuft..."):
                placeholder = st.empty()
                if self.formats.index(self.input_type) in [
                    InputFormat.DEMO.value,
                    InputFormat.FILE.value,
                    InputFormat.URL.value,
                ]:
                    prompt = USER_PROMPT.format(self.text)
                    self.output, tokens = self.get_completion(text=prompt, index=0)
                    self.tokens_in, self.tokens_out = tokens[0], tokens[1]
                    st.markdown(self.token_use_expression())
                elif (
                    self.formats.index(self.input_type)
                    == InputFormat.KEY_VALUE_PAIRS.value
                ):
                    self.run_csv_translation(placeholder)
                else:
                    st.warning("Diese Option wird noch nicht unterstützt.")

        if (self.input_type == self.formats[0]) & (self.output is not None):
            st.markdown("**Übersetzung**")
            st.markdown(self.output)
