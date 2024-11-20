# PayPay-OCR OCR部分担当

import csv
from datetime import datetime
import json
import cv2
from PIL import Image
import numpy as np
import pyocr.builders
from tqdm import tqdm

import pyocr
from PIL import Image, ImageEnhance
import os

import re

import argparse


def get_price(txt):
    price = -1
    for j, stri in enumerate(txt):
        price_t = 0
        m = re.finditer(r"\d+", stri)
        ml = list(m)
        # 数字あった
        if len(ml) == 1:
            # １つならその数字が金額や
            price_t = int(ml[0].group())
        elif len(ml) == 2:
            # 2つなら，間が離れすぎてなきゃその数字やねん
            sub = ml[1].start() - ml[0].start()
            if sub <= 3:
                # 2で1文字,3で2文字間にある．
                price_t = int(re.sub(r"\D", "", ", ".join(stri)))
            else:
                # 間の数字が３つ以上なら，後ろの数字が金額や
                price_t = int(ml[1].group())
        elif len(ml) >= 3:
            # ３つ以上検出されたら，末尾か，末尾２つやな．
            sub = ml[-1].start() - ml[-2].start()
            if sub <= 3:
                # 2で1文字,3で2文字間にある．
                price_t = int(re.sub(r"\D", "", ", ".join(ml[-2].group() + ml[-1].group())))
            else:
                # 間の数字が３つ以上なら，後ろの数字が金額や
                price_t = int(ml[-1].group())
        else:
            # 数字なかった
            continue

        # カードの中で，大きい候補がおそらく金額
        if price == -1:
            price = price_t
        else:
            # 金額候補が複数あった場合
            if price < price_t:
                price = price_t
    return price


# スクショが来ると，カードの配列を返す．
def get_cards_from_screen(frame):

    # cv2.imwrite("out/test.png", cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    # iPhone14proMax
    HEADER_HEIGHT = 392  # paypayのヘッダ部分
    OUTER_POINT = 10  # カードの文字被らなさそうなとこ
    CARD_MIN_HEIGHT = 200  # カードの最小高さ
    CARD_WIDTH = [24, 868]  # カードの両端の位置

    # ヘッダ切り取っていじる
    frame_gp = frame[HEADER_HEIGHT : frame.shape[0], 0 : frame.shape[1]]

    cv2.imwrite("out/test2.png", cv2.cvtColor(frame_gp, cv2.COLOR_BGR2RGB))

    # _, frame_gp = cv2.threshold(
    #     cv2.cvtColor(frame_gp, cv2.COLOR_BGR2GRAY), 128, 255, cv2.THRESH_BINARY
    # )

    # cv2.imwrite("out/test3.png", cv2.cvtColor(frame_gp, cv2.COLOR_BGR2RGB))

    # 矩形の開始・終了場所を調べる
    startend = []
    renkuke = False
    tmpstart = 0
    for i in range(frame_gp.shape[0] - 1):
        # 初めて白に出会った場合
        if (
            np.array_equal(frame_gp[i, CARD_WIDTH[0]], [255, 253, 255])
            and renkuke == False
        ):
            renkuke = True
            tmpstart = i
        # 白が終わったとき
        if (
            np.array_equal(frame_gp[i, CARD_WIDTH[0]], [255, 253, 255]) == False
            and renkuke == True
        ):
            renkuke = False
            startend.append([tmpstart, i])

    # frame_gp = cv2.cvtColor(frame_gp, cv2.COLOR_GRAY2BGR)
    co_frames = []

    # 切り出し
    for i in range(len(startend)):
        if startend[i][1] - startend[i][0] < CARD_MIN_HEIGHT:
            # print(i,"is too small")
            continue

        crop = frame[
            startend[i][0] + HEADER_HEIGHT : startend[i][1] + HEADER_HEIGHT,
            CARD_WIDTH[0] : CARD_WIDTH[1],
        ]
        co_frames.append(crop)

        # cv2.imwrite("out/test4.png", cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))

        # print("a")

        # cv2.imwrite("out/crip_" + str(i) + ".png", cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
    # cv2.imwrite("out/crp.png", cv2.cvtColor(frame_gp, cv2.COLOR_BGR2RGB))

    # print("fin")
    return co_frames


