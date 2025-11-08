# TalkLabs STT SDK

SDK Python para TalkLabs Speech-to-Text API - Compatível com 

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## Features

- ✅ **REST API** - Transcrição completa de arquivos
- ✅ **WebSocket Streaming** - Transcrição em tempo real
- ✅ **Deepgram Compatible** - API compatível com Deepgram
- ✅ **Múltiplos Modelos** - Suporte a diferentes modelos de transcrição
- ✅ **Async Support** - WebSocket assíncrono
- ✅ **Type Hints** - Totalmente tipado

## Instalação

```bash
pip install talklabs-stt
```

## Quick Start

### REST API (Síncrono)

```python
from talklabs_stt import STTClient

client = STTClient(api_key="tlk_live_xxxxx")

result = client.transcribe_file("audio.wav")
print(result["results"]["channels"][0]["alternatives"][0]["transcript"])
```

### WebSocket Streaming (Assíncrono)

```python
import asyncio
from talklabs_stt import STTClient

async def main():
    client = STTClient(api_key="tlk_live_xxxxx")

    def on_transcript(data):
        transcript = data["channel"]["alternatives"][0]["transcript"]
        if data["is_final"]:
            print(transcript)

    await client.transcribe_stream(
        "audio.wav",
        on_transcript=on_transcript
    )

asyncio.run(main())
```

## Uso Completo

### Inicialização

```python
from talklabs_stt import STTClient, TranscriptionOptions

# Cliente (sempre usa api.talklabs.com.br)
client = STTClient(api_key="tlk_live_xxxxx")

# Cliente com timeout customizado
client = STTClient(
    api_key="tlk_live_xxxxx",
    timeout=600  # 10 minutos
)
```

### Opções de Transcrição

```python
from talklabs_stt import TranscriptionOptions

options = TranscriptionOptions(
    model="large-v3",        # large-v3, medium, small
    language="pt",           # pt, en, es, etc.
    punctuate=True,          # Adicionar pontuação
    smart_format=True,       # Formatação inteligente
    detect_language=False,   # Detecção automática
    vad_filter=False,        # Filtro VAD
    interim_results=True     # Resultados intermediários (WebSocket)
)

result = client.transcribe_file("audio.wav", options=options)
```

### Com kwargs diretos

```python
result = client.transcribe_file(
    "audio.wav",
    model="large-v3",
    language="pt",
    punctuate=True,
    smart_format=True
)
```

## API Reference

### STTClient

#### `transcribe_file(audio_path, options=None, **kwargs)`

Transcreve arquivo completo via REST API.

**Args:**
- `audio_path` (str): Caminho do arquivo de áudio
- `options` (TranscriptionOptions, optional): Opções de transcrição
- `**kwargs`: Parâmetros adicionais

**Returns:** dict - Resultado -compatible

#### `transcribe_stream(audio_path, options=None, on_transcript=None, on_metadata=None, **kwargs)`

Transcreve via WebSocket streaming (async).

**Args:**
- `audio_path` (str): Caminho do arquivo
- `options` (TranscriptionOptions, optional): Opções
- `on_transcript` (callable, optional): Callback para transcrições
- `on_metadata` (callable, optional): Callback para metadata
- `**kwargs`: Parâmetros adicionais

#### `list_models()`

Lista modelos disponíveis.

**Returns:** dict - Lista de modelos disponíveis

## Migração do Deepgram

O SDK é 100% compatível com Deepgram. Para migrar:

```python
# Deepgram
from deepgram import DeepgramClient
dg = DeepgramClient(api_key)

# TalkLabs
from talklabs_stt import STTClient
client = STTClient(api_key)

# Mesma interface!
result = client.transcribe_file("audio.wav", language="pt")
```

## Exemplos

Ver pasta `examples/`:
- `transcribe_simple.py` - REST API básico
- `transcribe_stream.py` - WebSocket streaming
- `list_models.py` - Listar modelos
- `quick_start.py` - Exemplo rápido de uso

## Desenvolvimento

### Benchmark de Modelos

O projeto inclui um script de benchmark completo para testar todos os modelos:

```bash
# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Executar benchmark
python benchmark_models.py <arquivo_audio>

# Testar modelos específicos
python benchmark_models.py audio.wav --models tiny base medium

# Salvar relatório customizado
python benchmark_models.py audio.wav --output meu_relatorio.json
```

O benchmark testa:
- ✅ Velocidade de processamento (REST API e WebSocket)
- ✅ RTF (Real-Time Factor) de cada modelo
- ✅ Verifica se o servidor está **trocando os modelos corretamente**
- ✅ Gera relatórios visuais e JSON completo

Ver documentação completa em [BENCHMARK.md](BENCHMARK.md).

### Usando Makefile

O projeto inclui um Makefile para facilitar tarefas comuns:

```bash
# Verificação de código
make lint              # Verificar com flake8

# Build e publicação
make publish-test      # Publicar no TestPyPI
make publish           # Publicar no PyPI oficial

# Utilitários
make clean             # Limpar arquivos temporários
make help              # Ver todos os comandos
```

Para mais detalhes sobre desenvolvimento, ver [CONTRIBUTING.md](CONTRIBUTING.md).

## Troubleshooting

### Erro de autenticação

Verifique se a API key está correta e ativa.

### Timeout

Aumente o timeout:
```python
client = STTClient(api_key="...", timeout=600)
```

### Formato de áudio

Formatos suportados: WAV, MP3, FLAC, OGG, M4A

## License

MIT License - Ver LICENSE

## Support

- Email: support@talklabs.com.br
