import re
from logging import Logger
from time import sleep, time

from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    UnexpectedAlertPresentException
)
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = Logger(__name__)


class ElementsPressents:
    by: By
    element: str
    present: bool


class WebBase:
    def __init__(
        self,
        download_path='',
        anonimus=True,
        hidden=False,
        browser='Chrome',
        grid_url=None,
        timeout: float = 30
    ):
        self.download_path = download_path
        self.anonimus = anonimus
        self.hidden = hidden
        self.status = False
        self.browser = browser
        self.grid_url = grid_url
        self.timeout = timeout

    def start_driver(self) -> None:
        logger.debug(f'Configurando {self.browser}')

        if self.browser == 'Chrome':
            options = ChromeOptions()
            if self.hidden:
                options.add_argument('--headless=new')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            capabilities = DesiredCapabilities.CHROME.copy()

        elif self.browser == 'Firefox':
            options = FirefoxOptions()
            options.headless = self.hidden
            capabilities = DesiredCapabilities.FIREFOX.copy()

        elif self.browser == 'Edge':
            options = EdgeOptions()
            options.use_chromium = True
            if self.hidden:
                options.add_argument('--headless=new')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--window-size=1920,1080')
            capabilities = DesiredCapabilities.EDGE.copy()

        else:
            logger.error('Browser não suportado')
            raise ValueError('Browser não suportado')

        try:
            if self.grid_url:
                self.driver = webdriver.Remote(
                    command_executor=self.grid_url,
                    desired_capabilities=capabilities,
                    options=options,
                )
            elif self.browser == 'Chrome':
                self.driver = webdriver.Chrome(options=options)
            elif self.browser == 'Firefox':
                self.driver = webdriver.Firefox(options=options)
            elif self.browser == 'Edge':
                self.driver = webdriver.Edge(options=options)

            if not self.hidden:
                self.driver.maximize_window()

            self.status = True

        except Exception as ex:
            logger.error(f'Erro ao iniciar o driver: {ex}')
            self.status = False

    def validate_driver(self) -> bool:
        """Valida se o driver esta aberto."""
        try:
            if self.driver.current_url:
                return True
        except Exception:
            return False

    def restart_driver(self) -> None:
        """Caso não tenha nenhuma janela aberta, abre uma nova."""
        try:
            self.get_last_page()
        except Exception:
            self.close()
            self.start_driver()

    def get_last_page(self) -> str:
        """Retorna o nome da ultima janela aberta."""
        return str(self.driver.current_url).split('/')[-1]

    def close(self) -> bool:
        """Fecha o driver."""
        try:
            self.driver.quit()
            self.driver = None
            return True
        except Exception:
            return False

    def full_loading(self, timeout: float = 10) -> None:
        """Aguarda o carregamento completo da página."""
        WebDriverWait(self.driver, timeout).until(
            lambda _: self.driver.execute_script('return document.readyState')
            == 'complete'
        )

    def navigate(self, url: str, max_try: int = 3) -> bool:
        """Navega até uma página."""
        for _ in range(max_try):
            try:
                self.driver.get(url)
                self.full_loading()
                return True
            except TimeoutException:
                continue
            except WebDriverException:
                continue
        return False

    def remove_alert(self, msg: str = '', timeout: float = 1) -> bool:
        """Aceita um alerta generico."""
        try:
            if msg:
                WebDriverWait(self.driver, timeout).until(
                    EC.alert_is_present(), msg
                )
            else:
                WebDriverWait(self.driver, timeout).until(
                    EC.alert_is_present()
                )

            self.driver.switch_to.alert.accept()
            return True
        except TimeoutException:
            logger.warning('Não consta nenhum alerta para remoção!')
        return False

    def wait_inner_html(
        self,
        by: By,
        element: str,
        text: str = None,
        timeout: float = None,
        clear: bool = False,
    ) -> bool:
        """Aguarda que o elemento possua algum valor interno.

        Parameters
        ----------
        by : By
            By selenium
        element : str
            Elemento em sí.
        text : str, optional
            Texto para validação se contem ou não html, by default None
        timeout : float, optional
            Tempo limite de aguardo, by default 3

        Returns
        -------
        bool
            True se o elemento possue o text e False se não possui.
        """
        if not timeout:
            timeout = self.timeout        
        timeout = time() + timeout
        while True:
            if time() > timeout:
                break
            html = self.driver.find_element(by, element).get_attribute('value')
            if text is not None:
                pattern = re.compile('.*?' + re.escape(text) + '.*?')
                if re.search(pattern, html):
                    return True
            elif not clear and html:
                return True
            elif clear and not html:
                return True
        return False

    def wait(self, by: By, element: str, present=True, timeout=None) -> bool:
        """Aguarda um elemento estar ou não presente na página.

        Parameters
        ----------
        by : By
            By selenium
        element : str
            Elemento em sí.
        present : bool, optional
            Se aguardando o elemento está ou não na página, by default True
        timeout : int, optional
            tempo limite para elemento estar ou não presente, by default 30

        Returns
        -------
        bool
            True = Caso present seja True e o elemento está presente.
            True = Caso present seja False e o elemento não está presente.
            False = Caso present seja True e o elemento não está presente.
            False = Caso present seja False e o elemento está presente
        """
        if not timeout:
            timeout = self.timeout
        timeout = time() + timeout
        while True:
            if time() > timeout:
                break

            try:
                WebDriverWait(self.driver, 0.3).until(
                    EC.presence_of_element_located((by, element))
                )
                if present:
                    return True
            except (TimeoutException, UnexpectedAlertPresentException):
                if present:
                    continue
                return True
        return False

    def wait_clickable(
        self, by: By, element: str, clickable=True, timeout=None
    ) -> bool:
        """Aguarda um elemento estar ou não presente na página.

        Parameters
        ----------
        by : By
            By selenium
        element : str
            Elemento em sí.
        clickable : bool, optional
            Se aguarda o elemento ser clicavel ou não, by default True
        timeout : int, optional
            tempo limite para elemento ser ou não clicavel, by default 30

        Returns
        -------
        bool
            True = Caso clickable seja True e o elemento é clivavel.
            True = Caso clicable seja False e o elemento não é clicavel.
            False = Caso clickable seja True e o elemento não é clicavel.
            False = Caso clickable seja False e o elemento é clicavel.
        """
        if not timeout:
            timeout = self.timeout        
        if not timeout:
            timeout = self.timeout        
        timeout = time() + timeout
        while True:
            if time() > timeout:
                break

            try:
                WebDriverWait(self.driver, 0.3).until(
                    EC.element_to_be_clickable((by, element))
                )
                if clickable:
                    return True
            except TimeoutException:
                if clickable:
                    continue
                return True
        return False

    def click_js(self, by: By, element: str, wait_clickable: bool = False, timeout=None) -> bool:
        """Clica em um elemento atravez do javascript.

        Parameters
        ----------
        by : By
            By selenium
        element : str
            Elemento em sí.
        timeout : float, optional
            Tempo limite , by default 0.5

        Returns
        -------
        bool
            tempo limite de aguardo para elemento ser ou não clicavel
        """

        if wait_clickable:
            if not timeout:
                timeout = self.timeout
            self.wait_clickable(by, element, timeout=timeout)

        try:
            if by == 'id':
                self.driver.execute_script(
                    f"document.getElementById('{element}').click()"
                )
                sleep(0.03)
                return True
        except Exception as ex:
            logger.warning(f'Não foi possivel clicar via execute_script: {ex}')

        try:
            self.driver.find_element(by, element).click()
            sleep(0.03)
            return True
        except Exception as ex:
            logger.warning(
                f'Não foi possivel clicar via driver.find_element: {ex}'
            )

        try:
            self.driver.execute_script(
                'arguments[0].click();', self.driver.find_element(by, element)
            )
            sleep(0.03)
            return True
        except Exception as ex:
            logger.warning(
                f'Não foi possivel clicar via '
                f'execute_script + driver.find_element: {ex}'
            )

        return False

    def value_js(
        self,
        by: By,
        element: str,
        value: str = '',
        timeout: float = None,
        max_try: int = 3,
    ) -> bool:
        """Passa o value em um elemento atravez do javascript.

        Parameters
        ----------
        by : By
            By Selenium
        element : str
            Elemento em sí
        value : str, optional
            Valor que será passado, by default ''
        timeout : float, optional
            Tempo limite, by default 2
        max_try : int, optional
            Número maximo de tentativas, by default 3

        Returns
        -------
        bool
            True se elemento contem o valor passado.
            False se não contem.
        """
        if not timeout:
            timeout = self.timeout        
        self.wait(by, element, timeout=timeout)

        if by == 'id':
            self.clear_js(element)

        for _ in range(max_try):
            try:
                self.driver.execute_script(
                    f'arguments[0].value = "{value}";',
                    self.driver.find_element(by, element),
                )
            except Exception as ex:
                logger.warning(f'Falha ao inserir valor {element=} {ex}')

            if self.wait_inner_html(by, element, value, timeout):
                return True

            try:
                input_ele = self.driver.find_element(by, element)
                input_ele.clear()
                input_ele.send_keys(value)
            except Exception as ex:
                logger.warning(f'Falha ao inserir valor {element=} {ex}')

            if self.wait_inner_html(by, element, value, timeout):
                return True

        return False

    def print_pdf(self):
        """Realiza o print da janela atual e salva em pdf."""
        self.driver.execute_script('window.print();')

    def clear_js(self, id: str, max_try: int = 3) -> bool:
        """Limpa um input pelo ID atravez do javascript.

        Parameters
        ----------
        id : str
            ID do elemento que terá o value limpo
        max_try : int, optional
            Número maximo de tentativas de limpeza, by default 3

        Returns
        -------
        bool
            True se limpeza foi realizada
            False se não foi
        """
        for _ in range(max_try):
            try:
                self.driver.execute_script(
                    f'document.getElementById("{id}").value=""'
                )
                if self.wait_inner_html(by=By.ID, element=id, clear=True):
                    return True
            except Exception as ex:
                logger.warning(
                    f'Falha na tentativa de limpeza do elemento {id=} {ex}'
                )
        return False

    def wait_list_elements(
        self, elements: list[ElementsPressents], timeout: float = None
    ) -> None:
        if not timeout:
            timeout = self.timeout        
        timeout = time() + timeout

        while True:
            if time() > timeout:
                break
            for element in elements:
                if self.wait(
                    element.by, element.element, element.present, timeout=0.5
                ):
                    return element

        logger.warning(f'Tempo limite atingido {timeout=}')
        return False
