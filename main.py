import configparser
import datetime
import logging
import os.path
import re
import time

from typing import Any

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.appium_service import AppiumService
from selenium.common.exceptions import NoSuchElementException

from classes.adb import Adb
from classes.hamster_app import HamsterApp


class MainApp:
    """
    Class represents the main application.
    It handles Appium infrastructure and controls mobile applications.
    """

    def __init__(self) -> None:
        self.driver = None
        self.service = None
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
        self.adb = Adb()
        self.parse_config()

    @property
    def appium_server_url(self) -> str:
        """
        The property evaluates and caches the Appium server URL.
        """
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

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        logger.debug('Locking the device')
        self.driver.lock()
        logger.debug('Quitting driver')
        self.driver.quit()
        logger.debug('Stopping the Appium service')
        self.service.stop()

    def check_connected_devices(self) -> None:
        logger.info('Checking connected devices')
        while True:
            devices = self.adb.get_connected_devices()
            if not devices:
                logging.debug('No connected devices found')
                self.adb.connect()
                continue
            elif len(devices) > 1:
                input('Please disconnect the device and press Enter')
                continue
            name, status = devices[0]
            logging.debug(f'Checking device {name}')
            if re.match(r'(\d+\.){3}\d+:\d{4}', name):
                if status == 'device':
                    logging.debug(f'Found device {name}')
                    return
                else:
                    self.adb.reconnect()

    def parse_config(self) -> None:
        """
        Read config file and pass parsed values to according fields.
        """
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
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
        self.adb.ip = cfg.get('user_settings', 'ip_address').split(':')[0]
        config = {section: {k: v for k, v in cfg[section].items()}
                  for section in cfg.sections()}
        logger.debug(f'Config: {config}')

    @staticmethod
    def sleep_with_timer(max_energy: int) -> None:
        """
        Do nothing but show in the console the rest time.
        The time is evaluated according to the maximum energy value read
        in the time of the last hamster run.

        :param max_energy: maximum amount of energy available to the user
        """
        sleep_time_by_energy = max_energy * 0.3
        timeout = sleep_time_by_energy if sleep_time_by_energy < 3599 else 3599
        end_time = time.time() + timeout
        logger.debug(f'{max_energy=}. Sleeping for {int(timeout)} s')
        while time.time() < end_time:
            rest_time = datetime.datetime.fromtimestamp(end_time - time.time())
            print(f'Next run in {rest_time.strftime("%M:%S")}', end='\r')
            time.sleep(1)
        print('Running coin gathering...', end='\r')
        logger.info('Running coin gathering')

    def tap_coins(self) -> int:
        """
        Initialise HamsterApp and do the stuff all this is made for.
        """
        try:
            hamster = HamsterApp(self.driver)
        except TimeoutError:
            # There may be some issues on the app server side, so
            # just return a number and let sleep_with_timer work.
            print('App is not loaded. Will try again in 5 minutes')
            return 1000
        try:
            hamster.thank_you_button.click()
        except NoSuchElementException:
            print('No "Thank you" button found')
            logger.error('No "Thank you" button found')
        hamster.get_tap_coordinates()
        max_energy = hamster.collect_coins()
        if hamster.refill_energy():
            hamster.collect_coins()
        return max_energy


if __name__ == '__main__':
    logger = logging.getLogger()
    log_format = '%(asctime)s %(name)s %(levelname)s:\n    %(message)s'
    logging.basicConfig(format=log_format, filename='hamster_bot.log',
                        level=logging.NOTSET)
    app = MainApp()
    app.check_connected_devices()
    while True:
        with app:
            maximum_energy = app.tap_coins()
        app.sleep_with_timer(maximum_energy)
