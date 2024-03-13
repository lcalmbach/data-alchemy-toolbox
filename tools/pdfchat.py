# https://blog.nextideatech.com/chat-with-documents-using-langchain-gpt-4-python/
# https://github.com/shahidul034/Chat-with-pdf-using-LLM-langchain-and-streamlit
import os
import pyperclip
import streamlit as st
import pandas as pd
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.chains import QAGenerationChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from enum import Enum

from tools.tool_base import ToolBase, DEMO_PATH
from helper import (
    show_download_button,
    extract_text_from_file,
    get_var,
    save_uploadedfile
)

DEMO_FILE = DEMO_PATH + "documents.csv"


class InputFormat(Enum):
    DEMO = 0
    FILE = 1


class PdfChat(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "💬 PDF-Chat"
        self.model = 'gpt-4'
        self.formats = ["Demo", "PDF Datei hochladen", "URL"]
        self._input_type = None
        self._input_file = None
        self.user_prompt = None
        self.default_prompt = "Fasse das Dokument zusammen."
        self._response = None
        self.document_text = None
        self.retriever = None
        self.qa = None

        self.script_name, _ = os.path.splitext(__file__)
        self.intro = self.get_intro()

    @property
    def input_type(self):
        return self._input_type

    @input_type.setter
    def input_type(self, value):
        if value != self._input_type:
            self.response = None
            self.document_text = None
        self._input_type = value

    @property
    def input_file(self):
        return self._input_file

    @input_file.setter
    def input_file(self, value):
        if value != self._input_file:
            self.response = None
            self._input_file = value
            self.document_text = extract_text_from_file(self.input_file)
            with st.spinner("Lade Dokument..."):
                self.create_embeddings(self._input_file)
            
    def create_retriever(self, _embeddings, splits):
        try:
            vectorstore = FAISS.from_texts(splits, _embeddings)
        except (IndexError, ValueError) as e:
            st.error(f"Error creating vectorstore: {e}")
            return
        retriever = vectorstore.as_retriever(k=5)
        return retriever

    def split_texts(self, text, chunk_size, overlap):
        # Split texts
        # IN: text, chunk size, overlap, split_method
        # OUT: list of str splits

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=overlap)

        splits = text_splitter.split_text(text)
        if not splits:
            st.error("Failed to split document")
            st.stop()

        return splits

    def get_demo_documents(self):
        df = pd.read_csv(DEMO_FILE, sep=";")
        documents_dic = dict(zip(df["file_path"], df["title"]))
        return documents_dic

    def show_settings(self):
        self.input_type = st.radio("Input Format", options=self.formats)
        if self.formats.index(self.input_type) == InputFormat.DEMO.value:
            doc_options = self.get_demo_documents()
            self.input_file = DEMO_PATH + st.selectbox(
                "Dokument auswählen",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
            )
            
        elif self.formats.index(self.input_type) == InputFormat.FILE.value:
            uploaded_file = st.file_uploader(
                "PDF Datei",
                type=["pdf"],
                help="Lade die PDF-Datei hoch, deren Text du analysieren möchtest.",
            )
            if uploaded_file is not None:
                file_path, ok, err_msg = save_uploadedfile(uploaded_file, DEMO_PATH)
                if ok:
                    self.input_file = file_path
                else:
                    st.warning(err_msg)
        with st.expander('Vorschau Text', expanded=True):
            st.markdown(self.document_text)

    def check_input(self):
        """
        Checks if the text and user_prompt attributes are not None.

        Returns:
            bool: True if both text and user_prompt are not None,
                  False otherwise.
        """
        ok = self.response is not None and self.user_prompt is not None
        return ok

    def create_retriever(self, _embeddings, splits):
        try:
            vectorstore = FAISS.from_texts(splits, _embeddings)
        except (IndexError, ValueError) as e:
            st.error(f"Error creating vectorstore: {e}")
            return
        retriever = vectorstore.as_retriever(k=5)
        return retriever

    def create_embeddings(self, file_path: str):
        splits = self.split_texts(self.document_text, chunk_size=1000, overlap=0)
        # Display the number of text chunks
        num_chunks = len(splits)
        st.write(f"Number of text chunks: {num_chunks}")
        # Embed using OpenAI embeddings
            # Embed using OpenAI embeddings or HuggingFace embeddings
        embeddings = OpenAIEmbeddings()
        retriever = self.create_retriever(embeddings, splits)
        # Initialize the RetrievalQA chain with streaming output
        callback_handler = StreamingStdOutCallbackHandler()
        callback_manager = CallbackManager([callback_handler])

        chat_openai = ChatOpenAI(
            streaming=True, callback_manager=callback_manager, verbose=True, temperature=0)
        self.qa = RetrievalQA.from_chain_type(llm=chat_openai, retriever=retriever, chain_type="stuff", verbose=True)


    def run(self):
        prompt = st.text_area(
                label=f"Stelle eine Frage zum Dokument: **{self.input_file}**",
                value=self.default_prompt,
                height=400,
            )
        self.user_prompt = f'Antworte auf deutsch: ***{prompt}***'
        ok = self.user_prompt > ''
        if st.button("📨 Abschicken", disabled=(ok is False)):
            self.response = self.qa.run(self.user_prompt)

        if self.response is not None:
            with st.expander(f'🤖 {self.model}', expanded=True):
                st.markdown(self.response)
                if st.button("Text in Zwischenablage kopieren"):
                    pyperclip.copy(self.response)
