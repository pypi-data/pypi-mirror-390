"""
Testes de integração com o servidor real
Requer API key válida no arquivo .env
"""
import os
import pytest
from dotenv import load_dotenv
from talklabs_stt import STTClient, TranscriptionOptions

# Carrega variáveis de ambiente
load_dotenv()

# Configuração
API_KEY = os.getenv("TALKLABS_STT_API_KEY")
# BASE_URL = os.getenv("TALKLABS_STT_BASE_URL", "http://localhost:8001")
BASE_URL = os.getenv("TALKLABS_STT_BASE_URL", "https://api.talklabs.com.br/api/stt")

# Marca para testes de integração (rodam apenas se explicitamente solicitado)
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def client():
    """Fixture que cria um cliente para testes de integração"""
    if not API_KEY:
        pytest.skip("TALKLABS_STT_API_KEY não configurada no .env")

    # Cria cliente com base_url configurável
    client = STTClient(api_key=API_KEY)
    client.base_url = BASE_URL
    return client


@pytest.fixture(scope="module")
def sample_audio():
    """Fixture que retorna o caminho para um arquivo de áudio de teste"""
    # Procura por arquivo de áudio de teste
    audio_paths = [
        os.getenv("TEST_AUDIO_FILE"),
        "/home/TALKLABS/STT/teste_base_bookplay.wav",
        "tests/fixtures/audio_sample.wav",
        "audio_sample.wav"
    ]

    for audio_path in audio_paths:
        if audio_path and os.path.exists(audio_path):
            return audio_path

    pytest.skip("Nenhum arquivo de áudio de teste encontrado")


class TestIntegrationListModels:
    """Testes de integração para listagem de modelos disponíveis"""

    def test_list_models_success(self, client):
        """Testa se consegue listar modelos do servidor"""
        data = client.list_models()
        assert "models" in data, "Campo 'models' não encontrado na resposta"
        assert isinstance(data["models"], list), "Campo 'models' não é uma lista"
        assert len(data["models"]) > 0, "Lista de modelos está vazia"

        # Verifica estrutura do primeiro modelo
        first_model = data["models"][0]
        for field in ["name", "canonical_name", "tags", "language", "version", "description"]:
            assert field in first_model, f"Campo '{field}' ausente em um dos modelos"

        print(f"\n✅ Modelos disponíveis: {len(data['models'])}")
        for model in data["models"]:
            print(f"   - {model.get('name')} ({model.get('version')})")

    def test_list_models_contains_expected_names(self, client):
        """Verifica se os principais modelos estão disponíveis"""
        data = client.list_models()

        model_names = [m.get("name") for m in data.get("models", [])]
        expected_models = {
            "tiny", "base", "small", "medium",
            "large-v1", "large-v2", "large-v3", "turbo"
        }

        missing = expected_models - set(model_names)
        assert not missing, f"Modelos ausentes: {', '.join(missing)}"

        print(f"\n✅ Modelos esperados encontrados: {', '.join(model_names)}")


class TestIntegrationTranscribeFile:
    """Testes de integração para transcrição de arquivos"""

    def test_transcribe_file_basic(self, client, sample_audio):
        """Testa transcrição básica de arquivo"""
        result = client.transcribe_file(sample_audio)

        # Verifica estrutura da resposta
        assert "metadata" in result
        assert "results" in result
        assert "channels" in result["results"]

        # Verifica conteúdo
        channels = result["results"]["channels"]
        assert len(channels) > 0

        alternatives = channels[0].get("alternatives", [])
        assert len(alternatives) > 0

        transcript = alternatives[0].get("transcript", "")
        confidence = alternatives[0].get("confidence", 0)
        words = alternatives[0].get("words", [])

        assert len(transcript) > 0, "Transcrição vazia"
        assert confidence > 0, "Confiança igual a zero"
        assert len(words) > 0, "Nenhuma palavra retornada"

        print("\n✅ Transcrição básica:")
        print(f"   Duração: {result['metadata'].get('duration', 0):.2f}s")
        print(f"   Confiança: {confidence:.2%}")
        print(f"   Palavras: {len(words)}")
        print(f"   Texto: {transcript[:100]}...")

    def test_transcribe_file_with_options(self, client, sample_audio):
        """Testa transcrição com opções customizadas"""
        options = TranscriptionOptions(
            model="large-v3",
            language="pt",
            punctuate=True,
            smart_format=True
        )

        result = client.transcribe_file(sample_audio, options=options)

        # Verifica estrutura
        assert "results" in result
        transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]

        assert len(transcript) > 0
        print("\n✅ Transcrição com opções:")
        print(f"   Modelo: {options.model}")
        print(f"   Idioma: {options.language}")
        print(f"   Texto: {transcript[:100]}...")

    def test_transcribe_file_with_kwargs(self, client, sample_audio):
        """Testa transcrição com kwargs diretos"""
        result = client.transcribe_file(
            sample_audio,
            model="large-v3",
            language="pt",
            punctuate=True
        )

        assert "results" in result
        words = result["results"]["channels"][0]["alternatives"][0]["words"]

        assert len(words) > 0
        print("\n✅ Transcrição com kwargs:")
        print(f"   Total de palavras: {len(words)}")

        # Mostra primeiras 3 palavras
        if len(words) >= 3:
            print("   Primeiras palavras:")
            for word in words[:3]:
                print(f"     {word['start']:.2f}s - {word['end']:.2f}s: \"{word['word']}\"")


