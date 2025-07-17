import gradio_client.utils as _gc_utils

# תיקון לשגיאה שנגרמת כאשר additionalProperties = True
def _patched_json_schema_to_python_type(schema, defs=None):
    if isinstance(schema, bool):
        return "dict" if schema else "None"
    return _gc_utils._original_json_schema_to_python_type(schema, defs)

# שמירה על הפונקציה המקורית לשחזור אם נרצה
if not hasattr(_gc_utils, "_original_json_schema_to_python_type"):
    _gc_utils._original_json_schema_to_python_type = _gc_utils._json_schema_to_python_type
    _gc_utils._json_schema_to_python_type = _patched_json_schema_to_python_type

import gradio as gr
import os
import shutil
from datetime import datetime
from main import Main
from utils import *

MAX_SIZE_BYTES = 500 * 1024 * 1024  # 500MB
SUPPORTED_AUDIO_EXTENSIONS = [".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".wma", ".mp4", ".webm"]

def validate_audio(file_path):
    if not file_path:
        return False
    ext = os.path.splitext(file_path)[-1].lower()
    return ext in SUPPORTED_AUDIO_EXTENSIONS and os.path.getsize(file_path) <= MAX_SIZE_BYTES

def save_and_parse(username, email, file, names_str, starts_str, ends_str):
    try:
        print(f"DEBUG: Called with username={username}, email={email}, file={file}")
        
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
        for name, start, end in zip(names, starts, ends):
            if name and start and end:
                users_time[name] = {
                    "start": time_str_to_seconds(start),
                    "end": time_str_to_seconds(end)
                }

        processor = Main(dest_path, users_time, email)
        processor.run()
        return f"✅ File uploaded successfully.\nThe transcript will be sent to: {email}", dest_path, users_time
    
    except Exception as e:
        print(f"ERROR: {e}")
        return f"❌ Error: {str(e)}", None, None

# יצירת הממשק
def create_interface():
    with gr.Blocks(title="Audio Transcription App") as demo:
        gr.Markdown("# 🎤 Upload Audio and Define Speakers")

        with gr.Row():
            username = gr.Textbox(label="Username", placeholder="Enter your username")
            email = gr.Textbox(label="Email", placeholder="Enter your email")

        file = gr.File(
            label="Upload Audio File", 
            type="filepath", 
            file_types=SUPPORTED_AUDIO_EXTENSIONS
        )

        gr.Markdown("### 🗣️ Speaker Info (one per line)")

        with gr.Row():
            names_box = gr.Textbox(
                label="Speaker Names", 
                lines=4, 
                placeholder="e.g.\nAlice\nBob"
            )
            starts_box = gr.Textbox(
                label="Start Times (mm:ss)", 
                lines=4, 
                placeholder="e.g.\n00:05\n01:10"
            )
            ends_box = gr.Textbox(
                label="End Times (mm:ss)", 
                lines=4, 
                placeholder="e.g.\n01:00\n01:45"
            )

        submit = gr.Button("Submit", variant="primary")

        with gr.Row():
            status_out = gr.Textbox(label="Status", interactive=False)
        
        with gr.Row():
            path_out = gr.Textbox(label="Saved File Path", interactive=False)
            dict_out = gr.JSON(label="Users Time Dictionary")

        submit.click(
            fn=save_and_parse,
            inputs=[username, email, file, names_box, starts_box, ends_box],
            outputs=[status_out, path_out, dict_out]
        )

    return demo

if __name__ == "__main__":
    print("Starting Gradio app...")
    demo = create_interface()
    print("Launching on http://0.0.0.0:5000")
    
    # פתרון לבעיית svelte-i18n
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'C')
    except:
        pass
    
    demo.launch(
        server_name="0.0.0.0", 
        server_port=5000,
        debug=False,  # כיבוי debug כדי להימנע מבעיות JS
        show_error=False,
        quiet=True,
        favicon_path=None  # מניעת בעיות עם favicon
    )