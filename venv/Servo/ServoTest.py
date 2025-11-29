import time  # Import time module to introduce delays in the program
import busio  # Import busio module to set up I2C communication
from adafruit_motor import servo  # Import servo module to control the servo motor
from adafruit_pca9685 import PCA9685  # Import PCA9685 module to interface with the PCA9685 PWM controller
from board import SCL, SDA  # Import specific pins SCL and SDA for I2C communication

# Initialize I2C communication on the Raspberry Pi using the SCL and SDA pins.
# I2C 통신 활성화, 핀 설정 코드
i2c = busio.I2C(SCL, SDA)


# Create an instance of the PCA9685 class using the I2C communication.
# This instance will be used to control PWM signals, which are typically used for controlling servos.

pca = PCA9685(i2c, address=0x7f)

# Set the PWM frequency to 50Hz, which is the standard frequency for controlling servo motors.
pca.frequency = 50

# Create a ContinuousServo object on channel 0 of the PCA9685.
# A continuous servo can rotate indefinitely in either direction based on the throttle value.
# PCA9685 보드에서 몇번째 핀에 연결된 서보모터를 제어할 것인지.
# 0 ~ 15 번까지 있다.
servo14 = servo.ContinuousServo(pca.channels[14])
servo15 = servo.ContinuousServo(pca.channels[15])

# Set the throttle to full speed forward (1.0).
# Throttle value can range from -1.0 (full speed reverse) to 1.0 (full speed forward).
servo14.throttle = 1.0
servo15.throttle = 1.0

# # Keep the servo running at full speed for 3 seconds.
# time.sleep(3)

# # Stop the servo by setting the throttle to 0.0 (no movement).
# servo14.throttle = 0.0
# servo15.throttle = 0.0
# # Briefly sleep for 0.1 seconds to ensure the stop command is fully processed.
# time.sleep(0.1)

# # Deinitialize the PCA9685 to free up resources and reset the hardware.
# # PCA9685 동작 종료 코드
# pca.deinit()

# import time
# import busio
# from adafruit_motor import servo
# from adafruit_pca9685 import PCA9685
# from board import SCL, SDA
# import numpy as np
# import cv2

# # ==============================
# # 카메라 내부 파라미터 (IMX219 8MP)
# # ==============================
# fx, fy = 3280, 2464
# cx, cy = 1640, 1232

# # ==============================
# # 카메라 물리 파라미터
# # ==============================
# ch = 220.0  # cm
# d = 3.0     # cm

# # ==============================
# # PCA9685 설정
# # ==============================
# i2c = busio.I2C(SCL, SDA)
# pca = PCA9685(i2c, address=0x7f)  # 일반적으로 0x40
# pca.frequency = 50

# # ==============================
# # 서보 설정 (0~180도)
# # ==============================
# servo_tilt = servo.Servo(pca.channels[14])
# servo_yaw  = servo.Servo(pca.channels[15])

# # ==============================
# # 픽셀 → 각도 변환
# # ==============================
# def calc_servo_angles(u, v):
#     X = (u - cx) / fx
#     Y = (v - cy) / fy
#     Z = 1.0

#     theta_rad = np.arctan2(Y, Z)
#     theta_deg = np.degrees(theta_rad)

#     fl = ch / np.cos(theta_rad)

#     alpha_rad = np.arctan(fl / d)
#     alpha_deg = np.degrees(alpha_rad)

#     return theta_deg, alpha_deg

# # ==============================
# # 서보에 각도 적용
# # ==============================
# def move_servos(tilt_deg, yaw_deg):
#     tilt_angle = 90 + tilt_deg
#     yaw_angle  = 90 + yaw_deg

#     # 0~180 클램프
#     tilt_angle = max(0, min(180, tilt_angle))
#     yaw_angle  = max(0, min(180, yaw_angle))

#     servo_tilt.angle = tilt_angle
#     servo_yaw.angle  = yaw_angle

#     print(f"[SERVO] tilt={tilt_angle:.2f}, yaw={yaw_angle:.2f}")

# # ==============================
# # 카메라 열기
# # ==============================
# cap = cv2.VideoCapture(0)  # libcamera가 만든 /dev/video0

# if not cap.isOpened():
#     print("카메라 열기 실패!")
#     exit()

# # 해상도 설정 (원하는 출력 크기)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# print("카메라 시작됨")

# # ==============================
# # 메인 루프
# # ==============================

# if __name__ == "__main__":
# try:
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             continue

#         # 원하는 조준 좌표 (예시)
#         u, v = 800, 400

#         # ==========================
#         # 화면에 조준 십자선 표시
#         # ==========================
#         cv2.line(frame, (u-20, v), (u+20, v), (0, 0, 255), 2)
#         cv2.line(frame, (u, v-20), (u, v+20), (0, 0, 255), 2)
#         cv2.circle(frame, (u, v), 5, (0, 0, 255), -1)

#         # ==========================
#         # 각도 계산 및 적용
#         # ==========================
#         tilt_deg, yaw_deg = calc_servo_angles(u, v)
#         move_servos(tilt_deg, yaw_deg)

#         # 텍스트 표시
#         cv2.putText(frame, f"tilt={tilt_deg:.1f}, yaw={yaw_deg:.1f}",
#                     (30, 40), cv2.FONT_HERSHEY_SIMPLEX,
#                     1.0, (0, 255, 0), 2)

#         cv2.imshow("Camera Aim Assist", frame)

#         # 종료
#         if cv2.waitKey(1) & 0xFF == 27:  # ESC
#             break

# except KeyboardInterrupt:
#     print("종료 중...")

# finally:
#     cap.release()
#     cv2.destroyAllWindows()
#     pca.deinit()
