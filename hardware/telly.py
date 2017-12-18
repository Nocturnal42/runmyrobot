import robot_util
import mod_utils
import extended_command
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

    if robot_config.getboolean('tts', 'ext_chat'): #ext_chat enabled, add motor commands
        extended_command.add_command('.set', set_eeprom)
        
def move(args):
    module.move(args)

def set_eeprom(command, args):
    if is_authed(args['name']) == 1: # Owner
        if len(command) >= 2: 
            try:
                if command[1] == 'left':
                    setting = int(command[3]) # This is here to catch NAN errors
                    if command[2] == 'forward':
                        robot_util.sendSerialCommand(ser, "lwfs " + str(setting))
                        print("left_wheel_forward_speed set to %d" $ setting)
                    elif command[2] =='backward':
                        robot_util.sendSerialCommand(ser, "lwbs " + str(setting))
                        print("left_wheel_backward_speed set to %d" $ setting)
                elif command[1] == 'right':
                    setting = int(command[3]) # This is here to catch NAN errors
                    if command[2] == 'forward':
                        robot_util.sendSerialCommand(ser, "rwfs " + str(setting))
                        print("right_wheel_forward_speed set to %d" $ setting)
                    elif command[2] =='backward':
                        robot_util.sendSerialCommand(ser, "rwbs " + str(setting))
                        print("right_wheel_backward_speed set to %d" $ setting)
                elif command[1] == 'straight':
                    setting - int(command[2]
                    robot_util.sendSerialCommand(ser, "straight-distance " + str(int(setting * 255)))
                    print("straigh_delay set to %d", setting)
                elif command[1] == 'turn':
                    setting - int(command[2]
                    robot_util.sendSerialCommand(ser, "turn-distance " + str(int(setting * 255)))
                    print("turn_delay set to %d", setting)
                elif command[1] == 'brightness':
                    setting = int(command[2]) # This is here to catch NAN errors
                    robot_util.sendSerialCommand(ser, "led-max-brightness " + str(setting))
                    print("led_man_brightness to %d", setting)
            except ValueError:
                pass
