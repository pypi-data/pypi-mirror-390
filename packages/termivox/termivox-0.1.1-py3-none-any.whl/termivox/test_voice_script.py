# test_voice_script.py
"""
A simple script to test the Recognizer class with both English and French language support.
You can run this script with a --lang argument (en or fr) to test voice recognition and command mapping.
"""
import argparse
from termivox.voice.recognizer import Recognizer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', default='en', help='Language code for Vosk model (en or fr)')
    args = parser.parse_args()

    recognizer = Recognizer(lang=args.lang)
    print(f"[TEST] Voice recognizer started (lang={args.lang}). Speak now...")
    try:
        for text in recognizer.listen():
            print(f"[RECOGNIZED]: {repr(text)}")
    except KeyboardInterrupt:
        print("[TEST] Stopped by user.")
    finally:
        recognizer.close()

if __name__ == "__main__":
    main()
