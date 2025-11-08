from unittest.mock import MagicMock, patch

import pytest

from web_base import WebBase


@pytest.fixture
def mock_webdriver():
    """
    Fixture que simula o módulo selenium.webdriver.
    O patch é aplicado em 'web_base.webdriver'
    cobrindo execução local e remota.
    """
    with patch('web_base.config.webdriver') as mock_webdriver:
        mock_webdriver.Chrome = MagicMock()
        mock_webdriver.Firefox = MagicMock()
        mock_webdriver.Edge = MagicMock()
        mock_webdriver.Remote = MagicMock()
        yield mock_webdriver


@pytest.fixture
def web_base(mock_webdriver):
    """
    Fixture para criar uma instância de WebBase
    com um driver simulado (mock).
    """
    base = WebBase(browser='Chrome')
    base.driver = MagicMock()
    base.driver.current_url = 'http://fake-url.com/page'
    return base
