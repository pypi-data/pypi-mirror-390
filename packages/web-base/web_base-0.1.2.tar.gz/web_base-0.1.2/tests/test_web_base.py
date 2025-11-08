from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By

from web_base import ElementsPressents, WebBase


def test_start_driver_chrome(mock_webdriver):
    base = WebBase(browser='Chrome')
    base.start_driver()
    mock_webdriver.Chrome.assert_called_once()
    assert base.status is True
    base.driver.maximize_window.assert_called_once()


def test_start_driver_firefox(mock_webdriver):
    base = WebBase(browser='Firefox')
    base.start_driver()
    mock_webdriver.Firefox.assert_called_once()
    assert base.status is True
    base.driver.maximize_window.assert_called_once()


def test_start_driver_edge(mock_webdriver):
    base = WebBase(browser='Edge')
    base.start_driver()
    mock_webdriver.Edge.assert_called_once()
    assert base.status is True
    base.driver.maximize_window.assert_called_once()


def test_start_driver_remote(mock_webdriver):
    grid_url = 'http://localhost:4444/wd/hub'
    base = WebBase(browser='Chrome', grid_url=grid_url)
    base.start_driver()
    mock_webdriver.Remote.assert_called_once()
    assert base.status is True
    base.driver.maximize_window.assert_called_once()


def test_start_driver_unsupported_browser(mock_webdriver):
    base = WebBase(browser='Safari')
    with pytest.raises(ValueError, match='Browser não suportado'):
        base.start_driver()

    assert mock_webdriver.Chrome.call_count == 0


def test_validate_driver_success(web_base):
    assert web_base.validate_driver() is True


def test_validate_driver_failure(web_base):
    type(web_base.driver).current_url = PropertyMock(
        side_effect=WebDriverException
    )
    assert web_base.validate_driver() is False


def test_get_last_page(web_base):
    web_base.driver.current_url = 'http://test.com/last-page'
    assert web_base.get_last_page() == 'last-page'


def test_close(web_base):
    assert web_base.close() is True


def test_navigate_success(web_base):
    url = 'http://test.com'
    with patch.object(web_base, 'full_loading') as mock_loading:
        result = web_base.navigate(url)
        assert result is True
        web_base.driver.get.assert_called_with(url)
        mock_loading.assert_called_once()


def test_navigate_failure(web_base):
    url = 'http://test.com'
    web_base.driver.get.side_effect = TimeoutException
    with patch.object(web_base, 'full_loading'):
        result = web_base.navigate(url, max_try=2)
        assert result is False
        get_count = 2
        assert web_base.driver.get.call_count == get_count


@patch('web_base.config.WebDriverWait')
def test_wait_success(mock_wait, web_base):
    mock_wait.return_value.until.return_value = True
    result = web_base.wait(By.ID, 'test-id', present=True, timeout=1)
    assert result is True


@patch('web_base.config.WebDriverWait')
def test_wait_failure(mock_wait, web_base):
    mock_wait.return_value.until.side_effect = TimeoutException
    result = web_base.wait(By.ID, 'test-id', present=True, timeout=0.1)
    assert result is False


@patch('web_base.config.WebDriverWait')
def test_wait_for_absence_success(mock_wait, web_base):
    mock_wait.return_value.until.side_effect = TimeoutException
    result = web_base.wait(By.ID, 'test-id', present=False, timeout=0.1)
    assert result is True


@patch('web_base.config.WebDriverWait')
def test_wait_clickable_success(mock_wait, web_base):
    mock_wait.return_value.until.return_value = True
    result = web_base.wait_clickable(
        By.ID, 'test-id', clickable=True, timeout=1
    )
    assert result is True


@patch('web_base.config.WebDriverWait')
def test_wait_clickable_failure(mock_wait, web_base):
    mock_wait.return_value.until.side_effect = TimeoutException
    result = web_base.wait_clickable(
        By.ID, 'test-id', clickable=True, timeout=0.1
    )
    assert result is False


