import streamlit as st
import pandas as pd
import iso639
import os
import json
from enum import Enum

from helper import (
    extract_text_from_url,
    extract_text_from_file,
    extract_text_from_uploaded_file,
)
from tools.tool_base import ToolBase, DEMO_PATH, OUTPUT_PATH

SYSTEM_PROMPT_TEMPLATE = 'You will translate a user text from {} to {}. Only return the translated text, nothing else. If the input is a list, format the output as as list as well.'
USER_PROMPT = 'Translate the following text: {}'
DEMO_FILE = DEMO_PATH + 'demo_summary.txt'
FILE_FORMAT_OPTIONS = ['txt', 'pdf', 'json']


class InputFormat(Enum):
    DEMO = 0
    FILE = 1
    URL = 2
    KEY_VALUE_PAIRS = 3
    MULTI_LANG_JSON = 4


class Translation(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = 'Übersetzung'
        self.lang_source = 'de'
        self.lang_target = 'en'
        self.texts_df = pd.DataFrame()
        self.language_dict = self.get_language_dict()
        self.formats = [
            'Demo',
            'Text oder PDF Datei hochladen',
            'URL von Text oder PDF Datei',
            'Schlüssel-Wert-Paare in einer CSV-Datei',
            'JSON-Datei (Multi-lang-Format)',
        ]
        self.input_type = self.formats[0]
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.output = None
        self.separator = ';'
        self.data = None
        self.system_prompt = None

    def set_system_prompt(self, lang_source: str = None, lang_target: str = None):
        if lang_source is None:
            lang_source = self.lang_source
            lang_target = self.lang_target
        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            iso639.to_name(lang_source), iso639.to_name(lang_target)
        )
    
    def parse_json(self):
        def check_keys():
            ok = True
            valid_keys = ['source'] + list(self.language_dict.keys())
            for key in self.data.keys():
                ok = key in valid_keys
                if not ok:
                    st.warning(f'{key} ist kein erlaubter Sprachecode')
                    break
            return ok
        
        self.data = json.load(self.input_file)
        return check_keys()

    def show_settings(self):
        self.input_type = st.radio('Input Format', options=self.formats)
        index_source = list(self.language_dict.keys()).index(self.lang_source)
        index_target = list(self.language_dict.keys()).index(self.lang_target)
        if self.formats.index(self.input_type) != InputFormat.MULTI_LANG_JSON.value:
            self.lang_source = st.selectbox(
                label='Übersetze von',
                options=self.language_dict.keys(),
                format_func=lambda x: self.language_dict[x],
                index=index_source,
            )
            self.lang_target = st.selectbox(
                label='Übersetze nach',
                options=self.language_dict.keys(),
                format_func=lambda x: self.language_dict[x],
                index=index_target,
            )
        if self.formats.index(self.input_type) in [InputFormat.MULTI_LANG_JSON.value, InputFormat.FILE.value]:
            self.input_file = st.file_uploader(
                self.input_type,
                type=FILE_FORMAT_OPTIONS,
                help='Lade die Datei hoch, die du übersetzen möchtest.',
            )
            if self.input_file is not None:
                self.text = extract_text_from_uploaded_file(self.input_file)

        if self.formats.index(self.input_type) == InputFormat.DEMO.value:
            text = extract_text_from_file(DEMO_FILE)
            self.text = st.text_area(
                label='Text',
                value=text,
                height=400,
                help='Geben Sie den Text ein, den Sie übersetzen möchten.',
            )
        elif self.formats.index(self.input_type) == InputFormat.URL.value:
            self.input_file = st.text_input(
                label=self.input_type,
                help='Gib bitte die URL der Datei ein, den du übersetzen möchtest.',
            )
            if self.input_file is not None:
                self.text = extract_text_from_url(self.input_file)
        elif self.formats.index(self.input_type) == InputFormat.KEY_VALUE_PAIRS.value:
            self.separator = st.selectbox(
                label='Trennzeichen',
                options=[';', ',', '|', '\t'],
                help='Gib bitte das Trennzeichen ein, das du in der hochgeladenen Datei verwendest.',
            )
            self.input_file = st.file_uploader(
                self.input_type,
                type=['csv'],
                help='Lade die Datei hoch, die du übersetzen möchtest.',
            )
            if self.input_file is not None:
                self.data = pd.read_csv(self.input_file, sep=self.separator)
                self.data.columns = ['key', 'value']
                with st.expander('Schlüssel-Wert-Paare'):
                    st.dataframe(self.data)
        elif self.formats.index(self.input_type) == InputFormat.MULTI_LANG_JSON.value:
            if self.input_file:
                if self.parse_json():
                    with st.expander('Original'):
                        st.write(self.data['source'])
                    st.markdown(f'Übersetze von: {list(self.data.keys())[1]}')
                    st.markdown(f'Übersetze nach: {", ".join(list(self.data.keys())[2:])}')
                else:
                    st.warning("Die json Datei hat Fehler, bitte überprüfe das Format")
        else:
            st.warning("Diese Option wird noch nicht unterstützt.")

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

        Returns:self.language_dict[lang]
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

    def init_translation(self):
            """
            Initializes the translation dictionary as follows:
            - the translated dict is initialized empty
            - The source language is copied 1:1 to translated
            - an empty dictionary is created for each target language
            Returns:
                dict: The initialized translation dictionary.
            """
            translated = {}
            self.lang_source = list(self.data.keys())[1]
            for lang in list(self.data.keys()):
                if not (lang in ["source", self.lang_source]):
                    translated[lang] = {}
                else:
                    translated[lang] = self.data[lang]
            return translated
    
    def get_changed_items(self):
        """
        Retrieves a list of items that have been changed or are new in the translation data.
        For list, it checks if one item is new or changed in the list and marks it as changed.

        Returns:
            list: A list of keys representing the changed or new items.
        """
        changed_and_new_items = []
        source_dict = self.data["source"]
        source_lang_dict = self.data[self.lang_source]
        for k, v in source_dict.items():
            if k not in source_lang_dict:
                changed_and_new_items.append(k)
            elif type(source_dict[k]) == list:
                for item in source_dict[k]:
                    if not item.encode("utf-8") in [
                        x.encode("utf-8") for x in source_lang_dict[k]
                    ]:
                        changed_and_new_items.append(k)
                        break
                    elif item.encode("utf-8") != source_lang_dict[k][
                        source_lang_dict[k].index(item)
                    ].encode("utf-8"):
                        changed_and_new_items.append(k)
                        break
            elif v.encode("utf-8") != source_lang_dict[k].encode("utf-8"):
                changed_and_new_items.append(k)
        return changed_and_new_items
    
    def get_items_to_translate(self, lang, changed_items: dict):
        """
        Retrieves the items that need to be translated for the specified language.

        Args:
            lang (str): The language code for which the translation is needed.

        Returns:
            dict: A dictionary containing the items to be translated.
        """
        result = {}
        source = self.data["source"]
        target = self.data[lang]
        in_keys = list(source.keys())
        out_keys = list(target.keys())
        for key in in_keys:
            if type(source[key]) == list:
                if not key in out_keys or key in changed_items:
                    result[key] = source[key]
                elif target[key] == []:
                    result[key] = source[key]
            else:
                # item has not been created yet
                if not key in out_keys or key in changed_items:
                    result[key] = source[key]
                elif target[key] == "":
                    result[key] = source[key]
        return result

    def parse_gpt_output(self, translated_dict: dict, lang: str):
        """_summary_

        Args:
            translated_dict (dict): dict with translations: only expressions
                                    marked in the source file to be translated are
                                    included.

        Returns:
            _type_: _description_
        """
        result = {}
        for key in list(self.data["source"].keys()):
            # if key has been translated, use it as previously translated
            if type(self.data["source"][key]) == list:
                if key in translated_dict.keys():
                    result[key] = translated_dict[key]
                else:
                    result[key] = self.data[lang][key]
            else:
                if key in translated_dict.keys():
                    result[key] = translated_dict[key]
                else:
                    result[key] = self.data[lang][key]
        return result
    
    def translate_json_file(self, progress):
        """
        Uses OpenAI-API to automatically translate texts from one language to another.

        Returns a dictionary with the translated texts. Note that this method requires the
        OPENAI_API_KEY environment variable to be set with a valid API key for OpenAI's GPT-3 service.

        By default, this method translates texts to English (the 'en' language code). To change the
        target language, modify the `self.data` attribute before calling this method.

        This method generates a prompt message and submits it to the GPT-3 API. The prompt message
        includes the contents of `self.data`, which contains a list of texts to translate.

        The API response is parsed to obtain the translated texts, which are returned as a
        dictionary with the original texts as keys and the translated texts as values.

        Example usage:
        >> translator = MyTranslator()
        >> result = translator.translate()
        >> # result will be a dictionary with the translated texts
        """

        translated = self.init_translation()
        changed_items = self.get_changed_items()
        st.markdown(f'{len(changed_items)} neue oder geänderte Ausdrücke gefunden.')
        #languages start with 3 item: 0: source: 1: source lang diff, 2: first lang
        cnt = 0
        target_lang_list = list(self.data.keys())[2:]
        total = len(changed_items) * len(target_lang_list)
        for lang in target_lang_list:
            items_to_translate = self.get_items_to_translate(lang, changed_items)
            language = self.language_dict[lang]
            self.set_system_prompt(self.lang_source, lang)
            for key, value in items_to_translate.items():
                text = json.dumps(value)
                response, tokens = self.get_completion(text, index=0)
                self.add_tokens(tokens)
                try:
                    translated[lang][key] = json.loads(response)
                except json.JSONDecodeError:
                    translated[lang][key] = response
                cnt += 1
                progress.progress(cnt / total, f'Übersetze nach {language} ({cnt}/{total}): {value}')
            translated[lang] = self.parse_gpt_output(translated[lang], lang)
        progress.progress(1.0, f'Übersetzung abgeschlossen ({cnt}/{total})')
            

        # synch source long with source so there are no differences after the translation
        translated[self.lang_source] = self.data['source']
        return translated
    
    def run(self):
        if st.button('Übersetzung'):
            placeholder = st.empty()
            progress = st.progress(0, text='Übersetzung läuft')
            if self.formats.index(self.input_type) in [
                InputFormat.DEMO.value,
                InputFormat.FILE.value,
                InputFormat.URL.value,
            ]:
                self.set_system_prompt(self.lang_source, self.lang_target)
                prompt = USER_PROMPT.format(self.text)
                self.output, tokens = self.get_completion(text=prompt, index=0)
                self.tokens_in, self.tokens_out = tokens[0], tokens[1]
                st.markdown(self.token_use_expression())
            elif (
                self.formats.index(self.input_type)
                == InputFormat.KEY_VALUE_PAIRS.value
            ):
                self.set_system_prompt(self.lang_source, self.lang_target)
                self.run_csv_translation(placeholder)
            elif self.formats.index(self.input_type) == InputFormat.MULTI_LANG_JSON.value:
                self.output = self.translate_json_file(progress)
            else:
                st.warning('Diese Option wird noch nicht unterstützt.')

        if self.output is not None:
            with st.expander('Übersetzung', expanded=True):
                st.write(self.output)
            st.download_button('Herunterladen', json.dumps(self.output), 'translation.json', 'json')
