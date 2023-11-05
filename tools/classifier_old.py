import openai
import time
import streamlit as st
import pandas as pd
import json
import re
import altair as alt
from datetime import datetime

from helper import get_var, get_random_word, create_file, append_row, zip_files


MAX_ERRORS = 3
LLM_RETRIES = 3
SLEEP_TIME_AFTER_ERROR = 30
OUTPUT_LONG = "./output/output_{}.csv"
OUTPUT_SHORT = "./output/output_short_{}.csv"
OUTPUT_STAT = "./output/output_stat_{}.csv"
OUTPUT_ZIP = "./output/output_{}.zip"
OUTPUT_ERROR = "./output/output_error_{}.txt"
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TEMP = 0.3
DEAFULT_TOP_P = 1.0
DEFAULT_MAX_TOKENS = 500
DEFAULT_FREQUENCY_PENALTY = 0.0
DEFAULT_PRESENCE_PENALTY = 0.0
MODEL_OPTIONS = ["gpt-3.5-turbo", "gpt-4"]
MODEL_TOKEN_PRICING = {
    "gpt-3.5-turbo": {"in": 0.0015, "out": 0.002},
    "gpt-4": {"in": 0.03, "out": 0.06},
}
SYSTEM_PROMPT_TEMPLATE = """You are a expert data labeller. You will be provided with a text. Your task is to assign the text to one to maximum {} of the following categories: [{}]
Answer with a list of indexes of the matching categories for the given text. If none of the categories apply to the text return [{}]. Always answer with a list of indices. The result list must only include numbers. For
examples: 
categories: [1: Bildung, 2: Bevölkerung, 3: Arbeit und Erwerb, 4: Energie]
text: "Wieviele Personen in Basel sind 100 jährig oder älter?"
output: [2]

categories: [1: Bildung, 2: Bevölkerung, 3: Arbeit und Erwerb, 4: Energie]
text: "Wie spät ist es?"
output: [-99]
"""


