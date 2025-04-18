from typing import Tuple, Dict, Any, List
from GraphAgent.utils.audio import (
    record_audio,
    play_audio,
    transcribe_with_groq,
    synthesize_audio_with_elevenlabs,
)


"""Interfaces for Audio Processing"""


def transcribe_audio(audio: Any) -> str:
    # Record audio if not provided, then transcribe using Groq API
    audio_file = audio if isinstance(audio, str) and audio else record_audio()
    # Transcribe with specified model and language
    return transcribe_with_groq(audio_file, model="whisper-large-v3", language="en")


def synthesize_speech(text: str) -> str:
    """
    Synthesize speech from text using ElevenLabs and play the audio.
    Returns the file path of the generated audio.
    """
    # Generate speech audio via ElevenLabs
    audio_file = synthesize_audio_with_elevenlabs(text)
    # Play the generated audio
    play_audio(audio_file)
    return audio_file


"""Interfaces for Robot Navigation"""


def get_current_pose() -> Tuple[float, float, float]:
    # Placeholder: Return current robot pose as (x, y, theta).
    return (0.0, 0.0, 0.0)


def query_memory(entity_type: str, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Placeholder: Query the structured memory with given criteria.
    return []


def send_nav_goal(x: float, y: float, theta: float) -> None:
    # Placeholder: Send navigation goal to the robot.
    print(f"Navigation goal sent: x={x}, y={y}, theta={theta}")


def get_nav_status() -> str:
    # Placeholder: Return the current status of the navigation.
    return "success"


def execute_robot_action(action: str, params: Dict[str, Any]) -> str:
    # Placeholder: Execute a direct robot action and return a status string.
    return f"Action {action} executed with params {params}"


if __name__ == "__main__":
    import sounddevice as sd
    import soundfile as sf

    # Example usage
    audio_file = record_audio()
    # Play audio
    print(f"Playing audio from {audio_file}...")

    def play_audio(file_path):
        """Play audio from the specified file path using sounddevice."""
        data, samplerate = sf.read(file_path)
        sd.play(data, samplerate)
        sd.wait()  # Wait until the audio is finished playing

    # Play the recorded audio
    play_audio(audio_file)
    transcription = transcribe_audio(audio_file)
    print(f"Transcription: {transcription}")
