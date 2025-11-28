"""
Test image and audio processing for Munimji.
"""
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from backend.whatsapp.image_processor import (
    extract_image_data,
    parse_extracted_to_command,
    extract_text_with_tesseract
)
from backend.whatsapp.audio_processor import transcribe_audio, convert_ogg_to_mp3


def print_divider(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60 + "\n")


async def test_image_extraction():
    """Test image text extraction."""
    print_divider("IMAGE PROCESSING TEST")
    
    # Create a test image with text
    test_image_path = Path(__file__).parent / "test_image.png"
    
    # Check if test image exists
    if not test_image_path.exists():
        print("⚠️  No test image found. Creating a simple test...")
        
        # Create a simple test image with PIL
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.new('RGB', (400, 200), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a font that supports Hindi, fallback to default
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            draw.text((20, 50), "Ramesh ke 500 rupay", fill='black', font=font)
            draw.text((20, 100), "udhaar - 27 Nov 2025", fill='black', font=font)
            
            img.save(test_image_path)
            print(f"✅ Created test image: {test_image_path}")
        except Exception as e:
            print(f"❌ Could not create test image: {e}")
            return
    
    print("Testing Groq Vision OCR...")
    try:
        result = await extract_image_data(str(test_image_path))
        print(f"📝 Extracted text:\n{result}\n")
        
        # Parse to command
        command = parse_extracted_to_command(result)
        print(f"🤖 Parsed command: {command}")
        print("✅ Image processing works!")
    except Exception as e:
        print(f"❌ Image extraction failed: {e}")
    
    # Cleanup
    if test_image_path.exists():
        os.remove(test_image_path)


async def test_audio_transcription():
    """Test audio transcription."""
    print_divider("AUDIO PROCESSING TEST")
    
    # Check for test audio file
    audio_dir = Path(__file__).parent.parent / "downloads" / "audio_files"
    test_files = list(audio_dir.glob("*.ogg")) + list(audio_dir.glob("*.mp3"))
    
    if not test_files:
        print("⚠️  No test audio files found in downloads/audio_files/")
        print("   To test, add an audio file there.")
        
        # Test ffmpeg availability
        print("\nChecking ffmpeg availability...")
        import subprocess
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ ffmpeg is available")
            else:
                print("❌ ffmpeg returned error")
        except FileNotFoundError:
            print("❌ ffmpeg not found - audio conversion won't work")
        return
    
    test_file = test_files[0]
    print(f"Testing with: {test_file}")
    
    try:
        result = await transcribe_audio(str(test_file))
        print(f"🎤 Transcription:\n{result}")
        print("✅ Audio transcription works!")
    except Exception as e:
        print(f"❌ Audio transcription failed: {e}")


async def test_parse_commands():
    """Test parsing extracted text to commands."""
    print_divider("COMMAND PARSING TEST")
    
    test_cases = [
        "Ramesh ke 500 rupay udhaar hai",
        "Rs. 1000 received from Mohan",
        "₹200 petrol expense",
        "Suresh ne 300 diye",
        "आज Sharma ji ko 500 ka saman becha",
    ]
    
    for text in test_cases:
        command = parse_extracted_to_command(text)
        print(f"📝 Input: {text}")
        print(f"🤖 Parsed: {command}\n")


async def main():
    print("="*60)
    print("   MUNIMJI - MEDIA PROCESSING TEST")
    print("="*60)
    
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  GROQ_API_KEY not set. Some tests may fail.")
    
    await test_parse_commands()
    await test_image_extraction()
    await test_audio_transcription()
    
    print("\n" + "="*60)
    print("   TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
