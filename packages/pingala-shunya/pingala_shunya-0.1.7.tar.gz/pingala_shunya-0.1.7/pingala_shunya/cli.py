"""
Command-line interface for Pingala Shunya transcription by Shunya Labs.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .transcriber import PingalaTranscriber


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="pingala",
        description="Transcribe audio files using Shunya Labs backends (ct2, transformers)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pingala audio.wav                          # Basic transcription (Pingala model)
  pingala audio.wav -o output.txt            # Save to file
  pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim  # Default Shunya Labs model
  pingala audio.wav --backend transformers   # Use transformers backend
  pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --backend transformers
  pingala audio.wav --device cpu             # Use CPU instead of GPU
  pingala audio.wav --beam-size 10           # Higher accuracy
  pingala audio.wav --language en            # Specify language
  pingala audio.wav --word-timestamps        # Include word-level timing
  pingala audio.wav --show-confidence        # Show confidence scores
  pingala audio.wav --vad                    # Enable voice activity detection
  pingala audio.wav --detect-language        # Detect language only

Supported models:
  • Default: shunyalabs/pingala-v1-en-verbatim (High-quality English transcription)
  • Custom: Any Hugging Face model or local path
  • Local path: /path/to/local/model

Supported backends:
  • ct2: High-performance CTranslate2 optimization (default)
  • transformers: Hugging Face transformers library

Developed by Shunya Labs for superior transcription quality.
        """,
    )
    
    parser.add_argument(
        "audio_file",
        type=str,
        help="Path to the audio file to transcribe"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (default: print to stdout)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="Model name or path (default: shunyalabs/pingala-v1-en-verbatim). "
             "Can be any Hugging Face model name or local path"
    )
    
    parser.add_argument(
        "--backend",
        type=str,
        choices=["ct2", "transformers"],
        help="Backend to use (auto-detected by default). "
             "ct2: High-performance CTranslate2 optimization. "
             "transformers: Hugging Face models."
    )
    
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        choices=["cuda", "cpu", "auto"],
        help="Device to run the model on (default: cuda)"
    )
    
    parser.add_argument(
        "--compute-type",
        type=str,
        default="float16",
        choices=["float16", "float32", "int8"],
        help="Compute precision (default: float16)"
    )
    
    parser.add_argument(
        "--beam-size",
        type=int,
        default=5,
        help="Beam size for decoding (default: 5)"
    )
    
    parser.add_argument(
        "--language",
        type=str,
        help="Language code (e.g., 'en' for English)"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        default="text",
        choices=["text", "srt", "vtt"],
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--word-timestamps",
        action="store_true",
        help="Include word-level timestamps"
    )
    
    parser.add_argument(
        "--show-confidence",
        action="store_true",
        help="Show confidence scores for segments"
    )
    
    parser.add_argument(
        "--show-words",
        action="store_true",
        help="Show individual word timestamps and confidence"
    )
    
    parser.add_argument(
        "--vad",
        action="store_true",
        help="Enable Voice Activity Detection filtering (ct2 only)"
    )
    
    parser.add_argument(
        "--detect-language",
        action="store_true",
        help="Only detect language, don't transcribe"
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Temperature for sampling (0.0 = deterministic, default: 0.0)"
    )
    
    parser.add_argument(
        "--compression-ratio-threshold",
        type=float,
        default=2.4,
        help="Compression ratio threshold for filtering (default: 2.4, ct2 only)"
    )
    
    parser.add_argument(
        "--log-prob-threshold",
        type=float,
        default=-1.0,
        help="Log probability threshold for filtering (default: -1.0, ct2 only)"
    )
    
    parser.add_argument(
        "--no-speech-threshold",
        type=float,
        default=0.6,
        help="No speech probability threshold (default: 0.6)"
    )
    
    parser.add_argument(
        "--initial-prompt",
        type=str,
        help="Initial prompt for the decoder"
    )
    
    parser.add_argument(
        "--hotwords",
        type=str,
        help="Hotwords to boost during decoding (ct2 only)"
    )
    
    parser.add_argument(
        "--task",
        type=str,
        default="transcribe",
        choices=["transcribe", "translate"],
        help="Task type (default: transcribe)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    return parser


def format_as_srt(segments, output_file: Optional[str] = None, word_timestamps: bool = False):
    """Format transcription segments as SRT subtitles."""
    lines = []
    for i, segment in enumerate(segments, 1):
        start_time = format_time_srt(segment.start)
        end_time = format_time_srt(segment.end)
        
        lines.append(f"{i}")
        lines.append(f"{start_time} --> {end_time}")
        
        if word_timestamps and segment.words:
            # Include word-level information in SRT
            text_with_words = ""
            for word in segment.words:
                text_with_words += f"{word.word} "
            lines.append(text_with_words.strip())
        else:
            lines.append(segment.text.strip())
        lines.append("")
    
    content = "\n".join(lines)
    
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        print(content)


def format_as_vtt(segments, output_file: Optional[str] = None, word_timestamps: bool = False):
    """Format transcription segments as WebVTT."""
    lines = ["WEBVTT", ""]
    
    for segment in segments:
        start_time = format_time_vtt(segment.start)
        end_time = format_time_vtt(segment.end)
        
        lines.append(f"{start_time} --> {end_time}")
        
        if word_timestamps and segment.words:
            # Include word-level information in VTT
            text_with_words = ""
            for word in segment.words:
                word_start = format_time_vtt(word.start)
                word_end = format_time_vtt(word.end)
                text_with_words += f"<{word_start}>{word.word}</{word_end}> "
            lines.append(text_with_words.strip())
        else:
            lines.append(segment.text.strip())
        lines.append("")
    
    content = "\n".join(lines)
    
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        print(content)


def format_time_srt(seconds: float) -> str:
    """Format time for SRT format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def format_time_vtt(seconds: float) -> str:
    """Format time for VTT format (HH:MM:SS.mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Check if audio file exists
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"Error: Audio file '{args.audio_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Initialize transcriber
    try:
        if args.verbose:
            model_name = args.model or "shunyalabs/pingala-v1-en-verbatim (default)"
            backend_name = args.backend or "auto-detected"
            print(f"Initializing transcriber:")
            print(f"  Model: {model_name}")
            print(f"  Backend: {backend_name}")
            print(f"  Device: {args.device}")
            print(f"  Compute type: {args.compute_type}")
        
        transcriber = PingalaTranscriber(
            model_name=args.model,
            device=args.device,
            compute_type=args.compute_type,
            backend=args.backend
        )
        
        if args.verbose:
            model_info = transcriber.get_model_info()
            print(f"  Model loaded successfully:")
            print(f"    Backend: {model_info.get('backend', 'unknown')}")
            print(f"    Model: {model_info.get('model_name', 'unknown')}")
            print(f"    Device: {model_info.get('device', 'unknown')}")
        
    except Exception as e:
        print(f"Error initializing transcriber: {e}", file=sys.stderr)
        if args.backend == "transformers":
            print("  Hint: Install transformers dependencies with: pip install 'pingala-shunya[transformers]'", file=sys.stderr)
        elif args.backend == "ct2":
            print("  Hint: Install CTranslate2 dependencies with: pip install 'pingala-shunya'", file=sys.stderr)
        sys.exit(1)
    
    # Language detection only
    if args.detect_language:
        try:
            if args.verbose:
                print(f"Detecting language for: {args.audio_file}")
            
            info = transcriber.detect_language(str(audio_path))
            
            print(f"Detected language: {info.language}")
            print(f"Confidence: {info.language_probability:.3f}")
            print(f"Duration: {info.duration:.2f} seconds")
            print(f"Duration after VAD: {info.duration_after_vad:.2f} seconds")
            
        except Exception as e:
            print(f"Error during language detection: {e}", file=sys.stderr)
            sys.exit(1)
        
        return
    
    # Transcribe audio
    try:
        if args.verbose:
            print(f"Transcribing audio file: {args.audio_file}")
            print(f"Parameters: beam_size={args.beam_size}, language={args.language}")
            print(f"Word timestamps: {args.word_timestamps}, VAD: {args.vad}")
        
        # Choose transcription method based on options
        if args.vad:
            segments, info = transcriber.transcribe_with_vad(
                str(audio_path),
                beam_size=args.beam_size,
                language=args.language,
                word_timestamps=args.word_timestamps,
                temperature=args.temperature,
                compression_ratio_threshold=args.compression_ratio_threshold,
                log_prob_threshold=args.log_prob_threshold,
                no_speech_threshold=args.no_speech_threshold,
                initial_prompt=args.initial_prompt,
                hotwords=args.hotwords,
                task=args.task
            )
        else:
            segments, info = transcriber.transcribe_file(
                str(audio_path),
                beam_size=args.beam_size,
                language=args.language,
                word_timestamps=args.word_timestamps,
                temperature=args.temperature,
                compression_ratio_threshold=args.compression_ratio_threshold,
                log_prob_threshold=args.log_prob_threshold,
                no_speech_threshold=args.no_speech_threshold,
                initial_prompt=args.initial_prompt,
                hotwords=args.hotwords,
                task=args.task
            )
        
        if args.verbose:
            print(f"Transcription completed. Found {len(segments)} segments.")
            print(f"Language: {info.language} (confidence: {info.language_probability:.3f})")
            print(f"Audio duration: {info.duration:.2f}s")
        
    except Exception as e:
        print(f"Error during transcription: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Output results
    try:
        if args.format == "srt":
            format_as_srt(segments, args.output, args.word_timestamps)
        elif args.format == "vtt":
            format_as_vtt(segments, args.output, args.word_timestamps)
        else:  # text format
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    for segment in segments:
                        confidence_str = f" (conf: {segment.confidence:.3f})" if args.show_confidence and segment.confidence else ""
                        f.write(f"[{segment.start:.2f}s -> {segment.end:.2f}s]{confidence_str} {segment.text}\n")
                        
                        if args.show_words and segment.words:
                            f.write("  Words: ")
                            for word in segment.words:
                                f.write(f"{word.word}[{word.start:.1f}-{word.end:.1f}]({word.probability:.2f}) ")
                            f.write("\n")
            else:
                transcriber.print_transcription(segments, args.show_confidence, args.show_words)
        
        if args.verbose and args.output:
            print(f"Transcription saved to: {args.output}")
            
    except Exception as e:
        print(f"Error saving output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 