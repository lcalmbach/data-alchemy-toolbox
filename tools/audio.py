import openai
import json
from helper import get_var
from moviepy.editor import *

openai.api_key = get_var("OPENAI_API_KEY")
audio_file_name = "./output_audio.mp3"


def transcribe(video_filename):
    # Load your video
    video = VideoFileClip(video_filename)

    # Extract audio from video
    print("extracting audio...")
    audio = video.audio
    print("saving audio file...")
    # Save the audio file

    audio.write_audiofile(audio_file_name)

    print("transcribing audio file...")
    audio_file = open(audio_file_name, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    with open("./audio_output.json", "w") as outfile:
        json.dump(transcript, outfile, indent=4)


transcribe("./Beat_Jans_13.09.2023_10h13.mp4")
