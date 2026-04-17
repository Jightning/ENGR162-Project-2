from buildhat import Motor
from basehat import IMUSensor, UltrasonicSensor
import time

motorL = Motor('D')
motorR = Motor('A')
#sensor_front = UltrasonicSensor()
#sensor_left = UltrasonicSensor()
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

prev_time = time.time()
turn = 0

try:
    #start()
    turn_right()

    while True:
        #front_dist = sensor_front.getDist()
        #left_dist = sensor_left.getDist()
        cur_time = time.time()
        dt = cur_time - prev_time
        gx, gy, gz = imu.getGyro()
       
        turn += gz * dt
        print(turn, dt)
       
        if (abs(turn) >= 80):
            print("Yay")
            stop()
            break
       
        prev_time = cur_time
       
    startL(100)
    startR(100)
    time.sleep(2)
 
               
       
except KeyboardInterrupt:
    stop()
    print("Code doth cease")
   
