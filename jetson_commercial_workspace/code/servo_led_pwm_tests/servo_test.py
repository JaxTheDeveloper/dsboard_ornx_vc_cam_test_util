from adafruit_servokit import ServoKit
import time

myKit = ServoKit(channels=16)

# while True:
#     myKit.servo[14].duty_cycle = 65000
#     myKit.servo[13].duty_cycle = 65000
#     myKit.servo[12].duty_cycle = 65000

# while True:
#     inputAngle = int(input("angle: "))
#     myKit.servo[8].angle = inputAngle

while True:
    for i in range (0, 180 + 1):
        myKit.servo[14].angle = i
        myKit.servo[13].angle = i
        myKit.servo[12].angle = i
        time.sleep(0.005)
    for i in range (180 - 1, -1, -1):
        myKit.servo[14].angle = i
        myKit.servo[13].angle = i
        myKit.servo[12].angle = i
        time.sleep(0.005)