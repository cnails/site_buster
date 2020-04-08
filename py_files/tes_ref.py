import requests as req
from lxml import html

sites = [
    'https://vk.com/',
    'https://skype.com',
    'https://stackoverflow.com/',
    'https://yandex.ru/',
    'https://www.youtube.com/?gl=RU&hl=ru'
]

heads = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'referer': 'https://google.com/'
}

a = req.get('https://www.whatismyreferer.com/', headers=heads).text
doc = html.document_fromstring(a)
lh = str(doc.xpath('/html/body/div[2]/div/strong/text()'))[0].resub(' ', '')
print(lh)
