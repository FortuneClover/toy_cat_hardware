import RPi.GPIO as GPIO
import time

SERVO_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz
servo.start(0)

try:
    for duty in range(20, 130, 5):  # 2.0% ~ 13.0%
        actual_duty = duty / 10.0
        print(f"Duty cycle: {actual_duty}%")
        servo.ChangeDutyCycle(actual_duty)
        time.sleep(1)
    servo.ChangeDutyCycle(0)
except KeyboardInterrupt:
    pass
finally:
    servo.stop()
    GPIO.cleanup()
