import streamlit as st
import time
import openai
from datetime import datetime
from tools.tool_base import (
    ToolBase,
    SLEEP_TIME_AFTER_ERROR,
    MODEL_OPTIONS,
    LLM_RETRIES,
    MAX_ERRORS,
)
import os
import json
import re
import pandas as pd
import altair as alt
from helper import create_file, append_row, zip_files, get_var


OUTPUT_LONG = "./data/output/output_{}.csv"
OUTPUT_SHORT = "./data/output/output_short_{}.csv"
OUTPUT_STAT = "./data/output/output_stat_{}.csv"
OUTPUT_ZIP = "./data/output/output_{}.zip"
OUTPUT_ERROR = "./data/output/output_error_{}.txt"
DEFAULT_MODEL = "gpt-3.5-turbo"

SYSTEM_PROMPT_TEMPLATE = """You are a expert data classifier. You will be provided with a text. Your task is to assign the text to one to maximum {0} of the following categories: [{1}]\n
Answer with a list of indexes of the matching categories for the given text. If none of the categories apply to the text return [{2}]. Always answer with a list of indices. The result list must only include numbers.\n
examples for categories: [1: Bildung, 2: Bevölkerung, 3: Arbeit und Erwerb, 4: Energie]\n
text: "Wieviele Personen in Basel sind 100-jährig oder älter?"\n
output: [2]\n
\n
categories: [1: Bildung, 2: Bevölkerung, 3: Arbeit und Erwerb, 4: Energie]\n
text: "Wie spät ist es?"\n
output: [{2}]
"""


