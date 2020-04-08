import logging
import os
import platform
import random
import urllib.parse
from random import randint
from time import sleep

import requests
import selenium
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from move_mouse import ActionChainsChild
from selenium import webdriver

logging.basicConfig(
    filename=os.path.join(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))), "sample.log"),
    level=logging.INFO
)
LOG = logging.getLogger("chrome_driver")


def return_driver(user_agent=None, proxy=False, hide=False, timeout=None, exclude_switches=True, exclude_photos=True):
    chrome_options = webdriver.ChromeOptions()
    ua = UserAgent()
    if user_agent is None:
        chrome_options.add_argument(f'--user-agent={ua.random}')
    else:
        try:
            ua = eval(f'ua.{user_agent}')
        except:
            print(f'bad user agent "{user_agent}", switching to random')
            chrome_options.add_argument(f'--user-agent={ua.random}')
        else:
            print('using the following User-Agent:', ua)
            chrome_options.add_argument(f'--user-agent={ua}')

    if exclude_switches:
        chrome_options.add_experimental_option("excludeSwitches", [
            "disable-background-networking",
            "disable-client-side-phishing-detection",
            "disable-default-apps",
            "disable-hang-monitor",
            "disable-popup-blocking",
            "disable-prompt-on-repost",
            "enable-automation",
            "enable-blink-features=ShadowDOMV0",
            "enable-logging",
            "force-fieldtrials=SiteIsolationExtensions/Control",
            "load-extension=/var/folders/zz/zyxvpxvq6csfxvn_n0001_y8000_qk/T/.com.google.Chrome.HPBfiz/internal",
            "log-level=0",
            "password-store=basic",
            "remote-debugging-port=0",
            "test-type=webdriver",
            "use-mock-keychain",
            "user-data-dir=/var/folders/zz/zyxvpxvq6csfxvn_n0001_y8000_qk/T/.com.google.Chrome.drJGEY",
            'enable-automation',
        ])

    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
    })
    if exclude_photos:
        chrome_options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2
        })
    if proxy:
        print(f'--proxy-server={proxy.split("://")[-1]}')
        chrome_options.add_argument(f'--proxy-server={proxy.split("://")[-1]}')
    chrome_options.add_argument('--profile-directory=Default')
    # chrome_options.add_argument("--start-maximized")
    if hide:
        chrome_options.add_argument('--headless')

    osplat = platform.system()
    # We need to add Linux here
    chromedriver = 'chromedriver.exe' if osplat == 'Windows' else 'chromedriver'

    driver = webdriver.Chrome(
        os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), chromedriver),
        options=chrome_options,
    )
    width = random.randint(900, 1400)
    height = random.randint(900, 1400)
    driver.set_window_size(width, height)

    if timeout is not None:
        driver.implicitly_wait(timeout)

    return driver


def send(driver, sel, text):
    """ send value 'text' to web element defined by selector """
    driver.find_element_by_css_selector(sel).send_keys(text)


def click(driver, sel):
    """ click on web element """
    driver.find_element_by_css_selector(sel).click()


def referer(driver, ref_link, main_link):
    import time
    """ get the main_link and make referer as ref_link """
    if '://' not in ref_link:
        ref_links = [f'http://{ref_link}', f'https://{ref_link}']
        LOG.info(
            f'Reference link "{ref_link}" was given without http(s)://, so we tried to add prefix to it.')
    else:
        ref_links = [ref_link]
    correct_ref_link = None
    for ref_links in ref_links:
        try:
            load = driver.get(ref_link)
            page_state = driver.execute_script('return document.readyState;')
            print(page_state)
            # print
            # if not load:
                # return
            correct_ref_link = ref_link
        except selenium.common.exceptions.InvalidArgumentException:
            continue
    if correct_ref_link is not None:
        driver.execute_script(f'window.location.href = "{main_link}";')
    else:
        LOG.info(
            f'Reference link "{ref_link}" was incorrect. We wasn\'t able to complete it to the correct one.')
        try:
            driver.get(main_link)
            page_state = driver.execute_script('return document.readyState;')
            print(page_state)
        except selenium.common.exceptions.InvalidArgumentException:
            LOG.info('Incorrect site was given')
            return False
    return True


def get(driver, link):
    """ get link from current page """
    driver.execute_script(f'window.location.href = "{link}";')


def find_by_css_selector(driver, sel):
    return driver.find_element_by_css_selector(sel)


def find_s(driver, sel):
    return driver.find_elements_by_css_selector(sel)


