"""
Configuração compartilhada dos testes pytest
"""
import pytest
import os


@pytest.fixture(scope="session")
def test_audio_path():
    """Retorna o caminho para um arquivo de áudio de teste"""
    # Você pode ajustar este caminho conforme necessário
    return os.getenv("TEST_AUDIO_FILE", "/home/TALKLABS/STT/teste_base_bookplay.wav")


@pytest.fixture(scope="session")
def test_api_key():
    """Retorna uma API key de teste"""
    return os.getenv("TALKLABS_STT_API_KEY", "tlk_test_local_key")


@pytest.fixture(scope="session")
def test_base_url():
    """Retorna a URL base para testes"""
    return os.getenv("TALKLABS_STT_BASE_URL", "http://localhost:8001")
