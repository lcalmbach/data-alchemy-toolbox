import streamlit as st
import os
from tools.tool_base import ToolBase
from moviepy.editor import VideoFileClip
from openai import OpenAI
import pyperclip
from helper import get_var

AUDIO_DEMO_FILE = "./data/demo/demo_audio.mp3"
OUTPUT_FILE = "./output/audio_output.txt"


class Speech2Text(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Audio zu Text"
        self.formats = ["Demo", "Audio/Video Datei", "Sammlung von Audio-Dateien (zip)"]
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.output = {}
        self.file = ""
        self.text = ""

    def show_settings(self):
        self.input_type = st.radio("Input für Speech2Text", options=self.formats)
        if self.formats.index(self.input_type) == 0:
            self.file = AUDIO_DEMO_FILE
            st.audio(AUDIO_DEMO_FILE)

    def extract_audio_from_video(self, video_file: str) -> str:
        audio_file_name = video_file.name.split(".")[0] + ".mp3"
        video = VideoFileClip(video_file)
        audio = video.audio
        audio.write_audiofile(audio_file_name)
        return audio_file_name

    def transcribe(self, filename: str) -> str:
        if filename.endswith(".mp4"):
            audio_file_name = self.extract_audio_from_video(filename)
        elif filename.endswith(".zip"):
            st.warning("Zip-Dateien werden noch nicht unterstützt.")
        else:
            audio_file_name = filename

        audio_file = open(audio_file_name, "rb")
        client = OpenAI(
            api_key=get_var("OPENAI_API_KEY"),
        )
        transcript = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, response_format="text"
        )
        return transcript

    def run(self):
        if st.button("Transkribieren"):
            with st.spinner("Transkribiere Audio..."):
                if self.formats.index(self.input_type) == 0:
                    self.text = self.transcribe(self.file)
                    if self.text != "":
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
                else:
                    st.info("Diese Option ist noch nicht verfügbar.")
