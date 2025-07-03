import gradio as gr
import os
import shutil
from datetime import datetime
from main import Main
from utils import *

MAX_SIZE_BYTES = 500 * 1024 * 1024  # 500MB
SUPPORTED_AUDIO_EXTENSIONS = [".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".wma", ".mp4", ".webm"]

def validate_audio(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    return ext in SUPPORTED_AUDIO_EXTENSIONS and os.path.getsize(file_path) <= MAX_SIZE_BYTES

def save_and_parse(username, email, file, names_str, starts_str, ends_str):
    if not username or not email or not file:
        return "❌ Missing fields", None, None

    if not validate_audio(file.name):
        return "❌ File must be a supported audio type and under 500MB", None, None

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_dir = os.path.join("uploads", username, timestamp)
    os.makedirs(save_dir, exist_ok=True)

    dest_path = os.path.join(save_dir, "audio.wav")
    shutil.copy(file.name, dest_path)

    names = [n.strip() for n in names_str.splitlines()]
    starts = [s.strip() for s in starts_str.splitlines()]
    ends = [e.strip() for e in ends_str.splitlines()]

    if not (len(names) == len(starts) == len(ends)):
        return "❌ The number of names, start times, and end times must match", None, None

    users_time = {}
    users_time = {}
    for name, start, end in zip(names, starts, ends):
        if name and start and end:
            users_time[name] = {
                "start": time_str_to_seconds(start),
                "end": time_str_to_seconds(end)
            }

    processor = Main(dest_path, users_time, email)
    processor.run()
    return f"✅ File uploaded successfully.\nThe transcript will be sent to: {email}", dest_path, users_time


with gr.Blocks() as demo:
    gr.Markdown("# 🎤 Upload Audio and Define Speakers")

    with gr.Row():
        username = gr.Textbox(label="Username")
        email = gr.Textbox(label="Email")

    file = gr.File(label="Upload Audio File", type="filepath", file_types=SUPPORTED_AUDIO_EXTENSIONS)

    gr.Markdown("### 🗣️ Speaker Info (one per line)")

    with gr.Row():
        names_box = gr.Textbox(label="Speaker Names", lines=4, placeholder="e.g.\nAlice\nBob")
        starts_box = gr.Textbox(label="Start Times (mm:ss)", lines=4, placeholder="e.g.\n00:05\n01:10")
        ends_box = gr.Textbox(label="End Times (mm:ss)", lines=4, placeholder="e.g.\n01:00\n01:45")

    submit = gr.Button("Submit")

    status_out = gr.Textbox(label="Status")
    path_out = gr.Textbox(label="Saved File Path")
    dict_out = gr.JSON(label="Users Time Dictionary")

    submit.click(
        fn=save_and_parse,
        inputs=[username, email, file, names_box, starts_box, ends_box],
        outputs=[status_out, path_out, dict_out]
    )

demo.launch(server_name="0.0.0.0", server_port=5000)
