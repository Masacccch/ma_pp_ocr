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

# from argparse import ArgumentParser
import argparse


# スクショが来ると，カードの配列を返す．
def get_cards_from_screen(frame):

    HEADER_HEIGHT = 170  # paypayのヘッダ部分
    OUTER_POINT = [5,100] # paypayの背景の場所
    CARD_MIN_HEIGHT = 200 # カードの最小高さ
    CARD_WIDTH = [20,1050] # カードの両端の位置

    # ヘッダ切り取っていじる
    frame_gp = frame[HEADER_HEIGHT : frame.shape[0], 0 : frame.shape[1]]

    # 紫で背景塗り潰しして2値化ちゃん
    _, frame_gp, _, _ = cv2.floodFill(frame_gp, None, seedPoint=OUTER_POINT, newVal=(100, 0, 100))
    _, frame_gp = cv2.threshold(
        cv2.cvtColor(frame_gp, cv2.COLOR_BGR2GRAY), 128, 255, cv2.THRESH_BINARY
    )

    # 矩形の開始・終了場所を調べる
    startend = []
    renkuke = False
    tmpstart = 0
    for i in range(frame_gp.shape[0] - 1):
        # 初めて白に出会った場合
        if frame_gp[i, CARD_WIDTH[0]] == 255 and renkuke == False:
            renkuke = True
            tmpstart = i
        # 白が終わったとき
        if frame_gp[i, CARD_WIDTH[0]] == 0 and renkuke == True:
            renkuke = False
            startend.append([tmpstart, i])

    frame_gp = cv2.cvtColor(frame_gp, cv2.COLOR_GRAY2BGR)
    co_frames = []

    for i in range(len(startend)):
        if startend[i][1] - startend[i][0] < CARD_MIN_HEIGHT:
            # print(i,"is too small")
            continue

        crop = frame[startend[i][0]+HEADER_HEIGHT : startend[i][1]+HEADER_HEIGHT, CARD_WIDTH[0]:CARD_WIDTH[1]]
        co_frames.append(crop)

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

parser = argparse.ArgumentParser()

parser.add_argument('arg1',default='ppd.mp4')
parser.add_argument('arg2',default='20', type=int)

args=parser.parse_args()


# 動画のパスを指定
video_path = args.arg1

if not os.path.exists('out'):
    os.mkdir('out')

# 動画を読み込む
cap = cv2.VideoCapture(video_path)

# フレームリストを初期化
frames = np.empty((0, 1920, 1080, 3), np.uint8)
# frames_normal = []

# フレーム間引き
PER = args.arg2

# フレームを読み込む
print("動画を読み込んでいます...")
cnt = 0
while True:
    ret, frame = cap.read()
    cnt = cnt + 1
    if cnt % PER != 0:
        print("-", end="")
        continue
    else:
        print("*", end="")
    if not ret: #  or cnt > 25
        break
    # フレームをRGBに変換 (OpenCVはBGRで読み込むので)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frames = np.append(frames, frame[np.newaxis], axis=0)
    # frames_normal.append(frame)

# 動画の読み込みを終了
cap.release()

# def cardtxt2dict(framenum,cardnum,str):
#     fnum = framenum
#     cnum = cardnum
#     num, title, shop, date, price = str.split()
#     d = {"fnum":fnum,"cnum":cnum,"title":title,"shop":shop,"date":date,"price":price}
#     return d

d_list = []

print("\nStart OCR")

errlist = []
errcnt = 0

tools = pyocr.get_available_tools()
tool = tools[0]
builder = pyocr.builders.TextBuilder(tesseract_layout=6)
for i in tqdm(range(len(frames))):  # len(frames)
    cards = get_cards_from_screen(frames[i])
    errcnt = 0
    for j in range(len(cards)):
        pilimage= Image.fromarray(cards[j])
        text = tool.image_to_string(pilimage,lang='jpn',builder=builder).replace(" ", "").split()
        k = re.sub(r"\D", "", text[0])
        v = next((d["Num"] for d in d_list if d["Num"] == k), None)
        if v is None:
            d = {"Fn": i, "Cn": j, "Num": k, "str": text[1:]}
            d_list.append(d)
            errcnt = errcnt +1 
            # print("alreadyExist",end="")
    # 記録
    errlist.append([i,j,errcnt])

with open("out/"+video_path +"_"+str(PER)+".json", mode="wt", encoding="utf-8") as f:
    json.dump(d_list, f, ensure_ascii=False, indent=2)

print("finish")
# print("nextCard")
# text = text.replace(" ", "")
# with open("out/text.txt",mode='a') as f:
#     f.write("Frame="+str(i)+"Cards="+str(j)+"\n"+text+"\n")

# 辞書の中身
# Frame=0Cards=0
# 決済番号03498895099141480453
# ダイソーに支払い
# 愛知東海店
# 2020年11月27日18時50分
# 110m
# Frame,Card,num,title,shop,date,price


# # 最初のフレームを追加
# stitched_frames = [frames[0]]

# np.save("out/fr1", frames[1])

# # フレーム間の重複を削除
# print("\nフレーム間の重複を削除しています...")
# for i in tqdm(range(1, len(frames))):
#     overlap_height = detect_overlap(stitched_frames[-1], frames[i])
#     if overlap_height > 0:
#         new_frame = frames[i][overlap_height:]
#     else:
#         new_frame = frames[i]
#     stitched_frames.append(new_frame)

# # 縦長画像の高さを計算
# total_height = sum(frame.shape[0] for frame in stitched_frames)
# frame_width = frames[0].shape[1]

# # 縦長画像を作成
# stitched_image = Image.new("RGB", (frame_width, total_height))

# # 各フレームを縦に結合
# print("フレームを縦に結合しています...")
# current_y = 0
# for frame in tqdm(stitched_frames):
#     frame_image = Image.fromarray(frame)
#     stitched_image.paste(frame_image, (0, current_y))
#     current_y += frame_image.height

# # 縦長画像を保存
# stitched_image.save("stitched_image2.png")

# print("縦長画像の作成が完了しました")
