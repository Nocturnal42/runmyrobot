# TODO move all defs to the top of the file, out of the way of the flow of execution.
# TODO add config option to disable charging stuff
# TODO / MAYBE move charging stuff into specific hardware handlers and a module.
# TODO make charge reporting more modular

import platform
import urllib2
import traceback
import re
import argparse
import telly
import robot_util
import thread
import subprocess
import os.path
import networking
import time
import schedule

from threading import Timer

# fail gracefully if configparser is not installed
try:
    import ConfigParser
except ImportError:
    print "Please check that you are using python 2.7 and that configparser is installed (sudo python -m pip install ConfigParser)\n"
    sys.exit()

# parse the letsrobot.conf file and set the basic values
robot_config = ConfigParser.ConfigParser()
try: 
    robot_config.readfp(open('letsrobot.conf'))
except IOError:
    print "unable to read letsrobot.conf, please check that you have copied letsrobot.sample.conf to letsrobot.conf and modified it appropriately."
    sys.exit()
except:
    print "Error in letsrobot.conf:", sys.exc_info()[0]
    sys.exit()

# This is required to allow us to get True / False boolean values from the
# command line    
def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')    

# TODO assess these and other options in the config to see which ones are most 
# appropriate to be overidden from the command line.
# check the command line for and config file overrides.
parser = argparse.ArgumentParser(description='start robot control program')
parser.add_argument('--robot-id', help='Robot ID', default=robot_config.get('robot', 'robot_id'))
parser.add_argument('--info-server', help="Server that robot will connect to for information about servers and things", default=robot_config.get('misc', 'info_server'))
parser.add_argument('--type', help="Serial or motor_hat or gopigo2 or gopigo3 or l298n or motozero or pololu", default=robot_config.get('robot', 'type'))
parser.add_argument('--custom-hardware', type=str2bool, default=robot_config.getboolean('misc', 'custom_hardware'))
parser.add_argument('--custom-tts', type=str2bool, default=robot_config.getboolean('misc', 'custom_tts'))
parser.add_argument('--custom-chat', type=str2bool, default=robot_config.getboolean('misc', 'custom_chat'))
parser.add_argument('--ext-chat-command', type=str2bool, default=robot_config.getboolean('tts', 'ext_chat'))
parser.add_argument('--debug-messages', type=str2bool, default=robot_config.getboolean('misc', 'debug_messages'))
commandArgs = parser.parse_args()

# push command line variables back into the config
robot_config.set('robot', 'robot_id', str(commandArgs.robot_id))
robot_config.set('robot', 'type', commandArgs.type)
robot_config.set('misc', 'info_server', commandArgs.info_server)
robot_config.set('misc', 'custom_hardware', str(commandArgs.custom_hardware))
robot_config.set('misc', 'custom_tts', str(commandArgs.custom_tts))
robot_config.set('misc', 'custom_chat', str(commandArgs.custom_chat))
robot_config.set('tts', 'ext_chat', str(commandArgs.ext_chat_command))
robot_config.set('misc', 'debug_messages', str(commandArgs.debug_messages))


# set variables pulled from the config
robotID = commandArgs.robot_id
infoServer = commandArgs.info_server
debug_messages = commandArgs.debug_messages
ext_chat = commandArgs.ext_chat_command
no_chat_server = robot_config.getboolean('misc', 'no_chat_server')


if debug_messages:
    print commandArgs

# Charging stuff
chargeValue = robot_config.getfloat('misc', 'chargeValue')
secondsToCharge = 60.0 * 60.0 * robot_config.getfloat('misc', 'charge_hours')
secondsToDischarge = 60.0 * 60.0 * robot_config.getfloat('misc', 'discharge_hours')
chargeIONumber = robot_config.getint('misc', 'chargeIONumber')

# TODO : This really doesn't belong here, should probably be in start script.
# watch dog timer
if robot_config.getboolean('misc', 'watchdog'):
    import os
    os.system("sudo modprobe bcm2835_wdt")
    os.system("sudo /usr/sbin/service watchdog start")

if debug_messages:
    print "info server:", infoServer

# Load and start TTS
import tts.tts as tts
tts.setup(robot_config)
global drivingSpeed

# If custom hardware extensions have been enabled, load them if they exist. Otherwise load the default
# controller for the specified hardware type.
if commandArgs.custom_hardware:
    try:
        module = __import__('hardware.hardware_custom', fromlist=['hardware_custom'])
    except ImportError:
        module = __import__("hardware."+commandArgs.type, fromlist=[commandArgs.type])
else:    
    module = __import__("hardware."+commandArgs.type, fromlist=[commandArgs.type])

#call the hardware module setup function
module.setup(robot_config)
move_handler = module.move

