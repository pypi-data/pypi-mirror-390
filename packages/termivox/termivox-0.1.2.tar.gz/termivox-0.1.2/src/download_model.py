import os
import zipfile
import requests
from pathlib import Path

# Model URLs
MODELS = {
    "en": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "name": "vosk-model-small-en-us-0.15"
    },
    "fr": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip",
        "name": "vosk-model-small-fr-0.22"
    }
}

def get_models_dir():
    """Get the user's termivox models directory."""
    models_dir = Path.home() / ".termivox" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir

def download_model(lang="en"):
    """Download and extract a Vosk voice model.

    Args:
        lang: Language code (en or fr)
    """
    if lang not in MODELS:
        print(f"Unsupported language: {lang}. Available: {', '.join(MODELS.keys())}")
        return

    model_info = MODELS[lang]
    models_dir = get_models_dir()
    model_dir = models_dir / model_info["name"]
    model_zip = models_dir / f"{model_info['name']}.zip"

    if model_dir.exists():
        print(f"Model already exists at: {model_dir}")
        return

    print(f"Downloading {lang} Vosk model...")
    print(f"Saving to: {models_dir}")

    try:
        r = requests.get(model_info["url"], stream=True)
        r.raise_for_status()

        with open(model_zip, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print("Extracting model...")
        with zipfile.ZipFile(model_zip, "r") as zip_ref:
            zip_ref.extractall(models_dir)

        model_zip.unlink()  # Remove zip file
        print(f"✓ Model downloaded and extracted to: {model_dir}")
    except Exception as e:
        print(f"✗ Error downloading model: {e}")
        if model_zip.exists():
            model_zip.unlink()

def main():
    """Download English model by default."""
    import argparse
    parser = argparse.ArgumentParser(description="Download Vosk voice models for Termivox")
    parser.add_argument("--lang", default="en", choices=["en", "fr"],
                       help="Language model to download (default: en)")
    args = parser.parse_args()

    download_model(args.lang)

if __name__ == "__main__":
    main()
