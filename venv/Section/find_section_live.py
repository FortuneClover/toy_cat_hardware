# camera.py 실시간 영상 JPEG 프레임으로 변환코드
import sys
sys.path.append('/usr/lib/python3/dist-packages')

import cv2
from picamera2 import Picamera2
from libcamera import controls
import numpy as np

fx = 2592
fy = 1944
cx = 1296
cy = 972
k1 = -0.317640
k2 = -0.099809
k3 = -0.006748
k4 = 0.010827

dist = np.array([k1, k2, k3, k4], dtype=np.float64)

mtx = np.array([[fx, 0, cx],
                [0, fy, cy],
                [0, 0, 1]], dtype=np.float64)

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (2592, 1944)}))
picam2.start()

# 고정된 해상도 기준 (예: 카메라 해상도에 맞게 조정)
frame_shape = (2592, 1944)  # height, width
height, width = frame_shape

# 대응점 정의 (카메라 영상 상의 좌표 기준으로 조정 필요)
ptSrc = np.array([
    [950, 527],
    [2200, 500],
    [2200, 1400],
    [800, 1500]
], dtype=np.float32)

# 중심점 계산
center = np.mean(ptSrc, axis=0)

# 삼각형 분할 정의
polygons = [
    np.array([ptSrc[0], ptSrc[1], center], dtype=np.int32).reshape((-1, 1, 2)),
    np.array([ptSrc[1], ptSrc[2], center], dtype=np.int32).reshape((-1, 1, 2)),
    np.array([ptSrc[2], ptSrc[3], center], dtype=np.int32).reshape((-1, 1, 2)),
    np.array([ptSrc[3], ptSrc[0], center], dtype=np.int32).reshape((-1, 1, 2)),
]

# 마스크 생성 및 내부 좌표 계산 (고정)
mask = np.zeros((height, width), dtype=np.uint8)
cv2.fillPoly(mask, polygons, color=255)
ys, xs = np.where(mask == 255)
coords_inside = np.column_stack((xs, ys))

# 루프: 실시간 영상 위에 좌표 및 폴리곤 시각화
while True:
    frame = picam2.capture_array()

    # 현재 프레임 해상도와 다르면 리사이즈 또는 좌표 조정 필요
    if frame.shape[0] != height or frame.shape[1] != width:
        frame = cv2.resize(frame, (width, height))

    vis_img = frame.copy()

    # 대응점 및 중심점 표시
    for i, s in enumerate(ptSrc):
        cv2.circle(vis_img, tuple(s.astype(int)), 10, (255, 0, 0), -1)
        cv2.putText(vis_img, f"S{i+1}", (int(s[0]) + 10, int(s[1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    cv2.circle(vis_img, tuple(center.astype(int)), 10, (0, 0, 255), -1)
    cv2.putText(vis_img, "Center", (int(center[0]) + 10, int(center[1]) - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # 내부 좌표 시각화 (너무 많을 경우 일부만)
    for pt in coords_inside[::100]:  # 성능을 위해 일부만 (100개마다 1개)
        cv2.circle(vis_img, tuple(pt), 1, (0, 255, 0), -1)

    # 윤곽선 시각화
    colors = [(255, 0, 0), (0, 0, 255), (165, 165, 165), (255, 255, 255)]
    for poly, color in zip(polygons, colors):
        cv2.polylines(vis_img, [poly], isClosed=True, color=color, thickness=3)

    # 화면 출력
    cv2.imshow("Live Overlay", vis_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()