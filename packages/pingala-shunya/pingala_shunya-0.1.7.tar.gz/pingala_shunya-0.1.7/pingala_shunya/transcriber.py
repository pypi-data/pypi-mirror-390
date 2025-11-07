"""
Pingala Transcriber module for speech-to-text transcription.
Supports multiple backends: ct2 (CTranslate2), transformers.
Developed by Shunya Labs.
"""

from typing import List, Tuple, Optional, Iterator, Dict, Any, Union
from abc import ABC, abstractmethod
import os
import warnings


class WordSegment:
    """Represents a word-level transcription segment with timing and confidence."""
    
    def __init__(self, word: str, start: float, end: float, probability: float):
        self.word = word
        self.start = start
        self.end = end
        self.probability = probability
    
    def __str__(self) -> str:
        return f"{self.word}[{self.start:.2f}-{self.end:.2f}]({self.probability:.2f})"
    
    def __repr__(self) -> str:
        return f"WordSegment(word='{self.word}', start={self.start}, end={self.end}, probability={self.probability})"


class TranscriptionSegment:
    """Represents a transcription segment with timing information and metadata."""
    
    def __init__(
        self, 
        start: float, 
        end: float, 
        text: str,
        words: Optional[List[WordSegment]] = None,
        avg_logprob: Optional[float] = None,
        no_speech_prob: Optional[float] = None,
        compression_ratio: Optional[float] = None,
        temperature: Optional[float] = None
    ):
        self.start = start
        self.end = end
        self.text = text
        self.words = words or []
        self.avg_logprob = avg_logprob
        self.no_speech_prob = no_speech_prob
        self.compression_ratio = compression_ratio
        self.temperature = temperature
    
    @property
    def confidence(self) -> Optional[float]:
        """Calculate confidence score from average log probability."""
        if self.avg_logprob is not None:
            import math
            return math.exp(self.avg_logprob)
        return None
    
    def __str__(self) -> str:
        return f"[{self.start:.2f}s -> {self.end:.2f}s] {self.text}"
    
    def __repr__(self) -> str:
        return f"TranscriptionSegment(start={self.start}, end={self.end}, text='{self.text}', confidence={self.confidence})"


class TranscriptionInfo:
    """Contains metadata about the transcription process."""
    
    def __init__(
        self,
        language: str,
        language_probability: float,
        duration: float,
        duration_after_vad: float,
        all_language_probs: Optional[List[Tuple[str, float]]] = None
    ):
        self.language = language
        self.language_probability = language_probability
        self.duration = duration
        self.duration_after_vad = duration_after_vad
        self.all_language_probs = all_language_probs or []
    
    def __repr__(self) -> str:
        return f"TranscriptionInfo(language='{self.language}', confidence={self.language_probability:.3f}, duration={self.duration:.2f}s)"


