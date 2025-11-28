import os
import logging
import subprocess
import tempfile
from pathlib import Path
from groq import Groq

LOG = logging.getLogger(__name__)


def convert_ogg_to_mp3(input_path: str) -> str:
    """
    Convert OGG/OPUS audio (WhatsApp format) to MP3 using ffmpeg.
    Returns path to converted file.
    """
    try:
        # Create temp file for output
        output_path = input_path.rsplit('.', 1)[0] + '.mp3'
        
        # Use ffmpeg to convert
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-acodec', 'libmp3lame', '-ar', '16000', '-ac', '1',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            LOG.warning(f"ffmpeg conversion warning: {result.stderr}")
            # Return original if conversion fails
            return input_path
            
        return output_path
        
    except FileNotFoundError:
        LOG.warning("ffmpeg not found, using original audio file")
        return input_path
    except Exception as e:
        LOG.warning(f"Audio conversion failed: {e}")
        return input_path


async def transcribe_audio(file_path: str) -> str:
    """
    Transcribes audio file using Groq Whisper API.
    Handles WhatsApp OGG/OPUS format by converting to MP3 first.
    """
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        # Convert OGG to MP3 if needed (WhatsApp sends OGG/OPUS)
        file_ext = file_path.lower().split('.')[-1]
        if file_ext in ['ogg', 'opus', 'oga']:
            LOG.info(f"Converting {file_ext} to MP3 for Whisper...")
            file_path = convert_ogg_to_mp3(file_path)
        
        client = Groq(api_key=api_key)
        
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3",
                language="hi",  # Hindi (also handles Hinglish well)
                temperature=0,
                response_format="verbose_json",
            )
            
            text = transcription.text.strip()
            LOG.info(f"Transcribed audio: {text[:100]}...")
            return text
            
    except Exception as e:
        LOG.exception("Error transcribing audio: %s", e)
        raise


async def transcribe_and_parse(file_path: str) -> dict:
    """
    Transcribe audio and return structured result with confidence.
    """
    try:
        text = await transcribe_audio(file_path)
        return {
            "success": True,
            "text": text,
            "source": "voice_message"
        }
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "error": str(e)
        }