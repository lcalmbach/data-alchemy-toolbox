import streamlit as st
import os

class ToolBase:
    def __init__(self):
        pass

    def get_intro(self):
        with open(f'{self.script_name}.md', 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        return markdown_content

    def show_settings(self):
        pass

    def run(self):
        pass

    def show_ui(self):
        st.subheader(self.title)
        tabs = st.tabs(['⚙️Einstellungen', '🔧App', '💁informationen'])
        with tabs[0]:
            self.show_settings()
        with tabs[1]:
            self.run()
        with tabs[2]:
            text = self.intro
            st.markdown(text, unsafe_allow_html=True)