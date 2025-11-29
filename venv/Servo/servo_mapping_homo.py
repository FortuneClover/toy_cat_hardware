import sys
import os
import time
import math
import numpy as np
import cv2

# 현재 파일 기준 상위 폴더 경로 얻기
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 상위 폴더를 모듈 경로에 추가
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from Laser import laser_on, laser_off

# ---- 설정 ----
CAMERA_HEIGHT = 1.0  # 카메라 높이 (m)
x_scale = 0.02 / 100   # 100픽셀당 2cm → m/px
y_scale = 0.025 / 100  # 100픽셀당 2.5cm → m/px

# ---- 테스트 포인트 (픽셀) ----
points = [[276, 71], [376, 71], [376, 171], [276, 171], [276, 71]]

# ---- 이미지 상 4점 → 실제 좌표 4점 대응 ----
image_points = np.array([
    [276, 71],   # 좌상
    [376, 71],   # 우상
    [376, 171],  # 우하
    [276, 171]   # 좌하
], dtype=np.float32)

world_points = np.array([
    [276 * x_scale, 71 * y_scale],
    [376 * x_scale, 71 * y_scale],
    [376 * x_scale, 171 * y_scale],
    [276 * x_scale, 171 * y_scale]
], dtype=np.float32)

# 호모그래피 계산
H, status = cv2.findHomography(image_points, world_points)

# ---- 픽셀 → 실제 좌표 변환 ----
def pixel_to_world(u, v, H):
    pixel_point = np.array([[u, v, 1]]).T
    world_point = H @ pixel_point
    world_point /= world_point[2, 0]  # Homogeneous to Cartesian
    x = world_point[0, 0]
    y = world_point[1, 0]
    return x, y

# ---- 실제 좌표 → 서보 각도 ----
def world_to_servo_angle(x, y, H_camera=CAMERA_HEIGHT):
    theta_pan = math.atan2(x, H_camera)
    theta_tilt = math.atan2(y, H_camera)
    pan_deg = math.degrees(theta_pan)
    tilt_deg = math.degrees(theta_tilt)
    return pan_deg, tilt_deg

# ---- 서보 초기화 ----
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x7f)
pca.frequency = 50

servo_x_motor = servo.Servo(pca.channels[14])
servo_y_motor = servo.Servo(pca.channels[15])

print("🚀 Servo control 시작합니다. (Ctrl+C 로 종료)")
laser_on()

try:
    for tx, ty in points:
        # 1) 호모그래피로 실제 좌표 계산
        x, y = pixel_to_world(tx, ty, H)
        
        # 2) 실제 좌표 → 서보 각도
        pan, tilt = world_to_servo_angle(x, y)
        
        # 3) 서보 범위 제한 및 매핑
        servo_pan  = max(0, min(180, 90 + pan))
        servo_tilt = max(0, min(180, 90 - tilt))
        
        print(f"➡️ pixel: {tx:.2f},{ty:.2f} -> world: {x:.3f},{y:.3f} -> servo: {servo_pan:.2f},{servo_tilt:.2f}")
        
        # 4) 서보 이동
        servo_x_motor.angle = servo_pan
        servo_y_motor.angle = servo_tilt
        
        time.sleep(3)

except KeyboardInterrupt:
    print("🛑 정지합니다.")
    laser_off()

finally:
    servo_x_motor.angle = 90
    servo_y_motor.angle = 90
    pca.deinit()
    laser_off()
    print("🔌 PCA9685 종료 완료.")
