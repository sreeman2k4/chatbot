# Ollama Setup Guide

This project is configured to use Ollama as the local LLM provider. Follow these steps to get it running:

## 1. Install Ollama

### Windows
1. Download from [https://ollama.ai](https://ollama.ai)
2. Run the installer
3. Ollama will start automatically as a Windows service

### macOS
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## 2. Start Ollama Service

### Windows
- Ollama starts automatically as a Windows service
- You can also start it manually from the Start menu

### macOS/Linux
```bash
ollama serve
```

## 3. Pull a Model

Pull at least one model to get started:

```bash
# Pull the default Llama2 model (recommended)
ollama pull llama2

# Or try other models
ollama pull mistral
ollama pull codellama
```

## 4. Verify Installation

Check if Ollama is running:

```bash
# Check service status
ollama list

# Test API endpoint
curl http://localhost:11434/api/tags
```

## 5. Start the Project

Now you can start the development environment:

### Windows
```bash
start-dev.bat
```

### macOS/Linux
```bash
./start-dev.sh
```

## 6. Test the Backend

Once running, test the Ollama integration:

- **Health Check**: `http://localhost:8000/api/health`
- **Ollama Status**: `http://localhost:8000/api/ollama/status`
- **Available Models**: `http://localhost:8000/api/models`

## Troubleshooting

### Ollama Service Not Running
- Check if Ollama is installed correctly
- Restart the Ollama service
- Verify port 11434 is not blocked by firewall

### No Models Available
- Run `ollama pull llama2` to download a model
- Check `ollama list` to see available models

### Connection Errors
- Ensure Ollama is running on `http://localhost:11434`
- Check if the service is accessible via `curl http://localhost:11434/api/tags`

## Model Recommendations

- **llama2**: Good general-purpose model, balanced performance
- **mistral**: Fast and efficient, good for chat
- **codellama**: Specialized for code generation
- **llama2:13b**: Higher quality but slower than 7b versions

## Performance Tips

- Use smaller models (7B) for faster responses
- Use larger models (13B+) for better quality
- Ensure you have sufficient RAM (at least 8GB for 7B models)
- GPU acceleration available for supported models
