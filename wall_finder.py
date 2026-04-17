from buildhat import Motor
from basehat import IMUSensor, UltrasonicSensor
import time

motorL = Motor('D')
motorR = Motor('A')
sensor_front = UltrasonicSensor('A6')
sensor_right = UltrasonicSensor('A2')
imu = IMUSensor()

# intial variables
SPEED = 100 # Base speed of the robot
DIST_MIN = 5 # Distance considered too close in cm
DIST_MAX = 10 # Max distance before wall isn't considered significant

def stop():
    motorL.stop()
    motorR.stop()

def startL(speed):
    motorL.start(-speed)

def startR(speed):
    motorR.start(speed)

def start(speed=SPEED):
    startL(speed)
    startR(speed)
   
def turn_right(speed=SPEED):
    startL(speed)
    startR(-speed)

def turn_left(speed=SPEED):
    startL(-speed)
    startR(speed)

def dynamic_turn(speed=SPEED):
    while True:
        front_dist = sensor_front.getDist()
        right_dist = sensor_right.getDist()

        if front_dist > DIST_MAX or right_dist > DIST_MAX:
            start(speed)
            return
        else:
            if right_dist < DIST_MAX:
                startL(speed)
            else:
                startR(speed)


prev_time = time.time()
turn = 0

try:
    start()
    while True:
        front_dist = sensor_front.getDist()
        right_dist = sensor_right.getDist()
        # cur_time = time.time()
        # dt = cur_time - prev_time
        # gx, gy, gz = imu.getGyro()
       
        # turn += gz * dt
        # print(turn, dt)
       
        # if (abs(turn) >= 80):
        #     print("Yay")
        #     stop()
        #     break

        if front_dist > DIST_MAX:
            dynamic_turn()
            

        time.sleep(2)
except KeyboardInterrupt:
    stop()
    print("Code doth cease")
   