class TranscriptionBackend(ABC):
    """Abstract base class for transcription backends."""
    
    @abstractmethod
    def load_model(self, model_name: str, device: str, compute_type: str, **kwargs):
        """Load the model."""
        pass
    
    @abstractmethod
    def transcribe(
        self, 
        audio_path: str, 
        **kwargs
    ) -> Tuple[List[TranscriptionSegment], TranscriptionInfo]:
        """Transcribe audio file."""
        pass
    
    @abstractmethod
    def detect_language(self, audio_path: str) -> TranscriptionInfo:
        """Detect language of audio file."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        pass


class CT2Backend(TranscriptionBackend):
    """Backend using CTranslate2 for optimized inference."""
    
    def __init__(self):
        self.model = None
        self.model_name = None
        self.device = None
        self.compute_type = None
    
    def load_model(self, model_name: str, device: str, compute_type: str, **kwargs):
        """Load CTranslate2 model via faster-whisper."""
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(model_name, device=device, compute_type=compute_type)
            self.model_name = model_name
            self.device = device
            self.compute_type = compute_type
        except ImportError:
            raise RuntimeError("CTranslate2 backend not available. Install with: pip install faster-whisper")
        except Exception as e:
            raise RuntimeError(f"Failed to load CTranslate2 model '{model_name}': {e}")
    
    def transcribe(
        self, 
        audio_path: str,
        beam_size: int = 5,
        word_timestamps: bool = False,
        language: Optional[str] = None,
        **kwargs
    ) -> Tuple[List[TranscriptionSegment], TranscriptionInfo]:
        """Transcribe using CTranslate2."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=beam_size,
                word_timestamps=word_timestamps,
                language=language,
                **kwargs
            )
        except IndexError as e:
            # Handle language detection failure - fallback to English
            if language is None:
                warnings.warn(
                    f"Language detection failed for audio file '{audio_path}'. "
                    "This can happen with very short audio, silent audio, or corrupted files. "
                    "Falling back to English. You can specify language explicitly (e.g., language='en') to avoid this warning.",
                    UserWarning
                )
                try:
                    segments, info = self.model.transcribe(
                        audio_path,
                        beam_size=beam_size,
                        word_timestamps=word_timestamps,
                        language="en",  # Fallback to English
                        **kwargs
                    )
                except Exception as fallback_error:
                    raise RuntimeError(
                        f"Transcription failed for audio file '{audio_path}'. "
                        f"Language detection failed and fallback to English also failed: {fallback_error}. "
                        "Please check if the audio file is valid and not corrupted."
                    )
            else:
                # Re-raise if language was explicitly specified
                raise RuntimeError(f"Transcription failed for audio file '{audio_path}' with specified language '{language}': {e}")
        except RuntimeError as e:
            # Handle alignment heads error for word timestamps
            if "alignment_heads" in str(e) and word_timestamps:
                warnings.warn(
                    f"Word-level timestamps not supported by this model ('{self.model_name}'). "
                    "The model lacks 'alignment_heads' configuration. "
                    "Falling back to transcription without word timestamps. "
                    "To get word timestamps, use a model that supports them (e.g., 'openai/whisper-tiny').",
                    UserWarning
                )
                # Retry without word timestamps
                segments, info = self.model.transcribe(
                    audio_path,
                    beam_size=beam_size,
                    word_timestamps=False,  # Disable word timestamps
                    language=language,
                    **kwargs
                )
            else:
                raise RuntimeError(f"Transcription failed for audio file '{audio_path}': {e}")
        except Exception as e:
            raise RuntimeError(f"Transcription failed for audio file '{audio_path}': {e}")
        
        result = []
        try:
            for segment in segments:
                words = []
                if word_timestamps and hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        words.append(WordSegment(
                            word=word.word,
                            start=word.start,
                            end=word.end,
                            probability=word.probability
                        ))
                
                result.append(TranscriptionSegment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text,
                    words=words,
                    avg_logprob=getattr(segment, 'avg_logprob', None),
                    no_speech_prob=getattr(segment, 'no_speech_prob', None),
                    compression_ratio=getattr(segment, 'compression_ratio', None),
                    temperature=getattr(segment, 'temperature', None)
                ))
        except RuntimeError as e:
            # Handle alignment heads error during segment processing
            if "alignment_heads" in str(e) and word_timestamps:
                warnings.warn(
                    f"Word-level timestamps failed during processing for model '{self.model_name}'. "
                    "Retrying without word timestamps.",
                    UserWarning
                )
                # Retry the entire transcription without word timestamps
                return self.transcribe(
                    audio_path,
                    beam_size=beam_size,
                    word_timestamps=False,  # Disable word timestamps
                    language=language,
                    **kwargs
                )
            else:
                raise
        
        transcription_info = TranscriptionInfo(
            language=info.language,
            language_probability=info.language_probability,
            duration=info.duration,
            duration_after_vad=info.duration_after_vad
        )
        
        return result, transcription_info
    
    def detect_language(self, audio_path: str) -> TranscriptionInfo:
        """Detect language using CTranslate2."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        segments, info = self.model.transcribe(audio_path, beam_size=1)
        list(segments)  # Consume generator to populate info
        
        return TranscriptionInfo(
            language=info.language,
            language_probability=info.language_probability,
            duration=info.duration,
            duration_after_vad=info.duration_after_vad
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get CTranslate2 model info."""
        return {
            "backend": "ct2",
            "model_name": self.model_name,
            "device": self.device,
            "compute_type": self.compute_type,
            "model_size_in_memory": getattr(self.model, "model_size_in_memory", "Unknown") if self.model else None
        }


