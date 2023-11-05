
import streamlit as st
import time


class Speech2Text():
    def __init__(self):
        self.title = "Spracherkennung"

    def show_ui(self):
        st.subheader(self.title)
        tabs = st.tabs(['⚙️Einstellungen', '🔧App', '💁informationen'])
        with tabs[0]:
            file = st.file_uploader('Datei hochladen')
        with tabs[1]:
            if st.button("Starten"):
                with st.spinner("Transkription läuft..."):
                    time.sleep(10)
                st.success("Anonymisierung erfolgreich!")
        with tabs[2]:
            text = "Lade ein Video oder Aduiofile hoch und lasse es transkribieren."
            st.markdown(text, unsafe_allow_html=True)
    def run(self):
        ...
