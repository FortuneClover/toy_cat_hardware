import sys
import os

# 현재 파일 기준 상위 폴더 경로 얻기
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 카메라 렌즈로부터 레이저까지의 x거리 : 7~8cm
# 카메라 렌즈로부터 레이저까지의 y거리 : 1~2cm
# 카메라 렌즈로부터 레이저까지의 직선거리 : 8cm
# 1단 축으로부터 레이저까지의 x거리 : 1cm
# 1단 축으로부터 레이저까지의 y거리  : 1.5~2cm
# 1단 축으로부터 레이저까지의 직선거리  : 2.5cm

# 상위 폴더를 모듈 경로에 추가
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    import time  # Import time module to introduce delays in the program
    import busio  # Import busio module to set up I2C communication
    from adafruit_motor import servo  # Import servo module to control the servo motor
    from adafruit_pca9685 import PCA9685  # Import PCA9685 module to interface with the PCA9685 PWM controller
    from board import SCL, SDA  # Import specific pins SCL and SDA for I2C communication
    from Laser import laser_on, laser_off
    import math

    # LASER_OFFSET_X = -0.08  # 카메라 기준 왼쪽으로 8cm -> x축 음수
    # LASER_OFFSET_Y = 0.02   # 카메라 기준 위쪽으로 2cm -> y축 양수
    LASER_OFFSET_X = -0.3
    LASER_OFFSET_Y = 0.2


    def pixel_to_servo_angle(u, v,
                         H=1,          # 카메라 높이(미터)
                         p=1.12e-6,      # 픽셀 크기(미터)
                         f=3.04e-3,      # 초점거리(미터)
                         width=640, height=480):

        # 1) 이미지 중심
        uc = width / 2
        vc = height / 2

        # 2) 픽셀당 실제 길이
        L = (H * p) / f
        
        # temp
        x_scale = 0.02 / 100
        y_scale = 0.025 / 100

        # 3) 픽셀 → 바닥 좌표
        # x = -(u - uc) * L + LASER_OFFSET_X
        # y = -(v - vc) * L + LASER_OFFSET_Y
        x = (u - uc) * x_scale + LASER_OFFSET_X
        y = -(v - vc) * y_scale + LASER_OFFSET_Y

        # 4) 바닥 좌표 → 서보 각도
        theta_pan  = math.atan2(x, H) # 좌우
        theta_tilt = math.atan2(y, H) # 상하

        # 5) 각도를 degree로 변환
        pan_deg  = math.degrees(theta_pan)
        tilt_deg = math.degrees(theta_tilt)

        return pan_deg, tilt_deg, x, y

    def map_range(value, min_input, max_input, min_output, max_output):
        return min_output + ( (value - min_input) * (max_output - min_output) / (max_input - min_input) )


    def point_to_servo(x, y):
        # 좌우(servo14): x축 기준
        servo_x = map_range(x, 0, 480, 1.0, -1.0)

        # 상하(servo15): y축 기준 (상하 반전 필요할 수도 있음)
        servo_y = map_range(y, 0, 640, 1.0, -1.0)

        return servo_x, servo_y

    def point_to_servo_angle(x, y):
        # 좌우(servo14): x축 기준, 0~180도
        servo_x = map_range(x, 0, 480, 180, 0)

        # 상하(servo15): y축 기준, 0~180도
        # 상하 반전 필요시: map_range(y, 0, 640, 180, 0)
        servo_y = map_range(y, 0, 640, 0, 180)

         # 각도를 0~180으로 clamp
        servo_x = max(0, min(180, servo_x))
        servo_y = max(0, min(180, servo_y))

        return servo_x, servo_y

    # print(point_to_servo(48.375, 122.75))
    # print(point_to_servo(297.375, 123.75))
    # print(point_to_servo(584.375, 1.75))

    # ---- 1) Section polygon 세팅 ----
    # points = [[0.375, 28.75], [91.375, 45.75], [104.375, 1.75], [158.375, 4.75], [123.375, 161.75], [10.375, 164.75], [1.375, 33.75]]
    # points = [[105.375, 359.75], [173.375, 161.75], [281.375, 51.75], [394.375, 170.75], [435.375, 344.75], [118.375, 362.75]]
    # points = [[250, 69], [350, 69], [450, 69], [550, 69], [650, 69]]
    
    # x test
    # points = [[550, 69], [650, 69]]
    # y test
    points = [[276, 71], [376, 71], [376, 171], [276, 171], [276, 71]]

    # ---- 2) Servo 초기화 ----
    i2c = busio.I2C(SCL, SDA)

    pca = PCA9685(i2c, address=0x7f)
    pca.frequency = 50

    # servo_x = servo.ContinuousServo(pca.channels[14])  # 좌우
    # servo_y = servo.ContinuousServo(pca.channels[15])  # 상하
    servo_x_motor = servo.Servo(pca.channels[14])  # 좌우 서보
    servo_y_motor = servo.Servo(pca.channels[15])  # 상하 서보


    print("🚀 Servo control 시작합니다. (Ctrl+C 로 종료)")
    laser_on()
    try:
        for tx, ty in points:
            # print(tx, ty)
            # pan, tilt, x, y = pixel_to_servo_angle(320, 240)
            pan, tilt, x, y = pixel_to_servo_angle(tx, ty)
            # print("pan:", pan, "tilt:", tilt)
            # print("real-world coords:", x, y)

            # ---- 4) 서보 좌표 매핑 ----
            # sx, sy = point_to_servo(x, y)
            sx, sy = point_to_servo_angle(tx, ty)

            # print(f"➡️ Servo throttle = X:{sx:.2f}, Y:{sy:.2f}")
            # print(f"➡️ Servo angle = X:{sx:.2f}, Y:{sy:.2f}")
            print(f"➡️ Servo angle = X:{x:.2f}, Y:{y:.2f}")

            # ---- 5) 서보모터 움직임 ----
            # servo_x.throttle = sx
            # servo_y.throttle = sy
            # servo_x_motor.angle = sx
            # servo_y_motor.angle = sy
            
            # temp
            servo_pan  = 90 + pan
            servo_tilt = 90 - tilt  # y축 반전 필요

            # 서보 범위 제한
            servo_pan  = max(0, min(180, servo_pan))
            servo_tilt = max(0, min(180, servo_tilt))

            
            print(f"➡️ pixel x,y = {tx:.2f}, {ty:.2f}")
            print(f"➡️ world x,y = {x:.2f}, {y:.2f}")
            print(f"➡️ servo pan tilt = {servo_pan:.2f}, {servo_tilt:.2f}")

            # ===== 서보 이동 =====
            servo_x_motor.angle = servo_pan
            servo_y_motor.angle = servo_tilt

            # 유지 시간
            time.sleep(3)

            # ---- 6) 잠시 멈춤 ----
            # servo_x.throttle = 0
            # servo_y.throttle = 0
            # time.sleep(0.2)

    except KeyboardInterrupt:
        print("🛑 정지합니다.")
        lsaer_off()

    finally:
        # 안전하게 off
        # servo_x.throttle = 0
        # servo_y.throttle = 0
        servo_x_motor.angle = 90
        servo_y_motor.angle = 90
        pca.deinit()
        laser_off()
        print("🔌 PCA9685 종료 완료.")