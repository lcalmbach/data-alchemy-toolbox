import streamlit as st
import os
from tools.tool_base import ToolBase
from moviepy.editor import VideoFileClip
from openai import OpenAI
import pyperclip
from enum import Enum

from helper import get_var, check_file_type, save_uploadedfile

AUDIO_DEMO_FILE = "./data/demo/demo_audio.mp3"
AUDIO_TEMP_FILE = "./data/temp/temp_audio."
OUTPUT_FILE = "./output/audio_output.txt"
FILE_FORMAT_OPTIONS = ["mp4", "mp3"]


class InputFormat(Enum):
    DEMO = 0
    FILE = 1
    ZIPPED_FILE = 2
    S3 = 3


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
        if self.formats.index(self.input_type) == InputFormat.DEMO.value:
            self.file = AUDIO_DEMO_FILE
            st.audio(AUDIO_DEMO_FILE)
        elif self.formats.index(self.input_type) == InputFormat.FILE.value:
            self.input_file = st.file_uploader(
                "MP4 oder MP3 Datei hochladen",
                type=FILE_FORMAT_OPTIONS,
                help="Lade die Datei hoch, die du transkribieren möchtest.",
            )
            if self.input_file is not None:
                self.file = AUDIO_TEMP_FILE + self.input_file.name.split(".")[1]
                save_uploadedfile(self.input_file, self.file)

        elif self.formats.index(self.input_type) == InputFormat.ZIPPED_FILE.value:
            self.input_file = st.file_uploader(
                "MP4 oder MP3 Datei hochladen",
                type=["zip"],
                help="Lade die ZIP Datei hoch, welche die zu transkribierenden Dateien enthält. Achtung, die Datei darf nicht grösser als 200 MB sein.",
            )

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
                elif self.formats.index(self.input_type) == InputFormat.FILE.value:
                    self.text = self.transcribe(self.file)
                else:
                    st.info("Diese Option ist noch nicht verfügbar.")
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
