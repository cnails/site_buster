import copy
import json
import os
import random
import re
import time

import PySimpleGUI as sg
import pycountry
from PySimpleGUI import LISTBOX_SELECT_MODE_EXTENDED
from change_ip import get_proxies, return_proxies
from check_visible import is_visible
from chrome_driver import (LOG, mouse_click, referer, return_driver, send_search_request)
from get_urls import (correct_new_urls, find_all_new_urls, get_full_path,
                      get_full_path_with_digiseller, get_host)
from move_mouse import mouse_move_to_element, random_movements
from numpy.random import choice
from scrolling import get_scroll_height, scroll

TIME_SLEEP = 0
MAX_STEP = 5
PAIR = (100000, 500000)
PROGRESS = 0
COUNTRY_NAME_TO_ISO = 'country_name_to_iso.json'
SECONDS_TO_SCROLL = (6, 16)
WINDOW_LOCATION = (0, 0)
LAYER_2_WIDTH = 60

sg.theme('Reddit')
my_font = ("Helvetica", 25)
my_size = (1100, 650)
sg.set_options(font=my_font, background_color='lightblue',
               slider_relief=sg.RELIEF_RIDGE, progress_meter_relief=sg.RELIEF_RIDGE)
nl = '\n'

# ------ Menu Definition ------ #
menu_def = [['File', ['Open', 'Save', 'Exit', 'Properties']],
            ['Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
            ['Help', 'About...'], ]


class Mouse():
    def __init__(self):
        self.x = 0
        self.y = 0


def get_location_characteristics(web_element):
    elem_top_bound = web_element.location.get('y')
    elem_height = web_element.size.get('height')
    elem_lower_bound = elem_top_bound + elem_height
    return elem_top_bound, elem_lower_bound


def get_window_characteristics(driver):
    win_upper_bound = driver.execute_script('return window.pageYOffset')
    win_height = driver.execute_script(
        'return document.documentElement.clientHeight')
    win_lower_bound = win_upper_bound + win_height
    return win_upper_bound, win_lower_bound


def write_country_name_to_iso():
    iso_to_country_name = {}
    for iso in proxies:
        country = pycountry.countries.get(alpha_2=iso)
        if hasattr(country, 'official_name'):
            iso_to_country_name[iso] = country.official_name
        elif hasattr(country, 'name'):
            iso_to_country_name[iso] = country.name
        else:
            iso_to_country_name[iso] = iso
    country_name_to_iso = {value: key for key,
                                          value in iso_to_country_name.items()}

    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jsons', COUNTRY_NAME_TO_ISO),
              'w', encoding='utf-8') as f:
        json.dump(country_name_to_iso(), f)

with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jsons', COUNTRY_NAME_TO_ISO), 'r',
          encoding='utf-8') as f:
    country_name_to_iso = json.load(f)

list_values = tuple(sorted(country_name_to_iso.keys()))
x_size = max([len(elem) for elem in list_values]) + 1

# print(x_size)

