# Changelog

## [1.0.0] - 2025-11-07

### Added
- **First Official Release**: Shunya Labs is now officially released as v1.0.0
- Complete speech transcription package with CT2 and Transformers backends
- Unified API for transcribing audio files with state-of-the-art models
- Support for `shunyalabs/pingala-v1-en-verbatim` model by default
- Word-level timestamps with precise timing for individual words
- Confidence scores for transcription quality assessment
- Voice Activity Detection (VAD) for filtering silence and background noise
- Automatic language detection and identification
- Multiple output formats: Text, SRT subtitles, and WebVTT
- Streaming support for processing segments as they are generated
- Advanced parameter control for fine-tuning transcription
- Rich command-line interface with comprehensive options
- Comprehensive error handling and validation
- Auto-detection of optimal backend for each model

### Backend Features
- **CT2 Backend**: High-performance CTranslate2 optimization (default)
  - Fastest inference with GPU acceleration
  - Full parameter control and VAD support
  - True streaming transcription
  - Optimized for production use
  
- **Transformers Backend**: Hugging Face models and latest research
  - Access to latest models and research
  - Easy fine-tuning integration
  - Any Seq2Seq model on Hugging Face Hub

### Performance
- GPU optimization with FP16/INT8 quantization support
- CPU optimization with multi-threading control
- Efficient memory usage and batch processing
- Performance benchmarks and optimization tips

### Documentation
- Comprehensive README with installation instructions
- Quick start guide with examples
- Backend comparison and recommendations
- Troubleshooting guide for common issues
- Hardware recommendations for different use cases

### CLI Features
- `shunyalabs` command-line tool
- Support for all backends and advanced parameters
- Multiple output formats (text, SRT, VTT)
- Language detection mode
- Word-level timestamp display
- Confidence score visualization

### Developer Experience
- Clean, unified API across all backends
- Type hints and comprehensive docstrings
- Development dependencies (pytest, black, flake8, mypy)
- Example scripts demonstrating all features

### Package Information
- Package name: `shunyalabs`
- Module name: `shunyalabs`
- CLI command: `shunyalabs`
- Version: 1.0.0
- License: MIT
- Python support: 3.8+

### Installation
- Available via pip: `pip install shunyalabs`
- Optional dependencies for complete installation
- Docker support with CUDA libraries
