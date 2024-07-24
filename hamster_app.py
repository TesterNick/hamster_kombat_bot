import logging
import random
import time

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException


logger = logging.getLogger()


class HamsterApp:

    def __init__(self, driver: webdriver.Remote):
        print('Running Hamster', end='\r')
        logger.info('Running Hamster')
        self.driver = driver
        self.url = "https://t.me/hamsteR_kombat_bot/start"
        self.root = None
        self.earn_per_tap = None
        self._tap_zone = {'low_x': 0, 'upp_x': 0, 'low_y': 0, 'upp_y': 0}
        self.load()
        tries = 10
        while not self.wait_for_loading() and tries > 0:
            tries -= 1
            self.reload()
        # print(self.driver.page_source)

    @property
    def boost_button(self):
        logger.debug('Getting Boost button')
        xpath = ('/*/android.view.View[1]/android.view.View[8]'
                 '/android.view.View/android.widget.TextView[@text="Boost"]')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def energy_element(self):
        logger.debug('Getting Energy element')
        xpath = ('/*/android.view.View[1]'
                 '/android.view.View[8]/android.widget.TextView')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def go_ahead_button(self):
        logger.debug('Getting Go Ahead button')
        xpath = ('/*/android.view.View[3]/android.view.View'
                 '/android.view.View[2]/android.widget.Button')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def hamster_button(self):
        logger.debug('Getting Hamster button')
        xpath = ('/*/android.view.View[1]/android.view.View[8]'
                 '/android.widget.Button')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def error_message(self):
        logger.debug('Looking for error messages')
        xpath = '//*/android.widget.TextView[@text="Ooops, try again please"]'
        return self.driver.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def loading_screen(self):
        logger.debug('Checking the loading screen')
        xpath = '//*/android.widget.Image[@text="Loading screen"]'
        try:
            return self.driver.find_element(by=AppiumBy.XPATH, value=xpath)
        except NoSuchElementException:
            logger.debug('No loading screen found')
            return None

    @property
    def refill_energy_element(self):
        logger.debug('Getting refill energy button')
        xpath = '/*/android.view.View[1]/android.view.View[2]'
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def thank_you_button(self):
        logger.debug('Getting Thank You button')
        xpath = ('/*/android.view.View[3]/android.view.View'
                 '/android.view.View[2]/android.widget.Button')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    def get_available_refills(self):
        logger.debug('Getting available refills')
        xpath = '/*/android.widget.TextView[2]'
        parent = self.refill_energy_element
        refills_element = parent.find_element(by=AppiumBy.XPATH, value=xpath)
        available_refills = int(refills_element.text[0])
        logger.debug(f'{available_refills=}')
        return available_refills

    def get_energy(self):
        logger.debug('Getting Energy')
        el_text = self.energy_element.text
        current_energy, max_energy = (int(n) for n in el_text.split(' / '))
        logger.debug(f'{current_energy=}, {max_energy=}')
        return current_energy, max_energy

    def check_refill_timer(self):
        logger.debug('Getting refill timer')
        xpath = '/*/android.view.View/android.widget.TextView'
        try:
            el = self.refill_energy_element.find_element(by=AppiumBy.XPATH,
                                                         value=xpath)
            logger.debug(f'Refill timer text: {el.text}')
            return True
        except NoSuchElementException:
            logger.debug('No refill timer found')
            return False

    def check_error_message(self):
        try:
            error = self.error_message
        except NoSuchElementException:
            logger.debug('No error messages found')
            return False
        else:
            if error.get_attribute('displayed') == 'true':
                error_name = f'{error.get_attribute("name")}'
                print(error_name)
                logger.debug(f'Found error: {error_name}')
                return True

    def collect_coins(self):
        print('Collecting coins')
        logger.info('Collecting coins')
        cur_energy, max_energy = self.get_energy()
        print(f'current_energy: {cur_energy}')
        if not self.earn_per_tap:
            for _ in range(2):
                self.do_random_tap()
            energy_after = self.get_energy()[0]
            self.earn_per_tap = (cur_energy - energy_after) // 10
            logger.debug(f'{self.earn_per_tap=}')
            cur_energy = energy_after
        for _ in range(cur_energy // (self.earn_per_tap - 3) // 5):
            self.do_random_tap()
        return max_energy

    def do_random_tap(self):
        r = random.randint
        low_x = self._tap_zone['low_x']
        upp_x = self._tap_zone['upp_x']
        low_y = self._tap_zone['low_y']
        upp_y = self._tap_zone['upp_y']
        self.driver.tap([(r(low_x, upp_x), r(low_y, upp_y)) for _ in range(5)])

    def get_tap_coordinates(self):
        r = self.hamster_button.rect.copy()
        self._tap_zone = {
            'low_x': r['x'] + r['width'] // 4,
            'upp_x': r['x'] + r['width'] // 4 * 3,
            'low_y': r['y'] + r['height'] // 4,
            'upp_y': r['y'] + r['height'] // 4 * 3
        }

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
                logger.error('App is not loaded')
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
