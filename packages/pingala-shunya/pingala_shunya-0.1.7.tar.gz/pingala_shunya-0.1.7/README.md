# Pingala Shunya

A comprehensive speech transcription package by **Shunya Labs AI** supporting **ct2 (CTranslate2)** and **transformers** backends. Get superior transcription quality with unified API and advanced features.

## Overview

Pingala Shunya provides a unified interface for transcribing audio files using state-of-the-art backends optimized by Shunya Labs. Whether you want the high-performance CTranslate2 optimization or the flexibility of Hugging Face transformers, Pingala Shunya delivers exceptional results with the `shunyalabs/pingala-v1-en-verbatim` model.

## Features

- **Shunya Labs Optimized**: Built by Shunya Labs for superior performance
- **CT2 Backend**: High-performance CTranslate2 optimization (default)
- **Transformers Backend**: Hugging Face models and latest research
- **Auto-Detection**: Automatically selects the best backend for your model
- **Unified API**: Same interface across all backends
- **Word-Level Timestamps**: Precise timing for individual words
- **Confidence Scores**: Quality metrics for transcription segments and words
- **Voice Activity Detection (VAD)**: Filter out silence and background noise
- **Language Detection**: Automatic language identification
- **Multiple Output Formats**: Text, SRT subtitles, and WebVTT
- **Streaming Support**: Process segments as they are generated
- **Advanced Parameters**: Full control over all backend features
- **Rich CLI**: Command-line tool with comprehensive options
- **Error Handling**: Comprehensive error handling and validation

## Installation

### Standard Installation (All Backends Included)
```bash
pip install pingala-shunya
```

This installs all dependencies including:
- **faster-whisper** ≥ 0.10.0 (CT2 backend)
- **transformers** == 4.52.4 (Transformers backend)
- **ctranslate2** == 4.4.0 (GPU acceleration)
- **librosa** ≥ 0.10.0 (Audio processing)
- **torch** ≥ 1.9.0 & **torchaudio** ≥ 0.9.0 (PyTorch)
- **datasets** ≥ 2.0.0 & **numpy** ≥ 1.21.0

### Development Installation

```bash
# Complete installation with development tools
pip install "pingala-shunya[complete]"
```

This adds development tools: `pytest`, `black`, `flake8`, `mypy`

### Requirements

- Python 3.8 or higher
- CUDA-compatible GPU (recommended for optimal performance)
- PyTorch and torchaudio

