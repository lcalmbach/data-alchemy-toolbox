import streamlit as st
import pandas as pd
import os


class Intro:
    def __init__(self, logger):
        self.intro = self.get_intro()
        self.logger = logger

    def get_intro(self):
        df = pd.read_csv('./data/quotes.csv', sep=';')
        quote = df.sample(1)
        quote = quote.iloc[0]['quote'] + f'(*{quote.iloc[0]["author"]}*)<br><br>' 
        script_name, script_extension = os.path.splitext(__file__)
        with open(f"{script_name}.md", "r", encoding="utf-8") as file:
            markdown_content = file.read()
        return markdown_content.format(quote)

    def show_settings():
        ...

    def show_ui(self):
        st.image("./assets/splash_screen_w.png")
        st.markdown(self.intro, unsafe_allow_html=True)

    def run(self):
        ...
