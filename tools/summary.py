
import streamlit as st
import time

class Summary():
    def __init__(self):
        self.title = "Zusammenfassung"

    def show_ui(self):
        st.subheader(self.title)
        tabs = st.tabs(['⚙️Einstellungen', '🔧App', '💁informationen'])
        with tabs[0]:
            file = st.file_uploader('Datei hochladen')
        with tabs[1]:
            if st.button("Starten"):
                with st.spinner("Zusammenfassung läuft..."):
                    time.sleep(10)
                st.success("Zusammenfassung erfolgreich!")
        with tabs[2]:
            text = "ipse lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris"
            st.markdown(text, unsafe_allow_html=True)
    def run(self):
        ...
