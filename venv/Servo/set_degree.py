import RPi.GPIO as GPIO
import time

# 사용할 GPIO 핀 번호
SERVO_PIN = 18

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# PWM 객체 생성, 주파수 = 50Hz
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def set_angle(angle):
    # 각도를 PWM 듀티사이클로 변환 (0~180도 → 5~10)
    duty = 2.5 + (angle / 180.0) * 10
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)  # 모터가 움직일 시간
    pwm.ChangeDutyCycle(0)  # 서보 떨림 방지

try:
    while True:
        angle = int(input("각도 입력 (0~180): "))
        if 0 <= angle <= 180:
            set_angle(angle)
        else:
            print("0~180 사이의 값을 입력하세요.")
except KeyboardInterrupt:
    pass

# 정리
pwm.stop()
GPIO.cleanup()
