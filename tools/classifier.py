
import streamlit as st
import time
from tools.tool_base import ToolBase


class Classifier(ToolBase):
    def __init__(self):
        self.title = "Klassifizerung"

    def show_settings():
        ...

    def run(self):
        ...


    def show_ui(self):
        st.subheader(self.title)
        tabs = st.tabs(['⚙️Einstellungen', '🔧App', '💁informationen'])
        with tabs[0]:
            self.show_settings()
        with tabs[1]:
            if st.button("Starten"):
                with st.spinner("Klassifizierung läuft..."):
                    time.sleep(10)
                st.success("Anonymisierung erfolgreich!")
        with tabs[2]:
            text = "ipse lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris"
            st.markdown(text, unsafe_allow_html=True)
    
    