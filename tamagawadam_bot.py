#-*- coding: utf-8 -*-

import datetime
import urllib.request

from bs4 import BeautifulSoup

import twitter

# GRP = USR004:玉川ダム、USR005:台ダム
grp = 'USR004'

# KTM = 1:１時間毎、2:30分毎、3:10分毎
ktm = 3

# 現在の時刻の5分前を取得
now = datetime.datetime.now() - datetime.timedelta(minutes=5)

# 時間を60分・30分・10分単位に補正する
n = 60

if ktm == 2:
    n = 30
elif ktm == 3:
    n = 10

cut_time = now - datetime.timedelta(minutes=(now.minute % n))

url = 'http://183.176.244.72/cgi/170_USER_010_01.cgi?GID=170_USER_010&UI=U777&SI=00000&MNU=1&LO=88&BTY=IE6X&NDT=1&SK=0000000&DT={0}&GRP={1}&TPG=1&PG=1&KTM={2}'.format(
    cut_time.strftime('%Y%m%d%H%M'), grp, ktm)

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
}

req = urllib.request.Request(url, None, headers)

try:

    html = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html, 'html5lib')

    result = []
    day = ''

    for trs in soup.select('body > table:nth-of-type(7) > tbody > tr'):

        # 列 => セル => セル内の列 => セル内のセル の順に取得
        dam = [[[i.get_text(strip=True) for i in tr.select('td')]
                for tr in tds.select('tr')]
               for tds in trs.select('td > table > tbody')]

        # 行・列入替
        temp = list(map(list, zip(*dam)))

        for j in temp:

            # Flatten
            data = sum(j, [])

            # 日付なし補完
            if data[0]:
                day = data[0]
            else:
                data[0] = day

            # 欠測の場合は除外
            try:
                x = float(data[6])

            except:
                pass

            else:
                data[6] = x
                result.append(data)

except:

    print('{}'.format(now.strftime('%Y/%m/%d %H:%M')))
    pass

else:

    # Twitter設定
    api = twitter.Api(
        consumer_key='',
        consumer_secret='',
        access_token_key='',
        access_token_secret='')

    # 6:00か12:00か18:00のデータがあれば利用、なければ最新を利用
    for k in result:
        if k[1] in ['6:00', '12:00', '18:00']:
            tw = k
            break
    else:
        tw = result[-1]

    # 12:00で貯水率が0.2より増えてない場合は投稿しない
    if now.hour == 12 and (result[-1][6] - result[0][6]) < 0.2:
        pass
    else:
        twit = 'ただいまの玉川ダムの貯水率は{}%です（{}）\n#今治 #玉川ダム #貯水率'.format(tw[6], tw[1])

    status = api.PostUpdate(twit.strip())

    print(status.text)