class TestIntegrationTranscribeStream:
    """Testes de integração para streaming WebSocket"""

    @pytest.mark.asyncio
    async def test_transcribe_stream_basic(self, client, sample_audio):
        """Testa streaming básico via WebSocket"""
        results = {
            "metadata_received": False,
            "final_count": 0,
            "interim_count": 0,
            "transcripts": []
        }

        def on_metadata(data):
            results["metadata_received"] = True

        def on_transcript(data):
            is_final = data.get("is_final", False)
            transcript = data.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")

            if is_final:
                results["final_count"] += 1
                results["transcripts"].append(transcript)
            else:
                results["interim_count"] += 1

        # Executa streaming
        await client.transcribe_stream(
            sample_audio,
            on_metadata=on_metadata,
            on_transcript=on_transcript,
            interim_results=True
        )

        # Verifica resultados
        assert results["metadata_received"], "Metadata não foi recebida"
        assert results["final_count"] > 0, "Nenhum resultado final recebido"
        assert len(results["transcripts"]) > 0, "Nenhuma transcrição recebida"

        full_transcript = " ".join(results["transcripts"])
        assert len(full_transcript) > 0, "Transcrição final vazia"

        print("\n✅ Streaming básico:")
        print(f"   Resultados finais: {results['final_count']}")
        print(f"   Resultados interim: {results['interim_count']}")
        print(f"   Transcrição: {full_transcript[:100]}...")

    @pytest.mark.asyncio
    async def test_transcribe_stream_with_options(self, client, sample_audio):
        """Testa streaming com opções"""
        options = TranscriptionOptions(
            model="large-v3",
            language="pt",
            interim_results=True
        )

        final_transcripts = []

        def on_transcript(data):
            if data.get("is_final"):
                transcript = data["channel"]["alternatives"][0]["transcript"]
                final_transcripts.append(transcript)

        await client.transcribe_stream(
            sample_audio,
            options=options,
            on_transcript=on_transcript
        )

        assert len(final_transcripts) > 0, "Nenhuma transcrição final"

        print("\n✅ Streaming com opções:")
        print(f"   Segmentos finais: {len(final_transcripts)}")
        print(f"   Texto completo: {' '.join(final_transcripts)[:100]}...")


class TestIntegrationCompatibility:
    """Testes de compatibilidade SDK vs Servidor"""

    def test_sdk_version_compatibility(self, client):
        """Verifica se o SDK é compatível com o servidor"""
        # Testa se consegue listar modelos (operação básica)
        try:
            models = client.list_models()
            assert "models" in models
            print("\n✅ SDK compatível com servidor")
            print("   SDK versão: 1.0.1")
            print(f"   Modelos disponíveis: {len(models['models'])}")
        except Exception as e:
            pytest.fail(f"SDK incompatível com servidor: {e}")

    def test_api_response_structure(self, client, sample_audio):
        """Verifica se a estrutura da resposta está correta"""
        result = client.transcribe_file(sample_audio)

        # Verifica estrutura Deepgram-compatible
        required_keys = ["metadata", "results"]
        for key in required_keys:
            assert key in result, f"Chave '{key}' faltando na resposta"

        assert "channels" in result["results"], "Chave 'channels' faltando"
        assert len(result["results"]["channels"]) > 0, "Nenhum canal na resposta"

        channel = result["results"]["channels"][0]
        assert "alternatives" in channel, "Chave 'alternatives' faltando"
        assert len(channel["alternatives"]) > 0, "Nenhuma alternativa"

        alternative = channel["alternatives"][0]
        required_alt_keys = ["transcript", "confidence", "words"]
        for key in required_alt_keys:
            assert key in alternative, f"Chave '{key}' faltando na alternativa"

        print("\n✅ Estrutura da resposta compatível com Deepgram API")


# Função auxiliar para rodar os testes de integração
def run_integration_tests():
    """
    Executa os testes de integração
    Use: python -m pytest tests/test_integration.py -v -m integration
    """
    pass


if __name__ == "__main__":
    # Permite executar os testes diretamente
    print("Para executar os testes de integração, use:")
    print("pytest tests/test_integration.py -v -m integration")
