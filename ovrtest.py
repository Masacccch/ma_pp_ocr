import cv2
from PIL import Image
import numpy as np
from tqdm import tqdm


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



# 動画のパスを指定
video_path = "ppdc2.mp4"

# 動画を読み込む
cap = cv2.VideoCapture(video_path)

# フレームリストを初期化
frames = np.empty((0, 1920, 1080, 3), np.uint8)
# frames_normal = []

# フレームを読み込む
print("動画を読み込んでいます...")
cnt = 0
while True:
    ret, frame = cap.read()
    cnt = cnt + 1
    if cnt % 10 != 0:
        print("-", end="")
        continue
    else:
        print("*", end="")
    if not ret:  # or cnt > 25:
        break
    # フレームをRGBに変換 (OpenCVはBGRで読み込むので)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frames = np.append(frames,frame[np.newaxis],axis=0)
    # frames_normal.append(frame)

# 動画の読み込みを終了
cap.release()

# 最初のフレームを追加
stitched_frames = [frames[0]]

np.save('out/fr1',frames[1])

# # フレーム間の重複を削除
# print("\nフレーム間の重複を削除しています...")
# for i in tqdm(range(1, len(frames))):
#     overlap_height = detect_overlap(stitched_frames[-1], frames[i])
#     if overlap_height > 0:
#         new_frame = frames[i][overlap_height:]
#     else:
#         new_frame = frames[i]
#     stitched_frames.append(new_frame)

# 縦長画像の高さを計算
total_height = sum(frame.shape[0] for frame in stitched_frames)
frame_width = frames[0].shape[1]

# 縦長画像を作成
stitched_image = Image.new("RGB", (frame_width, total_height))

# 各フレームを縦に結合
print("フレームを縦に結合しています...")
current_y = 0
for frame in tqdm(stitched_frames):
    frame_image = Image.fromarray(frame)
    stitched_image.paste(frame_image, (0, current_y))
    current_y += frame_image.height

# 縦長画像を保存
stitched_image.save("stitched_image2.png")

print("縦長画像の作成が完了しました")
