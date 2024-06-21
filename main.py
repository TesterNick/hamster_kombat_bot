import configparser
import datetime
import random
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.appium_service import AppiumService
from selenium.common.exceptions import NoSuchElementException


class HamsterApp:

    def __init__(self, driver: webdriver.Remote):
        print('Running Hamster', end='\r')
        self.driver = driver
        self.url = "https://t.me/hamsteR_kombat_bot/start"
        self.root = None
        self._earn_per_tap = None
        self.load()
        tries = 10
        while not self.wait_for_loading() and tries > 0:
            tries -= 1
            self.reload()
        # print(self.driver.page_source)

    @property
    def boost_button(self):
        xpath = ('/*/android.view.View[1]/android.view.View[7]'
                 '/android.view.View/android.widget.TextView')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def energy_element(self):
        xpath = ('/*/android.view.View[1]'
                 '/android.view.View[7]/android.widget.TextView')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def go_ahead_button(self):
        xpath = ('/*/android.view.View[3]/android.view.View'
                 '/android.view.View[2]/android.widget.Button')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def hamster_button(self):
        xpath = ('/*/android.view.View[1]/android.view.View[7]'
                 '/android.widget.Button')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def error_message(self):
        xpath = '//*/android.widget.TextView[@text="Ooops, try again please"]'
        return self.driver.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def loading_screen(self):
        xpath = '//*/android.widget.Image[@text="Loading screen"]'
        try:
            return self.driver.find_element(by=AppiumBy.XPATH, value=xpath)
        except NoSuchElementException:
            return None

    @property
    def refill_energy_element(self):
        xpath = '/*/android.view.View[1]/android.view.View[2]'
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def thank_you_button(self):
        xpath = ('/*/android.view.View[3]/android.view.View'
                 '/android.view.View[2]/android.widget.Button')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    def get_available_refills(self):
        xpath = '/*/android.widget.TextView[2]'
        parent = self.refill_energy_element
        refills = parent.find_element(by=AppiumBy.XPATH, value=xpath)
        return int(refills.text[0])

    def get_energy(self):
        el_text = self.energy_element.text
        current_energy, max_energy = (int(n) for n in el_text.split(' / '))
        print(f'{current_energy=}')
        return current_energy, max_energy

    def check_refill_timer(self):
        xpath = '/*/android.view.View/android.widget.TextView'
        try:
            self.refill_energy_element.find_element(by=AppiumBy.XPATH,
                                                    value=xpath)
            return True
        except NoSuchElementException:
            return False

    def check_error_message(self):
        try:
            error = self.error_message
        except NoSuchElementException:
            return False
        else:
            if error.get_attribute('displayed') == 'true':
                print(f'{error.get_attribute("name")}')
                return True

    def collect_coins(self):
        print('Collecting coins')
        r = self.hamster_button.rect.copy()
        low_x = r['x'] + r['width'] // 4
        upp_x = r['x'] + r['width'] // 4 * 3
        low_y = r['y'] + r['height'] // 4
        upp_y = r['y'] + r['height'] // 4 * 3
        cur_energy, max_energy = self.get_energy()
        print(f'current_energy: {cur_energy}')
        r = random.randint
        while self.get_energy()[0] > 10:
            taps = [(r(low_x, upp_x), r(low_y, upp_y)) for _ in range(5)]
            self.driver.tap(taps)
        return max_energy

    def wait_for_loading(self, timeout=30):
        end_time = time.time() + timeout
        time.sleep(1)
        not_found = 0
        while time.time() < end_time:
            try:
                root_path = ('//android.webkit.WebView[@text="Hamster Kombat"]'
                             '/android.view.View/android.view.View')
                self.root = self.driver.find_element(by=AppiumBy.XPATH,
                                                     value=root_path)
            except NoSuchElementException:
                not_found += 1
                if not_found == 3:
                    self.load()
            else:
                if self.check_error_message():
                    return False
                elif self.loading_screen:
                    time.sleep(0.1)
                else:
                    return True
        raise TimeoutError('App is not loaded')

    def load(self):
        self.driver.get(self.url)

    def reload(self):
        xpath = '//*/android.widget.ImageButton'
        self.driver.find_element(by=AppiumBy.XPATH, value=xpath).click()
        reload_xpath = '//*[@text="Reload Page"]'
        self.driver.find_element(by=AppiumBy.XPATH, value=reload_xpath).click()

    def refill_energy(self):
        self.boost_button.click()
        time.sleep(1)
        if not self.check_refill_timer() and self.get_available_refills():
            self.refill_energy_element.click()
            time.sleep(1)
            self.go_ahead_button.click()
            time.sleep(1)
            return True
        return False


class MainApp:

    def __init__(self):
        self.host = None
        self.port = None
        self.capabilities = {
            'platformName': 'Android',
            'automationName': 'uiautomator2',
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
        if not self._appium_server_url:
            self._appium_server_url = f'http://{self.host}:{self.port}'
        return self._appium_server_url

    def __enter__(self):
        print('Running Appium server', end='\r')
        self.service = AppiumService()
        self.service.start(args=['--address', self.host, '-p', self.port],
                           timeout_ms=20000,)
        options = UiAutomator2Options().load_capabilities(self.capabilities)
        self.driver = webdriver.Remote(self.appium_server_url, options=options)
        if self.driver.is_locked():
            self.driver.unlock()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.lock()
        if self.driver:
            self.driver.quit()
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

    @staticmethod
    def sleep_with_timer(max_energy):
        sleep_time_by_energy = max_energy * 0.3
        timeout = sleep_time_by_energy if sleep_time_by_energy < 3600 else 3600
        end_time = time.time() + timeout
        while time.time() < end_time:
            rest_time = datetime.datetime.fromtimestamp(end_time - time.time())
            print(f'Next run in {rest_time.strftime('%M:%S')}', end='\r')
            time.sleep(1)
        print('Running coin gathering...', end='\r')

    def tap_coins(self):
        hamster = HamsterApp(self.driver)
        try:
            hamster.thank_you_button.click()
        except NoSuchElementException:
            print('No "Thank you" button found')
        max_energy = hamster.collect_coins()
        if hamster.refill_energy():
            hamster.collect_coins()
        return max_energy


if __name__ == '__main__':
    app = MainApp()
    while True:
        with app:
            maximum_energy = app.tap_coins()
        app.sleep_with_timer(maximum_energy)
