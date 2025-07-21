import subprocess
import os

pinokio_app_root = os.path.dirname(__file__)
video_crafter_path = os.path.join(pinokio_app_root, "VideoCrafter")
gradio_app_script = os.path.join(video_crafter_path, "gradio_app.py")

if not os.path.exists(gradio_app_script):
    print(f"Error: gradio_app.py not found at {gradio_app_script}")
    print("Please ensure the VideoCrafter project is correctly installed by running the 'Install' command.")
    exit(1) # Or raise FileNotFoundError

print(f"Launching VideoCrafter from: {video_crafter_path}")
subprocess.run(["python", gradio_app_script], cwd=video_crafter_path)