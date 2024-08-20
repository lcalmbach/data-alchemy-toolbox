import streamlit as st
import os
import pyperclip
from moviepy.editor import VideoFileClip
from enum import Enum
import re

from tools.tool_base import ToolBase, OUTPUT_PATH, TEMP_PATH
from helper import extract_text_from_uploaded_file, extract_text_from_url


FILE_FORMAT_OPTIONS = ["mp4"]


class InputFormat(Enum):
    FILE = 0


class Video2Audio(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "🚧Video zu Audio"
        self.formats = [
            "mp4 Datei hochladen",
        ]
        self.text = None
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()

    def show_settings(self):
        self.input_type = st.radio("Input Format", options=self.formats)

        if self.formats.index(self.input_type) == InputFormat.FILE.value:
            self.input_file = st.file_uploader(
                "mp4 Datei",
                type=FILE_FORMAT_OPTIONS,
                help="Lade die Video-Datei hoch, deren Audio du extrahieren möchtest.",
            )

    def save_uploaded_file(self, uploaded_file):
        os.makedirs(TEMP_PATH, exist_ok=True)
        file_path = os.path.join(TEMP_PATH, uploaded_file.name)
        
        # Save the file
        with open(file_path, "wb") as file:
            file.write(uploaded_file.read())
        
        return file_path

    def extract_audio_from_video(self, video_file_path: str, output_audio_file_path: str):
        video = VideoFileClip(video_file_path)
        audio = video.audio
        audio.write_audiofile(output_audio_file_path)
        video.close()


    def run(self):
        if st.button("Konvertierung Starten"):
            input_file_path =  self.save_uploaded_file(self.input_file)
            output_audio_file_path = os.path.join(OUTPUT_PATH, self.input_file.name)
            self.extract_audio_from_video(input_file_path, output_audio_file_path)
            st.success(f"Audio extracted successfully! [Download Audio]({output_audio_file_path})")

