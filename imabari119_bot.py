# --- coding: utf-8 ---

"""
えひめ医療情報ネットの今治市地区の当番医案内から今日の医療機関をツイート
"""

import datetime
import re
from selenium import webdriver

from bs4 import BeautifulSoup

import twitter

# Windows
# driver = webdriver.PhantomJS()

# Ubuntu
driver = webdriver.PhantomJS('/usr/local/bin/phantomjs')

# ブラウザ操作
driver.get("http://www.qq.pref.ehime.jp/qq38/qqport/kenmintop/")
driver.find_element_by_css_selector(
    "div.group2 > input.each-menu-citizen__button-hover").click()
driver.find_element_by_id("id_blockCd000004").click()
driver.find_element_by_name("forward_next").click()

# スクリーンショット
# driver.save_screenshot("ss.png")

html = driver.page_source
driver.quit()

soup = BeautifulSoup(html, 'html.parser')

table = soup.find_all(
    'table', class_='comTblGyoumuCommon', summary='検索結果一覧を表示しています。')


shimanami = ['吉海町', '宮窪町', '伯方町', '上浦町', '大三島町', '関前']

# 今日の日付
today = datetime.date.today()

# 指定日
# today = datetime.date(2017, 6, 4)


for i in table:

    # 日付取得
    date = i.td.get_text(strip=True).split()
    hiduke = datetime.datetime.strptime(date[0], '%Y年%m月%d日')

    if hiduke.date() == today:

        mae = []
        result = []

        for hospital in i.find_all('tr', id=re.compile('1|2|3')):

            temp = hospital.get_text('|', strip=True).split('|')

            # ID 病院名 住所 昼 昼TEL 夜 夜TEL 診療科目 受付時間
            if hospital['id'] == '1':
                byouin = [9] + temp[1:]

            elif hospital['id'] == '2':
                byouin = [9] + mae[1:7] + temp

            elif hospital['id'] == '3':
                byouin = [9] + temp

            # 夜間の電話がないところは空白挿入
            if byouin[5] != 'TEL（夜）':
                byouin.insert(5, 'TEL（夜）')
                byouin.insert(6, None)

            # 昼間と夜間が同じ病院の場合は結合
            if len(byouin) > 9:
                jikan = '\n'.join(byouin[8:]).replace('17:30\n17:30～', '')
                byouin[8] = jikan

            # 診療科目のID
            # 0:救急
            # 2:内科
            # 4:小児科
            # 8:島嶼部
            # 9:その他

            if byouin[7] == '内科':
                byouin[0] = 2

            elif byouin[7] == '小児科':
                byouin[0] = 4

            elif byouin[7] == '指定なし':

                # 住所が島嶼部の場合は、診療科目を島嶼部に変更
                for j in shimanami:
                    if j in byouin[2]:

                        byouin[0] = 8
                        byouin[7] = '島嶼部'

                        break

                # それ以外の場合は救急、診療科目をNoneに変更
                else:
                    byouin[0] = 0
                    byouin[7] = None

            # id="2"の時用に直前の病院を保存
            mae = byouin[:10]

            # 結果を保存
            result.append(byouin[:10])

        # ID、時間の順でソート
        hospital_list = sorted(result, key=lambda x: (x[0], x[8]))

        # 文章作成
        # 日付・曜日
        twit_date = ['{0[0]} {0[1]}'.format(date)]

        # 陸地部
        twit_riku = [('【{0[7]}】\n'.format(x) if x[7] else '') +
                     '{0[1]}\n{0[8]}'.format(x) for x in hospital_list if x[0] < 8]

        # 島嶼部・その他
        twit_sima = [('【{0[7]}】\n'.format(x) if x[7] else '') +
                     '{0[1]}\n{0[8]}'.format(x) for x in hospital_list if x[0] > 7]

        # 全文
        twit_all = '\n\n'.join(twit_date + twit_riku + twit_sima).strip()

        api = twitter.Api(consumer_key='',
                          consumer_secret='',
                          access_token_key='',
                          access_token_secret='')

        # 140文字以内か
        if len(twit_all) < 140:
            # 全文ツイート
            api.PostUpdate(twit_all)

        else:
            # 島嶼部他ツイート
            api.PostUpdate('\n\n'.join(twit_date + twit_sima).strip())
            # 陸地部ツイート
            api.PostUpdate('\n\n'.join(twit_date + twit_riku).strip())

        break
