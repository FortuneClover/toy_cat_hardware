import RPi.GPIO as GPIO
import time

# 사용할 GPIO 핀 번호 설정
SERVO_PIN_1 = 17  # 첫 번째 서보모터 연결 핀
SERVO_PIN_2 = 22  # 두 번째 서보모터 연결 핀

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN_1, GPIO.OUT)
GPIO.setup(SERVO_PIN_2, GPIO.OUT)

# PWM 객체 생성 (주파수 50Hz)
servo1 = GPIO.PWM(SERVO_PIN_1, 50)
servo2 = GPIO.PWM(SERVO_PIN_2, 50)

# PWM 시작 (초기 duty cycle 0)
servo1.start(0)
servo2.start(0)

# 각도 -> 듀티 사이클 변환 함수
def set_angle(servo, angle):
    duty = 2.5 + (angle / 18)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.1)
    servo.ChangeDutyCycle(0)  # 서보 떨림 방지

try:
    while True:
        print("open")
        set_angle(servo1, 0)
        set_angle(servo2, 180)
        time.sleep(2)

        print("close")
        set_angle(servo1, 90)
        set_angle(servo2, 90)
        time.sleep(2)

except KeyboardInterrupt:
    print("종료 중...")

finally:
    servo1.stop()
    servo2.stop()
    GPIO.cleanup()
