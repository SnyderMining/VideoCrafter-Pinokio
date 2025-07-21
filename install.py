import subprocess
import os
import shutil # Not directly used in final version, but good to keep in mind for cleanup/moves

# --- Configuration ---
# URL of the specific VideoCrafter GitHub repository you forked from
VIDEO_CRAFTER_REPO = "https://github.com/AILab-CVC/VideoCrafter.git"
# Name of the subfolder where VideoCrafter will be cloned inside your Pinokio app's root
VIDEO_CRAFTER_DIR_NAME = "VideoCrafter"

# --- Model Download Configuration ---
# IMPORTANT: These URLs and target paths are based on common VideoCrafter setups.
# YOU MUST VERIFY these against the README or installation guide of
# https://github.com/AILab-CVC/VideoCrafter for the exact models and their required locations.
# Uncomment or add more models as needed for the features you want to enable.
MODELS_TO_DOWNLOAD = [
    {
        "name": "VideoCrafter2 (320x512) Text-to-Video",
        "url": "https://huggingface.co/VideoCrafter/VideoCrafter2/resolve/main/model.ckpt",
        "target_path_in_repo": "checkpoints/base_512_v2/model.ckpt" # This path is standard for VC2 base
    },
    {
        "name": "VideoCrafter1 (576x1024) Text-to-Video",
        "url": "https://huggingface.co/VideoCrafter/Text2Video-1024/resolve/main/model.ckpt",
        "target_path_in_repo": "checkpoints/text2video_1024_v1/model.ckpt" # Common path for this model
    },
    {
        "name": "VideoCrafter1 (320x512) Text-to-Video",
        "url": "https://huggingface.co/VideoCrafter/Text2Video-512/resolve/main/model.ckpt",
        "target_path_in_repo": "checkpoints/text2video_512_v1/model.ckpt" # Common path for this model
    },
    {
        "name": "VideoCrafter1 (640x1024) Image-to-Video (DynamiCrafter_1024)",
        "url": "https://huggingface.co/Doubiiu/DynamiCrafter_1024/resolve/main/model.ckpt",
        "target_path_in_repo": "checkpoints/i2v_1024_v1/model.ckpt" # Path might need adjustment based on AILab-CVC setup
    },
    {
        "name": "VideoCrafter1 (320x512) Image-to-Video",
        "url": "https://huggingface.co/VideoCrafter/Image2Video-512/resolve/main/model.ckpt",
        "target_path_in_repo": "checkpoints/i2v_512_v1/model.ckpt" # Common path for this model
    }
]

# --- Script Logic ---

# Get the directory where install.py is located (your Pinokio app's root)
pinokio_app_root = os.path.dirname(__file__)
video_crafter_path = os.path.join(pinokio_app_root, VIDEO_CRAFTER_DIR_NAME)

def run_command(command, cwd=None, description=""):
    """Helper function to run shell commands and print status."""
    print(f"\n--- {description} ---")
    try:
        # Using text=True for string input/output, capture_output=False to show live output
        process = subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=False)
        print(f"--- {description} COMPLETED ---")
    except subprocess.CalledProcessError as e:
        print(f"Error during {description}:")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Return Code: {e.returncode}")
        # If capture_output=False, stdout/stderr might be empty here, but the user saw it live
        # print(f"Stdout:\n{e.stdout}") # Uncomment if capture_output=True
        # print(f"Stderr:\n{e.stderr}") # Uncomment if capture_output=True
        print(f"--- {description} FAILED ---")
        # Exit the script if a critical command fails
        exit(1)
    except FileNotFoundError:
        print(f"Error: Command '{command[0]}' not found. Make sure it's in your system's PATH.")
        print("For 'git', ensure Git is installed. For 'pip', ensure Python is correctly set up.")
        print(f"--- {description} FAILED ---")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during {description}: {e}")
        print(f"--- {description} FAILED ---")
        exit(1)

def install_videocrafter():
    # 1. Clone VideoCrafter Repository
    if not os.path.exists(video_crafter_path):
        print(f"VideoCrafter directory '{VIDEO_CRAFTER_DIR_NAME}' not found.")
        run_command(
            ["git", "clone", VIDEO_CRAFTER_REPO, VIDEO_CRAFTER_DIR_NAME],
            cwd=pinokio_app_root, # Clone into the Pinokio app's root
            description=f"Cloning VideoCrafter from {VIDEO_CRAFTER_REPO}"
        )
    else:
        print(f"\n--- VideoCrafter directory '{VIDEO_CRAFTER_DIR_NAME}' already exists. ---")
        print("Attempting to pull latest changes to ensure it's up to date...")
        run_command(["git", "pull"], cwd=video_crafter_path, description="Pulling latest VideoCrafter changes")

    # 2. Install Python Dependencies
    requirements_file = os.path.join(video_crafter_path, "requirements.txt")
    if os.path.exists(requirements_file):
        print(f"Found requirements.txt at {requirements_file}.")
        run_command(
            ["pip", "install", "-r", requirements_file],
            cwd=video_crafter_path, # VERY IMPORTANT: run pip from the cloned repo's directory
            description=f"Installing Python dependencies for VideoCrafter"
        )
    else:
        print(f"\n--- WARNING: requirements.txt not found at {requirements_file}. Skipping pip install. ---")
        print("Please verify the path or if VideoCrafter changed its dependency management.")
        print("This may cause issues if dependencies are not met.")

    # 3. Download Models
    print("\n--- Starting Model Downloads ---")
    if not MODELS_TO_DOWNLOAD:
        print("No models configured for download. Please add entries to MODELS_TO_DOWNLOAD if needed.")
    else:
        for model_info in MODELS_TO_DOWNLOAD:
            model_url = model_info["url"]
            relative_target_path = model_info["target_path_in_repo"]
            full_target_path = os.path.join(video_crafter_path, relative_target_path)
            model_name = model_info["name"]

            # Create necessary directories (e.g., 'checkpoints/base_512_v2/')
            os.makedirs(os.path.dirname(full_target_path), exist_ok=True)

            if not os.path.exists(full_target_path) or os.path.getsize(full_target_path) == 0:
                print(f"Downloading {model_name} from {model_url} to {full_target_path}...")
                # Use curl for downloading large files. Pinokio environments typically have curl.
                run_command(
                    ["curl", "-L", model_url, "-o", full_target_path], # -L handles redirects, -o specifies output file
                    description=f"Downloading {model_name}"
                )
            else:
                print(f"Model '{model_name}' already exists at {full_target_path} (and is not empty). Skipping download.")

    print("\n--- Model Downloads COMPLETED (or skipped) ---")
    print("\nVideoCrafter installation process finished.")
    print("You can now run the 'Run VideoCrafter' command from Pinokio.")

if __name__ == "__main__":
    install_videocrafter()