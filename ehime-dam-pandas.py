import datetime
import time

import pandas as pd
from tqdm import tqdm

# 時間
def timeconv(x):
    H, M = map(int, x.split(":"))
    return datetime.timedelta(hours=H, minutes=M)

# GRP = USR004:玉川ダム、USR005:台ダム、USR010:鹿野川ダム、USR011:野村ダム
grp = "USR004"

# 結果
result = []

# 期間（2019/04/25 00:10　～　2019/04/27 00:00）
period = pd.date_range("2019-04-25 04:00:00", "2019-04-27 00:00:00", freq="4H")

for i in tqdm(period):

    url = "http://183.176.244.72/cgi/170_USER_010_01.cgi?GID=170_USER_010&UI=U777&SI=00000&MNU=1&LO=88&BTY=IE6X&NDT=1&SK=0000000&DT={0}&GRP={1}&TPG=1&PG=1&KTM=3".format(
        i.strftime("%Y%m%d%H%M"), grp
    )

    # 時間調整
    dt = i - datetime.timedelta(hours=4)

    # ダム情報をスクレイピング
    dam = pd.read_html(url, na_values=["欠測", "−"])

    # データを結合
    data = pd.concat([pd.concat(i, axis=1) for i in zip(*[iter(dam[4:])] * 6)])

    # 列名を登録
    data.columns = ["日付", "時間", "貯水位", "全流入量", "全放流量", "貯水量", "貯水率"]

    # 日付を補完
    data["日付"].fillna(method="ffill", inplace=True)

    # 日付と時間から年を補完し、日時を作成
    data["日時"] = pd.to_datetime(data["日付"], format="%m/%d").apply(lambda x: x.replace(year=dt.year)) + data["時間"].apply(timeconv)

    # 日付と時間を削除
    data.drop(["日付", "時間"], axis=1, inplace=True)

    # 日時をインデックス
    data.set_index("日時", inplace=True)

    # 結果を保存
    result.append(data)

    # スリープ
    time.sleep(3)

# 結果を結合
df = pd.concat(result)
df

# 欠損確認
df[df.isnull().any(axis=1)]

df.info()

# 欠損値を補完
# df.fillna(method="ffill", inplace=True)
# df.fillna(method="bfill", inplace=True)

df[["貯水位", "貯水量"]].plot(secondary_y=["貯水量"], figsize=(10, 5))

df[["全流入量", "全放流量", "貯水量"]].plot(secondary_y=["貯水量"], figsize=(10, 5))
