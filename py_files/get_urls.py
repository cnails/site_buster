import json
import re
from urllib.parse import urlparse

import selenium
from selenium.webdriver.support.ui import WebDriverWait


TIMEOUT = 0.25
nl = '\n'


def get_host(url):
    url = urlparse(url)
    return f'{url.scheme}://{url.netloc}'


def get_full_path(url):
    url = urlparse(url)
    if url.fragment and 'digiseller' not in url.fragment:
        return f'{url.scheme}://{url.netloc}{url.path}#{url.fragment}'
    return f'{url.scheme}://{url.netloc}{url.path}'.strip('/')


def get_full_path_with_digiseller(url):
    url = urlparse(url)
    return f'{url.scheme}://{url.netloc}{url.path}#!digiseller'


def find_attributes(pair):
    elems = pair[0].find_elements_by_xpath(pair[1])
    if elems:
        return elems
    return False


def find_attribute(pair):
    try:
        return pair[0].get_attribute(pair[1])
    except selenium.common.exceptions.StaleElementReferenceException:
        return False


def find_hrefs(driver, selector):
    try:
        return WebDriverWait((driver, selector), TIMEOUT).until(find_attributes)
    except selenium.common.exceptions.TimeoutException:
        return []


def find_new_hrefs(driver, hrefs, selector):
    new_urls = set()
    for href_ in hrefs:
        try:
            href = WebDriverWait(
                (href_, selector), TIMEOUT).until(find_attribute)
        except selenium.common.exceptions.TimeoutException:
            pass
        else:
            new_urls.add((href, selector, href_))
    return new_urls


def find_data_routes(driver, data_routes):
    new_urls = set()
    selector = "data-route"
    for data_route in data_routes:
        try:
            data_route = WebDriverWait(
                (data_route, selector), TIMEOUT).until(find_attribute)
        except selenium.common.exceptions.TimeoutException:
            pass
        else:
            if not data_route.endswith(('home', 'reviews', 'refund')):
                new_urls.add((data_route, selector))
    return new_urls


def correct_new_urls(
        driver, new_urls, all_urls, main_host, main_full_path, main_full_path_with_digiseller):
    urls = set()
    for url in new_urls:
        url_host = get_host(url)
        new_urls_ = []
        if url_host == main_host:
            new_urls_.append(url)
        if url.startswith(('#', '/')):
            if 'detail' in url or 'article' in url:
                new_urls_.append(f'{main_full_path_with_digiseller}{url}')
            else:
                new_urls_.append(f'{main_full_path}{url}')
        for new_url_ in new_urls_:
            new_url_ = new_url_.strip('#/')
            new_url_ = re.sub(r'#[^#!/]*$', '', new_url_)
            if new_url_ is not None and not new_url_.lower().endswith((
                'css', 'js', 'jpeg', 'jpg', 'jfif', 'exif', 'tiff', 'gif', 'bmp', 'png', 'ppm',
                    'pgm', 'pbm', 'pnm', 'webp', 'hdr', 'heif', 'bat', 'bpg', 'gif', 'svg')):
                splits = new_url_.split('/')[-4:]
                if not (len(splits) == 2 and splits[-2] == splits[-1]) and not (
                        len(splits) == 4 and splits[-4:-2] == splits[-2:]) \
                        and not (new_url_.count('digiseller') > 1) and not (
                        'articles' in new_url_ and 'detail' in new_url_) \
                        and not (new_url_.count('articles') > 1) and new_url_ not in all_urls:
                    urls.add((url, new_url_))
    return urls


def find_all_new_urls(driver):
    a_hrefs = find_hrefs(driver, "//a[@href]")
    button_hrefs = find_hrefs(driver, "//button[@href]")
    data_routes = find_hrefs(driver, "//a[@data-route]")
    srcs = find_hrefs(driver, "//img[@src]")
    option_values = find_hrefs(driver, "//option[@value]")
    new_urls = set()
    new_urls |= find_new_hrefs(driver, a_hrefs, "href")
    new_urls |= find_new_hrefs(driver, button_hrefs, "href")
    new_urls |= find_data_routes(driver, data_routes)
    new_urls |= find_new_hrefs(driver, srcs, "src")
    new_urls |= find_new_hrefs(driver, option_values, "value")
    return new_urls


def get_all_urls_of_site(url):
    from chrome_driver import return_driver
    driver = return_driver()
    all_urls = set()
    urls = {url}
    while urls:
        print(f'Current number of urls to walk through: {len(urls)}')
        url = urls.pop()
        if url.strip('/') in all_urls:
            continue
        try:
            driver.get(url)
        except selenium.common.exceptions.InvalidArgumentException:
            continue
        html_source = driver.page_source
        if re.search('(?:[^0-9]|^)404(?:[^0-9]|$)', html_source):
            continue
        all_urls.add(url.strip('/'))
        main_host = get_host(url)
        main_full_path = get_full_path(url)
        main_full_path_with_digiseller = get_full_path_with_digiseller(url)
        new_urls = set([elem[0] for elem in find_all_new_urls(driver)])
        new_urls -= all_urls
        urls |= {pair[1] for pair in correct_new_urls(
            driver, new_urls, all_urls, main_host, main_full_path, main_full_path_with_digiseller)}

    with open('all_urls.json', 'w', encoding='utf-8') as f:
        json.dump(list(all_urls), f)

    return all_urls


def main():
    print('all urls:',
          get_all_urls_of_site(
              'https://github.com/'
          ))


if __name__ == '__main__':
    main()