def test_click_js_by_id(web_base):
    with patch.object(web_base, 'wait_clickable', return_value=True):
        result = web_base.click_js(By.ID, 'test-id')
        assert result is True
        web_base.driver.execute_script.assert_called_with(
            "document.getElementById('test-id').click()"
        )


def test_click_js_by_find_element(web_base):
    web_base.driver.execute_script.side_effect = Exception('JS click failed')
    with patch.object(web_base, 'wait_clickable', return_value=True):
        result = web_base.click_js(By.XPATH, '//button')
        assert result is True
        web_base.driver.find_element.assert_called_with(By.XPATH, '//button')
        web_base.driver.find_element.return_value.click.assert_called_once()


def test_value_js_success(web_base):
    with patch.object(web_base, 'wait', return_value=True), patch.object(
        web_base, 'wait_inner_html', return_value=True
    ):
        result = web_base.value_js(By.ID, 'test-input', 'test-value')
        assert result is True
        web_base.driver.execute_script.assert_called()


def test_value_js_fallback_to_send_keys(web_base):
    with patch.object(web_base, 'wait', return_value=True), patch.object(
        web_base, 'wait_inner_html', side_effect=[False, True]
    ):
        web_base.driver.execute_script.side_effect = Exception(
            'JS value set failed'
        )
        result = web_base.value_js(By.ID, 'test-input', 'test-value')
        assert result is True
        web_base.driver.find_element.return_value.send_keys.assert_called_with(
            'test-value'
        )


def test_clear_js_success(web_base):
    with patch.object(web_base, 'wait_inner_html', return_value=True):
        result = web_base.clear_js('test-id')
        assert result is True
        web_base.driver.execute_script.assert_called_with(
            'document.getElementById("test-id").value=""'
        )


def test_wait_list_elements_found(web_base):
    element1 = ElementsPressents()
    element1.by = By.ID
    element1.element = 'id1'
    element1.present = True

    element2 = ElementsPressents()
    element2.by = By.ID
    element2.element = 'id2'
    element2.present = True

    with patch.object(
        web_base, 'wait', side_effect=[False, True]
    ) as mock_wait:
        result = web_base.wait_list_elements([element1, element2], timeout=1)
        assert result == element2
        call_count = 2
        assert mock_wait.call_count == call_count


def test_wait_list_elements_not_found(web_base):
    element1 = ElementsPressents()
    element1.by = By.ID
    element1.element = 'id1'
    element1.present = True

    with patch.object(web_base, 'wait', return_value=False):
        result = web_base.wait_list_elements([element1], timeout=0.1)
        assert result is False


def test_start_driver_exception_sets_status_false_and_logs_error():
    base = WebBase(browser='Chrome')

    with patch(
        'web_base.config.webdriver.Chrome',
        side_effect=Exception('Falha simulada'),
    ), patch('web_base.config.logger') as mock_logger:
        base.grid_url = None  # força execução local
        base.start_driver()

        # Verifica se o status foi definido como False
        assert base.status is False

        # Verifica se o logger.error foi chamado com a mensagem esperada
        mock_logger.error.assert_called()
        args, _ = mock_logger.error.call_args
        assert 'Erro ao iniciar o driver' in args[0]
        assert 'Falha simulada' in args[0]


def test_restart_driver_calls_close_and_start_on_exception():
    base = WebBase(browser='Chrome')
    base.driver = MagicMock()

    with patch.object(
        base, 'get_last_page', side_effect=Exception('Falha simulada')
    ), patch.object(base, 'close') as mock_close, patch.object(
        base, 'start_driver'
    ) as mock_start:
        base.restart_driver()

        mock_close.assert_called_once()
        mock_start.assert_called_once()


def test_close_exception_returns_false():
    base = WebBase(browser='Chrome')
    base.driver = MagicMock()

    base.driver.quit.side_effect = Exception('Falha ao fechar o driver')

    result = base.close()

    assert result is False
