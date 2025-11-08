# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-11-04

### Changed
- **BREAKING**: Removido parâmetro `base_url` do construtor `STTClient`
- Base URL agora é fixo: `https://api.talklabs.com.br/api/stt`
- Simplificação da API para evitar confusão e garantir uso correto do API Gateway

### Migration Guide
```python
# Antes (v1.0.0)
client = STTClient(api_key="key", base_url="https://api.talklabs.com.br/api/stt")

# Agora (v1.0.1)
client = STTClient(api_key="key")  # base_url é fixo
```

## [1.0.0] - 2025-11-04

### Added
- ✨ Initial release
- REST API support para transcrição completa
- WebSocket streaming para transcrição em tempo real
- Compatibilidade com Deepgram API
- Suporte a múltiplos modelos de transcrição (large-v3, medium, small)
- Dataclass `TranscriptionOptions` para configuração
- Métodos `health_check()` e `list_models()`
- Documentação completa e exemplos
- Type hints em toda a biblioteca
- Logging estruturado
- Suporte async/await para WebSocket

### Features
- Transcrição com word-level timestamps
- Confidence scores
- Smart formatting para português
- Detecção automática de idioma
- VAD (Voice Activity Detection)
- Resultados intermediários no streaming

### Compatibility
- Python 3.9+
- Deepgram API compatible
- Cross-platform (Windows, macOS, Linux)
