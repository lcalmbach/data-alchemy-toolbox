import streamlit as st
from streamlit_option_menu import option_menu
import logging
from tools import (
    classifier,
    sentiment_analysis,
    tokenizer,
    speech2text,
    summarizer,
    translation,
    # anonymizer,
    intro,
    pdf2text,
    pdfchat,
    image2text,
    finder,
    moderator,
    text2speech,
    imagegen,
    ocr,
    video2audio,
    simplify_language
)

__version__ = "0.1.20"
__author__ = "data-alchemists des DigiLab BS"
__author_email__ = "lukas.calmbach@bs.ch"
VERSION_DATE = "2024-12-12"
MY_EMOJI = "🧰"
MY_NAME = "Data-Alchemy-Toolbox"
GIT_REPO = "https://github.com/lcalmbach/data-alchemy-toolbox"
APP_URL = "https://data-alchemy-toolbox.streamlit.app/"

menu_dic = {
    "Übersicht": intro.Intro,
    # "Anonymisierung": anonymizer.Anonymizer, # takes up too much space on streamlit sharing
    "Klassifizierung": classifier.Classifier,
    "Sentiment-Analyse": sentiment_analysis.SentientAnalysis,  
    "Speech2Text": speech2text.Speech2Text,
    "Image2Text": image2text.Image2Text,
    "Zusammenfassung": summarizer.Summary,
    "Übersetzung": translation.Translation,
    "PDF2TXT": pdf2text.Pdf2Text,
    "PDF-Chatbot": pdfchat.PdfChat,
    "Tokenizer": tokenizer.Tokenizer,
    "Finder": finder.Finder,
    "Moderator": moderator.Moderator,
    "Text zu Audio": text2speech.Text2Speech,
    "Bildgenerator": imagegen.ImageGenerator,
    # "Texterkennung": ocr.Ocr,
    "Video2Audio": video2audio.Video2Audio,
    "Sprache vereinfachen": simplify_language.SimplifyLanguage,
}

# https://icons.getbootstrap.com/?q=image 
menu_icons = [
    "house",
    # "person",
    "arrows-fullscreen",
    "emoji-smile",
    "mic-fill",
    "card-image",
    "arrows-angle-contract",
    "globe",
    "file-earmark-pdf",
    "chat",
    "body-text",
    "search",
    "sign-stop",
    "soundwave",
    "card-image",
    # "card-text",
    "camera-reels",
    "bandaid"
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

_warning_msg = """
        Diese Applikation ist eine öffentliche Applikation um zu demonstrieren, was mit KI möglich ist. Die Daten werden auf öffentlichen KI Modellen verarbeiten.
        Der Datenschutz ist nicht gewährleistet. Verarbeiten Sie keine sensiblen Informationen auf dieser Anwendung.
        Mitarbeiter der Kantonalen Verwaltung Basel-Stadt wird dringend empfohlen die internen KI Anwendungen vom DCC Data Competence Ceter am Statistischen Amt Basel-Stadt zu verwenden.
        Sie finden weiter Informationen und Links zu den Anwendungen auf dem [Basel-Stadt Intranet](https://my.intranet.bs.ch/SitePages/News.aspx?ItemId=10637) oder auf [bs.ch/ki](https://bs.ch/ki).
        """

@st.dialog("Öffentliche Demonstration")
def warning_message():
    st.warning(_warning_msg, icon="⚠️")

def main():
    """
    Main function of the application. Initializes the layout, creates the 
    sidebar menu, and displays the selected application.
    """

    init_layout()
    logger = logging.getLogger("data-alchemy-toolbox")

    st.warning(_warning_msg, icon="⚠️")

    warning_message()

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