class TransformersBackend(TranscriptionBackend):
    """Backend using Hugging Face transformers library."""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.model_name = None
        self.device = None
    
    def load_model(self, model_name: str, device: str, compute_type: str, **kwargs):
        """Load transformers model."""
        try:
            from transformers import WhisperForConditionalGeneration, WhisperProcessor
            import torch
            
            self.model_name = model_name
            self.device = device
            
            # Load model and processor using Whisper-specific classes
            self.model = WhisperForConditionalGeneration.from_pretrained(model_name)
            self.processor = WhisperProcessor.from_pretrained(model_name)
            
            # Move model to device
            device_obj = torch.device(device if device == "cuda" and torch.cuda.is_available() else "cpu")
            self.model = self.model.to(device_obj)
            
        except ImportError:
            raise RuntimeError("transformers backend not available. Install with: pip install transformers torch librosa")
        except Exception as e:
            raise RuntimeError(f"Failed to load transformers model '{model_name}': {e}")
    
    def transcribe(
        self, 
        audio_path: str,
        beam_size: int = 5,
        word_timestamps: bool = False,
        language: Optional[str] = None,
        **kwargs
    ) -> Tuple[List[TranscriptionSegment], TranscriptionInfo]:
        """Transcribe using transformers."""
        if self.model is None or self.processor is None:
            raise RuntimeError("Model not loaded")
        
        try:
            import torch
            import librosa
            from transformers import pipeline
            import numpy as np
            
            # Load and preprocess audio with librosa first to handle various formats
            try:
                audio, sr = librosa.load(audio_path, sr=16000)
                duration = len(audio) / sr
                
                # Ensure audio is not empty
                if len(audio) == 0:
                    raise ValueError("Audio file appears to be empty or corrupted")
                
            except Exception as audio_error:
                raise RuntimeError(
                    f"Failed to load audio file '{audio_path}'. "
                    f"Supported formats: wav, mp3, flac, ogg, opus, m4a. "
                    f"Error: {audio_error}"
                )
            
            # Create pipeline with explicit tokenizer and feature_extractor
            pipe = pipeline(
                "automatic-speech-recognition",
                model=self.model,
                tokenizer=self.processor.tokenizer,
                feature_extractor=self.processor.feature_extractor,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device=torch.device(self.device if self.device == "cuda" and torch.cuda.is_available() else "cpu"),
            )
            
            # Process the preprocessed audio array instead of file path
            result = pipe(audio)
            
            # Process results
            segments = []
            if "chunks" in result:
                for chunk in result["chunks"]:
                    segments.append(TranscriptionSegment(
                        start=chunk["timestamp"][0] if chunk["timestamp"][0] is not None else 0.0,
                        end=chunk["timestamp"][1] if chunk["timestamp"][1] is not None else duration,
                        text=chunk["text"].strip(),
                        words=[],  # Transformers doesn't provide word-level timestamps by default
                        avg_logprob=None,
                        no_speech_prob=None,
                        compression_ratio=None,
                        temperature=None
                    ))
            else:
                # Single segment result
                segments.append(TranscriptionSegment(
                    start=0.0,
                    end=duration,
                    text=result["text"].strip(),
                    words=[],
                    avg_logprob=None,
                    no_speech_prob=None,
                    compression_ratio=None,
                    temperature=None
                ))
            
            # Create transcription info
            transcription_info = TranscriptionInfo(
                language=language or "unknown",
                language_probability=1.0,
                duration=duration,
                duration_after_vad=duration
            )
            
            return segments, transcription_info
            
        except ImportError as e:
            raise RuntimeError(f"Missing dependencies for transformers backend: {e}")
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")
    
    def detect_language(self, audio_path: str) -> TranscriptionInfo:
        """Detect language using transformers (basic implementation)."""
        try:
            import librosa
            
            audio, sr = librosa.load(audio_path, sr=16000)
            duration = len(audio) / sr
            
            # Basic language detection (could be enhanced with dedicated models)
            return TranscriptionInfo(
                language="unknown",
                language_probability=0.5,
                duration=duration,
                duration_after_vad=duration
            )
        except Exception as e:
            raise RuntimeError(f"Language detection failed: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get transformers model info."""
        return {
            "backend": "transformers",
            "model_name": self.model_name,
            "device": self.device,
            "compute_type": "auto",
            "model_size_in_memory": "Unknown"
        }


def _detect_model_backend(model_name: str, backend: Optional[str] = None) -> str:
    """Auto-detect appropriate backend for a model."""
    if backend:
        return backend
    
    # Check if it's a Hugging Face model path
    if "/" in model_name and not model_name.startswith("./") and not model_name.startswith("/"):
        # Check if it's Shunya Labs model (use ct2 for optimal performance)
        if "shunyalabs" in model_name.lower():
            return "ct2"
        # Other HF models use transformers
        return "transformers"
    
    # Default to ct2 for maximum performance
    return "ct2"


class PingalaTranscriber:
    """
    Speech transcription class by Shunya Labs.
    
    This class provides a unified interface for transcribing audio files using
    different backends: ct2 (CTranslate2) and transformers.
    Optimized for Shunya Labs models with superior performance.
    """
    
    DEFAULT_MODEL_NAME = "shunyalabs/pingala-v1-en-verbatim"
    
    def __init__(
        self, 
        model_name: Optional[str] = None,
        device: str = "cuda", 
        compute_type: str = "float16",
        backend: Optional[str] = None
    ):
        """
        Initialize the Pingala transcriber by Shunya Labs.
        
        Args:
            model_name (str, optional): Name/path of the model to use.
                Defaults to "shunyalabs/pingala-v1-en-verbatim".
                Can be:
                - Shunya Labs models: "shunyalabs/pingala-v1-en-verbatim"
                - Custom Hugging Face models (as needed)
                - Local model paths: "/path/to/local/model"
            device (str): Device ("cuda", "cpu", "auto")  
            compute_type (str): Precision ("float16", "float32", "int8")
            backend (str, optional): Backend ("ct2", "transformers"). Auto-detects if None.
        """
        self.model_name = model_name or self.DEFAULT_MODEL_NAME
        self.device = device
        self.compute_type = compute_type
        
        # Detect or set backend
        self.backend_name = _detect_model_backend(self.model_name, backend)
        
        # Initialize backend
        if self.backend_name == "ct2":
            self.backend = CT2Backend()
        elif self.backend_name == "transformers":
            self.backend = TransformersBackend()
        else:
            raise ValueError(f"Unsupported backend: {self.backend_name}. Supported: ct2, transformers")
        
        # Load model
        try:
            self.backend.load_model(self.model_name, device, compute_type)
        except Exception as e:
            # Fallback to ct2 if model loading fails with transformers
            if self.backend_name == "transformers":
                warnings.warn(f"Failed to load with transformers backend: {e}. Falling back to ct2.")
                self.backend_name = "ct2"
                self.backend = CT2Backend()
                self.backend.load_model(self.model_name, device, compute_type)
            else:
                raise
    
    def detect_language(self, audio_path: str) -> TranscriptionInfo:
        """
        Detect the language of an audio file.
        
        Args:
            audio_path (str): Path to the audio file
        
        Returns:
            TranscriptionInfo: Language detection information
        
        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If language detection fails
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        return self.backend.detect_language(audio_path)
    
    def transcribe_file(
        self,
        audio_path: str,
        beam_size: int = 5,
        best_of: Optional[int] = None,
        patience: float = 1.0,
        length_penalty: float = 1.0,
        repetition_penalty: float = 1.0,
        no_repeat_ngram_size: int = 0,
        temperature: Union[float, List[float], Tuple[float, ...]] = 0.0,
        compression_ratio_threshold: Optional[float] = 2.4,
        log_prob_threshold: Optional[float] = -1.0,
        no_speech_threshold: Optional[float] = 0.6,
        condition_on_previous_text: bool = True,
        prompt_reset_on_temperature: float = 0.5,
        initial_prompt: Optional[str] = None,
        prefix: Optional[str] = None,
        suppress_blank: bool = True,
        suppress_tokens: Optional[List[int]] = [-1],
        without_timestamps: bool = False,
        max_initial_timestamp: float = 0.0,
        word_timestamps: bool = False,
        prepend_punctuations: str = "\"'([{-",
        append_punctuations: str = "\"'.。,，!！?？:：\")]}",
        vad_filter: bool = False,
        vad_parameters: Optional[Dict[str, Any]] = None,
        language: Optional[str] = None,
        task: str = "transcribe",
        hotwords: Optional[str] = None,
        hallucination_silence_threshold: Optional[float] = None
    ) -> Tuple[List[TranscriptionSegment], TranscriptionInfo]:
        """
        Transcribe an audio file with full control over parameters.
        Note: Not all parameters are supported by all backends.
        
        Args:
            audio_path (str): Path to the audio file
            beam_size (int): Beam size for decoding (default: 5)
            word_timestamps (bool): Include word-level timestamps (default: False)
            language (str, optional): Language code (e.g., "en")
            task (str): Task type - "transcribe" or "translate" (default: "transcribe")
            [Additional parameters for ct2 backend]
        
        Returns:
            Tuple[List[TranscriptionSegment], TranscriptionInfo]: Transcription segments and info
        
        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If transcription fails
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Prepare parameters (backend will filter out unsupported ones)
        params = {
            "beam_size": beam_size,
            "best_of": best_of,
            "patience": patience,
            "length_penalty": length_penalty,
            "repetition_penalty": repetition_penalty,
            "no_repeat_ngram_size": no_repeat_ngram_size,
            "temperature": temperature,
            "compression_ratio_threshold": compression_ratio_threshold,
            "log_prob_threshold": log_prob_threshold,
            "no_speech_threshold": no_speech_threshold,
            "condition_on_previous_text": condition_on_previous_text,
            "prompt_reset_on_temperature": prompt_reset_on_temperature,
            "initial_prompt": initial_prompt,
            "prefix": prefix,
            "suppress_blank": suppress_blank,
            "suppress_tokens": suppress_tokens,
            "without_timestamps": without_timestamps,
            "max_initial_timestamp": max_initial_timestamp,
            "word_timestamps": word_timestamps,
            "prepend_punctuations": prepend_punctuations,
            "append_punctuations": append_punctuations,
            "vad_filter": vad_filter,
            "vad_parameters": vad_parameters or {},
            "language": language,
            "task": task,
            "hotwords": hotwords,
            "hallucination_silence_threshold": hallucination_silence_threshold
        }
        
        return self.backend.transcribe(audio_path, **params)
    
    def transcribe_file_simple(
        self,
        audio_path: str,
        beam_size: int = 5,
        language: Optional[str] = None,
        word_timestamps: bool = False
    ) -> List[TranscriptionSegment]:
        """
        Simple transcription method for backward compatibility.
        
        Args:
            audio_path (str): Path to the audio file
            beam_size (int): Beam size for decoding (default: 5)
            language (str, optional): Language code (e.g., "en")
            word_timestamps (bool): Include word-level timestamps (default: False)
        
        Returns:
            List[TranscriptionSegment]: List of transcription segments
        """
        segments, _ = self.transcribe_file(
            audio_path,
            beam_size=beam_size,
            language=language,
            word_timestamps=word_timestamps
        )
        return segments
    
    def transcribe_with_word_timestamps(
        self,
        audio_path: str,
        beam_size: int = 5,
        language: Optional[str] = None,
        **kwargs
    ) -> Tuple[List[TranscriptionSegment], TranscriptionInfo]:
        """
        Transcribe with word-level timestamps enabled.
        
        Args:
            audio_path (str): Path to the audio file
            beam_size (int): Beam size for decoding (default: 5)
            language (str, optional): Language code (e.g., "en")
            **kwargs: Additional transcription parameters
        
        Returns:
            Tuple[List[TranscriptionSegment], TranscriptionInfo]: Segments with word timestamps and info
        """
        return self.transcribe_file(
            audio_path,
            beam_size=beam_size,
            language=language,
            word_timestamps=True,
            **kwargs
        )
    
    def transcribe_file_generator(
        self,
        audio_path: str,
        beam_size: int = 5,
        language: Optional[str] = None,
        word_timestamps: bool = False,
        **kwargs
    ) -> Iterator[TranscriptionSegment]:
        """
        Transcribe an audio file and yield segments as they are processed.
        Note: Only ct2 backend supports true streaming.
        
        Args:
            audio_path (str): Path to the audio file
            beam_size (int): Beam size for decoding (default: 5)
            language (str, optional): Language code (e.g., "en")
            word_timestamps (bool): Include word-level timestamps (default: False)
            **kwargs: Additional transcription parameters
        
        Yields:
            TranscriptionSegment: Transcription segments as they are processed
        """
        segments, _ = self.transcribe_file(
            audio_path,
            beam_size=beam_size,
            language=language,
            word_timestamps=word_timestamps,
            **kwargs
        )
        
        for segment in segments:
            yield segment
    
    def transcribe_with_vad(
        self,
        audio_path: str,
        beam_size: int = 5,
        language: Optional[str] = None,
        vad_parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[List[TranscriptionSegment], TranscriptionInfo]:
        """
        Transcribe with Voice Activity Detection (VAD) filtering.
        Note: Only supported by ct2 backend.
        
        Args:
            audio_path (str): Path to the audio file
            beam_size (int): Beam size for decoding (default: 5)
            language (str, optional): Language code (e.g., "en")
            vad_parameters (dict, optional): VAD configuration parameters
            **kwargs: Additional transcription parameters
        
        Returns:
            Tuple[List[TranscriptionSegment], TranscriptionInfo]: Filtered segments and info
        """
        if self.backend_name != "ct2":
            warnings.warn(f"VAD filtering not supported by {self.backend_name} backend. Proceeding without VAD.")
            return self.transcribe_file(
                audio_path,
                beam_size=beam_size,
                language=language,
                **kwargs
            )
        
        default_vad_params = {
            "threshold": 0.5,
            "min_speech_duration_ms": 250,
            "max_speech_duration_s": float("inf"),
            "min_silence_duration_ms": 2000,
            "window_size_samples": 1024,
            "speech_pad_ms": 400
        }
        
        if vad_parameters:
            default_vad_params.update(vad_parameters)
        
        return self.transcribe_file(
            audio_path,
            beam_size=beam_size,
            language=language,
            vad_filter=True,
            vad_parameters=default_vad_params,
            **kwargs
        )
    
    def print_transcription(self, segments: List[TranscriptionSegment], show_confidence: bool = False, show_words: bool = False):
        """
        Print transcription segments in a formatted way.
        
        Args:
            segments (List[TranscriptionSegment]): List of transcription segments
            show_confidence (bool): Show confidence scores (default: False)
            show_words (bool): Show word-level timestamps (default: False)
        """
        for segment in segments:
            confidence_str = f" (conf: {segment.confidence:.3f})" if show_confidence and segment.confidence else ""
            print(f"[{segment.start:6.2f}s -> {segment.end:6.2f}s]{confidence_str} {segment.text}")
            
            if show_words and segment.words:
                print("  Words:", end=" ")
                for word in segment.words:
                    print(f"{word.word}[{word.start:.1f}-{word.end:.1f}]({word.probability:.2f})", end=" ")
                print()  # New line after words
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model and backend.
        
        Returns:
            Dict[str, Any]: Model and backend information
        """
        return self.backend.get_model_info() 