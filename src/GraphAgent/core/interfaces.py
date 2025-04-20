from typing import Tuple, Dict, Any, List
from ..utils.audio import (
    record_audio,
    play_audio,
    transcribe_with_groq,
    synthesize_audio_with_elevenlabs,
)

import src.Simulator.simulation_api as sim  # type: ignore


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
    # Delegate to simulation API for pose
    return sim.get_current_pose_from_sim()


def query_memory(entity_type: str, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Placeholder: Query the structured memory with given criteria.
    return []


def send_nav_goal(x: float, y: float, theta: float) -> None:
    # Delegate to simulation API for navigation goal
    sim.send_nav_goal_to_sim(x, y, theta)


def get_nav_status() -> str:
    # Delegate to simulation API for navigation status
    return sim.get_nav_status_from_sim()


def execute_robot_action(action: str, params: Dict[str, Any]) -> str:
    # Delegate to simulation API for direct robot actions
    return sim.execute_robot_action_in_sim(action, params)


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