class Classifier(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Klassifizerung"
        self._texts_df = pd.DataFrame()
        self._categories_dic = {}
        self._settings = {}
        self.results_df = pd.DataFrame()
        self.stats_df = pd.DataFrame()
        self.errors = []
        self.category_list_expression = ""

        self.formats = ["Demo", "Upload csv/xlsx", "Interaktive Eingabe"]
        self.input_type = self.formats[0]
        self.no_match_code = -99
        self.no_match_code_options = []
        self.max_categories = 10
        self.model = MODEL_OPTIONS[0]

        self.key = f"_{datetime.now().strftime('%Y-%m-%d-%H-%M')}"
        self.output_file_long = OUTPUT_LONG.format(self.key)
        self.output_file_short = OUTPUT_SHORT.format(self.key)
        self.output_file_stat = OUTPUT_STAT.format(self.key)
        self.output_errors = OUTPUT_ERROR.format(self.key)
        self.output_file_zip = OUTPUT_ZIP.format(self.key)

        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()

    @property
    def texts_df(self):
        return self._texts_df

    @texts_df.setter
    def texts_df(self, value):
        self._texts_df = value

    @property
    def categories_dic(self):
        return self._categories_dic

    @categories_dic.setter
    def categories_dic(self, value):
        self._categories_dic = value
        cat_list = []
        for k, v in value.items():
            cat_list.append(f'{k}: "{v}"')
        self.category_list_expression = ",".join(cat_list)

    @property
    def system_prompt(self):
        return SYSTEM_PROMPT_TEMPLATE.format(
            self.max_categories, self.category_list_expression, self.no_match_code
        )

    def calc_stats(self):
        """Analyzes the results of the API call and returns a DataFrame with
        the results.

        Args:
            None

        Returns:
            pandas.DataFrame: A DataFrame containing the results of the API
            call.

        Raises:
            None
        """
        self.results_df = pd.read_csv(self.output_file_short, sep=";")
        agg_df = (
            self.results_df.groupby("cat_id")["text_id"]
            .size()
            .reset_index(name="count")
        )
        agg_df["cat_code"] = agg_df["cat_id"].apply(lambda x: self.categories_dic[x])
        agg_df.to_csv(self.output_file_stat, sep=";")
        return agg_df

    def preview_data(self):
        """
        Display a preview of the texts dataframe and categories dictionary using Streamlit expanders and tables.
        """
        with st.expander("Demo-Texte", expanded=False):
            st.dataframe(self.texts_df)
        with st.expander("Kategorien", expanded=False):
            st.dataframe(self.categories_dic)
        st.markdown("**System Prompt**")
        st.markdown(self.system_prompt)

    def show_settings(self):
        self.input_type = st.radio("Input", options=self.formats)

        if self.formats.index(self.input_type) == 0:
            self.texts_df = pd.read_excel("./data/demo/demo_texts.xlsx")
            self.texts_df.columns = ["text_id", "text"]
            categories_df = pd.read_excel("./data/demo/demo_categories.xlsx")
            categories_df.columns = ["cat_id", "text"]
            self.categories_dic = dict(
                zip(categories_df["cat_id"], categories_df["text"])
            )
            self.max_categories = st.number_input(
                "Maximale Anzahl Kategorien",
                min_value=1,
                max_value=10,
                value=3,
                step=1,
            )
            self.no_match_code = st.selectbox(
                "Code für keine Übereinstimmung",
                options=self.categories_dic.keys(),
                format_func=lambda x: self.categories_dic[x],
                help="Wählen Sie den Code, der zurückgegeben wird, wenn keine Übereinstimmung gefunden wurde.",
            )
            self.preview_data()

        else:
            st.warning("Diese Option wird noch nicht unterstützt.")

    def show_stats(self):
        bar_chart = (
            alt.Chart(self.stats_df)
            .mark_bar()
            .encode(
                x=alt.X("count:Q", sort="-y"),
                y="cat_code:O",
            )
            .properties(height=alt.Step(20))
        )
        st.altair_chart(bar_chart, use_container_width=True)

    def get_completion(self, text, index):
        """Generates a response using the OpenAI ChatCompletion API based on
        the given text.

        Args:
            text (str): The user's input.

        Returns:
            str: The generated response.

        Raises:
            None
        """

        def convert_to_list(expression: str):
            pattern = r"\b\d+\b"
            # Find all occurrences of the pattern
            matches = re.findall(pattern, expression)
            # Convert all matches to integers
            codes = [int(match) for match in matches]
            return codes

        openai.api_key = get_var("OPENAI_API_KEY")
        retries = LLM_RETRIES
        tokens = []
        while retries > 0:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": text},
                    ],
                    temperature=self.temperature,
                    request_timeout=15,
                    max_tokens=self.max_tokens,
                    # top_p=self.settings["top_p"],
                    # frequency_penalty=self.settings["frequency_penalty"],
                    # presence_penalty=self.settings["presence_penalty"],
                )
                tokens.append(response["usage"]["prompt_tokens"])
                tokens.append(response["usage"]["completion_tokens"])
                indices = response["choices"][0]["message"]["content"]
                try:
                    indices = json.loads(indices)
                except Exception as err:
                    print(err)
                    indices = convert_to_list(indices)
                return indices, tokens
            except Exception as err:
                st.error(f"OpenAIError {err}, Index = {index}")
                retries -= 1
                time.sleep(SLEEP_TIME_AFTER_ERROR)
        return [], 0

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
        if st.button("Klassifizieren"):
            cnt = 1
            self.errors = []

            create_file(self.output_file_long, ["text_id", "text", "result"])
            create_file(self.output_file_short, ["text_id", "cat_id"])
            create_file(self.output_errors, ["time", "text_id", "error_message"])
            placeholder = st.empty()
            for index, row in self.texts_df.iterrows():
                text = (
                    row["text"]
                    .replace(chr(13), " ")
                    .replace(chr(10), " ")
                    .replace(";", " ")
                )
                placeholder.write(
                    f"Classify {cnt}/{len(self.texts_df)}: {text[:50] + '...'}, index= {index}"
                )
                indices, tokens = self.get_completion(text, index)
                if len(indices) > 0:
                    placeholder.write(
                        f"Result {cnt}/{len(self.texts_df)}: {text[:50] + '...'}, index= {index}, output: {indices} "
                    )
                    append_row(self.output_file_long, [[index, text, str(indices)]])
                    append_row(
                        self.output_file_short, [(index, item) for item in indices]
                    )
                    self.tokens_in += tokens[0]
                    self.tokens_out += tokens[1]
                    cnt += 1
                else:
                    placeholder.write(
                        f"Error {cnt}/{len(self.texts_df)}: {text[:50] + '...'}, index= {index}"
                    )
                    self.errors.append(index)

                # if loop has failed 3 times quit
                if len(self.errors) == MAX_ERRORS:
                    break

            placeholder.markdown(self.token_use_expression(tokens))
            self.stats_df = self.calc_stats()
            self.show_stats()
            file_names = [
                self.output_file_long,
                self.output_file_short,
                self.output_file_stat,
                self.output_errors,
            ]
            zip_files(file_names, self.output_file_zip)
            if os.path.exists(self.output_file_zip):
                with open(self.output_file_zip, "rb") as fp:
                    btn = st.download_button(
                        label="Herunterladen",
                        data=fp,
                        file_name=self.output_file_zip,
                        mime="application/zip",
                        help="Klicken Sie auf den Button, um die Ergebnisse der Klassifizierung herunterzuladen.",
                    )
