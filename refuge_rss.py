import datetime
import pytz
import os
import re
from urllib.parse import urljoin
from urllib.request import urlopen

from bs4 import BeautifulSoup

import feedgenerator
from bottle import route, run


def get_refuge(url):

    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.select_one('#main_container > h1, h3').get_text(strip=True)

    date_pattern = re.compile(
        '(\d{4})年(\d{1,2})月(\d{1,2})日[ 　](\d{1,2})時(\d{1,2})分')
    result = date_pattern.search(title)

    if result:
        d = [int(i) for i in result.groups()]
        timezone = pytz.timezone("Asia/Tokyo")
        d.extend([0, 0, timezone])
        pubdate = datetime.datetime(*d)

    description = soup.select_one('#main_container > p').get_text(strip=True)

    return title, url, description, pubdate


def scraping(url, css_select):

    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    result = [
        get_refuge(urljoin(url, i.get('href')))
        for i in soup.select(css_select)
    ]

    return result


@route('/urge/')
def index_urge():

    # 避難準備情報、避難勧告、避難指示情報

    urge = scraping('http://www.city.imabari.ehime.jp/bousai/kankoku/',
                    '#main_container > p > a')

    feed = feedgenerator.Rss201rev2Feed(
        title="今治市の避難情報",
        link="http://www.city.imabari.ehime.jp/bousai/kankoku/",
        description="避難準備情報、避難勧告、避難指示情報",
        language="ja", )

    for i in urge:
        feed.add_item(title=i[0], link=i[1], description=i[2], pubdate=i[3])

    return feed.writeString('utf-8')


@route('/shelter/')
def index_shelter():

    # 避難所情報

    shelter = scraping('http://www.city.imabari.ehime.jp/bousai/hinanjo/',
                       '#main_container > div > p > a')

    feed = feedgenerator.Rss201rev2Feed(
        title="今治市の避難所情報",
        link="http://www.city.imabari.ehime.jp/bousai/hinanjo/",
        description="避難所情報",
        language="ja", )

    for i in shelter:
        feed.add_item(title=i[0], link=i[1], description=i[2], pubdate=i[3])

    return feed.writeString('utf-8')


run(host=os.getenv("IP", "0.0.0.0"), port=int(os.environ.get("PORT", 8080)))