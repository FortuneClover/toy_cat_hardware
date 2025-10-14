import cv2
import numpy as np
import random
from shapely.geometry import Polygon, Point

# 1. 이미지 불러오기
original_img = cv2.imread("undistorted_2592x1944.jpg")
if original_img is None:
    raise FileNotFoundError("이미지를 불러올 수 없습니다.")

height, width = original_img.shape[:2]

# 2. 마스크와 시각화용 이미지 생성
mask = np.zeros((height, width), dtype=np.uint8)        # 1채널 마스크
vis_img = original_img.copy()                            # 시각화용 이미지

# 3. 대응점 정의
ptSrc = np.array([
    [950, 527],
    [2200, 500],
    [2200, 1400],
    [800, 1500]
], dtype=np.float32)

# 4. 무게 중심 계산
center = np.mean(ptSrc, axis=0)

# 5. 시각화: 라벨 및 중심점 표시
for i, s in enumerate(ptSrc):
    cv2.circle(vis_img, tuple(s.astype(int)), 10, (255, 0, 0), -1)
    cv2.putText(vis_img, f"S{i+1}", (int(s[0]) + 10, int(s[1]) - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

cv2.circle(vis_img, tuple(center.astype(int)), 10, (0, 0, 255), -1)
cv2.putText(vis_img, "Center", (int(center[0]) + 10, int(center[1]) - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

def scale_around_point(points, scale_factors, origin):
    """
    points: (N, 2) ndarray - 도형 좌표
    scale_factors: (2,) or scalar - x, y 축 배율 또는 하나의 값
    origin: (2,) - 스케일링 기준점 (x, y)
    """
    points = np.asarray(points)
    origin = np.asarray(origin)
    
    # 1. 원점 기준으로 이동
    shifted_points = points - origin
    
    # 2. 스케일링 적용
    if np.isscalar(scale_factors):
        scaled_points = shifted_points * scale_factors
    else:
        scaled_points = shifted_points * scale_factors
    
    # 3. 다시 원위치
    result = scaled_points + origin
    return result

# 테스트
ptSrc = np.array([
    [950, 527],
    [2200, 500],
    [2200, 1400],
    [800, 1500]
], dtype=np.float32)

center = np.mean(ptSrc, axis=0)  # 도형 중심에서 스케일링

scaled_poly = scale_around_point(ptSrc, scale_factors=(0.8, 0.8), origin=center)

for i, s in enumerate(scaled_poly):
    cv2.circle(vis_img, tuple(s.astype(int)), 10, (0, 0, 255), -1)
    cv2.putText(vis_img, f"S{i+1}", (int(s[0]) + 10, int(s[1]) - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

cv2.circle(vis_img, tuple(center.astype(int)), 10, (0, 255, 0), -1)
cv2.putText(vis_img, "Scaled_Center", (int(center[0]) + 10, int(center[1]) - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

# 다각형 정의
poly = Polygon(scaled_poly)

# 랜덤 좌표 생성
def generate_point(poly):
    min_x, min_y, max_x, max_y = poly.bounds
    
    while True:
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)
        point = Point(x, y)
        
        if poly.contains(point):
            return x, y

for _ in range(30):
    x, y = generate_point(poly)
    cv2.circle(vis_img, (int(x),int(y)), 10, (255, 255, 255), -1)

# 10. 출력
cv2.namedWindow("Polygon Area Visualization", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Polygon Area Visualization", 960, 540)
cv2.imshow("Polygon Area Visualization", vis_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
