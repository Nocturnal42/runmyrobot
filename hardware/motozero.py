import RPi.GPIO as GPIO
import time

Motor1A = None
Motor1B = None
Motor1Enable = None
Motor2A = None
Motor2B = None
Motor2Enable = None
Motor3A = None
Motor3B = None
Motor3Enable = None
Motor4A = None
Motor4B = None
Motor4Enable = None

def setup(robot_config):
    global Motor1A = None
    global Motor1B = None
    global Motor1Enable = None
    global Motor2A = None
    global Motor2B = None
    global Motor2Enable = None
    global Motor3A = None
    global Motor3B = None
    global Motor3Enable = None
    global Motor4A = None
    global Motor4B = None
    global Motor4Enable = None

    Motor1A = robot_config/getint('motozero', 'Motor1A')
    Motor1B = robot_config/getint('motozero', 'Motor1B')
    Motor1Enable = robot_config/getint('motozero', 'Motor1Enable')
    Motor2A = robot_config/getint('motozero', 'Motor2A')
    Motor2B = robot_config/getint('motozero', 'Motor2B')
    Motor2Enable = robot_config/getint('motozero', 'Motor2Enable')
    Motor3A = robot_config/getint('motozero', 'Motor3A')
    Motor3B = robot_config/getint('motozero', 'Motor3B')
    Motor3Enable = robot_config/getint('motozero', 'Motor3Enable')
    Motor4A = robot_config/getint('motozero', 'Motor4A')
    Motor4B = robot_config/getint('motozero', 'Motor4B')
    Motor4Enable = robot_config/getint('motozero', 'Motor4Enable')

    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(Motor1A,GPIO.OUT)
    GPIO.setup(Motor1B,GPIO.OUT)
    GPIO.setup(Motor1Enable,GPIO.OUT)

    GPIO.setup(Motor2A,GPIO.OUT)
    GPIO.setup(Motor2B,GPIO.OUT)
    GPIO.setup(Motor2Enable,GPIO.OUT) 

    GPIO.setup(Motor3A,GPIO.OUT)
    GPIO.setup(Motor3B,GPIO.OUT)
    GPIO.setup(Motor3Enable,GPIO.OUT)

    GPIO.setup(Motor4A,GPIO.OUT)
    GPIO.setup(Motor4B,GPIO.OUT)
    GPIO.setup(Motor4Enable,GPIO.OUT)
	

def move(args):
    direction = args['command']
    
    if direction == 'F':
        GPIO.output(Motor1B, GPIO.HIGH)
        GPIO.output(Motor1Enable,GPIO.HIGH)

        GPIO.output(Motor2B, GPIO.HIGH)
        GPIO.output(Motor2Enable, GPIO.HIGH)

        GPIO.output(Motor3A, GPIO.HIGH)
        GPIO.output(Motor3Enable, GPIO.HIGH)

        GPIO.output(Motor4B, GPIO.HIGH)
        GPIO.output(Motor4Enable, GPIO.HIGH)

        time.sleep(0.3)

        GPIO.output(Motor1B, GPIO.LOW)
        GPIO.output(Motor2B, GPIO.LOW)
        GPIO.output(Motor3A, GPIO.LOW)
        GPIO.output(Motor4B, GPIO.LOW)
    if direction == 'B':
        GPIO.output(Motor1A, GPIO.HIGH)
        GPIO.output(Motor1Enable, GPIO.HIGH)

        GPIO.output(Motor2A, GPIO.HIGH)
        GPIO.output(Motor2Enable, GPIO.HIGH)

        GPIO.output(Motor3B, GPIO.HIGH)
        GPIO.output(Motor3Enable, GPIO.HIGH)

        GPIO.output(Motor4A, GPIO.HIGH)
        GPIO.output(Motor4Enable, GPIO.HIGH)

        time.sleep(0.3)

        GPIO.output(Motor1A, GPIO.LOW)
        GPIO.output(Motor2A, GPIO.LOW)
        GPIO.output(Motor3B, GPIO.LOW)
        GPIO.output(Motor4A, GPIO.LOW)

    if direction =='L':
        GPIO.output(Motor3B, GPIO.HIGH)
        GPIO.output(Motor3Enable, GPIO.HIGH)

        GPIO.output(Motor1A, GPIO.HIGH)
        GPIO.output(Motor1Enable, GPIO.HIGH)

        GPIO.output(Motor2B, GPIO.HIGH)
        GPIO.output(Motor2Enable, GPIO.HIGH)

        GPIO.output(Motor4B, GPIO.HIGH)
        GPIO.output(Motor4Enable, GPIO.HIGH)

        time.sleep(0.3)

        GPIO.output(Motor3B, GPIO.LOW)
        GPIO.output(Motor1A, GPIO.LOW)
        GPIO.output(Motor2B, GPIO.LOW)
        GPIO.output(Motor4B, GPIO.LOW)

    if direction == 'R':
        GPIO.output(Motor3A, GPIO.HIGH)
        GPIO.output(Motor3Enable, GPIO.HIGH)

        GPIO.output(Motor1B, GPIO.HIGH)
        GPIO.output(Motor1Enable, GPIO.HIGH)

        GPIO.output(Motor2A, GPIO.HIGH)
        GPIO.output(Motor2Enable, GPIO.HIGH)

        GPIO.output(Motor4A, GPIO.HIGH)
        GPIO.output(Motor4Enable, GPIO.HIGH)

        time.sleep(0.3)

        GPIO.output(Motor3A, GPIO.LOW)
        GPIO.output(Motor1B, GPIO.LOW)
        GPIO.output(Motor2A, GPIO.LOW)
        GPIO.output(Motor4A, GPIO.LOW)
