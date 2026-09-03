from kokoro import KPipeline
import soundfile as sf


pipeline = KPipeline(lang_code='a')

def text_to_speech(text: str, output_path: str = 'output.wav') -> str:
    generator = pipeline(text, voice='af_heart')
    for i, (gs, ps, audio) in enumerate(generator):
        sf.write(output_path, audio, 24000)
        break
    return output_path
