import RPi.GPIO as GPIO
import time

LASER_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(LASER_PIN, GPIO.OUT)

try:
    print("레이저 ON")
    GPIO.output(LASER_PIN, GPIO.LOW)  # 레이저 켜기
    time.sleep(5)  # 5초 동안 유지

    print("레이저 OFF")
    GPIO.output(LASER_PIN, GPIO.HIGH)   # 레이저 끄기

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