layout_1 = [
    [sg.Menu(menu_def, tearoff=True)],
    # [sg.Text('Choose your settings!', size=(
    #     x_size, 0), justification='center')],
    # [sg.Text('Insert site:', size=(int(x_size / 6), 1)),
    [sg.InputText(key='_SITE_', size=(int(x_size // 1.7), 1)),
    sg.Text('- сайт для накрутки',)],
    # [sg.InputText(key='_SITE_', default_text='https://travelhack.moscow/')],
    [sg.Text('выберете страны:')],
    [sg.Input(
        tooltip='Choose proxy\'s countries', do_not_clear=True, size=(int(x_size // 2.6) + 1, 1),
        enable_events=True, key='_COUNTRY_'),
        sg.Text('выбранные страны:')],
    [sg.Listbox(
        values=list_values, size=(int(x_size // 2.6), 3), key='_LIST_',
        select_mode=LISTBOX_SELECT_MODE_EXTENDED, default_values=[
            'Russian Federation'],
        enable_events=True, bind_return_key=True),
        sg.Listbox(values=['Russian Federation'], enable_events=True,
            size=(int((x_size + 1) // 2.6), 3), key='_CHOSEN_')],
    [sg.Input(key='_NUM_OF_PAGES_', enable_events=True, size=(int(x_size // 2.5), 1)),
        sg.Text('- глубина просмотра',)],
    # [sg.Slider(range=(1, 10), orientation='h', size=(
    #     1 * x_size, 25), default_value=5, key='_NUM_OF_PAGES_')],
    [sg.Input(key='_TIME_OF_VISIT_', enable_events=True, size=(int(x_size // 2.5), 1)),
        sg.Text('- время одного визита на сайте (в секундах)')],
    # [sg.Slider(range=(1, 100), orientation='h', size=(
        # 1 * x_size, 25), default_value=50, key='_TIME_OF_VISIT_')],
    [sg.Text('переходы с сайтов:', size=(25, 1)), sg.Text('поисковые запросы (один на строку):')],
    [sg.Multiline(size=(int(x_size / 2), 3), key='_REFERERS_',
                  default_text='https://yandex.ru/'),
    sg.Multiline(size=(int(x_size / 2), 3), key='_REQUESTS_'),],
    # [sg.Text('Insert query requests for yandex.ru (every request on one line):', size=(x_size, 1))],
    # [sg.Multiline(size=(x_size, 3), key='_REQUESTS_')],
    [sg.Submit(), sg.Cancel()]
]

window_1 = sg.Window('IP choosing', layout_1,
                     location=WINDOW_LOCATION, size=my_size, keep_on_top=True)

alert_label = [
    [sg.Text(f'Please add info about referer\n sites or requests for search', size=(35, 2))],
    [sg.Ok(size=(22, 2))]
]


def show_alert():
    alert = sg.Window('Alert', copy.deepcopy(alert_label), location=(
        320, 500), size=(400, 150), keep_on_top=True)
    while True:
        event, _ = alert.read()
        if event is None or event == 'Ok':
            break
    alert.close()


def get_the_following_urls(url, driver, urls_you_was_already):
    """ get urls """
    main_host = get_host(url)
    main_full_path = get_full_path(url)
    main_full_path_with_digiseller = get_full_path_with_digiseller(url)
    new_urls = find_all_new_urls(driver)
    url_to_web_element = {triple[0]: triple[-1] for triple in new_urls}
    urls_to_go = correct_new_urls(
        driver, [pair[0] for pair in new_urls], [], main_host, main_full_path, main_full_path_with_digiseller)
    pure_urls = {pair[0] for pair in urls_to_go}
    pure_urls = {
        re.sub(r'#[^#!/]*$', '', pure_url) for pure_url in pure_urls}
    pure_urls -= urls_you_was_already
    print(f'Pure urls:{nl}{pure_urls}')
    return pure_urls, url_to_web_element


def walk_the_path(referers, num_of_pages, proxies, time_of_visit, link, ref_requests):
    while proxies:
        proxy = proxies.pop()
        # proxy = '62.33.207.201:80'
        driver = return_driver(proxy=proxy)
        mouse = Mouse()
        # TODO: uncomment
        # width = driver.get_window_size['width']
        # height = driver.get_window_size['height']

        if referers:
            link_referer = random.sample(referers + ref_requests, 1)[0]
        else:
            LOG.info('No referers')
            link_referer = choice(ref_requests)

        urls_to_go = set()
        urls_you_was_already = set()
        url = link
        check_ref = referer(driver, link_referer, url)
        if check_ref == False:
            raise ValueError("Incorrect url given")
        if check_ref == None:
            driver.quit()
            walk_the_path(referers, num_of_pages, proxies,
                time_of_visit, site, ref_requests)
        global PROGRESS
        for i in range(num_of_pages):
            urls_you_was_already.add(url)
            print('debug')
            
            # if html contains "404", get another url
            html_source = driver.page_source
            if re.search('(?:[^0-9]|^)404(?:[^0-9]|$)', html_source) and urls_to_go:
                pure_urls = {pair[0] for pair in urls_to_go}
                pure_urls = {re.sub(r'#[^#!/]*$', '', pure_url)
                             for pure_url in pure_urls}
                pure_urls -= urls_you_was_already
                if pure_urls:
                    url = pure_urls.pop()
                else:
                    driver.back()
                    continue

            # time to scroll
            time_ = max(random.uniform(*SECONDS_TO_SCROLL),
                        time_of_visit / (num_of_pages - i))
            wait = random.uniform(time_ / 2, time_)
            if i == num_of_pages - 1:
                wait = time_of_visit
            time_of_visit -= wait

            pure_urls, url_to_web_element = get_the_following_urls(
                url, driver, urls_you_was_already)

            if pure_urls:
                url = pure_urls.pop()
                print(f'CHOSEN URL: {url}')
                web_element = url_to_web_element[url]
                num_of_times_in_a_row = random.randint(*PAIR)
                elem_top_bound, elem_lower_bound = get_location_characteristics(
                    web_element)
                max_height = get_scroll_height(driver)
                win_upper_bound, win_lower_bound = get_window_characteristics(
                    driver)
                if elem_top_bound < (max_height - driver.get_window_size()['height']) / 2:
                    sign = 1
                else:
                    sign = -1
                end = time.time() + wait
                while time.time() < end:
                    for _ in range(10):
                        STEP = random.randint(1, MAX_STEP)
                        max_height = get_scroll_height(driver)
                        win_upper_bound, win_lower_bound = get_window_characteristics(
                            driver)
                        elem_top_bound, elem_lower_bound = get_location_characteristics(
                            web_element)
                        if not num_of_times_in_a_row or \
                                max_height - win_lower_bound < 15 or win_upper_bound < 15:
                            num_of_times_in_a_row = 0
                            prob = win_upper_bound / \
                                (max_height - driver.get_window_size()['height'])
                            prob = min(prob, 1)
                            prob = max(0, prob)
                            sign = choice([-1, 1], p=[prob, 1 - prob])
                            time.sleep(TIME_SLEEP)
                        else:
                            num_of_times_in_a_row -= 1
                        if num_of_times_in_a_row <= 0:
                            num_of_times_in_a_row = random.randint(*PAIR)
                        scroll(driver, sign * STEP)
                        time.sleep(TIME_SLEEP)
                    random_movements(driver, mouse)
                while not is_visible(driver, web_element):
                    STEP = random.randint(1, MAX_STEP)
                    elem_top_bound, elem_lower_bound = get_location_characteristics(
                        web_element)
                    win_upper_bound, win_lower_bound = get_window_characteristics(
                        driver)
                    while elem_lower_bound < win_upper_bound:
                        elem_top_bound, elem_lower_bound = get_location_characteristics(
                            web_element)
                        win_upper_bound, win_lower_bound = get_window_characteristics(
                            driver)
                        elem_top_bound, elem_lower_bound = get_location_characteristics(
                            web_element)
                        scroll(driver, -STEP)
                        time.sleep(TIME_SLEEP)
                    else:
                        scroll(driver, -STEP)
                    # while elem_top_bound > win_lower_bound:
                    #     scroll(driver, STEP)
                    #     time.sleep(TIME_SLEEP)
                    # else:
                    #     scroll(driver, STEP)

                mouse_move_to_element(driver, mouse, web_element)
                mouse_click(driver)
            else:
                driver.back()
            PROGRESS += 1
        driver.quit()


while True:
    full_list = set()
    prev_new_values = set()
    prev_list = set()
    all_list = set()
    # _, values = window_1.read()
    # window_1.Element('_LIST_').update(values=values['_LIST_'])
    while True:
        event, values = window_1.read()
        if event is None or event in ['Cancel']:
            break
        if values is not None:
            print(f"values['_COUNTRY_']: {values['_COUNTRY_']}")
            print(f"values['_LIST_']: {values['_LIST_']}")
        # if event == '_BROWSE_':
        #     window_1.Element('_PROXY_FILE_').update(values['_BROWSE_'].split('/')[-1])

        if event in ['_NUM_OF_PAGES_']:
            res = ''
            for c in values['_NUM_OF_PAGES_']:
                res += c if c in [str(i) for i in range(10)] else ''
                if len(res) > 1:
                    break
            window_1.Element('_NUM_OF_PAGES_').update(res)

        if event in ['_TIME_OF_VISIT_']:
            res = ''
            for c in values['_TIME_OF_VISIT_']:
                res += c if c in [str(i) for i in range(10)] else ''
                if len(res) > 2:
                    break
            window_1.Element('_TIME_OF_VISIT_').update(res)

        if values is not None and values['_COUNTRY_'] is not None:
            search = values['_COUNTRY_'].lower().strip()
            new_values = {
                elem for elem in list_values if search in elem.lower()}
            if new_values == prev_new_values:
                full_list = (full_list - prev_list) | set(values['_LIST_'])
            else:
                full_list |= set(values['_LIST_'])
            new_values_list = sorted(new_values)
            window_1.Element('_LIST_').update(values=new_values_list, set_to_index=[
                new_values_list.index(country) for country in full_list if country in new_values_list])
            prev_new_values = new_values
            prev_list = set(values['_LIST_'])
            # print(full_list)
            all_list |= full_list
            window_1.Element('_CHOSEN_').update(sorted(all_list))
        # try:
            # window_1.Element('_CHOSEN_').update(sorted(full_list))
        # except Exception:
            # pass
        print(event)

        if event in ['_CHOSEN_']:
            print('\n\n\n\n')
            all_list -= set(values['_CHOSEN_'])
            window_1.Element('_CHOSEN_').update(sorted(all_list))

        if event in ['Submit']:
            if values['_REFERERS_'].strip() and values['_REQUESTS_'].strip():
                show_alert()
            else:
                break
        elif event is None or event in ['Cancel']:
            break
    window_1.close()

    print(f'event: {event}')
    if event == 'Submit':
        print(values['_LIST_'])
        countries = [country_name_to_iso[country]
                     for country in values['_LIST_']]
        get_proxies(len(countries), countries=countries)
        proxies = return_proxies()
        proxies = [f'{proxy.host}:{proxy.port}' for proxy in proxies]
        print(f'using the following proxies: {", ".join(proxies)}')
        num_of_pages = int(values['_NUM_OF_PAGES_'])
        time_of_visit = int(values['_TIME_OF_VISIT_'])
        referers = [elem.strip()
                    for elem in values['_REFERERS_'].split(nl) if elem.strip()]
        site = values['_SITE_']
        search_requests = [elem.strip()
                           for elem in values['_REQUESTS_'].split(nl) if elem.strip()]
        ref_requests = send_search_request(search_requests)
        count_views = values['_COUNT_VIEWS_']

        layout_2 = [
            [sg.Menu(menu_def, tearoff=True)],
            [sg.Text(
                f"Site for busting - {site}", size=(LAYER_2_WIDTH, 1),
                justification='center')],
            [sg.Text(
                f"Proxies from the following countries: {', '.join(countries)}", size=(LAYER_2_WIDTH, 1),
                justification='center')],
            [sg.Text(
                f"The number of pages to walk over: {num_of_pages} pages", size=(LAYER_2_WIDTH, 1),
                justification='center')],
            [sg.Text(
                f"The time of visit: {time_of_visit} seconds", size=(LAYER_2_WIDTH, 1),
                justification='center')],
            [sg.Text(
                f"Referers:", size=(LAYER_2_WIDTH, 1), justification='center')],
            [sg.ProgressBar(
                num_of_pages, orientation='h', size=(LAYER_2_WIDTH, 10), key='progressbar')],
            [sg.Button('To The Main Page'), sg.Cancel()]
        ]

        if referers:
            layout_2.append([sg.Text(f"{nl.join(referers)}", size=(
                60, len(referers)), justification='center')])
        else:
            layout_2.append(
                [sg.Text("No referers", size=(60, len(referers)), justification='center')])

        print('SHOULD OPEN HERE_1')
        window_2 = sg.Window('Walking the site', layout_2, location=WINDOW_LOCATION,
                             size=my_size, keep_on_top=True)
        print('SHOULD OPEN HERE_2')

        # need to add thread
        walk_the_path(referers, num_of_pages, proxies,
                      time_of_visit, site, ref_requests)

        event, values = window_2.read()

        # TODO:
        # while True:
        #     event, values = window_2.read()
        #     print(event, values)
        #     progress_bar.UpdateBar(PROGRESS)
        #     if event is None or event == 'Cancel':
        #         break

        window_2.close()
        if event == 'To The Main Page':
            continue
        break
    else:
        break
