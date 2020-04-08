import json
import os

import requests


def has_connection(driver):
    try:
        driver.find_element_by_xpath(
            '//span[@jsselect="heading" and @jsvalues=".innerHTML:msg"]')
        return False
    except Exception:
        return True


def main():
    with open(
            os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), 'jsons', f'proxies.json'),
            'r', encoding='utf-8') as f:
        data = json.load(f)

    new_data = {}
    url = 'https://yandex.ru/'
    for country, proxies in data.items():
        print(f'country: {country}')
        correct_proxies = []
        for proxy in proxies:
            protocol = 'http'
            if proxy.startswith('https'):
                protocol += 's'
            try:
                requests.get(url, proxies={protocol: proxy}, timeout=5)
                correct_proxies.append(proxy)
            except:
                pass
        new_data[country] = correct_proxies

    with open(
            os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), 'jsons', f'good_proxies.json'),
            'w', encoding='utf-8') as f:
        json.dump(new_data, f)

    # with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jsons', 'good_proxies.json'), 'r', encoding='utf-8') as f:
    #     proxies = json.load(f)

    # with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jsons', 'proxies.json'), 'w', encoding='utf-8') as f:
    #     proxies = {key: value for key, value in proxies.items() if value}
    #     json.dump(proxies, f)


if __name__ == '__main__':
    main()
