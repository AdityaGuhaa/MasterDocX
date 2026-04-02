import io
import os
from api.settings import settings
from typing import Generator
import subprocess
import tempfile
import math


class TTSEngine:
    def __init__(self):
        """Initialize TTS engine"""
        # Check if espeak is available (common TTS engine)
        self.espeak_available = self._check_espeak()

    def _check_espeak(self):
        """Check if espeak is available"""
        try:
            subprocess.run(["espeak", "--version"],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
            return True
        except (FileNotFoundError, subprocess.SubprocessError):
            return False

    def synthesize(self, text: str) -> Generator[bytes, None, None]:
        """Synthesize text to speech and return audio stream"""
        if not text.strip():
            # Return empty WAV for empty text
            yield self._create_empty_wav()
            return

        if self.espeak_available:
            # Use espeak if available
            try:
                # Create temporary file for WAV output
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_path = tmp_file.name

                # Generate speech with espeak
                subprocess.run([
                    "espeak",
                    "-w", tmp_path,
                    "-s", "150",  # Speed
                    "-p", "50",   # Pitch
                    "-a", "100",  # Amplitude
                    text
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # Read and yield the WAV file
                with open(tmp_path, 'rb') as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        yield chunk

                # Clean up temp file
                os.unlink(tmp_path)
                return
            except Exception:
                pass  # Fall back to basic WAV

        # Fallback: generate basic WAV with beep for demonstration
        yield self._create_beep_wav()

    def _create_empty_wav(self) -> bytes:
        """Create a minimal WAV file with silence"""
        wav_data = bytearray([
            0x52, 0x49, 0x46, 0x46,  # "RIFF"
            0x24, 0x00, 0x00, 0x00,  # Chunk size (36 bytes)
            0x57, 0x41, 0x56, 0x45,  # "WAVE"
            0x66, 0x6d, 0x74, 0x20,  # "fmt "
            0x10, 0x00, 0x00, 0x00,  # Subchunk size (16 bytes)
            0x01, 0x00,              # Audio format (PCM)
            0x01, 0x00,              # Number of channels (1)
            0x40, 0x1f, 0x00, 0x00,  # Sample rate (8000 Hz)
            0x80, 0x3e, 0x00, 0x00,  # Byte rate (8000)
            0x01, 0x00,              # Block align (1)
            0x08, 0x00,              # Bits per sample (8)
            0x64, 0x61, 0x74, 0x61,  # "data"
            0x00, 0x00, 0x00, 0x00   # Data size (0 bytes)
        ])
        return bytes(wav_data)

    def _create_beep_wav(self) -> bytes:
        """Create a simple WAV file with a beep sound"""
        # WAV header for a simple tone
        wav_data = bytearray([
            0x52, 0x49, 0x46, 0x46,  # "RIFF"
            0x24, 0x08, 0x00, 0x00,  # Chunk size
            0x57, 0x41, 0x56, 0x45,  # "WAVE"
            0x66, 0x6d, 0x74, 0x20,  # "fmt "
            0x10, 0x00, 0x00, 0x00,  # Subchunk size (16 bytes)
            0x01, 0x00,              # Audio format (PCM)
            0x01, 0x00,              # Number of channels (1)
            0x40, 0x1f, 0x00, 0x00,  # Sample rate (8000 Hz)
            0x40, 0x1f, 0x00, 0x00,  # Byte rate
            0x01, 0x00,              # Block align
            0x08, 0x00,              # Bits per sample (8)
            0x64, 0x61, 0x74, 0x61,  # "data"
            0x00, 0x08, 0x00, 0x00   # Data size
        ])

        # Add some simple sine wave data (beep sound)
        sample_rate = 8000
        duration = 0.5  # 0.5 seconds
        frequency = 440  # A4 note

        samples = int(sample_rate * duration)
        for i in range(samples):
            # Generate sine wave sample
            sample = int(127 + 127 * math.sin(2 * math.pi * frequency * i / sample_rate))
            wav_data.append(sample)

        # Update file size in header
        file_size = len(wav_data) - 8
        wav_data[4] = file_size & 0xff
        wav_data[5] = (file_size >> 8) & 0xff
        wav_data[6] = (file_size >> 16) & 0xff
        wav_data[7] = (file_size >> 24) & 0xff

        # Update data size
        data_size = len(wav_data) - 44
        wav_data[40] = data_size & 0xff
        wav_data[41] = (data_size >> 8) & 0xff
        wav_data[42] = (data_size >> 16) & 0xff
        wav_data[43] = (data_size >> 24) & 0xff

        return bytes(wav_data)

    def synthesize_file(self, text: str, output_path: str):
        """Synthesize text to speech and save to file"""
        with open(output_path, "wb") as f:
            for chunk in self.synthesize(text):
                f.write(chunk)