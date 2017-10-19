from __future__ import print_function
import RPi.GPIO as GPIO
import datetime
import os
import getpass
import random
import atexit

try:
    from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
    motorsEnabled = True
except ImportError:
    print("You need to install Adafruit_MotorHAT")
    print("Please install Adafruit_MotorHAT for python and restart this script.")
    print("To install: cd /usr/local/src && sudo git clone https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library.git")
    print("cd /usr/local/src/Adafruit-Motor-HAT-Python-Library && sudo python setup.py install")
    print("Running in test mode.")
    print("Ctrl-C to quit")
    motorsEnabled = False

# todo: specificity is not correct, this is specific to a bot with a claw, not all motor_hat based bots
from Adafruit_PWM_Servo_Driver import PWM

mh = None
turningSpeedActuallyUsed = None
dayTimeDrivingSpeedActuallyUsed = None
nightTimeDrivingSpeedActuallyUsed = None
drivingSpeed = 0

servoMin = [150, 150, 130]  # Min pulse length out of 4096
servoMax = [600, 600, 270]  # Max pulse length out of 4096
armServo = [300, 300, 300]

def setSpeedBasedOnCharge(chargeValue)
    global dayTimeDrivingSpeedActuallyUsed
    global nightTimeDrivingSpeedActuallyUsed

    if chargeValue < 30:
        multiples = [0.2, 1.0]
        multiple = random.choice(multiples)
        dayTimeDrivingSpeedActuallyUsed = int(float(commandArgs.day_speed) * multiple)
        nightTimeDrivingSpeedActuallyUsed = int(float(commandArgs.night_speed) * multiple)
    else:
        dayTimeDrivingSpeedActuallyUsed = commandArgs.day_speed
        nightTimeDrivingSpeedActuallyUsed = commandArgs.night_speed

def updateChargeApproximation():

    global chargeValue
    
    username = getpass.getuser()
    path = "/home/pi/charge_state_%s.txt" % username

    # read charge value
    # assume it is zero if no file exists
    if os.path.isfile(path):
        file = open(path, 'r')
        try:
            chargeValue = float(file.read())
            print("error reading float from file", path)
        except:
            chargeValue = 0
        file.close()
    else:
        print("setting charge value to zero")
        chargeValue = 0

    chargePerSecond = 1.0 / secondsToCharge
    dischargePerSecond = 1.0 / secondsToDischarge
    
    if GPIO.input(chargeIONumber) == 1:
        chargeValue += 100.0 * chargePerSecond * chargeCheckInterval
    else:
        chargeValue -= 100.0 * dischargePerSecond * chargeCheckInterval

    if chargeValue > 100.0:
        chargeValue = 100.0
    if chargeValue < 0:
        chargeValue = 0.0
        
    # write new charge value
    file = open(path, 'w')
    file.write(str(chargeValue))
    file.close()        

    print("charge value updated to", chargeValue)
    return chargeValue

def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

def incrementArmServo(channel, amount):

    armServo[channel] += amount

    print("arm servo positions:", armServo)

    if armServo[channel] > servoMax[channel]:
        armServo[channel] = servoMax[channel]
    if armServo[channel] < servoMin[channel]:
        armServo[channel] = servoMin[channel]
    pwm.setPWM(channel, 0, armServo[channel])

def runMotor(motorIndex, direction):
    motor = mh.getMotor(motorIndex+1)
    if direction == 1:
        motor.setSpeed(drivingSpeed)
        motor.run(Adafruit_MotorHAT.FORWARD)
    if direction == -1:
        motor.setSpeed(drivingSpeed)
        motor.run(Adafruit_MotorHAT.BACKWARD)
    if direction == 0.5:
        motor.setSpeed(128)
        motor.run(Adafruit_MotorHAT.FORWARD)
    if direction == -0.5:
        motor.setSpeed(128)
        motor.run(Adafruit_MotorHAT.BACKWARD)

def setup(robot_config):
    global mh
    global turningSpeedActuallyUsed
    global dayTimeDrivingSpeedActuallyUsed
    global nightTimeDrivingSpeedActuallyUsed
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(chargeIONumber, GPIO.IN)

    if motorsEnabled:
        # create a default object, no changes to I2C address or frequency
        mh = Adafruit_MotorHAT(addr=0x60)
        #mhArm = Adafruit_MotorHAT(addr=0x61)
        atexit.register(turnOffMotors)
        motorA = mh.getMotor(1)
        motorB = mh.getMotor(2)

    # Initialise the PWM device
    pwm = PWM(0x42)
    pwm.setPWMFreq(60)    # Set frequency to 60 Hz
    
    turningSpeedActuallyUsed = robot_config.getint('motor_hat', 'turning_speed')
    dayTimeDrivingSpeedActuallyUsed = robot_config.getint('misc', 'day_speed')
    nightTimeDrivingSpeedActuallyUsed = robot_config.getint('misc', 'night_speed')


def move( args ):
    command = args['command']
    
    global drivingSpeed
    
    now = datetime.datetime.now()
    now_time = now.time()
    # if it's late, make the robot slower
    if now_time >= datetime.time(21,30) or now_time <= datetime.time(9,30):
        #print("within the late time interval")
        drivingSpeedActuallyUsed = nightTimeDrivingSpeedActuallyUsed
    else:
        drivingSpeedActuallyUsed = dayTimeDrivingSpeedActuallyUsed
    
    if commandArgs.type == 'motor_hat' and motorsEnabled:
        motorA.setSpeed(drivingSpeed)
        motorB.setSpeed(drivingSpeed)
        if command == 'F':
            drivingSpeed = drivingSpeedActuallyUsed
            for motorIndex in range(4):
                runMotor(motorIndex, forward[motorIndex])
            time.sleep(straightDelay)
        if command == 'B':
            drivingSpeed = drivingSpeedActuallyUsed
            for motorIndex in range(4):
                runMotor(motorIndex, backward[motorIndex])
            time.sleep(straightDelay)
        if command == 'L':
            drivingSpeed = turningSpeedActuallyUsed
            for motorIndex in range(4):
                runMotor(motorIndex, left[motorIndex])
            time.sleep(turnDelay)
        if command == 'R':
            drivingSpeed = turningSpeedActuallyUsed
            for motorIndex in range(4):
                runMotor(motorIndex, right[motorIndex])
            time.sleep(turnDelay)
        if command == 'U':
            #mhArm.getMotor(1).setSpeed(127)
            #mhArm.getMotor(1).run(Adafruit_MotorHAT.BACKWARD)
            incrementArmServo(1, 10)
            time.sleep(0.05)
        if command == 'D':
            #mhArm.getMotor(1).setSpeed(127)
            #mhArm.getMotor(1).run(Adafruit_MotorHAT.FORWARD)
            incrementArmServo(1, -10)
            time.sleep(0.05)
        if command == 'O':
            #mhArm.getMotor(2).setSpeed(127)
            #mhArm.getMotor(2).run(Adafruit_MotorHAT.BACKWARD)
            incrementArmServo(2, -10)
            time.sleep(0.05)
        if command == 'C':
            #mhArm.getMotor(2).setSpeed(127)
            #mhArm.getMotor(2).run(Adafruit_MotorHAT.FORWARD)
            incrementArmServo(2, 10)
            time.sleep(0.05)

    turnOffMotors()
#        if command == 'WALL':
#            handleLoudCommand()
#            os.system("aplay -D plughw:2,0 /home/pi/wall.wav")
