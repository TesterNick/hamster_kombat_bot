import logging
import math
import random
import time

from appium.webdriver import WebElement, Remote
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException


logger = logging.getLogger()


class HamsterApp:

    def __init__(self, driver: Remote) -> None:
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
    def boost_button(self) -> WebElement:
        """
        Button which opens Boosts menu.
        """
        logger.debug('Getting Boost button')
        xpath = ('/*/android.view.View[1]/android.view.View[8]'
                 '/android.view.View/android.widget.TextView[@text="Boost"]')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def energy_element(self) -> WebElement:
        """
        Element containing current and maximal energy.
        """
        logger.debug('Getting Energy element')
        xpath = ('/*/android.view.View[1]'
                 '/android.view.View[8]/android.widget.TextView')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def go_ahead_button(self) -> WebElement:
        """
        Button confirming boost activation.
        """
        logger.debug('Getting Go Ahead button')
        xpath = ('/*/android.view.View[3]/android.view.View'
                 '/android.view.View[2]/android.widget.Button')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def hamster_button(self) -> WebElement:
        """
        The main button with a hamster users tap.
        """
        logger.debug('Getting Hamster button')
        xpath = ('/*/android.view.View[1]/android.view.View[8]'
                 '/android.widget.Button')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def error_message(self) -> WebElement:
        """
        Popup containing error messages.
        """
        logger.debug('Looking for error messages')
        xpath = '//*/android.widget.TextView[@text="Ooops, try again please"]'
        return self.driver.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def loading_screen(self) -> WebElement | None:
        """
        The screen which is shown while Hamster Kombat is loading.
        """
        logger.debug('Checking the loading screen')
        xpath = '//*/android.widget.Image[@text="Loading screen"]'
        try:
            return self.driver.find_element(by=AppiumBy.XPATH, value=xpath)
        except NoSuchElementException:
            logger.debug('No loading screen found')
            return None

    @property
    def refill_energy_element(self) -> WebElement:
        """
        Button with information about available refills
        and cooldown timer if any.
        """
        logger.debug('Getting refill energy button')
        xpath = '/*/android.view.View[1]/android.view.View[2]'
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    @property
    def thank_you_button(self) -> WebElement:
        """
        The first button users see when the app is loaded. It has a text
        "Thank you <exchange name>".
        """
        logger.debug('Getting Thank You button')
        xpath = ('/*/android.view.View[3]/android.view.View'
                 '/android.view.View[2]/android.widget.Button')
        return self.root.find_element(by=AppiumBy.XPATH, value=xpath)

    def get_available_refills(self) -> int:
        """
        Find the text showing amount of available refills and parse it.

        :return: number of available refills.
        """
        logger.debug('Getting available refills')
        xpath = '/*/android.widget.TextView[2]'
        parent = self.refill_energy_element
        refills_element = parent.find_element(by=AppiumBy.XPATH, value=xpath)
        available_refills = int(refills_element.text[0])
        logger.debug(f'{available_refills=}')
        return available_refills

    def get_energy(self) -> tuple[int, int]:
        """
        Find the text showing energy and parse it.

        :return: tuple of numbers representing
                 the current energy and its maximum.
        """
        el_text = self.energy_element.text
        current_energy, max_energy = (int(n) for n in el_text.split(' / '))
        logger.debug(f'{current_energy=}, {max_energy=}')
        return current_energy, max_energy

    def check_refill_timer(self) -> bool:
        """
        Find the text showing the cooldown time to the next refill.

        :return: if the timer is shown on the screen
        """
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

    def check_error_message(self) -> bool:
        """
        Find the text showing the error message.

        :return: if the message is shown on the screen
        """
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

    def collect_coins(self) -> int:
        """
        Determine the current and maximal energy and evaluates the
        number of taps required to collect all the coins.
        More taps are performed to mitigate the risk of synchronization errors
        when taps are actually counted with delay rather than in real time.

        :return: energy maximum
        """
        print('Collecting coins')
        logger.info('Collecting coins')
        cur_energy, max_energy = self.get_energy()
        print(f'current_energy: {cur_energy}')
        if not self.earn_per_tap:
            for _ in range(2):
                self.do_random_tap()
            energy_after = self.get_energy()[0]
            self.earn_per_tap = math.ceil((cur_energy - energy_after) / 10)
            logger.debug(f'{self.earn_per_tap=}')
            cur_energy = energy_after
        for _ in range(cur_energy // (self.earn_per_tap - 3) // 5):
            self.do_random_tap()
        return max_energy

    def do_random_tap(self) -> None:
        """
        Get 5 random coordinates and perform multi-touch with 5 fingers.
        """
        r = random.randint
        low_x = self._tap_zone['low_x']
        upp_x = self._tap_zone['upp_x']
        low_y = self._tap_zone['low_y']
        upp_y = self._tap_zone['upp_y']
        self.driver.tap([(r(low_x, upp_x), r(low_y, upp_y)) for _ in range(5)])

    def get_tap_coordinates(self) -> None:
        """
        Get hamster_button borders coordinates and store them as a property.
        Since accessing screen elements is quite a slow operation
        and the button does not change it's size and location,
        this allows to increase the performance.
        """
        r = self.hamster_button.rect.copy()
        self._tap_zone = {
            'low_x': r['x'] + r['width'] // 4,
            'upp_x': r['x'] + r['width'] // 4 * 3,
            'low_y': r['y'] + r['height'] // 4,
            'upp_y': r['y'] + r['height'] // 4 * 3
        }

    def wait_for_loading(self, timeout: int = 30) -> bool:
        """
        Wait while loading is over and handle possible errors
        on different stages.

        :param timeout: maximum time in seconds to wait for loading
        :return: if the app is loaded successfully.
        """
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
                    not_found = 0
            else:
                if self.check_error_message():
                    return False
                elif self.loading_screen:
                    time.sleep(0.5)
                else:
                    return True
        raise TimeoutError('App is not loaded')

    def load(self) -> None:
        """
        Start Hamster Kombat miniapp.
        """
        self.driver.get(self.url)

    def reload(self) -> None:
        """
        Find the software reload button in the miniapp menu and click it.
        """
        xpath = '//*/android.widget.ImageButton'
        self.driver.find_element(by=AppiumBy.XPATH, value=xpath).click()
        reload_xpath = '//*[@text="Reload Page"]'
        self.driver.find_element(by=AppiumBy.XPATH, value=reload_xpath).click()

    def refill_energy(self) -> bool:
        """
        Open the Boosts menu, check refill's availability and,
        if it is available, activate it.

        :return: if the refill was successful
        """
        self.boost_button.click()
        time.sleep(1)
        if not self.check_refill_timer() and self.get_available_refills():
            self.refill_energy_element.click()
            time.sleep(1)
            self.go_ahead_button.click()
            time.sleep(1)
            return True
        return False
