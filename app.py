import streamlit as st
from streamlit_option_menu import option_menu
import logging
from tools import (
    classifier,
    tokenizer,
    speech2text,
    summarizer,
    translation,
    anonymizer,
    intro,
    pdf2text,
    pdfchat,
    image2text,
    finder,
    moderator
)

__version__ = "0.1.3'"
__author__ = "data-alchemists des DigiLab BS"
__author_email__ = "data-alchemists@bs.ch"
VERSION_DATE = "2024-03-01"
MY_EMOJI = "🔧"
MY_NAME = "Data Alchemy Toolbox"
GIT_REPO = "https://github.com/lcalmbach/data-alchemy-toolbox"
APP_URL = "https://data-alchemy-toolbox.streamlit.app/"

menu_dic = {
    "Übersicht": intro.Intro,
    "Anonymisierung": anonymizer.Anonymizer,
    "Klassifizierung": classifier.Classifier,
    "Speech2Text": speech2text.Speech2Text,
    "Image2Text": image2text.Image2Text,
    "Zusammenfassung": summarizer.Summary,
    "Übersetzung": translation.Translation,
    "PDF2TXT": pdf2text.Pdf2Text,
    "PDF-Chatbot": pdfchat.PdfChat,
    "Tokenizer": tokenizer.Tokenizer,
    "Finder": finder.Finder,
    "Moderator*in": moderator.Moderator,
}

menu_icons = [
    "house",
    "person",
    "arrows-fullscreen",
    "mic-fill",
    "card-image",
    "arrows-angle-contract",
    "globe",
    "file-earmark-pdf",
    "chat",
    "body-text",
    "search",
    "sign-stop"
]


def show_info_box():
    """
    Displays an information box in the sidebar with author information, version number, and a link to the git repository.

    Parameters:
    None

    Returns:
    None
    """
    impressum = f"""<div style="background-color:#34282C; padding: 10px;border-radius: 15px; border:solid 1px white;">
    <small>Autoren: <a href="mailto:{__author_email__}">{__author__}</a><br>
    Version: {__version__} ({VERSION_DATE})<br>
    <a href="{GIT_REPO}">git-repo</a>
    """
    st.sidebar.markdown(impressum, unsafe_allow_html=True)


def init_layout():
    """
    Initializes the layout of the application by setting the page configuration, loading CSS styles, and displaying the
    logo in the sidebar.

    Returns:
        None
    """

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


def check_in_session_state(key: str, logger):
    """
    Checks if a given menu-item key is in the session state. If it is not, it
    initializes the key with a value from the menu dictionary.

    Args:
        key (str): The key to check in the session state.
        logger: The logger object to use for logging and passed to the menu-app
        object.

    Returns:
        None
    """
    if key not in st.session_state:
        st.session_state[key] = menu_dic[key](logger)


def main():
    init_layout()
    logger = logging.getLogger("data-alchemy-toolbox")
    menu_options = list(menu_dic.keys())
    with st.sidebar:
        st.markdown(f"## {MY_EMOJI} {MY_NAME}")
        # bootstrap icons: https://icons.getbootstrap.com/icons/arrows-angle-contract/
        menu_action = option_menu(
            None,
            menu_options,
            icons=menu_icons,
            menu_icon="cast",
            default_index=0,
        )

    check_in_session_state(menu_action, logger)
    app = st.session_state[menu_action]
    app.show_ui()
    show_info_box()


if __name__ == "__main__":
    main()
