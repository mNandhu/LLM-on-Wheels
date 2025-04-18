import sounddevice as sd
import soundfile as sf
import tempfile
from groq import Groq
import numpy as np

def record_audio(duration: int = 5, fs: int = 16000) -> str:
    print(f"Recording audio for {duration} seconds...")
    
    # Verify device capabilities
    dev_info = sd.query_devices(sd.default.device[0], 'input')
    assert dev_info['max_input_channels'] > 0, "No input channels"
    
    recording = sd.rec(int(duration * fs), 
                      samplerate=fs, 
                      channels=1,
                      dtype="int16",
                      blocking=True)  # Explicit blocking
    
    if np.all(recording == 0):
        raise ValueError("Silent recording - check microphone")
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        sf.write(tmp_file.name, recording, fs, subtype='PCM_16')
        print(f"Peak amplitude: {np.max(np.abs(recording))}")
        
    return tmp_file.name



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

if __name__ == "__main__":
    # Example usage
    audio_file = record_audio(duration=5, fs=16000)
    print(f"Recorded audio saved to: {audio_file}")
    # transcription = transcribe_with_groq(audio_file)
    # print
