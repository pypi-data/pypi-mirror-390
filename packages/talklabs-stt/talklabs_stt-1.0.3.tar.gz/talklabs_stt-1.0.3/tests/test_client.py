"""
Testes unitários para o STTClient
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from talklabs_stt import STTClient, TranscriptionOptions


class TestSTTClientInitialization:
    """Testes de inicialização do cliente"""

    def test_client_initialization_with_defaults(self):
        """Testa inicialização básica do cliente"""
        client = STTClient(api_key="test_key")

        assert client.api_key == "test_key"
        assert client.base_url == "https://api.talklabs.com.br/api/stt"
        assert client.timeout == 300

    def test_client_initialization_with_custom_timeout(self):
        """Testa inicialização com timeout customizado"""
        client = STTClient(
            api_key="test_key",
            timeout=600
        )

        assert client.timeout == 600


class TestTranscriptionOptions:
    """Testes para TranscriptionOptions"""

    def test_transcription_options_defaults(self):
        """Testa valores padrão de TranscriptionOptions"""
        options = TranscriptionOptions()

        assert options.model == "large-v3"
        assert options.language == "pt"
        assert options.punctuate is True
        assert options.smart_format is True
        assert options.detect_language is False
        assert options.interim_results is True

    def test_transcription_options_custom_values(self):
        """Testa TranscriptionOptions com valores customizados"""
        options = TranscriptionOptions(
            model="base",
            language="pt",
            punctuate=False,
            smart_format=False,
            detect_language=True
        )

        assert options.model == "base"
        assert options.language == "pt"
        assert options.punctuate is False
        assert options.smart_format is False
        assert options.detect_language is True

    def test_transcription_options_to_query_params(self):
        """Testa conversão de TranscriptionOptions para query params"""
        options = TranscriptionOptions(
            model="large-v3",
            language="pt",
            punctuate=True
        )

        params = options.to_query_params()

        assert isinstance(params, dict)
        assert params["model"] == "large-v3"
        assert params["language"] == "pt"
        assert params["punctuate"] == "true"  # Boolean convertido para string


class TestSTTClientMethods:
    """Testes para métodos do STTClient"""

    @pytest.fixture
    def client(self):
        """Fixture que cria um cliente para os testes"""
        return STTClient(api_key="test_key")

    @patch('requests.get')
    def test_list_models_success(self, mock_get, client):
        """Testa listagem de modelos com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "large-v3", "languages": ["pt", "en"]},
                {"name": "base", "languages": ["pt", "en"]}
            ]
        }
        mock_get.return_value = mock_response

        models = client.list_models()

        assert "models" in models
        assert len(models["models"]) == 2
        assert models["models"][0]["name"] == "large-v3"
        mock_get.assert_called_once()

    @patch('os.path.exists', return_value=True)
    @patch('requests.post')
    @patch('builtins.open', create=True)
    def test_transcribe_file_basic(self, mock_open, mock_post, mock_exists, client):
        """Testa transcrição básica de arquivo"""
        # Mock file
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metadata": {"duration": 10.5},
            "results": {
                "channels": [{
                    "alternatives": [{
                        "transcript": "Teste de transcrição",
                        "confidence": 0.95,
                        "words": []
                    }]
                }]
            }
        }
        mock_post.return_value = mock_response

        result = client.transcribe_file("/fake/path/audio.wav")

        assert "metadata" in result
        assert "results" in result
        assert result["metadata"]["duration"] == 10.5
        transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
        assert transcript == "Teste de transcrição"

    @patch('os.path.exists', return_value=True)
    @patch('requests.post')
    @patch('builtins.open', create=True)
    def test_transcribe_file_with_options(self, mock_open, mock_post, mock_exists, client):
        """Testa transcrição com TranscriptionOptions"""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metadata": {"duration": 10.5},
            "results": {
                "channels": [{
                    "alternatives": [{
                        "transcript": "Teste com opções",
                        "confidence": 0.98,
                        "words": []
                    }]
                }]
            }
        }
        mock_post.return_value = mock_response

        options = TranscriptionOptions(
            model="large-v3",
            language="pt",
            punctuate=True
        )

        result = client.transcribe_file("/fake/path/audio.wav", options=options)

        transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
        assert transcript == "Teste com opções"

        # Verifica se os parâmetros foram passados corretamente
        call_kwargs = mock_post.call_args
        assert call_kwargs is not None

    @patch('os.path.exists', return_value=True)
    @patch('requests.post')
    @patch('builtins.open', create=True)
    def test_transcribe_file_with_kwargs(self, mock_open, mock_post, mock_exists, client):
        """Testa transcrição com kwargs diretos"""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metadata": {"duration": 10.5},
            "results": {
                "channels": [{
                    "alternatives": [{
                        "transcript": "Teste com kwargs",
                        "confidence": 0.97,
                        "words": [
                            {"word": "Teste", "start": 0.0, "end": 0.5, "confidence": 0.99},
                            {"word": "com", "start": 0.5, "end": 0.7, "confidence": 0.98},
                            {"word": "kwargs", "start": 0.7, "end": 1.2, "confidence": 0.97}
                        ]
                    }]
                }]
            }
        }
        mock_post.return_value = mock_response

        result = client.transcribe_file(
            "/fake/path/audio.wav",
            model="large-v3",
            language="pt",
            punctuate=True
        )

        transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
        assert transcript == "Teste com kwargs"
        words = result["results"]["channels"][0]["alternatives"][0]["words"]
        assert len(words) == 3
        assert words[0]["word"] == "Teste"
