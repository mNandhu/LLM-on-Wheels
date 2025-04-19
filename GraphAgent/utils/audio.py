import sounddevice as sd
import soundfile as sf
import tempfile
from groq import Groq
import numpy as np
from dotenv import load_dotenv
import os
from elevenlabs.client import ElevenLabs

load_dotenv()


def record_audio(duration: int = 5, fs: int = 16000) -> str:
    print(f"Recording audio for {duration} seconds...")

    # Verify device capabilities
    dev_info = sd.query_devices(sd.default.device[0], "input")
    assert dev_info["max_input_channels"] > 0, "No input channels"

    recording = sd.rec(
        int(duration * fs), samplerate=fs, channels=1, dtype="int16", blocking=True
    )  # Explicit blocking

    if np.all(recording == 0):
        raise ValueError("Silent recording - check microphone")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        sf.write(tmp_file.name, recording, fs, subtype="PCM_16")
        print(f"Peak amplitude: {np.max(np.abs(recording))}")

    return tmp_file.name


def play_audio(audio_file_path: str):
    print("Playing audio...")
    data, samplerate = sf.read(audio_file_path)
    sd.play(data, samplerate)
    sd.wait()


def transcribe_with_groq(
    file_path: str, model: str = "whisper-large-v3", language: str = "en"
) -> str:
    """
    Transcribes the given audio file using Groq API and returns the transcription text.
    """
    client = Groq()
    with open(file_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=f,
            model=model,
            language=language,
            response_format="text",
            temperature=0.0,
        )
    # Groq SDK may return an object or dict
    if hasattr(transcription, "text"):
        return transcription.text
    if isinstance(transcription, dict) and "text" in transcription:
        return transcription["text"]
    return str(transcription)


def synthesize_audio_with_elevenlabs(
    text: str,
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb",
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
) -> str:
    """
    Synthesize speech using ElevenLabs TTS and save it to a temporary file.
    Returns the path to the generated audio file.
    """

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not set in environment")
    client = ElevenLabs(api_key=api_key)
    # The convert() method returns a generator yielding byte chunks
    audio_stream = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        output_format=output_format,
    )
    # Write streamed audio chunks to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        for chunk in audio_stream:
            tmp.write(chunk)
        return tmp.name


if __name__ == "__main__":
    # Example usage
    audio_file = record_audio(duration=5, fs=16000)
    print(f"Recorded audio saved to: {audio_file}")
    # transcription = transcribe_with_groq(audio_file)
    # print
