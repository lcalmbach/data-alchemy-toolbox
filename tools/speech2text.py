# https://github.com/stefanrmmr/streamlit-audio-recorder/tree/main

import streamlit as st
import os
from moviepy.editor import VideoFileClip
from openai import OpenAI
import pyperclip
from enum import Enum
import zipfile

from helper import get_var, save_uploadedfile
from tools.tool_base import ToolBase, TEMP_PATH, OUTPUT_PATH, DEMO_PATH
from st_audiorec import st_audiorec

DEMO_FILE = DEMO_PATH + "demo_audio.mp3"
TEMP_FILE = TEMP_PATH + "temp_audio."
OUTPUT_FILE = OUTPUT_PATH + "audio_output.txt"
FILE_FORMAT_OPTIONS = ["mp4", "mp3"]


class InputFormat(Enum):
    DEMO = 0
    FILE = 1
    RECORD = 2


def save_wav_audio_data(wav_audio_data, file_name):
    """
    Save WAV audio data to a file.

    Parameters:
    - wav_audio_data: Bytes-like object containing the WAV audio data.
    - file_name: String with the desired file name for the saved audio.
    """
    # Open a file in binary write mode
    with open(file_name, 'wb') as audio_file:
        audio_file.write(wav_audio_data)


class Speech2Text(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Audio zu Text"
        self.formats = ["Demo", "Audio/Video Datei", "Audio aufnehmen"]
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.input_file = None
        self.output_file = None
        self.text = ""

    def show_settings(self):
        """
        Zeigt die Einstellungen für Speech2Text an.

        Diese Methode ermöglicht es dem Benutzer, den Eingabeformaten für Speech2Text auszuwählen und die entsprechenden Aktionen
        basierend auf dem ausgewählten Eingabetyp zu verarbeiten. Eingabetypen sind Demo (fixed demo Datei), User lädt mp3/4 Datei
        hoch und: User lädt gezippte Datei mit mp3, mp4 Dateien hoch.

        Returns:
            None
        """
        self.input_type = st.radio("Input für Speech2Text", options=self.formats)
        if self.formats.index(self.input_type) == InputFormat.DEMO.value:
            self.output_file = DEMO_FILE
            st.audio(DEMO_FILE)
        elif self.formats.index(self.input_type) == InputFormat.FILE.value:
            self.input_file = st.file_uploader(
                "MP4 oder MP3 Datei hochladen",
                type=FILE_FORMAT_OPTIONS,
                help="Lade die Datei hoch, die du transkribieren möchtest.",
            )
            if self.input_file is not None:
                file = TEMP_PATH + self.input_file.name
                ok, err_msg = save_uploadedfile(self.input_file, TEMP_PATH)
                if ok:
                    self.output_file = file
                    st.audio(self.output_file)
        elif self.formats.index(self.input_type) == InputFormat.RECORD.value:
            self.wav_audio_data = st_audiorec()

    def extract_audio_from_video(self, video_file: str) -> str:
        audio_file_name = video_file.replace(".mp4", ".mp3")
        video = VideoFileClip(video_file)
        audio = video.audio
        audio.write_audiofile(audio_file_name)
        return audio_file_name

    def file2audio(self, filename: str) -> bytes:
        if filename.endswith(".mp4"):
            audio_file_name = self.extract_audio_from_video(filename)
        else:
            audio_file_name = filename
        return open(audio_file_name, "rb")
    
    def get_formatted_binary(self, wav_audio_data):
        """
        Save WAV audio data to a file.

        Parameters:
        - wav_audio_data: Bytes-like object containing the WAV audio data.
        - file_name: String with the desired file name for the saved audio.
        """
        # Open a file in binary write mode
        dummy_file = './dummy.wav'
        with open('./dummy.wav', 'wb') as audio_file:
            audio_file.write(wav_audio_data)
        return open(dummy_file, "rb")
            
    def transcribe(self, audio_stream: bytes) -> str:
        client = OpenAI(
            api_key=get_var("OPENAI_API_KEY"),
        )
        transcript = client.audio.transcriptions.create(
            model="whisper-1", file=audio_stream, response_format="text"
        )
        return transcript

    def run(self):
        if st.button("Transkribieren"):
            with st.spinner("Transkribiere Audio..."):
                if self.formats.index(self.input_type) in (InputFormat.FILE.value, InputFormat.DEMO.value):
                    audio = self.file2audio(self.output_file)
                    self.text = self.transcribe(audio)
                elif (
                    self.formats.index(self.input_type) == InputFormat.RECORD.value
                ):
                    audio = self.get_formatted_binary(self.wav_audio_data)
                    self.text = self.transcribe(audio)
                else:
                    st.info("Diese Option ist noch nicht verfügbar.")
        
        if self.text != "":
            st.markdown("**Transkript**")
            st.markdown(self.text)
            cols = st.columns(2, gap="small")
            with cols[0]:
                if st.button("📋 Text in Zwischenablage kopieren"):
                    pyperclip.copy(
                        self.text,
                    )
            with cols[1]:
                st.download_button(
                    label="⬇️ Datei herunterladen",
                    data=self.text,
                    file_name=OUTPUT_FILE,
                    mime="text/plain",
                )
