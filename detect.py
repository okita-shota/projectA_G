import cv2
import math
from ultralytics import YOLO

# モデルの読み込み。姿勢推論用のモデルデータを読み込む
model = YOLO("yolov8n-pose.pt")

# 本体のウェブカメラからキャプチャする設定
video_path = 0  # 本体に付属のカメラを指定
capture = cv2.VideoCapture(video_path)

# keypointの位置毎の名称定義
KEYPOINTS_NAMES = [
    "nose",
    "eye(L)",
    "eye(R)",
    "ear(L)",
    "ear(R)",
    "shoulder(L)",
    "shoulder(R)",
    "elbow(L)",
    "elbow(R)",
    "wrist(L)",
    "wrist(R)",
    "hip(L)",
    "hip(R)",
    "knee(L)",
    "knee(R)",
    "ankle(L)",
    "ankle(R)",
]

# スクワット回数
squat_count = 0
# 前回の判定結果 (True: スクワット状態, False: 非スクワット状態)
previous_state = False 

# スクワット判定関数
def is_squat(keypoints):
    try:
        # 左膝の角度を計算
        left_knee_angle = calculate_angle(keypoints[11], keypoints[13], keypoints[15])
    except (IndexError, TypeError):
        return False  # 骨格情報が正しく取得できなかった場合はFalseを返す

    # 角度が閾値以下になったらスクワットと判定
    if left_knee_angle < 100:  # 閾値は適宜調整
        return True
    else:
        return False

def calculate_angle(a, b, c):
    # 3点の座標から角度を計算
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang

while capture.isOpened():
    success, frame = capture.read()
    if success:
        # 推論を実行
        results = model(frame)

        annotatedFrame = results[0].plot()

        # 検出オブジェクトの名前、バウンディングボックス座標を取得
        names = results[0].names
        classes = results[0].boxes.cls
        boxes = results[0].boxes

        for box, cls in zip(boxes, classes):
            name = names[int(cls)]
            x1, y1, x2, y2 = [int(i) for i in box.xyxy[0]]

        if len(results[0].keypoints) == 0:
            continue

        # 姿勢分析結果のキーポイントを取得する
        keypoints = results[0].keypoints
        confs = keypoints.conf[0].tolist()  # 推論結果:1に近いほど信頼度が高い
        xys = keypoints.xy[0].tolist()  # 座標

        # スクワット判定
        current_state = is_squat(xys)

        # 状態遷移時にカウントアップ
        if current_state and not previous_state:
            squat_count += 1

        previous_state = current_state

        for index, keypoint in enumerate(zip(xys, confs)):
            score = keypoint[1]

            # スコアが0.5以下なら描画しない
            if score < 0.5:
                continue

            x = int(keypoint[0][0])
            y = int(keypoint[0][1])
            # 紫の四角を描画
            annotatedFrame = cv2.rectangle(
                annotatedFrame,
                (x, y),
                (x + 3, y + 3),
                (255, 0, 255),
                cv2.FILLED,
                cv2.LINE_AA,
            )
            # キーポイントの部位名称を描画
            annotatedFrame = cv2.putText(
                annotatedFrame,
                KEYPOINTS_NAMES[index],
                (x + 5, y),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1.3,
                color=(255, 0, 255),
                thickness=2,
                lineType=cv2.LINE_AA,
            )

        # スクワット回数を表示
        cv2.putText(
            annotatedFrame,
            f"Squat Count: {squat_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        print("------------------------------------------------------")

        cv2.imshow("YOLOv8 human pose estimation", annotatedFrame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

capture.release()
cv2.destroyAllWindows()