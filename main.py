import configparser
import datetime
import logging
import time

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.appium_service import AppiumService
from selenium.common.exceptions import NoSuchElementException

from hamster_app import HamsterApp


class MainApp:

    def __init__(self):
        self.host = None
        self.port = None
        self.capabilities = {
            'platformName': 'Android',
            'deviceName': 'Android',
            'appPackage': 'org.telegram.messenger',
            'appActivity': '.DefaultIcon',
            'noReset': "true",
            'fullReset': "false",
            'forceAppLaunch': True,
            'shouldTerminateApp': True,
            'language': 'en',
            'locale': 'US'
        }
        self._appium_server_url = None
        self.parse_config()

    @property
    def appium_server_url(self):
        logger.debug('Getting Appium server url')
        if not self._appium_server_url:
            self._appium_server_url = f'http://{self.host}:{self.port}'
        logger.debug(f'Return url: {self._appium_server_url}')
        return self._appium_server_url

    def __enter__(self):
        print('Running Appium server', end='\r')
        logger.info('Running Appium server')
        self.service = AppiumService()
        self.service.start(args=['--address', self.host, '-p', self.port],
                           timeout_ms=20000,)
        options = UiAutomator2Options().load_capabilities(self.capabilities)
        self.driver = webdriver.Remote(self.appium_server_url, options=options)
        if self.driver.is_locked():
            self.driver.unlock()

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug('Locking the device')
        self.driver.lock()
        if self.driver:
            logger.debug('Quitting driver')
            self.driver.quit()
        logger.debug('Stopping the Appium service')
        self.service.stop()

    def parse_config(self):
        cfg = configparser.ConfigParser()
        cfg.read('config.ini')
        self.host = cfg.get('appium_service', 'host')
        self.port = cfg.get('appium_service', 'port')
        unlock_type = cfg.get('user_settings', 'unlock_type', fallback=None)
        if unlock_type:
            pin = cfg.get('user_settings', 'unlock_key', fallback=None)
            if not pin:
                msg = 'unlock_key is required if there is unlock_type'
                raise RuntimeError(msg)
            self.capabilities['unlockType'] = unlock_type
            self.capabilities['unlockKey'] = pin
            pass
        config = {section: {k: v for k, v in cfg[section].items()}
                  for section in cfg.sections()}
        logger.debug(f'Config: {config}')

    @staticmethod
    def sleep_with_timer(max_energy):
        sleep_time_by_energy = max_energy * 0.3
        timeout = sleep_time_by_energy if sleep_time_by_energy < 3599 else 3599
        end_time = time.time() + timeout
        logger.debug(f'{max_energy=}. Sleeping for {timeout} s')
        while time.time() < end_time:
            rest_time = datetime.datetime.fromtimestamp(end_time - time.time())
            print(f'Next run in {rest_time.strftime('%M:%S')}', end='\r')
            time.sleep(1)
        print('Running coin gathering...', end='\r')
        logger.info('Running coin gathering')

    def tap_coins(self):
        hamster = HamsterApp(self.driver)
        try:
            hamster.thank_you_button.click()
        except NoSuchElementException:
            print('No "Thank you" button found')
            logger.error('No "Thank you" button found')
        max_energy = hamster.collect_coins()
        if hamster.refill_energy():
            hamster.collect_coins()
        return max_energy


if __name__ == '__main__':
    logger = logging.getLogger()
    log_format = '%(asctime)s %(name)s %(levelname)s:\n    %(message)s'
    logging.basicConfig(format=log_format, filename='hamster_bot.log',
                        encoding='utf-8', level=logging.NOTSET)
    app = MainApp()
    while True:
        with app:
            maximum_energy = app.tap_coins()
        app.sleep_with_timer(maximum_energy)
