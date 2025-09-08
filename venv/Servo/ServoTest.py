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
servo1 = servo.ContinuousServo(pca.channels[0])
servo3 = servo.ContinuousServo(pca.channels[2])

# Set the throttle to full speed forward (1.0).
# Throttle value can range from -1.0 (full speed reverse) to 1.0 (full speed forward).
servo1.throttle = 1.0
servo3.throttle = 1.0

# Keep the servo running at full speed for 3 seconds.
time.sleep(3)

# Stop the servo by setting the throttle to 0.0 (no movement).
servo1.throttle = 0.0
servo3.throttle = 0.0
# Briefly sleep for 0.1 seconds to ensure the stop command is fully processed.
time.sleep(0.1)

# Deinitialize the PCA9685 to free up resources and reset the hardware.
# PCA9685 동작 종료 코드
pca.deinit()