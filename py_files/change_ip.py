import asyncio
import json
import os
from collections import defaultdict

from proxybroker import Broker


async def save(proxies, filename):
    """Save proxies to a file."""
    with open(
            os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), 'jsons', f'{filename}.json'),
            'w', encoding='utf-8') as f:
        country_to_proxies = defaultdict(list)
        while True:
            proxy = await proxies.get()
            if proxy is None:
                break
            print(proxy)
            # proto = 'https' if 'HTTPS' in proxy.types else 'http'
            country_to_proxies[proxy.geo.code].append(
                f'{proxy.host}:{proxy.port}')
        json.dump(country_to_proxies, f)


found_proxies = set()


async def save_to_variable(proxies):
    while True:
        proxy = await proxies.get()
        if proxy is None:
            break
        found_proxies.add(proxy)
        print('Found proxy: %s' % proxy)


def get_proxies(count, countries=['US']):
    proxies = asyncio.Queue()
    broker = Broker(proxies)
    tasks = asyncio.gather(broker.find(
        types=['HTTP', 'HTTPS'], countries=countries, limit=count),
        save_to_variable(proxies))  # save(proxies, filename='proxies')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)


def return_proxies():
    global found_proxies
    returned_proxies = found_proxies
    found_proxies = set()
    return returned_proxies


def main():
    print(get_proxies(10, countries=['RU']))
    # with open(
    #         os.path.join(os.path.dirname(os.path.dirname(
    #             os.path.abspath(__file__))), 'jsons', 'proxies.json'),
    #         'w', encoding='utf-8') as f:
    #     data = json.load(f)


if __name__ == '__main__':
    main()
