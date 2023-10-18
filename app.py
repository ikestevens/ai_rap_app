import streamlit as st
from gtts import gTTS
import pydub
from pydub import AudioSegment, effects
from io import BytesIO
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import types
import re
import time
import tempfile
from moviepy.editor import *

# Define a function to be executed when the button is pressed
def generate_rap(song_title, song_lyrics, selected_audio_file_path):
    st.write("Creating Rap...")
    tts = gTTS(text=song_lyrics, lang='en')

    # Create a BytesIO buffer and write the audio data to it
    buffer = BytesIO()
    tts.write_to_fp(buffer)

    # Seek to the beginning of the buffer before reading from it
    buffer.seek(0)

    audio_segment = AudioSegment.from_file(buffer)

    # Change playback speed (speed up by 1.5x for example)
    fast_audio = audio_segment.speedup(playback_speed=1.25)
    fast_audio.export(f'{song_title}.mp3', format='mp3')

    speech_audio = pydub.AudioSegment.from_mp3(f'{song_title}.mp3')
    background_music = pydub.AudioSegment.from_mp3(selected_audio_file_path)
    combined_audio = speech_audio.overlay(background_music-10, loop=True)
    combined_audio.export(f"{song_title}_rap.mp3", format="mp3")

    # Combine the image and audio into a video file (MP4)
    audio_clip = AudioFileClip(f"{song_title}_rap.mp3")

    return f"{song_title}_rap.mp3"

def generate_video(rap_mp3, picture):
    song_name = rap_mp3.replace("_rap.mp3", "")
    # If 'picture' is a PIL Image object (or similar) from Streamlit
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
        # Write the contents of the uploaded file to the temporary file
        temp_img.write(picture.getvalue())

        # image
        image_clip = ImageClip(temp_img.name, duration=audio_clip.duration)

        # final video
        final_video = image_clip.set_audio(audio_clip)
        final_video.write_videofile(f"{song_name}_vid.mp4", codec="libx264", audio_codec="aac", fps=24)
        st.write(f"Saved video as {song_name}_vid.mp4")

st.title('AI Rap App')

# Map song name to the corresponding audio file path
audio_file_paths = {
    "Nuthin' But A G Thang": "nothing.mp3",
    "It Was A Good Day": "good_day.mp3",
    "Role Model": "role_model.mp3"
}

# Create a sidebar with a dropdown to select an audio file
selected_file_name = st.sidebar.selectbox("Select beat", list(audio_file_paths.keys()))

# Create a function to display and play the selected audio file
def play_audio(audio_file_path):
    if audio_file_path:
        audio_file = open(audio_file_path, "rb").read()
        st.audio(audio_file, format='audio/mp3', start_time=0)

# Display the selected audio file in the main content area
st.sidebar.write("Preview beat:")
selected_audio_file_path = audio_file_paths.get(selected_file_name, None)
st.sidebar.audio(open(selected_audio_file_path, "rb").read(), format='audio/mp3', start_time=0)

# Use st.text_input() to create a single-line input for the song title
song_title = st.text_input("Enter song title here")

song_lyrics = st.text_area("Enter song lyrics here")

# Create a button widget
if st.button("Generate Rap"):
    # Assuming the `generate_rap` function returns the path to the generated MP3 file
    generated_audio_path = generate_rap(song_title, song_lyrics, selected_audio_file_path)

    # Preview the generated MP3 in Streamlit
    st.audio(generated_audio_path)

# Create a file uploader widget for PNG images
picture = st.file_uploader("Upload a PNG image", type=["png"])

# Create a button widget
if st.button("Generate Video"):
    try:
        generate_video(generated_audio_path, picture)
    except:
        st.write("Must generate rap first")