class Classifier:
    """
    A class for categorizing text data using OpenAI's GPT-3 API.

    Attributes:
        df_texts (pandas.DataFrame): A DataFrame containing the text data to be categorized.
        dict_categories (dict): A dictionary mapping category names to their corresponding IDs.
        category_list_expression (str): A string containing a comma-separated list of category names and IDs.

    Methods:
        run(): Runs the GPT-3 API on each row of the input DataFrame and categorizes the text according to the user's instructions.
    """

    def __init__(self):

        self._texts_df = pd.DataFrame()
        self._settings = {}
        self._dict_categories = {}
        self._settings = {}
        self.results_df = pd.DataFrame()
        self.stats_df = pd.DataFrame()
        self.errors = []
        self.category_list_expression = ""
        self.key = f"_{datetime.now().strftime('%Y-%m-%d-%H-%M')}"
        self.output_file_long = OUTPUT_LONG.format(self.key)
        self.output_file_short = OUTPUT_SHORT.format(self.key)
        self.output_file_stat = OUTPUT_STAT.format(self.key)
        self.output_errors = OUTPUT_ERROR.format(self.key)
        self.output_file_zip = OUTPUT_ZIP.format(self.key)
        self.tokens_in = 0
        self.tokens_out = 0

    @property
    def texts_df(self):
        return self._texts_df

    @texts_df.setter
    def texts_df(self, value):
        self._texts_df = value

    @property
    def category_dic(self):
        return self._category_dic

    @category_dic.setter
    def category_dic(self, value):
        self._category_dic = value
        cat_list = []
        for k, v in value.items():
            cat_list.append(f'{k}: "{v}"')
        self.category_list_expression = ",".join(cat_list)

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        """
        Setter method for the `category_dic` attribute of the `GPTClassifier` class.
        Updates the `_settings` attribute with the new `value`, and calls the `complete_settings` method.
        Also updates the `system_prompt` attribute with a new string, based on the `category_list_expression`
        and the `max_categories` value from the `value` dictionary.

        Args:
        - value (dict): A dictionary containing the new settings for the classifier.
            Should have the following keys:
            - "model_name_or_path": A string representing the name or path of the GPT model to use.
            - "tokenizer_name_or_path": A string representing the name or path of the tokenizer to use.
            - "category_list": A list of strings representing the categories to classify.
            - "max_categories": An integer representing the maximum number of categories to output.
        """
        self._settings = value
        self.complete_settings()
        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            self.category_list_expression,
            value["max_categories"],
            value["code_for_no_match"],
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
        agg_df["cat_code"] = agg_df["cat_id"].apply(lambda x: self.category_dic[x])
        agg_df.to_csv(self.output_file_stat, sep=";")
        return agg_df

    def complete_settings(self):
        if "model" not in self.settings:
            self.settings["model"] = DEFAULT_MODEL
        if "temperature" not in self.settings:
            self.settings["temperature"] = DEFAULT_TEMP
        if "max_tokens" not in self.settings:
            self.settings["max_tokens"] = DEFAULT_MAX_TOKENS
        if "top_p" not in self.settings:
            self.settings["top_p"] = DEAFULT_TOP_P
        if "frequency_penalty" not in self.settings:
            self.settings["frequency_penalty"] = DEFAULT_FREQUENCY_PENALTY
        if "presence_penalty" not in self.settings:
            self.settings["presence_penalty"] = DEFAULT_PRESENCE_PENALTY
        if "max_categories" not in self.settings:
            self.settings["max_categories"] = 3

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
                    model=self.settings["model"],
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": text},
                    ],
                    temperature=self.settings["temperature"],
                    request_timeout=15,
                    max_tokens=self.settings["max_tokens"],
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

    def show_menu(self):
        def show_menu():
            def main() -> None:
                
                st.header(APP_NAME)
                global lang

                init_lang_dict_complete("app.py")

                if not ("lang" in st.session_state):
                    # first item is default language
                    st.session_state["used_languages_dict"] = get_used_languages()
                    st.session_state["lang"] = next(
                        iter(st.session_state["used_languages_dict"].items())
                    )[0]
                    refresh_lang()

                lang = st.session_state["lang_dict"]
                lottie_search_names, ok = get_lottie()
                if ok:
                    with st.sidebar:
                        st_lottie(lottie_search_names, height=140, loop=20)
                else:
                    pass
                display_language_selection()
                mode_options = lang["mode-options"]


                sel_mode = st.radio(lang["mode"], options=mode_options)
                if mode_options.index(sel_mode) == 0:
                    df_texts, dic_categories = get_demo_data()
                if mode_options.index(sel_mode) == 1:
                    df_texts, dic_categories = get_uploaded_files()
                    with st.columns(3)[0]:
                        llm_settings["max_categories"] = st.number_input(
                            lang['max_categories'], 1, 100, 3, 1
                        )
                if mode_options.index(sel_mode) == 2:
                    df_texts, dic_categories = get_user_input()

                llm_settings["code_for_no_match"] = st.selectbox(
                    lang["code_for_no_match"],
                    list(dic_categories.keys()),
                    format_func=lambda x: dic_categories[x],
                )
                if not df_texts.empty and dic_categories:
                    df_texts = record_selection(df_texts, llm_settings)
                    preview_input(df_texts, dic_categories)
                    if not df_texts.empty and dic_categories:
                        if not ("classifier" in st.session_state):
                            st.session_state["classifier"] = gpt_classifier.Classifier()
                        classifier = st.session_state["classifier"]
                        classifier.texts_df = df_texts
                        classifier.category_dic = dic_categories
                        classifier.settings = llm_settings
                        if st.button(lang["classify"]):
                            placeholder = st.empty()

                            with st.spinner(lang["classifying"]):
                                classifier.run(placeholder)
                            if len(classifier.errors) > 0:
                                st.warning(
                                    f"{lang['error_message_result']} {','.join(classifier.errors)}"
                                )
                            else:
                                st.success(lang["classify-success"])

                            if os.path.exists(classifier.output_file_zip):
                                # Read the zip file as bytes
                                with open(classifier.output_file_zip, "rb") as fp:
                                    btn = st.download_button(
                                        label=lang['download_results'],
                                        data=fp,
                                        file_name="download.zip",
                                        mime="application/zip",
                                        help=lang['download_help_text']
                                    )
                                        
        def get_settings():
            """
            Prompts the user to enter model poarameters and returns them as a dictionary.
            Default values are dinfed in the gpt_classifier module.

            Returns:
                settings (dict): A dictionary containing the user-entered settings.
            """
            settings = {}
            with st.sidebar.expander(lang["llm_settings"]):

                settings["selection_type"] = st.selectbox(
                    "Selection type",
                    options=selection_options,
                    help=lang['selection_type_help'],
                )
                if selection_options.index(settings["selection_type"]) == 0:
                    settings["from_rec"] = 0
                    settings["to_rec"] = MAX_RECORDS
                elif selection_options.index(settings["selection_type"]) == 1:
                    settings["from_rec"] = st.number_input("From record", 0, MAX_RECORDS, 0, 10)
                    settings["to_rec"] = st.number_input("To record", 0, MAX_RECORDS, 10, 10)
                elif selection_options.index(settings["selection_type"]) == 2:
                    settings["max_records"] = st.number_input(
                        "Max. number of records", 10, MAX_RECORDS, 10, 10
                    )
                settings["model"] = st.selectbox(lang['model'], gpt_classifier.MODEL_OPTIONS)
                settings["temperature"] = st.slider(
                    label=lang['temperature'],
                    value=gpt_classifier.DEFAULT_TEMP,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.1,
                    help=lang["help_temperature"],
                )
                settings["max_tokens"] = st.slider(
                    label=lang['max_number_of_tokens'],
                    value=gpt_classifier.DEFAULT_MAX_TOKENS,
                    min_value=0,
                    max_value=4096,
                    step=1,
                    help=lang["help_max_tokens"],
                )
                settings["max_categories"] = 3

            return settings


        def preview_input(df_texts, dic_categories):
            """
            Displays the input data for preview in the Streamlit app.

            Args:
            - df_texts (pandas.DataFrame): A DataFrame containing the input texts.
            - dic_categories (dict): A dictionary containing the categories and their corresponding labels.

            Returns:
            - None
            """
            with st.expander(lang["texts"], expanded=False):
                st.write(df_texts)

            with st.expander(lang["categories"], expanded=False):
                st.write(dic_categories)


        def get_uploaded_files():
            """
            This function allows the user to upload two Excel files - one with expressions and one with categories.
            If the user uploads an Excel file with expressions, the function loads the file into a pandas DataFrame and
            drops any rows with missing values. It then sets the index to the 'id' column and returns the resulting DataFrame.

            If the user uploads an Excel file with categories, the function loads the file into a pandas DataFrame,
            renames the columns to 'id' and 'category', and returns a dictionary of category IDs and category names.

            If either file is not uploaded, an empty dictionary and an empty DataFrame are returned.

            Returns:
                df_texts (pandas.DataFrame): DataFrame containing the loaded expressions Excel file (if any).
                dic_categories (dict): Dictionary containing the ID-category mapping from the loaded categories Excel file (if any).
            """

            uploaded_file = st.file_uploader(lang["upload-excel-expressions"], type=["xlsx"])
            uploaded_categories = st.file_uploader(
                lang["upload-excel-categories"], type=["xlsx"]
            )
            dic_categories, df_texts = {}, pd.DataFrame()
            if uploaded_file:
                # Load the Excel file into a DataFrame
                df_texts = pd.read_excel(uploaded_file)
                df_texts.dropna(inplace=True)
                df_texts.columns = ["id", "text"]
                df_texts["id"] = df_texts["id"].astype(int)
                df_texts.set_index("id", inplace=True)

            if uploaded_categories:
                # Load the Excel file into a DataFrame
                df_categories = pd.read_excel(uploaded_categories)
                df_categories.columns = ["id", "category"]
                dic_categories = dict(
                    zip(list(df_categories["id"]), list(df_categories["category"]))
                )
            return df_texts, dic_categories


        def get_user_input():
            """
            Prompts the user to enter text and categories, and returns them as a
            DataFrame and a dictionary.

            Returns:
                df_texts (pd.DataFrame): A DataFrame containing the user-entered text.
                dic_categories (dict): A dictionary mapping category indices to
                category names.
            """
            text = st.text_area(lang["text_to_classify"])
            categories = st.text_area(lang["categories_csv"])

            df_texts = pd.DataFrame({"id": [1], "text": [text]})
            df_texts.set_index("id", inplace=True)

            categories = categories.split(",")
            dic_categories = {i + 1: item for i, item in enumerate(categories)}
            return df_texts, dic_categories


        @st.cache_data
        def get_demo_data():
            """
            This function loads demo data from two Excel files - one with expressions and one with categories.
            It reads the demo expressions Excel file into a pandas DataFrame and drops any rows with missing values.
            It then renames the columns to 'id' and 'text', converts the 'id' column to integer type and sets it as the index.
            Next, it reads the categories Excel file into another pandas DataFrame, renames the columns to 'id' and 'category',
            creates a dictionary of category IDs and category names and returns it along with the expressions DataFrame.

            Returns:
                df_texts (pandas.DataFrame): DataFrame containing the loaded demo expressions Excel file.
                dic_categories (dict): Dictionary containing the ID-category mapping from the loaded demo categories Excel file.
            """

            df_texts = pd.read_excel(DEMO_TEXT_FILE)
            df_texts.dropna(inplace=True)
            df_texts.columns = ["id", "text"]
            df_texts["id"] = df_texts["id"].astype(int)
            df_texts["text"] = df_texts["text"].str.replace(r"[\r\n]", ",", regex=True)
            df_texts.set_index("id", inplace=True)

            df_categories = pd.read_excel(DEMO_CATEGORY_FILE)
            df_categories.columns = ["id", "category"]
            dic_categories = dict(
                zip(list(df_categories["id"]), list(df_categories["category"]))
            )

            return df_texts, dic_categories


        @st.cache_data
        def record_selection(df: pd.DataFrame, settings: dict) -> pd.DataFrame:
            """
            This function randomly select a fixed number of records from a pandas DataFrame that needs to be provided as input.

            Args:
                df (pandas.DataFrame): The DataFrame to sample from.
                no_records (int): The number of records required in the returned DataFrame.

            Returns:
                pd.DataFrame: The sampled DataFrame.
            """
            df = df.dropna()
            if settings["selection_type"] == selection_options[0]:
                df = df[:MAX_RECORDS]
            elif settings["selection_type"] == selection_options[1]:
                df = df[settings["from_rec"] : settings["to_rec"]]
            elif settings["selection_type"] == selection_options[2]:
                df = df.sample(n=settings["max_records"])

            df["text"] = df["text"].str.replace(r"[\r\n]", " ", regex=True)

            return df


    def run(self, placeholder):
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

        cnt = 1
        self.errors = []

        create_file(self.output_file_long, ["text_id", "text", "result"])
        create_file(self.output_file_short, ["text_id", "cat_id"])
        create_file(self.output_errors, ["time", "text_id", "error_message"])
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
                append_row(self.output_file_short, [(index, item) for item in indices])
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
        cost_tokens_in = (
            MODEL_TOKEN_PRICING[self.settings["model"]]["in"] * self.tokens_in / 1000
        )
        cost_tokens_out = (
            MODEL_TOKEN_PRICING[self.settings["model"]]["out"] * self.tokens_out / 1000
        )
        placeholder.markdown(
            f"""Tokens in: {self.tokens_in} Cost: ${cost_tokens_in: .2f}\n
Tokens out: {self.tokens_out} Cost: ${cost_tokens_out: .2f}\n
Total tokens: {self.tokens_in + self.tokens_out} Cost: ${(cost_tokens_in + cost_tokens_out): .2f}
"""
        )
        self.stats_df = self.calc_stats()
        self.show_stats()
        file_names = [
            self.output_file_long,
            self.output_file_short,
            self.output_file_stat,
            self.output_errors,
        ]
        zip_files(file_names, self.output_file_zip)