#load the extended chat commands
if ext_chat:
    import extended_command
    extended_command.setup(robot_config)
    extended_command.move_handler=move_handler
    move_handler = extended_command.move_auth

# TODO Add the custom chat handler loader
# Load a custom chat handler if enabled and exists, otherwise define a dummy.

#def setServoPulse(channel, pulse):
#  pulseLength = 1000000                   # 1,000,000 us per second
#  pulseLength /= 60                       # 60 Hz
#  print "%d us per period" % pulseLength
#  pulseLength /= 4096                     # 12 bits of resolution
#  print "%d us per bit" % pulseLength
#  pulse *= 1000
#  pulse /= pulseLength
#  pwm.setPWM(channel, 0, pulse)

def isInternetConnected():
    try:
        urllib2.urlopen('https://www.google.com', timeout=1)
        return True
    except urllib2.URLError as err:
        return False
    
def configWifiLogin(secretKey):
    WPA_FILE_TEMPLATE = robot_config.get('misc', 'wpa_template')
    
    url = 'https://%s/get_wifi_login/%s' % (infoServer, secretKey)
    try:
        print "GET", url
        response = urllib2.urlopen(url).read()
        responseJson = json.loads(response)
        print "get wifi login response:", response

        with open("/etc/wpa_supplicant/wpa_supplicant.conf", 'r') as originalWPAFile:
            originalWPAText = originalWPAFile.read()

        wpaText = WPA_FILE_TEMPLATE.format(name=responseJson['wifi_name'], password=responseJson['wifi_password'])


        print "original(" + originalWPAText + ")"
        print "new(" + wpaText + ")"
        
        if originalWPAText != wpaText:

            wpaFile = open("/etc/wpa_supplicant/wpa_supplicant.conf", 'w')        

            print wpaText
            print
            wpaFile.write(wpaText)
            wpaFile.close()

            say("Updated wifi settings. I will automatically reset in 10 seconds.")
            time.sleep(8)
            say("Reseting")
            time.sleep(2)
            os.system("reboot")
        
    except:
        print "exception while configuring setting wifi", url
        traceback.print_exc()

#def times(lst, number):
#    return [x*number for x in lst]
#
#forward = json.loads(commandArgs.forward)
#backward = times(forward, -1)
#left = json.loads(commandArgs.left)
#right = times(left, -1)
#straightDelay = commandArgs.straight_delay 
#turnDelay = commandArgs.turn_delay


# TODO impliment a exclusive control function in hardware / tts / chat custom.
# this will probably mean a dummy function in all the handlers.    
def handle_exclusive_control(args):
        if 'status' in args and 'robot_id' in args and args['robot_id'] == robotID:

            status = args['status']

        if status == 'start':
                print "start exclusive control"
        if status == 'end':
                print "end exclusive control"
                
                
def handle_chat_message(args):
    print "chat message received:", args

    if ext_chat:
        extended_command.handler(args)
            
    rawMessage = args['message']
    withoutName = rawMessage.split(']')[1:]
    message = "".join(withoutName)
    urlRegExp = "(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"

    try:
        if message[1] == ".":
            exit()
        elif robot_config.getboolean('tts', 'anon_tts') != True and args['anonymous'] == True:
            exit()
        elif robot_config.getboolean('tts', 'filter_url_tts') == True and re.search(urlRegExp, message):
            exit()
        else:
            tts.say(message, args)
    except IndexError:
        exit()
            
# TODO changeVolumeHighThenNormal() and handleLoudCommand() dont belong here, should
# be in a custom handler
def changeVolumeHighThenNormal():
    os.system("amixer -c 2 cset numid=3 %d%%" % 100)
    time.sleep(25)
    os.system("amixer -c 2 cset numid=3 %d%%" % robot_config.getint('tts', 'tts_volume'))

def handleLoudCommand(seconds):
    thread.start_new_thread(changeVolumeHighThenNormal, (seconds,))

handlingCommand = False
    
def handle_command(args):
        global handlingCommand
        handlingCommand = True

        if 'command' in args and 'robot_id' in args and args['robot_id'] == robotID:
        
            if debug_messages:
                print('got command', args)

            move_handler(args)


# TODO WALL and LOUD don't belong here, should be in custom handler.
            if command in ("SOUND2", "WALL", "LOUD"):
                handlingCommand = False
            
            if command == 'LOUD':
                handleLoudCommand(25)

            if commandArgs.type == 'motor_hat':
                if command == 'WALL':
                    handleLoudCommand(25)
                    os.system("aplay -D plughw:2,0 /home/pi/wall.wav")
                if command == 'SOUND2':
                    handleLoudCommand(25)
                    os.system("aplay -D plughw:2,0 /home/pi/sound2.wav")
                                                        
        handlingCommand = False
	   

