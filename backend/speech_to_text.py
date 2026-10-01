import os

# Keep CPU memory usage lower on small cloud instances
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import whisper
import tempfile

_model = None


def get_whisper_model():
    global _model

    if _model is None:
        # Use WHISPER_MODEL from environment.
        # Local default: medium
        # Render demo: set WHISPER_MODEL=base
        model_name = os.getenv("WHISPER_MODEL", "medium")

        print(f"Loading Whisper model: {model_name}")
        _model = whisper.load_model(model_name)

    return _model


def transcribe_marathi_audio(audio_bytes, filename_hint="audio.webm"):
    model = get_whisper_model()

    suffix = os.path.splitext(filename_hint)[1] or ".webm"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        result = model.transcribe(
            tmp_path,
            language="mr",
            task="translate"
        )
    finally:
        os.remove(tmp_path)

    return {
        "english_text": result["text"].strip(),
    }


if __name__ == "__main__":
    import sys

    model = get_whisper_model()
    result = model.transcribe(
        sys.argv[1],
        task="translate"
    )

    print("Detected language:", result["language"])
    print("English (translated):", result["text"].strip())

