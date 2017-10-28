from __future__ import print_function
import RPi.GPIO as GPIO
import time
import extended_command

debug_messages=None

sleeptime=None 
rotatetimes=None

StepPinForward=None
StepPinBackward=None
StepPinLeft=None
StepPinRight=None

def set_rotate_time(command, args):
    global rotatetimes
    if extended_command.is_authed(args['name']) == 2: # Owner
        if len(command) > 1:
            rotatetimes=float(command[1])
            print("rotate time multiplier set to : %d" % float(command[1]))

def set_sleep_time(command, args):
    global sleeptime
    if extended_command.is_authed(args['name']) == 2: # Owner
        if len(command) > 1:
            sleeptime=float(command[1])
            print("sleep time set to : %d" % float(command[2]))


def setup(robot_config):
    global debug_messages
    global StepPinForward
    global StepPinBackward
    global StepPinLeft
    global StepPinRight
    global sleeptime
    global rotatetimes
    
    debug_messages = robot_config.get('misc', 'debug_messages')
    sleeptime = robot_config.getfloat('l298n', 'sleeptime')
    rotatetimes = robot_config.getfloat('l298n', 'rotatetimes')
    
    if debug_messages:
        mode=GPIO.getmode()
        print(" mode ="+str(mode))

    GPIO.cleanup()
    
    if robot_config.getboolean('tts', 'ext_chat'): #ext_chat enabled, add motor commands
        extended_command.add_command('.set_rotate_time', set_rotate_time)
        extended_command.add_command('.set_sleep_time', set_sleep_time)

# TODO passing these as tuples may be unnecessary, it may accept lists as well. 
    StepPinForward = tuple(robot_config.get('l298n', 'StepPinForward').split(','))
    StepPinBackward = tuple(robot_config.get('l298n', 'StepPinBackward').split(','))
    StepPinLeft = tuple(robot_config.get('l298n', 'StepPinLeft').split(','))
    StepPinRight = tuple(robot_config.get('l298n', 'StepPinRight').split(','))
	
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(StepPinForward, GPIO.OUT)
    GPIO.setup(StepPinBackward, GPIO.OUT)
    GPIO.setup(StepPinLeft, GPIO.OUT)
    GPIO.setup(StepPinRight, GPIO.OUT)

def move(args):
    direction = args['command']
    if direction == 'F':
        GPIO.output(StepPinForward, GPIO.HIGH)
        time.sleep(sleeptime)
        GPIO.output(StepPinForward, GPIO.LOW)
    if direction == 'B':
        GPIO.output(StepPinBackward, GPIO.HIGH)
        time.sleep(sleeptime)
        GPIO.output(StepPinBackward, GPIO.LOW)
    if direction == 'L':
        GPIO.output(StepPinLeft, GPIO.HIGH)
        time.sleep(sleeptime * rotatetimes)
        GPIO.output(StepPinLeft, GPIO.LOW)
    if direction == 'R':
        GPIO.output(StepPinRight, GPIO.HIGH)
        time.sleep(sleeptime * rotatetimes)
        GPIO.output(StepPinRight, GPIO.LOW)
       
