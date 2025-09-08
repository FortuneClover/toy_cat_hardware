import numpy as np
import cv2

# 카메라 행렬 및 왜곡 계수
fx = 2592
fy = 1944
cx = 1296
cy = 972
k1 = -0.317640
k2 = -0.099809
k3 = -0.006748
k4 = 0.010827  # fisheye 왜곡에서는 k4가 추가로 필요
dist = np.array([k1, k2, k3, k4], dtype=np.float64)

mtx = np.array([[fx, 0, cx],
                [0, fy, cy],
                [0, 0, 1]], dtype=np.float64)

# 이미지 불러오기
image = cv2.imread('testing_photo.jpg')
h, w = image.shape[:2]

# 새로운 카메라 행렬 계산
newcameramtx = mtx.copy()

# 왜곡 보정 매핑 생성
map1, map2 = cv2.fisheye.initUndistortRectifyMap(
    mtx, dist, np.eye(3), newcameramtx, (w, h), cv2.CV_16SC2)

# 보정 이미지 생성
dst = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

# 보정된 이미지 저장 (원래 해상도 유지)
cv2.imwrite('undistorted_2592x1944.jpg', dst)