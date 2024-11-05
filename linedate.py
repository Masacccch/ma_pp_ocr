# Lineの

from datetime import datetime
# matplotlibのpyplotをインポート
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # mdateのインポート

def countlen(str):
    if str[0] == '"' :
        # print("long!" + str)
        return -1*len(str)
    else :
        # print(len(str))
        return len(str)

print("start line read")

cnt = 0
date_object = datetime.strptime("00:01","%H:%M")

d_data = []
hom_cnt = yur_cnt =0
hom_len = yur_len = 0
longmode = False
is_bef_hom =True


with open('./Yuri_talk.txt') as f:
    for line in f:
        cnt+=1
        if cnt >100:
            break
            # pass

        # 10文字以上で日付かメッセージ
        if len(line) >= 10 :
            try:
                # メッセージかも
                message_time = datetime.strptime(line[:5], "%H:%M")

                mslen = countlen(line[12:])
                if mslen <= -1:
                    longmode = True
                    mslen = mslen*-1

                if line[6:7] == "本" :
                    hom_cnt += 1
                    hom_len += mslen
                    is_bef_hom = True
                elif line[6:7] == "田" :
                    yur_cnt += 1
                    yur_len += mslen
                    is_bef_hom = False
                # 変換結果の表示
                print(message_time,line,mslen)
            except ValueError:
                # 日付かも
                # 文字列を日付型に変換
                try:
                    n_date_object = datetime.strptime(line[:10], "%Y/%m/%d")
                    # 　こっから次の日の処理
                    # まず前回の日付のend
                    d_data.append([date_object,hom_cnt,hom_len,yur_cnt,yur_len])
                    date_object = n_date_object
                    hom_cnt = yur_cnt =0
                    hom_len = yur_len = 0
                    # 変換結果の表示
                    # print(date_object)
                except ValueError:
                    # ここで長文２行目以降の可能性
                    if longmode :
                        # 終端検知
                        if line[-2:-1]  == '"':
                            longmode = False

                        # lenカウント
                        if is_bef_hom :
                            hom_len += countlen(line)
                        else :
                            yur_cnt += countlen(line)
                        print("[L]",message_time, line, mslen)
                    # print("日付型への変換に失敗しました。")

        # print(line)
print ("end")
d_data = d_data[1:]

# # 横軸（x軸）に日付を設定
X = [row[0] for row in d_data]

# # 縦軸：hom cnt
HC = [row[1] for row in d_data]
HL = [row[2] for row in d_data]
YC = [row[3] for row in d_data]
YL = [row[4] for row in d_data]

# # グラフ作図
# plt.plot(X, HC, marker='o')
# plt.plot(X, HL, marker="o")
# plt.plot(X, YC, marker='o')
# plt.plot(X, YL, marker="o")

# plot用の箱を作成
fig, ax = plt.subplots(figsize=(19.2, 10.8))
ax2 = ax.twinx()

# x軸に時間、y軸にco2の排出量を記載
# CO2排出量
ax.plot(X,HC, marker="o", linestyle="--", color="red")
ax.plot(X, YC, marker="o", linestyle="--", color="pink")
ax.set_xlabel("Date")
ax.set_ylabel("Posts", color="r")
ax.tick_params("y", colors="r")

# メタン排出量
ax2.plot(X ,HL, marker="x", linestyle="-", color="black")
ax2.plot(X, YL, marker="x", linestyle="-", color="gray")
ax2.set_ylabel("Length", color="b")
ax2.tick_params("y", colors="b")

fig.autofmt_xdate(rotation=90)
locator = mdates.DayLocator(interval=2)
ax.xaxis.set_major_locator(locator)
plt.savefig("out/sin.png")

print("end2")
