"""
TalkLabs STT SDK - Speech-to-Text Client
Compatível com Deepgram API

Author: Francisco Lima
License: MIT
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, asdict
from typing import Optional, Callable, Dict

import requests
import websockets
import soundfile as sf
import numpy as np

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class TranscriptionOptions:
    """
    Opções de transcrição para TalkLabs STT.

    Attributes:
        model: Nome do modelo de transcrição (ex: "large-v3", "medium", "small")
        language: Código do idioma ISO 639-1 ("pt", "en", "es", etc.)
        punctuate: Adicionar pontuação ao texto transcrito
        smart_format: Formatação inteligente (capitalização, números, etc.)
        detect_language: Detectar idioma automaticamente (ignora 'language')
        vad_filter: Voice Activity Detection - remove silêncios
        interim_results: Enviar resultados intermediários (WebSocket apenas)
        encoding: Formato de áudio (WebSocket apenas)
        sample_rate: Taxa de amostragem em Hz (WebSocket apenas)
        channels: Número de canais de áudio (WebSocket apenas)

    Example:
        >>> opts = TranscriptionOptions(
        ...     model="large-v3",
        ...     language="pt",
        ...     punctuate=True,
        ...     smart_format=True
        ... )
    """

    # Core parameters
    model: str = "large-v3"  # Modelo padrão
    language: str = "pt"

    # Text processing
    punctuate: bool = True
    smart_format: bool = True
    detect_language: bool = False
    vad_filter: bool = False

    # WebSocket streaming parameters
    interim_results: bool = True
    encoding: str = "linear16"
    sample_rate: int = 16000
    channels: int = 1

    def to_query_params(self) -> Dict[str, str]:
        """
        Converte opções para query parameters HTTP.

        Returns:
            dict: Query parameters com valores convertidos para string

        Example:
            >>> opts = TranscriptionOptions(punctuate=True)
            >>> params = opts.to_query_params()
            >>> # {'model': 'large-v3', 'punctuate': 'true', ...}
        """
        params = {}
        for key, value in asdict(self).items():
            if isinstance(value, bool):
                params[key] = str(value).lower()
            elif value is not None:
                params[key] = str(value)
        return params

    def to_ws_params(self) -> Dict[str, str]:
        """
        Converte opções para query parameters WebSocket.

        Returns:
            dict: Query parameters específicos para WebSocket
        """
        return {
            "model": self.model,
            "language": self.language,
            "encoding": self.encoding,
            "sample_rate": str(self.sample_rate),
            "interim_results": str(self.interim_results).lower()
        }


# ============================================================
# MAIN CLIENT CLASS
# ============================================================

class STTClient:
    """
    Cliente TalkLabs STT para transcrição de áudio.

    Features:
        - REST API para transcrição completa de arquivos
        - WebSocket para streaming em tempo real
        - Suporte a múltiplos modelos de transcrição
        - Processamento de texto inteligente (pontuação, formatação)
        - Voice Activity Detection (VAD)
        - API compatível com Deepgram

    Args:
        api_key: Chave de API TalkLabs (ex: "tlk_live_xxxxx")
        timeout: Timeout para requisições em segundos (default: 300)

    Attributes:
        api_key: Chave de API fornecida
        base_url: URL base da API (fixo: "https://api.talklabs.com.br/api/stt")
        timeout: Timeout configurado em segundos

    Example:
        >>> from talklabs_stt import STTClient
        >>>
        >>> # Inicialização básica
        >>> client = STTClient(api_key="tlk_live_xxxxx")
        >>>
        >>> # Com timeout customizado
        >>> client = STTClient(api_key="tlk_live_xxxxx", timeout=600)
        >>>
        >>> # REST API - transcrição completa
        >>> result = client.transcribe_file("audio.wav")
        >>> print(result["results"]["channels"][0]["alternatives"][0]["transcript"])
        >>>
        >>> # WebSocket Streaming - tempo real
        >>> async def main():
        ...     def on_transcript(data):
        ...         if data["is_final"]:
        ...             print(f"Final: {data['channel']['alternatives'][0]['transcript']}")
        ...
        ...     await client.transcribe_stream(
        ...         "audio.wav",
        ...         on_transcript=on_transcript
        ...     )
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        api_key: str,
        timeout: int = 300
    ):
        """
        Inicializa o cliente STT.

        Args:
            api_key: API key do TalkLabs
            timeout: Timeout em segundos

        Raises:
            ValueError: Se api_key não for fornecida
        """
        if not api_key:
            raise ValueError("API key é obrigatória")

        self.api_key = api_key
        self.base_url = "https://api.talklabs.com.br/api/stt"
        self.timeout = timeout

        logger.info(f"[TalkLabs STT] 🎤 Cliente inicializado: {self.base_url}")

    # ============================================================
    # REST API METHODS
    # ============================================================

    def transcribe_file(
        self,
        audio_path: str,
        options: Optional[TranscriptionOptions] = None,
        **kwargs
    ) -> dict:
        """
        Transcreve um arquivo de áudio completo via REST API (síncrono).

        Args:
            audio_path: Caminho para o arquivo de áudio
            options: Opções de transcrição (ou None para padrões)
            **kwargs: Parâmetros adicionais (model, language, etc.)

        Returns:
            dict: Resultado da transcrição no formato Deepgram-compatible:
                {
                    "metadata": {...},
                    "results": {
                        "channels": [{
                            "alternatives": [{
                                "transcript": "texto transcrito",
                                "confidence": 0.95,
                                "words": [...]
                            }]
                        }]
                    }
                }

        Example:
            >>> # Uso básico
            >>> result = client.transcribe_file("audio.wav")
            >>>
            >>> # Com opções
            >>> opts = TranscriptionOptions(model="medium", language="en")
            >>> result = client.transcribe_file("audio.wav", options=opts)
            >>>
            >>> # Com kwargs diretos
            >>> result = client.transcribe_file(
            ...     "audio.wav",
            ...     model="large-v3",
            ...     language="pt",
            ...     punctuate=True
            ... )

        Raises:
            FileNotFoundError: Se o arquivo de áudio não existir
            requests.HTTPError: Se a API retornar erro
            Exception: Outros erros de rede ou processamento
        """
        # Valida arquivo
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")

        # Prepara opções
        if options is None:
            options = TranscriptionOptions()

        # Override com kwargs
        for key, value in kwargs.items():
            if hasattr(options, key):
                setattr(options, key, value)

        # Lê arquivo de áudio
        logger.info(f"[TalkLabs STT] 📂 Lendo arquivo: {audio_path}")
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        # Monta URL e headers
        url = f"{self.base_url}/v1/listen"
        headers = {
            "Content-Type": "audio/wav",
            "xi-api-key": self.api_key
        }

        # Query parameters
        params = options.to_query_params()

        logger.info(f"[TalkLabs STT] 🔄 Enviando para API: {url}")
        logger.debug(f"[TalkLabs STT] Parâmetros: {params}")

        try:
            # Faz requisição
            response = requests.post(
                url,
                params=params,
                headers=headers,
                data=audio_data,
                timeout=self.timeout
            )

            # Valida resposta
            if response.status_code != 200:
                error_msg = f"Erro {response.status_code}: {response.text}"
                logger.error(f"[TalkLabs STT] ❌ {error_msg}")
                raise Exception(error_msg)

            # Parse JSON
            result = response.json()

            # Log sucesso
            channels = result.get("results", {}).get("channels", [{}])
            alternatives = channels[0].get("alternatives", [{}])
            transcript = alternatives[0].get("transcript", "")
            logger.info(
                f"[TalkLabs STT] ✅ Transcrição completa: "
                f"{len(transcript)} caracteres"
            )

            return result

        except requests.RequestException as e:
            logger.exception(f"[TalkLabs STT] ❌ Erro na requisição: {e}")
            raise
        except Exception as e:
            logger.exception(f"[TalkLabs STT] ❌ Erro inesperado: {e}")
            raise

    # ============================================================
    # WEBSOCKET STREAMING METHODS
    # ============================================================

    async def transcribe_stream(
        self,
        audio_path: str,
        options: Optional[TranscriptionOptions] = None,
        on_transcript: Optional[Callable[[dict], None]] = None,
        on_metadata: Optional[Callable[[dict], None]] = None,
        chunk_size: int = 8000,
        **kwargs
    ):
        """
        Transcreve áudio via WebSocket streaming (assíncrono).

        Envia áudio em chunks e recebe transcrições progressivas.

        Args:
            audio_path: Caminho para o arquivo de áudio
            options: Opções de transcrição
            on_transcript: Callback para cada transcrição recebida
            on_metadata: Callback para metadata da sessão
            chunk_size: Tamanho dos chunks em bytes (default: 8000 = 0.5s @ 16kHz)
            **kwargs: Parâmetros adicionais

        Example:
            >>> async def main():
            ...     def on_transcript(data):
            ...         if data["is_final"]:
            ...             print(f"Final: {data['channel']['alternatives'][0]['transcript']}")
            ...         else:
            ...             print(f"Interim: {data['channel']['alternatives'][0]['transcript']}")
            ...
            ...     await client.transcribe_stream(
            ...         "audio.wav",
            ...         on_transcript=on_transcript
            ...     )
            >>>
            >>> asyncio.run(main())

        Raises:
            FileNotFoundError: Se o arquivo não existir
            websockets.exceptions.WebSocketException: Erro de conexão
        """
        # Valida arquivo
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")

        # Prepara opções
        if options is None:
            options = TranscriptionOptions()

        # Override com kwargs
        for key, value in kwargs.items():
            if hasattr(options, key):
                setattr(options, key, value)

        # Prepara áudio
        logger.info(f"[TalkLabs STT] 📂 Preparando áudio: {audio_path}")
        audio_bytes = self._prepare_audio_for_streaming(audio_path, options.sample_rate)

        # Monta URL WebSocket
        base_ws_url = self.base_url.replace("https://", "wss://").replace("http://", "ws://")
        params = options.to_ws_params()
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        ws_url = f"{base_ws_url}/v1/listen?{query_string}"

        logger.info(f"[TalkLabs STT] 🔌 Conectando WebSocket: {ws_url}")

        # Event para sinalizar quando receber resultado final
        final_received = asyncio.Event()

        try:
            async with websockets.connect(ws_url) as websocket:
                logger.info("[TalkLabs STT] ✅ WebSocket conectado")

                # Envia autenticação
                await websocket.send(json.dumps({"xi_api_key": self.api_key}))
                logger.debug("[TalkLabs STT] 🔐 Autenticação enviada")

                # Tasks paralelas
                send_task = asyncio.create_task(
                    self._send_audio(websocket, audio_bytes, chunk_size)
                )
                receive_task = asyncio.create_task(
                    self._receive_transcripts(websocket, on_transcript, on_metadata, final_received)
                )

                # Aguarda envio terminar
                await send_task

                # Aguarda receber resultado final (com timeout de segurança)
                try:
                    await asyncio.wait_for(final_received.wait(), timeout=10.0)
                except asyncio.TimeoutError:
                    logger.warning("[TalkLabs STT] ⚠️ Timeout aguardando resultado final")

                # Cancela recepção (se ainda estiver rodando)
                if not receive_task.done():
                    receive_task.cancel()
                    try:
                        await receive_task
                    except asyncio.CancelledError:
                        pass

                logger.info("[TalkLabs STT] ✅ Streaming finalizado")

        except websockets.exceptions.WebSocketException as e:
            logger.exception(f"[TalkLabs STT] ❌ Erro WebSocket: {e}")
            raise
        except Exception as e:
            logger.exception(f"[TalkLabs STT] ❌ Erro inesperado: {e}")
            raise

    async def _send_audio(self, websocket, audio_bytes: bytes, chunk_size: int):
        """Envia chunks de áudio para WebSocket"""
        try:
            total_chunks = len(audio_bytes) // chunk_size + 1
            logger.info(
                f"[TalkLabs STT] 📦 Enviando {total_chunks} chunks "
                f"({len(audio_bytes)} bytes)"
            )

            for i in range(0, len(audio_bytes), chunk_size):
                chunk = audio_bytes[i:i + chunk_size]
                await websocket.send(chunk)
                # Pequeno yield para não bloquear event loop
                await asyncio.sleep(0)

            # Finaliza
            await websocket.send(json.dumps({"type": "Finalize"}))
            logger.info("[TalkLabs STT] 📤 Áudio enviado completamente")

            # Fecha stream (servidor deve fechar após processar)
            try:
                await websocket.send(json.dumps({"type": "CloseStream"}))
            except Exception:
                pass  # Conexão pode já estar fechada

        except Exception as e:
            logger.error(f"[TalkLabs STT] ❌ Erro ao enviar áudio: {e}")
            raise

    async def _receive_transcripts(
        self,
        websocket,
        on_transcript: Optional[Callable],
        on_metadata: Optional[Callable],
        final_received: asyncio.Event
    ):
        """Recebe transcrições do WebSocket"""
        try:
            async for message in websocket:
                data = json.loads(message)

                # DEBUG: Log todas as mensagens recebidas
                logger.info(f"[TalkLabs STT] 📨 Mensagem recebida: type={data.get('type', 'UNKNOWN')}")

                # Metadata
                if data.get("type") == "Metadata":
                    logger.debug("[TalkLabs STT] 📋 Metadata recebida")
                    if on_metadata:
                        on_metadata(data)

                # Resultados
                elif data.get("type") == "Results":
                    alternatives = data.get("channel", {}).get("alternatives", [{}])
                    transcript = alternatives[0].get("transcript", "")
                    is_final = data.get("is_final", False)

                    status = "FINAL" if is_final else "INTERIM"
                    logger.info(f"[TalkLabs STT] {status}: {transcript}")

                    if on_transcript:
                        on_transcript(data)

                    # Sinaliza que recebeu resultado final
                    if is_final:
                        final_received.set()
                        # Continua recebendo caso haja mais mensagens
                        # mas a task principal já pode encerrar

                # Erro
                elif data.get("type") == "Error":
                    error_msg = data.get("error", data.get("message", "Unknown error"))
                    logger.error(f"[TalkLabs STT] ❌ Erro do servidor: {error_msg}")
                    final_received.set()  # Sinaliza erro também

                # DEBUG: Tipo desconhecido
                else:
                    logger.warning(f"[TalkLabs STT] ⚠️ Tipo de mensagem desconhecido: {data.get('type')} - Data: {data}")

        except asyncio.CancelledError:
            pass  # Normal quando task é cancelada
        except Exception as e:
            if "disconnect" not in str(e).lower() and "closed" not in str(e).lower():
                logger.error(f"[TalkLabs STT] ❌ Erro ao receber: {e}")
            final_received.set()  # Sinaliza erro

    def _prepare_audio_for_streaming(self, audio_path: str, target_sample_rate: int) -> bytes:
        """Prepara áudio para streaming (resample + convert to PCM16)"""
        try:
            # Lê áudio
            audio_data, sample_rate = sf.read(audio_path, dtype='float32')

            # Mono
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)

            # Resample se necessário
            if sample_rate != target_sample_rate:
                import scipy.signal
                num_samples = int(len(audio_data) * target_sample_rate / sample_rate)
                audio_data = scipy.signal.resample(audio_data, num_samples)

            # Normaliza
            audio_data = audio_data / np.max(np.abs(audio_data) + 1e-8)  # type: ignore

            # Convert to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)

            return audio_int16.tobytes()

        except Exception as e:
            logger.error(f"[TalkLabs STT] ❌ Erro ao preparar áudio: {e}")
            raise

    # ============================================================
    # UTILITY METHODS
    # ============================================================

    def list_models(self) -> dict:
        """
        Lista os modelos de transcrição disponíveis.

        Returns:
            dict: Lista de modelos disponíveis

        Example:
            >>> models = client.list_models()
            >>> for model in models["models"]:
            ...     print(model["name"])

        Raises:
            requests.HTTPError: Se a API retornar erro
        """
        url = f"{self.base_url}/v1/models"
        headers = {"xi-api-key": self.api_key}

        logger.info(f"[TalkLabs STT] 📋 Listando modelos: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            model_count = len(result.get("models", []))
            logger.info(f"[TalkLabs STT] ✅ {model_count} modelo(s) disponível(is)")
            return result

        except Exception as e:
            logger.exception(f"[TalkLabs STT] ❌ Erro ao listar modelos: {e}")
            raise
