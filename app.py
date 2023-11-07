import streamlit as st
from streamlit_option_menu import option_menu
import logging
from tools import (
    classifier,
    speech2text,
    summary,
    translation,
    anonymizer,
    intro,
    pdf2text,
)

__version__ = "0.0.2"
__author__ = "data-alchemists des Digilab BS"
__author_email__ = "data-alchemists@bs.ch"
VERSION_DATE = "2023-11-7"
MY_EMOJI = "🔧"
MY_NAME = "Data Alchemy Toolbox"
GIT_REPO = "https://github.com/lcalmbach/data-alchemy-toolbox"
APP_URL = "https://data-alchemy-toolbox.streamlit.app/"


def show_info_box():
    impressum = f"""<div style="background-color:powderblue; padding: 10px;border-radius: 15px;">
    <small>Autoren: <a href="mailto:{__author_email__}">{__author__}</a><br>
    Version: {__version__} ({VERSION_DATE})<br>
    <a href="{GIT_REPO}">git-repo</a>
    """
    st.sidebar.markdown(impressum, unsafe_allow_html=True)


def init_layout():
    def load_css():
        with open("./style.css") as f:
            st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

    st.set_page_config(
        initial_sidebar_state="auto",
        page_title=MY_NAME,
        page_icon=MY_EMOJI,
    )
    load_css()
    st.sidebar.image("./assets/logo.png", width=150)


def main():
    init_layout()
    logger = logging.getLogger("data-alchemy-toolbox")
    menu_options = [
        "Übersicht",
        "Anonymisierung",
        "Klassifizierung",
        "Speech2Text",
        "Zusammenfassung",
        "Übersetzung",
        "pdf2txt",
    ]
    with st.sidebar:
        st.markdown(f"## {MY_EMOJI} {MY_NAME}")
        # https://fonts.google.com/icons
        menu_action = option_menu(
            None,
            menu_options,
            icons=["info", "table", "search", "database"],
            menu_icon="cast",
            default_index=0,
        )

    if menu_action == menu_options[0]:
        if "intro" not in st.session_state:
            st.session_state["intro"] = intro.Intro(logger)
        app = st.session_state["intro"]
    elif menu_action == menu_options[1]:
        if "anonymizer" not in st.session_state:
            st.session_state["anonymizer"] = anonymizer.Anonymizer(logger)
        app = st.session_state["anonymizer"]
    elif menu_action == menu_options[2]:
        if "classifier" not in st.session_state:
            st.session_state["classifier"] = classifier.Classifier(logger)
        app = st.session_state["classifier"]
    elif menu_action == menu_options[3]:
        if "speech2text" not in st.session_state:
            st.session_state["speech2text"] = speech2text.Speech2Text(logger)
        app = st.session_state["speech2text"]
    elif menu_action == menu_options[4]:
        if "summary" not in st.session_state:
            st.session_state["summary"] = summary.Summary(logger)
        app = st.session_state["summary"]
    elif menu_action == menu_options[5]:
        if "translation" not in st.session_state:
            st.session_state["translation"] = translation.Translation(logger)
        app = st.session_state["translation"]
    elif menu_action == menu_options[6]:
        if "pdf2text" not in st.session_state:
            st.session_state["pdf2text"] = pdf2text.Pdf2Text(logger)
        app = st.session_state["pdf2text"]
    app.show_ui()
    show_info_box()


if __name__ == "__main__":
    main()
