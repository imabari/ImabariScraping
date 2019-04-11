import csv
import datetime
import time

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def date_span(start_date, end_date, hour_interval):

    res = []

    n = start_date

    while n < end_date:
        n += datetime.timedelta(hours=hour_interval)

        res.append(n)
    return res


# ----------------------------------------------------------------------
# 設定
# ----------------------------------------------------------------------

# GRP = USR004:玉川ダム、USR005:台ダム、USR010:鹿野川ダム、USR011:野村ダム
grp = 'USR004'

# KTM = 1:１時間毎、2:30分毎、3:10分毎
ktm = 3

# 開始日時から終了日時の00:00まで取得（60日前まで取得可能）

# 開始日時
start_date = datetime.datetime(2019, 3, 1)

# 終了日時
end_date = datetime.datetime(2019, 3, 31)

# １時間毎:24、30分毎:12、10分毎:4
hour_interval = 4

# ----------------------------------------------------------------------

# 日時のリストを作成
data_lists = date_span(start_date, end_date, hour_interval)

# リスト確認
# print(data_lists)

with open('dam.tsv', 'w') as fw:

    writer = csv.writer(fw, dialect='excel-tab', lineterminator='\n')

    # ヘッダー保存
    writer.writerow(['日付', '時刻', '貯水位', '全流入量', '全放流量', '貯水量', '貯水率'])

    for k in tqdm(data_lists):

        url = 'http://183.176.244.72/cgi/170_USER_010_01.cgi?GID=170_USER_010&UI=U777&SI=00000&MNU=1&LO=88&BTY=IE6X&NDT=1&SK=0000000&DT={0}&GRP={1}&TPG=1&PG=1&KTM={2}'.format(
            k.strftime('%Y%m%d%H%M'), grp, ktm)

        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }

        r = requests.get(url, headers=headers)

        if r.status_code == requests.codes.ok:

            soup = BeautifulSoup(r.content, 'html5lib')

            for trs in soup.select('body > table:nth-of-type(7) > tbody > tr'):

                # 列 => セル => セル内の列 => セル内のセル の順に取得
                temp = [[[i.get_text(strip=True) for i in tr.select('td')]
                         for tr in tds.select('tr')]
                        for tds in trs.select('td > table > tbody')]

                # 行・列入替
                dam = list(map(list, zip(*temp)))

                for j in dam:

                    # Flatten
                    data = sum(j, [])

                    writer.writerow(data)

        # サーバーへの不可軽減のため3秒に設定
        time.sleep(3)
