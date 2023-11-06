
import streamlit as st
import os
from tools.tool_base import ToolBase
from moviepy.editor import *
import openai


class Speech2Text(ToolBase):
    def __init__(self, logger):
        self.logger = logger
        self.title = "Audio zu Text"
        self.formats = ['Audio/Video Datei', 'Sammlung von Audio-Dateien (zip)']
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        self.output = {}

    def show_settings(self):
        self.input_type = st.radio(
            "Input für Speech2Text",
            options=self.formats
        )

    def extract_audio_from_video(self, video_file):
        audio_file_name = video_file.name.split('.')[0] + '.mp3'
        video = VideoFileClip(video_file)
        audio = video.audio
        audio.write_audiofile(audio_file_name)
        return audio_file_name

    def transcribe(filename):
        if filename.endswith('.mp4'):
            audio_file_name = self.extract_audio_from_video(filename)
        else:
            audio_file_name = filename
        
        audio_file = open(audio_file_name, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        with open('./audio_output.json', 'w') as outfile:
            json.dump(transcript, outfile, indent=4)


    def run(self):
        self.file = st.file_uploader('Audio Datei hochladen')
        
        if st.button("Starten"):
            if self.formats.index(self.input_type) == 0:
                if self.file:
                    self.text = self.extract_text_from_pdf(self.file)
                    dummy = st.text_area("Text", value=self.text, height=400)
                    
        if self.formats.index(self.input_type) == 0 and self.text != "":
            cols = st.columns(2, gap='small')
            with cols[0]:
                if st.button("Text in Zwischenablage kopieren"):
                    pyperclip.copy(self.text,)
                    st.success("Text wurde in die Zwischenablage kopiert.")
            with cols[1]:
                btn = st.download_button(
                    label="Text als txt-Datei herunterladen",
                    data=self.text,
                    file_name="pdf2text.txt",
                    mime="text/plain"
                )
