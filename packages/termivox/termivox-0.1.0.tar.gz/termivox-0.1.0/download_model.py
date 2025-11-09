import os
import zipfile
import requests

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_DIR = "src/voice_models/vosk-model-small-en-us-0.15"
MODEL_ZIP = "src/voice_models/vosk-model-small-en-us-0.15.zip"

def main():
    """Download and extract Vosk voice model for Termivox."""
    os.makedirs("src/voice_models", exist_ok=True)

    if not os.path.exists(MODEL_DIR):
        print("Downloading Vosk model...")
        r = requests.get(MODEL_URL, stream=True)
        with open(MODEL_ZIP, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("Extracting model...")
        with zipfile.ZipFile(MODEL_ZIP, "r") as zip_ref:
            zip_ref.extractall("src/voice_models/")
        os.remove(MODEL_ZIP)
        print("Model downloaded and extracted to:", MODEL_DIR)
    else:
        print("Model already exists at:", MODEL_DIR)

if __name__ == "__main__":
    main()