Unlike other transcription tools, FFmpeg does **not** need to be installed on the system. The audio is decoded with the Python library [PyAV](https://github.com/PyAV-Org/PyAV) which bundles the FFmpeg libraries in its package.

### GPU Support and CUDA Installation

#### GPU Requirements

GPU execution requires the following NVIDIA libraries to be installed:

* [cuBLAS for CUDA 12](https://developer.nvidia.com/cublas)
* [cuDNN 9 for CUDA 12](https://developer.nvidia.com/cudnn)

**Important**: The latest versions of `ctranslate2` only support CUDA 12 and cuDNN 9. For CUDA 11 and cuDNN 8, downgrade to the `3.24.0` version of `ctranslate2`. For CUDA 12 and cuDNN 8, use `ctranslate2==4.4.0` (already included in pingala-shunya):

```bash
pip install --force-reinstall ctranslate2==4.4.0
```

#### CUDA Installation Methods

<details>
<summary>Method 1: Docker (Recommended)</summary>

The easiest way is to use the official NVIDIA CUDA Docker image:
```bash
docker run --gpus all -it nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04
pip install pingala-shunya
```
</details>

<details>
<summary>Method 2: pip Installation (Linux only)</summary>

Install CUDA libraries via pip:
```bash
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12==9.*

export LD_LIBRARY_PATH=`python3 -c 'import os; import nvidia.cublas.lib; import nvidia.cudnn.lib; print(os.path.dirname(nvidia.cublas.lib.__file__) + ":" + os.path.dirname(nvidia.cudnn.lib.__file__))'`
```
</details>

<details>
<summary>Method 3: Manual Download (Windows & Linux)</summary>

Download pre-built CUDA libraries from [Purfview's repository](https://github.com/Purfview/whisper-standalone-win/releases/tag/libs). Extract and add to your system PATH.
</details>

### Performance Benchmarks

Based on faster-whisper benchmarks transcribing 13 minutes of audio:

#### GPU Performance (NVIDIA RTX 3070 Ti 8GB)

| Backend | Precision | Beam size | Time | VRAM Usage |
| --- | --- | --- | --- | --- |
| transformers (SDPA) | fp16 | 5 | 1m52s | 4960MB |
| **faster-whisper (CT2)** | fp16 | 5 | **1m03s** | 4525MB |
| **faster-whisper (CT2)** (`batch_size=8`) | fp16 | 5 | **17s** | 6090MB |
| **faster-whisper (CT2)** | int8 | 5 | 59s | 2926MB |

#### CPU Performance (Intel Core i7-12700K, 8 threads)

| Backend | Precision | Beam size | Time | RAM Usage |
| --- | --- | --- | --- | --- |
| **faster-whisper (CT2)** | fp32 | 5 | 2m37s | 2257MB |
| **faster-whisper (CT2)** (`batch_size=8`) | fp32 | 5 | **1m06s** | 4230MB |
| **faster-whisper (CT2)** | int8 | 5 | 1m42s | 1477MB |

*Pingala Shunya delivers superior performance with optimized CTranslate2 backend and efficient memory usage.*

## Supported Backends

### ct2 (CTranslate2) - Default
- **Performance**: Fastest inference with CTranslate2 optimization
- **Features**: Full parameter control, VAD, streaming, GPU acceleration
- **Models**: All compatible models, optimized for Shunya Labs models
- **Best for**: Production use, real-time applications

### transformers  
- **Performance**: Good performance with Hugging Face ecosystem
- **Features**: Access to latest models, easy fine-tuning integration
- **Models**: Any Seq2Seq model on Hugging Face Hub
- **Best for**: Research, latest models, custom transformer models

## Supported Models

### Default Model
- `shunyalabs/pingala-v1-en-verbatim` - High-quality English transcription model by Shunya Labs

### Shunya Labs Models
- `shunyalabs/pingala-v1-en-verbatim` - Optimized for English verbatim transcription
- More Shunya Labs models coming soon!

### Custom Models (Advanced Users)
- Any Hugging Face Seq2Seq model compatible with automatic-speech-recognition pipeline
- Local model paths supported

### Local Models
- `/path/to/local/model` - Local model directory or file

## Quick Start

### Basic Usage with Auto-Detection

```python
from pingala_shunya import PingalaTranscriber

# Initialize with default Shunya Labs model and auto-detected backend
transcriber = PingalaTranscriber()

# Simple transcription
segments = transcriber.transcribe_file_simple("audio.wav")

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

### Backend Selection

```python
from pingala_shunya import PingalaTranscriber

# Explicitly choose backends with Shunya Labs model
transcriber_ct2 = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim", backend="ct2")
transcriber_tf = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim", backend="transformers")  

# Auto-detection (recommended)
transcriber_auto = PingalaTranscriber()  # Uses default Shunya Labs model with ct2
```

### Advanced Usage with All Features

```python
from pingala_shunya import PingalaTranscriber

# Initialize with specific backend and settings
transcriber = PingalaTranscriber(
    model_name="shunyalabs/pingala-v1-en-verbatim",
    backend="ct2",
    device="cuda", 
    compute_type="float16"
)

# Advanced transcription with full metadata
segments, info = transcriber.transcribe_file(
    "audio.wav",
    beam_size=10,                    # Higher beam size for better accuracy
    word_timestamps=True,            # Enable word-level timestamps
    temperature=0.0,                 # Deterministic output
    compression_ratio_threshold=2.4, # Filter out low-quality segments
    log_prob_threshold=-1.0,         # Filter by probability
    no_speech_threshold=0.6,         # Silence detection threshold
    initial_prompt="High quality audio recording",  # Guide the model
    hotwords="Python, machine learning, AI",        # Boost specific words
    vad_filter=True,                 # Enable voice activity detection
    task="transcribe"                # or "translate" for translation
)

# Print transcription info
model_info = transcriber.get_model_info()
print(f"Backend: {model_info['backend']}")
print(f"Model: {model_info['model_name']}")
print(f"Language: {info.language} (confidence: {info.language_probability:.3f})")
print(f"Duration: {info.duration:.2f} seconds")

# Process segments with all metadata
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
    if segment.confidence:
        print(f"Confidence: {segment.confidence:.3f}")
    
    # Word-level details
    for word in segment.words:
        print(f"  '{word.word}' [{word.start:.2f}-{word.end:.2f}s] (conf: {word.probability:.3f})")
```

### Using Transformers Backend

```python
# Use Shunya Labs model with transformers backend
transcriber = PingalaTranscriber(
    model_name="shunyalabs/pingala-v1-en-verbatim",
    backend="transformers"
)

segments = transcriber.transcribe_file_simple("audio.wav")

# Auto-detection will use ct2 by default for Shunya Labs models
transcriber = PingalaTranscriber()  # Uses ct2 backend (recommended)
```

## Command-Line Interface

The package includes a comprehensive CLI supporting both backends:

### Basic CLI Usage

```bash
# Basic transcription with auto-detected backend
pingala audio.wav

# Specify backend explicitly  
pingala audio.wav --backend ct2
pingala audio.wav --backend transformers

# Use Shunya Labs model with different backends
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --backend ct2
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --backend transformers

# Save to file
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim -o transcript.txt

# Use CPU for processing
pingala audio.wav --device cpu
```

### Advanced CLI Features

```bash
# Word-level timestamps with confidence scores (ct2)
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --word-timestamps --show-confidence --show-words

# Voice Activity Detection (ct2 only)
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --vad --verbose

# Language detection with different backends
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --detect-language --backend ct2

# SRT subtitles with word-level timing
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --format srt --word-timestamps -o subtitles.srt

# Transformers backend with Shunya Labs model
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --backend transformers --verbose

# Advanced parameters (ct2)
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim \
  --beam-size 10 \
  --temperature 0.2 \
  --compression-ratio-threshold 2.4 \
  --log-prob-threshold -1.0 \
  --initial-prompt "This is a technical presentation" \
  --hotwords "Python,AI,machine learning"
```

### CLI Options Reference

| Option | Description | Backends | Default |
|--------|-------------|----------|---------|
| `--model` | Model name or path | All | shunyalabs/pingala-v1-en-verbatim |
| `--backend` | Backend selection | All | auto-detect |
| `--device` | Device: cuda, cpu, auto | All | cuda |
| `--compute-type` | Precision: float16, float32, int8 | All | float16 |
| `--beam-size` | Beam size for decoding | All | 5 |
| `--language` | Language code (e.g., 'en') | All | auto-detect |
| `--word-timestamps` | Enable word-level timestamps | ct2 | False |
| `--show-confidence` | Show confidence scores | All | False |
| `--show-words` | Show word-level details | All | False |
| `--vad` | Enable VAD filtering | ct2 | False |
| `--detect-language` | Language detection only | All | False |
| `--format` | Output format: text, srt, vtt | All | text |
| `--temperature` | Sampling temperature | All | 0.0 |
| `--compression-ratio-threshold` | Compression ratio filter | ct2 | 2.4 |
| `--log-prob-threshold` | Log probability filter | ct2 | -1.0 |
| `--no-speech-threshold` | No speech threshold | All | 0.6 |
| `--initial-prompt` | Initial prompt text | All | None |
| `--hotwords` | Hotwords to boost | ct2 | None |
| `--task` | Task: transcribe, translate | All | transcribe |

## Backend Comparison

| Feature | ct2 | transformers |
|---------|-----|--------------|
| **Performance** | Fastest | Good |
| **GPU Acceleration** | Optimized | Standard |
| **Memory Usage** | Lowest | Moderate |
| **Model Support** | Any model | Any HF model |
| **Word Timestamps** | Full support | Limited |
| **VAD Filtering** | Built-in | No |
| **Streaming** | True streaming | Batch only |
| **Advanced Params** | All features | Basic |
| **Latest Models** | Updated | Latest |
| **Custom Models** | CTranslate2 | Any format |

### Recommendations

- **Production/Performance**: Use `ct2` with Shunya Labs models
- **Latest Research Models**: Use `transformers`
- **Real-time Applications**: Use `ct2` with VAD
- **Custom Transformer Models**: Use `transformers`

## Performance Optimization

### Backend Selection Tips

```python
# Real-time/Production: Use ct2 with Shunya Labs model
transcriber = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim", backend="ct2")

# Maximum accuracy: Use Shunya Labs model with ct2  
transcriber = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim", backend="ct2")

# Alternative backend: Use transformers with Shunya Labs model
transcriber = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim", backend="transformers")

# Research/Latest models: Use transformers backend
transcriber = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim", backend="transformers")
```

### Hardware Recommendations

| Use Case | Model | Backend | Hardware |
|----------|-------|---------|----------|
| Real-time | shunyalabs/pingala-v1-en-verbatim | ct2 | GPU 4GB+ |
| Production | shunyalabs/pingala-v1-en-verbatim | ct2 | GPU 6GB+ |
| Maximum Quality | shunyalabs/pingala-v1-en-verbatim | ct2 | GPU 8GB+ |
| Alternative | shunyalabs/pingala-v1-en-verbatim | transformers | GPU 4GB+ |
| CPU-only | shunyalabs/pingala-v1-en-verbatim | any | 8GB+ RAM |

### GPU Optimization

```python
# Maximum performance on GPU - FP16 precision
transcriber = PingalaTranscriber(
    model_name="shunyalabs/pingala-v1-en-verbatim",
    device="cuda",
    compute_type="float16"  # Fastest GPU performance
)

# Memory constrained GPU - INT8 quantization
transcriber = PingalaTranscriber(
    model_name="shunyalabs/pingala-v1-en-verbatim", 
    device="cuda",
    compute_type="int8_float16"  # Lower memory usage
)

# Batched processing for multiple files
segments, info = transcriber.transcribe_file(
    "audio.wav",
    batch_size=8,  # Process multiple segments in parallel
    beam_size=5
)
```

### CPU Optimization

```python
# Optimized CPU settings
transcriber = PingalaTranscriber(
    model_name="shunyalabs/pingala-v1-en-verbatim",
    device="cpu",
    compute_type="int8"  # Lower memory, faster on CPU
)

# Control CPU threads for best performance
import os
os.environ["OMP_NUM_THREADS"] = "4"  # Adjust based on your CPU
```

### Memory Optimization Tips

- **GPU VRAM**: Use `int8_float16` compute type to reduce memory usage by ~40%
- **System RAM**: Use `int8` compute type on CPU to reduce memory usage
- **Batch Size**: Increase batch size if you have sufficient memory for faster processing
- **Model Size**: Consider smaller models for memory-constrained environments

### Performance Comparison Tips

When comparing against other implementations:
- Use same beam size (default is 5 in pingala-shunya)
- Compare with similar Word Error Rate (WER)
- Set consistent thread count: `OMP_NUM_THREADS=4 python script.py`
- Ensure similar transcription quality metrics

## Troubleshooting

### Common CUDA Issues

**Issue**: `RuntimeError: No CUDA capable device found`
```bash
# Check CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# If False, install CUDA toolkit or use CPU
transcriber = PingalaTranscriber(device="cpu")
```

**Issue**: `CUDA out of memory`
```python
# Solution 1: Use INT8 quantization
transcriber = PingalaTranscriber(compute_type="int8_float16")

# Solution 2: Reduce batch size
segments, info = transcriber.transcribe_file("audio.wav", batch_size=1)

# Solution 3: Use CPU
transcriber = PingalaTranscriber(device="cpu")
```

**Issue**: `cuDNN/cuBLAS library not found`
```bash
# Install CUDA libraries via pip (Linux)
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12==9.*

# Or use Docker
docker run --gpus all -it nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04
```

**Issue**: `ctranslate2` version compatibility
```bash
# For CUDA 12 + cuDNN 8 (default in pingala-shunya)
pip install ctranslate2==4.4.0

# For CUDA 11 + cuDNN 8
pip install ctranslate2==3.24.0
```

### Model Loading Issues

**Issue**: Model download fails
```python
# Use local model path
transcriber = PingalaTranscriber(model_name="/path/to/local/model")

# Or specify different Shunya Labs model
transcriber = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim")
```

**Issue**: Alignment heads error (word timestamps)
```python
# This is handled automatically with fallback to no word timestamps
# Word timestamps are supported with Shunya Labs models
transcriber = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim")
segments, info = transcriber.transcribe_file("audio.wav", word_timestamps=True)
```

## Examples

See `example.py` for comprehensive examples:

```bash
# Run with default backend (auto-detected)
python example.py audio.wav

# Test specific backends with Shunya Labs model
python example.py audio.wav --backend ct2
python example.py audio.wav --backend transformers  

# Test Shunya Labs model with different backends
python example.py audio.wav shunyalabs/pingala-v1-en-verbatim
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built by [Shunya Labs](https://shunyalabs.ai) for superior transcription quality
- Powered by CTranslate2 for optimized inference
- Supports [Hugging Face transformers](https://github.com/huggingface/transformers) 
- Uses the Pingala model from [Shunya Labs](https://shunyalabs.ai)

## About Shunya Labs

Visit [Shunya Labs](https://shunyalabs.ai) to learn more about our AI research and products. 
Contact us at [0@shunyalabs.ai](mailto:0@shunyalabs.ai) for questions or collaboration opportunities. 
