import re

import requests
from bs4 import BeautifulSoup

dam_name = '玉川ダム'
url = 'http://i.river.go.jp/_-p01-_/p/ktm1801070/?mtm=10&swd=&prf=3801&twn=3801202&rvr=&den=0972900700006'

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
}

r = requests.get(url, headers=headers)

if r.status_code == 200:

    soup = BeautifulSoup(r.content, 'html5lib')

    contents = soup.find('a', {'name': 'contents'}).get_text('\n', strip=True)

    # print(contents)

    # サブタイトル・単位を除去
    temp = re.sub(r'■\d{1,2}時間履歴\n単位：%\n', '', contents)

    # print(temp)

    datas = [i.split() for i in temp.splitlines()]

    for data in datas:

        try:
            float(data[1])
        except:
            continue
        else:
            print('ただいまの{0}の貯水率は{1[1]}%です（{1[0]}）'.format(dam_name, data))
            break

    else:
        print('取得できませんでした')
