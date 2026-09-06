import whisper
import tempfile
import os

_model = None


def get_whisper_model():
    global _model
    if _model is None:
        # "small" balances accuracy/speed for Marathi on CPU.
        # Use "base" instead if this is too slow on the demo machine.
        _model = whisper.load_model("small")
    return _model


def transcribe_marathi_audio(audio_bytes, filename_hint="audio.webm"):
    model = get_whisper_model()

    suffix = os.path.splitext(filename_hint)[1] or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        result = model.transcribe(tmp_path, language="mr", task="translate")
    finally:
        os.remove(tmp_path)

    return {
        "english_text": result["text"].strip(),
    }


if __name__ == "__main__":
    import sys
    model = get_whisper_model()
    result = model.transcribe(sys.argv[1], task="translate")
    print("Detected language:", result["language"])
    print("English (translated):", result["text"].strip())