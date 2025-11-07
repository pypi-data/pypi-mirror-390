"""
Pingala Shunya - A comprehensive speech transcription package.

This package provides multi-backend speech transcription capabilities using
faster-whisper, transformers, and openai-whisper with a unified API and
full access to all advanced features including word-level timestamps,
confidence scores, Voice Activity Detection (VAD), and language detection.

Supported Backends:
- faster-whisper: High-performance with GPU acceleration (default)
- transformers: Hugging Face models and latest research  
- openai-whisper: Original OpenAI implementation for compatibility

Features:
- Unified API across all backends
- Auto-detection of optimal backend for each model
- Word-level timestamps and confidence scores
- Voice Activity Detection (VAD) filtering
- Language detection and automatic identification
- Multiple output formats (text, SRT, VTT)
- Streaming transcription support
- Advanced parameter control
- Comprehensive CLI interface

Example:
    from pingala_shunya import PingalaTranscriber
    
    # Auto-detect backend based on model
    transcriber = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim")
    
    # Or specify backend explicitly
    transcriber = PingalaTranscriber(
        model_name="shunyalabs/pingala-v1-en-verbatim",
        backend="ct2"
    )
    
    # Transcribe with advanced features
    segments, info = transcriber.transcribe_file(
        "audio.wav",
        word_timestamps=True,
        beam_size=10
    )
"""

__version__ = "0.1.7"
__author__ = "Shunya Labs"
__email__ = "0@shunyalabs.ai"

from .transcriber import (
    PingalaTranscriber,
    TranscriptionSegment,
    WordSegment,
    TranscriptionInfo,
    TranscriptionBackend,
    CT2Backend,
    TransformersBackend
)

__all__ = [
    "PingalaTranscriber",
    "TranscriptionSegment", 
    "WordSegment",
    "TranscriptionInfo",
    "TranscriptionBackend",
    "CT2Backend",
    "TransformersBackend"
] 
