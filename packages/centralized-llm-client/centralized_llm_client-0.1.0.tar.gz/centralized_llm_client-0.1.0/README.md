# Centralized-LLM-Client

Unified Python client for interacting with multiple LLM providers (OpenAI, Gemini, OpenRouter) with automatic fallback, secure key management, file handling, and MongoDB logging.

## Features
- Automatic provider fallback (OpenAI, Gemini, OpenRouter)
- Secure API key management (encrypted, MongoDB Atlas)
- File handling: supports local, S3, and FastAPI UploadFile
- Detailed logging of all LLM calls to MongoDB Atlas
- S3 integration for file storage/retrieval

## Installation

Python 3.9+ required.

```bash
pip install Centralized-LLM-Client
# Or, for local development:
pip install -r src/requirements.txt
```

## Quickstart

```python
from src.CentralizedClient import CentralizedLLMClient
client = CentralizedLLMClient(username="alice")
response = await client.completion("Summarize this document.")
```

## Architecture

- **src/CentralizedClient/CentralizedLLMClient.py**: Main orchestration, provider fallback logic
- **Providers**: `gemini_provider.py`, `openai_provider.py`, `openrouter_provider.py` (wrap LLM APIs)
- **Key Management**: `key_manager.py` (encrypted keys, user/system fallback)
- **File Handling**: `file_processor.py` (temp files, S3/local/FastAPI)
- **Logging**: `llm_logger.py` (MongoDB Atlas logging)
- **External Integrations**: S3 (`utils/s3_file_manager.py`), MongoDB Atlas (`utils/atlas_client.py`)

## Environment Setup

- Set environment variables for S3, MongoDB Atlas, and LLM provider keys (see `.env` usage in utils)
- Place `key.bin` (encryption key) in project root for key decryption

## Testing

- Add tests in `tests/` and run with pytest:
	```bash
	pytest tests/
	```

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

MIT License