def on_handle_command(*args):
   if handlingCommand:
       return
   else:
       thread.start_new_thread(handle_command, args)

def on_handle_exclusive_control(*args):
   thread.start_new_thread(handle_exclusive_control, args)

def on_handle_chat_message(*args):
   thread.start_new_thread(handle_chat_message, args)

# Connect to the networking sockets
networking.setupSocketIO(robot_config)
controlSocketIO = networking.setupControlSocket(on_handle_command)
chatSocket = networking.setupChatSocket(on_handle_chat_message)
appServerSocketIO = networking.setupAppSocket(on_handle_exclusive_control)

# If reverse SSH is enabled and if the key file exists, import it and hook it in.
if robot_config.getboolean('misc', 'reverse_ssh') and os.path.isfile(robot_config.get('misc', 'reverse-ssh-key-file')):
    import reverse_ssh
    setupReverseSsh(robot_config)


def ipInfoUpdate():
    appServerSocketIO.emit('ip_information',
                  {'ip': subprocess.check_output(["hostname", "-I"]), 'robot_id': robotID})


# true if it's on the charger and it needs to be charging
def isCharging():
    print "is charging current value", chargeValue

    # only tested for motor hat robot currently, so only runs with that type
    if commandArgs.type == "motor_hat":
        print "RPi.GPIO is in sys.modules"
        if chargeValue < 99: # if it's not full charged already
            print "charge value is low"
            return GPIO.input(chargeIONumber) == 1 # return whether it's connected to the dock

    return False
    
def sendChargeState():
    charging = isCharging()
    chargeState = {'robot_id': robotID, 'charging': charging}
    appServerSocketIO.emit('charge_state', chargeState)
    print "charge state:", chargeState

def sendChargeStateCallback(x):
    sendChargeState()

if commandArgs.type == 'motor_hat':
    GPIO.add_event_detect(chargeIONumber, GPIO.BOTH)
    GPIO.add_event_callback(chargeIONumber, sendChargeStateCallback)

def identifyRobotId():
    if not no_chat_server:
        chatSocket.emit('identify_robot_id', robotID);
    appServerSocketIO.emit('identify_robot_id', robotID);
    
waitCounter = 1

identifyRobotId()

if platform.system() == 'Darwin':
    pass
    #ipInfoUpdate()
elif platform.system() == 'Linux':
    ipInfoUpdate()

lastInternetStatus = False

slow_for_low_battery = robot_config.getboolean('misc', 'slow_for_low_battery')
auto_wifi = robot_config.getboolean('misc', 'auto_wifi')
secret_key = robot_config.get('misc', 'secret_key')

# if auto_wifi is enabled, schdule a task for it.
def auto_wifi_task():
    if secret_key is not None:
         configWifiLogin(secret_key)
    t = Timer(10, auto_wifi_task)
    t.daemon = True
    t.start()
    
if auto_wifi:
    auto_wifi_task()

lastInternetStatus=None
#schedule a task to check internet status

def internetStatus_task():
    global lastInternetStatus
    internetStatus = isInternetConnected()
    if internetStatus != lastInternetStatus:
        if internetStatus:
            tts.say("ok")
        else:
            tts.say("missing internet connection")
    lastInternetStatus = internetStatus

schedule.repeat_task(120, internetStatus_task)

#schedule a task to tell the server our robot it.
def identifyRobot_task():
    # tell the server what robot id is using this connection
    identifyRobotId()
    
    if platform.system() == 'Linux':
        ipInfoUpdate()
    
schedule.task(60, identifyRobot_task)

#schedule a task to report charge status to the server
chargeCheckInterval = int(robot_config.getint('misc', 'chargeCheckInterval'))
def sendChargeState_task():
    if commandArgs.type == 'motor_hat':
        chargeValue = module.updateChargeApproximation()
        sendChargeState()
        if slow_for_low_battery:
            module.setSpeedBasedOnCharge(chargeValue)

schedule.task(chargeCheckInterval, sendChargeState_task)

#schedule tasks to tts out a message about battery percentage and need to charge
def reportBatteryStatus_task():
    if chargeValue < 30:
        tts.say("battery low, %d percent" % int(chargeValue))


def reportNeedToCharge():
    if not isCharging():
        if chargeValue <= 25:
            tts.say("need to charge")

if ((robot_config.get('tts', 'type') != 'none') and (slow_for_low_battery)):
    schedule.repeat_task(60, reportBatteryStatus_task)
    schedule.repeat_task(17, reportNeedToCharge)

while True:
    time.sleep(10)
                                
