import sys
sys.path.append('/usr/lib/python3/dist-packages')  # 가장 위에 추가

import time
import cv2
import numpy as np

# 수신되는 데이터 형식
# ✅ 새로운 놀이 범위 좌표 수신: [[295.375, 54.75], [342.375, 165.75], [487.375, 125.75], [399.375, 254.75], [450.375, 356.75], [317.375, 292.75], [223.375, 377.75], [249.375, 239.75], [119.375, 182.75], [249.375, 175.75], [287.375, 51.75]]

# 카메라 초기화
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=camera.resolution)

# 잠시 대기 (카메라 센서 준비)
time.sleep(0.1)

# 초기 대응점
ptSrc = np.array([
    [100, 50],
    [500, 50],
    [500, 400],
    [100, 400]
], dtype=np.float32)

def scale_around_point(points, scale_factors, origin):
    points = np.asarray(points)
    origin = np.asarray(origin)
    shifted_points = points - origin
    if np.isscalar(scale_factors):
        scaled_points = shifted_points * scale_factors
    else:
        scaled_points = shifted_points * scale_factors
    return scaled_points + origin

# 실시간 스트리밍
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    img = frame.array
    vis_img = img.copy()

    center = np.mean(ptSrc, axis=0)
    scaled_poly = scale_around_point(ptSrc, scale_factors=(0.8, 0.8), origin=center)

    # 원래 좌표 표시
    for i, s in enumerate(ptSrc):
        cv2.circle(vis_img, tuple(s.astype(int)), 5, (255, 0, 0), -1)
    
    # 스케일링 좌표 표시
    for i, s in enumerate(scaled_poly):
        cv2.circle(vis_img, tuple(s.astype(int)), 5, (0, 0, 255), -1)

    cv2.imshow("Pi Camera Polygon", vis_img)
    key = cv2.waitKey(1) & 0xFF

    rawCapture.truncate(0)  # 다음 프레임 준비

    if key == ord('q'):
        break

cv2.destroyAllWindows()