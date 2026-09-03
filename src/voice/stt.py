import whisper
import sounddevice as sd
from scipy.io.wavfile import write
from src.retrieval.graph_search import correct_artist_names

model = whisper.load_model('base')


def record_audio(duration_seconds: int = 5, sample_rate: int = 16000) -> str:
    """
    Record audio from the microphone for a fixed duration, save to a .wav file.
    """
    print(f"Recording for {duration_seconds} seconds...")
    recording = sd.rec(int(duration_seconds * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()  # blocks until recording finishes
    
    output_path = "recorded_audio.wav"
    write(output_path, sample_rate, recording)
    print("Recording saved.")
    return output_path


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe an audio file to text using Whisper
    """
    result = model.transcribe(audio_path)
    return result['text']



def record_and_transcribe(duration_seconds: int = 5) -> str:
    audio_path = record_audio(duration_seconds)
    raw_text = transcribe_audio(audio_path)
    return correct_artist_names(raw_text)
