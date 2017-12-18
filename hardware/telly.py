import robot_util
import mod_utils
module = None
ser = None

right_wheel_forward_speed = None
right_wheel_backward_speed = None
left_wheel_forward_speed = None
left_wheel_backward_speed = None
turn_delay = None
straight_delay = None
led_max_brightness = None


def setup(robot_config):
    global module
    global ser
    global straight_delay
    global turn_delay
    global right_wheel_forward_speed
    global right_wheel_backward_speed
    global left_wheel_forward_speed
    global right_wheel_backward_speed
    global led_max_brightness
    
    led_max_brightness = robot_config.get('telly', 'led-max-brightness')
    
    if robot_config.has_option('telly', 'right_wheel_forward_speed'):
        right_wheel_forward_speed = robot_config.get('telly', 'right_wheel_forward_speed')
    if robot_config.has_option('telly', 'right_wheel_backward_speed'):
        right_wheel_forward_speed = robot_config.get('telly', 'right_wheel_backward_speed')
    if robot_config.has_option('telly', 'left_wheel_forward_speed'):
        left_wheel_forward_speed = robot_config.get('telly', 'left_wheel_forward_speed')
    if robot_config.has_option('telly', 'left_wheel_backward_speed'):
        right_wheel_forward_speed = robot_config.get('telly', 'left_wheel_backward_speed')

    
    straight_delay = robot_config.getfloat('robot', 'straight_delay')
    turn_delay = robot_config.getfloat('robot', 'turn_delay')    
    
    module = mod_utils.import_module('hardware', 'serial_board')
    ser = module.setup(robot_config)

    sendSettings()

def move(args):
    module.move(args)

def sendSettings():

    if right_wheel_forward_speed is not None:
        robot_util.sendSerialCommand(ser, "rwfs " + right_wheel_forward_speed)

    if right_wheel_backward_speed is not None:
        robot_util.sendSerialCommand(ser, "rwbs " + right_wheel_backward_speed)

    if left_wheel_forward_speed is not None:
        robot_util.sendSerialCommand(ser, "lwfs " + left_wheel_forward_speed)

    if left_wheel_backward_speed is not None:
        robot_util.sendSerialCommand(ser, "lwbs " + left_wheel_backward_speed)

    if straight_delay is not None:
        robot_util.sendSerialCommand(ser, "straight-distance " + str(int(straight_delay * 255)))

    if turn_delay is not None:
        robot_util.sendSerialCommand(ser, "turn-distance " + str(int(turn_delay * 255)))
        
    if led_max_brightness is not None:
        robot_util.sendSerialCommand(ser, "led-max-brightness " + led_max_brightness)
