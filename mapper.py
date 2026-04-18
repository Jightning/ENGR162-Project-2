from buildhat import Motor
from basehat import IMUSensor, UltrasonicSensor
import time
import json

# Pathfinding is done via event logs, so when it turns it gets logged per cell
# Initial direction the robot is facing is assumed to be north

motorL = Motor('D')
motorR = Motor('A')
# TODO These numbers are prolly wrong
sensor_front = UltrasonicSensor(9)
sensor_right = UltrasonicSensor(18)
imu = IMUSensor()

JSON_LOG = True # TODO save path to a json, set to false if it errors

# initial variables
SPEED = 20 # Base speed of the robot
SLOW_SPEED = 5
DIST_MIN = 15 # Distance considered too close in cm
DIST_MAX = 25 # Max distance before wall isn't considered significant

TURN_SLOW_THRESHOLD = 8 # How many degrees before target to start slow turning
GYRO_BIAS = 0.0 # Gets set later, for gyro error correction
CELL_TRAVEL_TIME = 1.5 # TODO How long it takes to travel 1 "cell" 

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

# Initial gyro calibration, basically running gyro while stationary
# and tracking unwanted movement
def calibrate_gyro(samples=200):
    s = 0.0
    print(f"Calibrating gyro... Should take {0.01 * samples} seconds")
    # TODO Add tqdm if the pi allows it as an import PLEASEEEEE
    for _ in range(samples):
        gx, gy, gz = imu.getGyro()
        s += gz
        time.sleep(0.01)

    print("Done!\n")
    return s / samples


def turn_degrees(turn_func, degrees=90.0, speed=SPEED, tolerance=2.0):
    total = 0.0
    prev_time = time.time()

    turn_func(speed)

    # Main turn
    while total < (degrees - tolerance):
        # Having it slow down towards the end to get more precise
        if total > degrees - tolerance - TURN_SLOW_THRESHOLD:
            turn_func(SLOW_SPEED)

        # Change in time
        cur_time = time.time()
        dt = cur_time - prev_time
        prev_time = cur_time

        # Update rotation
        gx, gy, gz = imu.getGyro()
        total += abs(gz - GYRO_BIAS) * dt
        time.sleep(0.005)

    stop()

    # Accounting for overshoot I LOVE RECURSION YESSIR
    # TODO I'd be shocked if this doesn't cause issues
    # Just comment out if too weird lol
    overshoot = abs(total - degrees)
    if overshoot > tolerance:
        # hacky but might work
        # basically passing a lambda that reverses the intended direction
        # This might slow down with a lotta recursion but with a high enough tolerance it
        # shouldn't happen, which i'm forcing by having it gradually increase
        turn_degrees(lambda x: turn_func(-x), degrees=overshoot, tolerance=tolerance*1.1)

# TODO set this to 0 if there are issues
GYRO_BIAS = calibrate_gyro()

# JSON style pathing, lets upload to JSON file once code terminates
path = []

x = 0
y = 0
direction = 0 # initial facing directions (north)
directions = ['N', 'E', 'S', 'W']

def log(turned=False):
    path.append({
        "pos": (x, y),
        "dir": directions[direction],
        "turned": turned
    })
    print(f"({x}, {y}) going {directions[direction]}")

def update_coordinates():
    global x, y
    if direction == 0: y += 1 # North
    elif direction == 1: x += 1 # East
    elif direction == 2: y -= 1 # South
    elif direction == 3: x -= 1 # West

try:
    # Task 2
    # Uncomment 2 lines below, modify degrees and turn func
    # turn_degrees(turn_right, degrees=90.0)
    # return

    start()
    while True:
        front_dist = sensor_front.getDist
        right_dist = sensor_right.getDist

        # Task 5
        if right_dist > DIST_MAX: # Turn right if clear
            stop()
            turn_degrees(turn_right)
            direction = (direction + 1) % 4
            log(turned=True)
            
            # Travel one cell since its guaranteed
            start(SPEED)
            time.sleep(CELL_TRAVEL_TIME)

            update_coordinates()
            log()

        elif front_dist > DIST_MIN: # Travel one cell if clear
            start(SPEED)
            time.sleep(CELL_TRAVEL_TIME)

            update_coordinates()
            log()

        else: # Corner, turn left (new path not guaranteed)
            stop()
            turn_degrees(turn_left)
            direction = (direction - 1) % 4 
            log(turned=True)

        time.sleep(0.01)
except KeyboardInterrupt:
    stop()

    # dump path to a json to save it
    if JSON_LOG:
        with open('maze.json', 'w') as file:
            json.dump(path, file, indent=4)

    print("Code doth cease")
   