def detect_overlap(frame1, frame2, threshold=0.9):
    """
    2つのフレーム間の重複部分を検出し、その高さを返す
    """
    # print(frame2.shape[0],frame1.shape[0],frame2.shape[1],frame1.shape[1])
    if frame2.shape[0] > frame1.shape[0] or frame2.shape[1] > frame1.shape[1]:
        # フレーム2がフレーム1よりも大きい場合は処理をスキップ
        print("Bigger")
        return 0

    result = cv2.matchTemplate(frame1, frame2, cv2.TM_CCOEFF_NORMED)
    cv2.imwrite("out/frame1.png", cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
    cv2.imwrite("out/frame2.png", cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        overlap_height = frame1.shape[0] - max_loc[1]
        return overlap_height
    else:
        return 0


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


# 文字列からdatetimeを返す
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


# 日付以外も入ってる文字列たちからdatetimeを返す
def findDate_from_text(txt):
    no_date_cnt = 0
    parse_err_cnt = 0

    # たぶんいらん
    l = []

    no_date_flg = True
    getted_date = None
    dated_num = 0
    # このforは店名などそもそも日付じゃないのも来る
    for j, stri in enumerate(txt):
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
        return [None, None]
    # ちゃんと日付入ってたら
    else:
        # print("a")
        strcombined = txt[:dated_num] + txt[dated_num + 1 :]

        return [getted_date, strcombined]


parser = argparse.ArgumentParser()

# 実質ここで読むファイル指定
parser.add_argument("-v", "--video", default="mout.mp4")
parser.add_argument("-p", "--per", default="15", type=int)

args = parser.parse_args()


# 動画のパスを指定
video_path = args.video

if not os.path.exists("out"):
    os.mkdir("out")

# 動画を読み込む
cap = cv2.VideoCapture(video_path)

# フレームリストを初期化
FRAME_WIDTH = 886
frames = np.empty((0, 1920, FRAME_WIDTH, 3), np.uint8)
# frames_normal = []

# フレーム間引き
PER = args.per


# フレームを読み込む
print("動画を読み込んでいます...")
cnt = 0
# このwhileは毎フレームごとに全whileする，perでmodして間引き
while True:
    ret, frame = cap.read()
    cnt = cnt + 1
    if cnt % PER != 0:
        print("-", end="")
        continue
    else:
        print("*", end="")
    if not ret:  #  or cnt > 25
        break
    # フレームをRGBに変換 (OpenCVはBGRで読み込むので)
    # 後で使うのでframesにとっとく
    frames = np.append(
        frames, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)[np.newaxis], axis=0
    )
    # frames_normal.append(frame)

# 動画の読み込みを終了
cap.release()


d_list = []

print("\nStart OCR")

errlist = []
errcnt = 0

# OCRの準備
tools = pyocr.get_available_tools()
tool = tools[0]
builder = pyocr.builders.TextBuilder(tesseract_layout=6)


# フレームごと
for i in tqdm(range(len(frames))):  # len(frames)
    # カードを持ってくる
    cards = get_cards_from_screen(frames[i])
    errcnt = 0

    # 　切り出されたカードごとに処理
    for j in range(len(cards)):
        pilimage = Image.fromarray(cards[j])
        # OCR
        text = (
            tool.image_to_string(pilimage, lang="jpn", builder=builder)
            .replace(" ", "")
            .split()
        )

        try:
            res, strcomb = findDate_from_text(text)
        except TypeError:
            print("ERR")

        if res is None or strcomb is None:
            continue

        # すでに取得した日付かをチェック
        v = next((d["Date"] for d in d_list if d["Date"] == res), None)
        if v is None:
            price_out = get_price(strcomb)
            d = {"Fn": i, "Cn": j, "Date": res, "str": strcomb, "Price": price_out}
            d_list.append(d)
            errcnt = errcnt + 1
            # print("alreadyExist",end="")
    if len(cards) != 0 :
        # 記録
        errlist.append([i, j, errcnt])


# サポート外の型が指定されたときの挙動を定義
def custom_default(o):
    if hasattr(o, "__iter__"):
        # イテラブルなものはリストに
        return list(o)
    # elif isinstance(o, (datetime, date)):
    #     # 日時の場合はisoformatに
    #     return o.isoformat()
    else:
        # それ以外は文字列に
        return str(o)


with open(
    "out/" + video_path + "_" + str(PER) + ".json", mode="wt", encoding="utf-8"
) as f:
    json.dump(d_list, f, ensure_ascii=False, indent=2, default=custom_default)

fieldnames = ["Fn", "Cn", "Date", "str", "Price"]
with open("out/csv" + video_path + "_" + str(PER) +".csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(d_list)

print("finish")


# ↓金額だけ抜くやつ

#
# # 数字だけつまり金額だけ抜く
# price_a = re.sub(r"\D", "", ", ".join(strcombined))
# ddd = {
#     "Date": str(getted_date),
#     # "Num": di_ct["Num"],
#     "Price": price_a,
#     "str": strcombined,
# }
# dl.append(ddd)
# # print("next")