def find_element_by_link(page_on_site, link):
    """ test function """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15',
        'Cookie': 'cycada=bPpdsL6OmVuA/vHwOkwEZ6b5m1yT1mYEBUWGwH8FGDg=; _ym_d=1576847554; _ym_uid=1570718328767985713; _ym_visorc_22663942=b; _ym_visorc_52332406=b; mda_exp_enabled=1; noflash=true; sso_status=sso.passport.yandex.ru:synchronized_no_beacon; tc=1; user_country=ru; yandex_gid=213; yandex_plus_metrika_cookie=true; PHPSESSID=jsb8usnpa8ovgsjtjp9gg10kk3; mobile=no; _csrf_csrf_token=uDZ_fZZywgrIXC2KLpV2V6G_K71VsmISBCwNr0heC4U; _ym_isad=2; _ym_wasSynced=%7B%22time%22%3A1576844395295%2C%22params%22%3A%7B%22eu%22%3A0%7D%2C%22bkParams%22%3A%7B%7D%7D; mda=0; desktop_session_key=139f10f99471995a1b48eecf0b98f5888c9219d00a10771efaba78cabc3dbaaeecd4f9dfd069f86f3ebf8f6b3a2bfb97bd95a5a3387a5bf37859968e4d756ffafaf00965312aa4f2cc93c262df127542eb204f0518e55383ed78b02c0dce7e36; desktop_session_key.sig=dP943b2vDA3HinOlIUvCc8FOVBs; user-geo-country-id=2; user-geo-region-id=213; lfiltr=all; i=q5DjteMdDtdbTPiy8XS1deq7n8vXuonLoQeLibMR86Zz/u+f0CVJZDEJHTndsyoTjK9LBCz3DwQ8WWr5hbXDZSmu60I=; mda2_beacon=1575744883269; ya_sess_id=3:1575744883.5.1.1568026663610:lXu8Lg:1d.1|924553428.-1.0.1:201533161|894704379.-1.0.1:191832246.2:1397019|30:185633.95409.RVP7okPx9W_5Mm-mpZ96xd48jxs; yandex_login=uid-ledkxpyj; yandexuid=5418682411560849018; my_perpages=%7B%2260%22%3A200%7D; _ym_d=1574701806; _ym_uid=1570718328767985713',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'br, gzip, deflate',
        'Accept-Language': 'ru'
    })
    page = session.get(page_on_site)
    html = bs(page.text, 'html.parser')
    href = html.find_all(href=link)
    while link and not href:
        link = '/'.join(link.split('/')[1:])
        href = html.find_all(href=link)
        href.extend(html.find_all(href='/' + link))
    return href


def get_location(obj, ret=False):
    button = obj
    size = button.size
    if size['width'] or size['height'] == 0:
        return -1, -1
    print(f'size = {size}')
    location = button.location
    x = randint(-size['width'] + 1, size['width'] - 1)
    y = randint(-size['height'] + 1, size['height'] - 1)
    if ret:
        return x, y
    return location['x'] + x, location['y'] + y


def send_search_request(texts):
    lst = []
    for text in texts:
        lst.append(f'https://yandex.ru/search/?lr=213&text={urllib.parse.quote(text)}&noreask=1')
        lst.append(f'https://www.google.com/search?q={text}&oq={text}')
    return lst


def mouse_click(driver):
    ActionChainsChild(driver).click().perform()


def get_user_agent(driver):
    return driver.execute_script("return navigator.userAgent;")


if __name__ == '__main__':
    from scrolling import scroll
    from chrome_driver import return_driver

    # print(find_element_by_link('https://zonaofgames.ru/%d1%81%d0%b0%d0%b9%d1%82-%d0%b4%d0%bb%d1%8f-%d0%be%d0%b3%d1%80%d0%be%d0%bc%d0%bd%d0%be%d0%b3%d0%be-%d0%ba%d0%be%d0%bb%d0%b8%d1%87%d0%b5%d1%81%d1%82%d0%b2%d0%b0-%d0%b3%d0%b5%d0%b9%d0%bc%d0%b5%d1%80/%d0%b8%d0%b3%d1%80%d1%8b-%d0%ba%d0%bb%d1%8e%d1%87%d0%b8-%d0%bf%d0%b0%d1%82%d1%87%d0%b8/', 'https://zonaofgames.ru/%d1%81%d0%b0%d0%b9%d1%82-%d0%b4%d0%bb%d1%8f-%d0%be%d0%b3%d1%80%d0%be%d0%bc%d0%bd%d0%be%d0%b3%d0%be-%d0%ba%d0%be%d0%bb%d0%b8%d1%87%d0%b5%d1%81%d1%82%d0%b2%d0%b0-%d0%b3%d0%b5%d0%b9%d0%bc%d0%b5%d1%80/%d0%b8%d0%b3%d1%80%d1%8b-%d0%ba%d0%bb%d1%8e%d1%87%d0%b8-%d0%bf%d0%b0%d1%82%d1%87%d0%b8/#!digiseller/articles/96429'))
    # print()
    # print(find_element_by_link('https://zonaofgames.ru/%d1%81%d0%b0%d0%b9%d1%82-%d0%b4%d0%bb%d1%8f-%d0%be%d0%b3%d1%80%d0%be%d0%bc%d0%bd%d0%be%d0%b3%d0%be-%d0%ba%d0%be%d0%bb%d0%b8%d1%87%d0%b5%d1%81%d1%82%d0%b2%d0%b0-%d0%b3%d0%b5%d0%b9%d0%bc%d0%b5%d1%80/%d0%b8%d0%b3%d1%80%d1%8b-%d0%ba%d0%bb%d1%8e%d1%87%d0%b8-%d0%bf%d0%b0%d1%82%d1%87%d0%b8/', 'https://zonaofgames.ru/%d1%81%d0%b0%d0%b9%d1%82-%d0%b4%d0%bb%d1%8f-%d0%be%d0%b3%d1%80%d0%be%d0%bc%d0%bd%d0%be%d0%b3%d0%be-%d0%ba%d0%be%d0%bb%d0%b8%d1%87%d0%b5%d1%81%d1%82%d0%b2%d0%b0-%d0%b3%d0%b5%d0%b9%d0%bc%d0%b5%d1%80/%d0%b8%d0%b3%d1%80%d1%8b-%d0%ba%d0%bb%d1%8e%d1%87%d0%b8-%d0%bf%d0%b0%d1%82%d1%87%d0%b8/#!digiseller/detail/2640255'))
    driver = return_driver(user_agent='ie')
    referer(driver, 'https://yandex.ru/search/?lr=213&text=test&noreask=1',
            'https://zonaofgames.ru/')
    for i in range(50):
        sleep(0.5)
        scroll(driver, 10)
    get(driver, 'https://im-a-good-boye.itch.io/blawk')
    driver.quit()
