# crip.pyで作ったjsonをCSVで出す．

import csv
import json
import re
from datetime import datetime


def convert_to_datetime(nen, gatu, bi, ji, fun):
    # print(nen,gatu,bi,ji,fun,sep="-")
    # 年月日時分を datetime オブジェクトに変換
    dt = datetime(year=nen, month=gatu, day=bi, hour=ji, minute=fun)
    is_within_range(dt)
    return dt


def is_within_range(dt):
    # 2018年10月1日から今日までの範囲を設定
    start_date = datetime(2018, 10, 1)
    end_date = datetime.now()

    # 指定された日付が範囲内にあるかどうかを判定
    if start_date <= dt <= end_date:
        return True
    else:
        # print(nen,gatu,bi,ji,fun,sep="-")
        print(dt)
        raise ValueError
        return False


def find_date(str):
    snen = str.find("年")
    sgatu = str.find("月")
    sbi = str.find("日")
    sji = str.find("時")
    sfun = str.find("分")
    if snen != -1 and sgatu != -1 and sbi != -1 and sji != -1 and sfun != -1:

        nen = int(str[snen - 4 : snen])
        gatu = int(str[snen + 1 : sgatu])
        bi = int(str[sgatu + 1 : sbi])
        ji = int(str[sbi + 1 : sji])
        fun = int(str[sji + 1 : sfun])
        # print(nen, gatu, bi, ji, fun)
        res = convert_to_datetime(nen, gatu, bi, ji, fun)
        return res


with open("out/ppd.mp4_15.json") as f:
    d = json.load(f)

no_date_cnt = 0
parse_err_cnt = 0
date_conv_err = 0

l = []
dl = []

for index, di_ct in enumerate(d):
    # print(index,type(value))
    # ここでstrでfor回す
    no_date_flg = True
    getted_date = None
    dated_num = 0
    # このforは店名などそもそも日付じゃないのも来る
    for j, stri in enumerate(di_ct["str"]):
        if index == 3 and j == 1:
            print("stop")
        try:
            res_date = find_date(stri)
            if type(res_date) is datetime:
                l.append(res_date)
                getted_date = res_date
                no_date_flg = False
                dated_num = j
                continue
        except ValueError:
            parse_err_cnt += 1
            None
            # print("err")
    if no_date_flg:
        no_date_cnt += 1
    # ちゃんと日付入ってたら
    else:
        strcombined = di_ct["str"][:dated_num] + di_ct["str"][dated_num + 1 :]
        # 数字だけつまり金額だけ抜く
        price_a = re.sub(r"\D", "", ", ".join(strcombined))
        ddd = {
            "Date": str(getted_date),
            "Num": di_ct["Num"],
            "Price": price_a,
            "str": strcombined,
        }
        dl.append(ddd)
    # print("next")

    # dl.append(d)

fieldnames = [
    "Date",
    "Num",
    "Price",
    "str",
]
with open("out/outcsv.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(dl)

print("Fin")
