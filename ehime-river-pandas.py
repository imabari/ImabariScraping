import datetime
import time

import pandas as pd
from tqdm import tqdm


# 時間
def timeconv(x):
    H, M = map(int, x.split(":"))
    return datetime.timedelta(hours=H, minutes=M)


# 設定
# 東予東部 grp, tpg = "USR019", 2
# 東予西部 grp, tpg = "USR020", 1
# 中予     grp, tpg = "USR021", 2
# 南予北部 grp, tpg = "USR022", 2
# 南予南部 grp, tpg = "USR023", 2

grp, tpg = "USR020", 1

# 期間（2019/04/25 00:10　～　2019/04/27 00:00）
period = pd.date_range("2019-04-27 04:00:00", "2019-05-01 00:00:00", freq="4H")

# 結果
result = []

for now in tqdm(period):

    # 時間調整
    dt = now - datetime.timedelta(hours=4)

    tmp = []

    for pg in range(1, tpg + 1):

        url = "http://183.176.244.72/cgi/050_HQ_030_01.cgi?GID=050_HQ_030&UI=U777&SI=00000&LO=88&SRO=1&KKB=101100&DSP=11110&SKZ=111&NDT=1&MNU=1&BTY=IE6X&SSC=0&RBC=100&DT={0}&GRP={1}&TPG={2}&PG={3}&KTM=3".format(
            now.strftime("%Y%m%d%H%M"), grp, tpg, pg
        )

        # ダム情報をスクレイピング
        river = pd.read_html(url, na_values=["欠測", "−", "閉局"])

        # タイトル
        name = river[0].iloc[0, :].dropna().tolist()

        # データ個数
        n = len(name)

        # データを結合
        data = pd.concat([pd.concat(i, axis=1) for i in zip(*[iter(river[5:])] * n)])

        # 列名を登録
        data.columns = ["日付", "時間"] + name[1:]

        # 日付を補完
        data["日付"].fillna(method="ffill", inplace=True)

        # 日付と時間から年を補完し、日時を作成
        data["日時"] = pd.to_datetime(data["日付"], format="%m/%d").apply(
            lambda x: x.replace(year=dt.year)
        ) + data["時間"].apply(timeconv)

        # 日付と時間を削除
        data.drop(["日付", "時間"], axis=1, inplace=True)

        # 日時をインデックス
        data.set_index("日時", inplace=True)

        tmp.append(data)

        # スリープ
        time.sleep(3)

    # 結果を保存
    result.append(pd.concat(tmp, axis=1))

# 結果を結合
df = pd.concat(result)
df

# 矢印除去
df2 = df.applymap(lambda x: x.rstrip("↑↓→") if type(x) is str else x ).astype(float)

# 欠損確認
df2[df2.isnull().any(axis=1)]

df2.info()

# 欠損値を補完
# df2.fillna(method="ffill", inplace=True)
# df2.fillna(method="bfill", inplace=True)

df2.plot(figsize=(15, 5))
