# TODO move all defs to the top of the file, out of the way of the flow of execution.

import platform
import uuid
import urllib2
import json
import traceback
import re
import argparse
import telly
import robot_util
import thread
import subprocess

from socketIO_client import SocketIO, LoggingNamespace

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

# check the command line for and config file overrides.
parser = argparse.ArgumentParser(description='start robot control program')
parser.add_argument('--robot-id', help='Robot ID', default=robot_config.getint('robot', 'robot_id'))
parser.add_argument('--info-server', help="Server that robot will connect to for information about servers and things", default=robot_config.get('misc', 'info_server'))
parser.add_argument('--type', help="Serial or motor_hat or gopigo2 or gopigo3 or l298n or motozero or pololu", default=robot_config.get('robot', 'type'))
parser.add_argument('--custom-hardware', type=str2bool, default=robot_config.getboolean('misc', 'custom_hardware'))
parser.add_argument('--custom-tts', type=str2bool, default=robot_config.getboolean('misc', 'custom_tts'))
parser.add_argument('--custom-chat', type=str2bool, default=robot_config.getboolean('misc', 'custom_chat'))
parser.add_argument('--debug-messages', type=str2bool, default=robot_config.getboolean('misc', 'debug_messages'))
commandArgs = parser.parse_args()

# push command line variables back into the config
robot_config.set('robot', 'robot_id', str(commandArgs.robot_id))
robot_config.set('robot', 'type', commandArgs.type)
robot_config.set('misc', 'info_server', commandArgs.info_server)
robot_config.set('misc', 'custom_hardware', str(commandArgs.custom_hardware))
robot_config.set('misc', 'custom_tts', str(commandArgs.custom_tts))
robot_config.set('misc', 'custom_chat', str(commandArgs.custom_chat))
robot_config.set('misc', 'debug_messages', str(commandArgs.debug_messages))


# set variables pulled from the config
robotID = commandArgs.robot_id
infoServer = commandArgs.info_server
debug_messages = commandArgs.debug_messages;

if debug_messages:
    print commandArgs

# Charging stuff
chargeCheckInterval = robot_config.getfloat('misc', 'chargeCheckInterval')
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

# Load and start TTS
import tts.tts as tts
tts.setup(robot_config)
global drivingSpeed

# Load a custom chat handler if enabled and exists, otherwise define a dummy.

handlingCommand = False

def getControlHostPort():
    url = 'https://%s/get_control_host_port/%s' % (infoServer, commandArgs.robot_id)
    response = robot_util.getWithRetry(url)
    return json.loads(response)

def getChatHostPort():
    url = 'https://%s/get_chat_host_port/%s' % (infoServer, commandArgs.robot_id)
    response = robot_util.getWithRetry(url)
    return json.loads(response)

controlHostPort = getControlHostPort()
chatHostPort = getChatHostPort()

print "using socket io to connect to control", controlHostPort
print "using socket io to connect to chat", chatHostPort

print "connecting to control socket.io"
controlSocketIO = SocketIO(controlHostPort['host'], controlHostPort['port'], LoggingNamespace)
print "finished using socket io to connect to control host port", controlHostPort

print "connecting to chat socket.io"
chatSocket = SocketIO(chatHostPort['host'], chatHostPort['port'], LoggingNamespace)
print 'finished using socket io to connect to chat ', chatHostPort

print "connecting to app server socket.io"
appServerSocketIO = SocketIO('letsrobot.tv', 8022, LoggingNamespace)
print "finished connecting to app server"

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
    rawMessage = args['message']
    withoutName = rawMessage.split(']')[1:]
    message = "".join(withoutName)
    urlRegExp = "(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"
    if message[1] == ".":
       exit()
    elif commandArgs.anon_tts != True and args['anonymous'] == True:
       exit()   
    elif commandArgs.filter_url_tts == True and re.search(urlRegExp, message):
       exit()
    else:
          say(message)

# TODO changeVolumeHighThenNormal() and handleLoudCommand() dont belong here, should
# be in a custom handler
def changeVolumeHighThenNormal():

    os.system("amixer -c 2 cset numid=3 %d%%" % 100)
    time.sleep(25)
    os.system("amixer -c 2 cset numid=3 %d%%" % commandArgs.tts_volume)

def handleLoudCommand():

    thread.start_new_thread(changeVolumeHighThenNormal, ())
    
def handle_command(args):

        global handlingCommand

        if handlingCommand:
            return

        handlingCommand = True

        if 'command' in args and 'robot_id' in args and args['robot_id'] == robotID:

            print('got command', args)

            command = args['command']

# TODO WALL and LOUD don't belong here, should be in custom handler.
            if command == 'LOUD':
                handleLoudCommand()
                
        if commandArgs.type == 'motor_hat':
            if command == 'WALL':
                handleLoudCommand()
                os.system("aplay -D plughw:2,0 /home/pi/wall.wav")


# TODO Modify move to take args, so custom controllers have access to the full message,
# not just the command portion.
            module.move(command)
                                    
        handlingCommand = False

def handleStartReverseSshProcess(args):
    print "starting reverse ssh"
    appServerSocketIO.emit("reverse_ssh_info", "starting")

    returnCode = subprocess.call(["/usr/bin/ssh",
                                  "-X",
                                  "-i", commandArgs.reverse_ssh_key_file,
                                  "-N",
                                  "-R", "2222:localhost:22",
                                  commandArgs.reverse_ssh_host])

    appServerSocketIO.emit("reverse_ssh_info", "return code: " + str(returnCode))
    print "reverse ssh process has exited with code", str(returnCode)

    
def handleEndReverseSshProcess(args):
    print "handling end reverse ssh process"
    resultCode = subprocess.call(["killall", "ssh"])
    print "result code of killall ssh:", resultCode

def on_handle_command(*args):
   thread.start_new_thread(handle_command, args)

def on_handle_exclusive_control(*args):
   thread.start_new_thread(handle_exclusive_control, args)

def on_handle_chat_message(*args):
   thread.start_new_thread(handle_chat_message, args)

   
#from communication import socketIO
controlSocketIO.on('command_to_robot', on_handle_command)
appServerSocketIO.on('exclusive_control', on_handle_exclusive_control)
chatSocket.on('chat_message_with_name', on_handle_chat_message)


def startReverseSshProcess(*args):
   thread.start_new_thread(handleStartReverseSshProcess, args)

def endReverseSshProcess(*args):
   thread.start_new_thread(handleEndReverseSshProcess, args)

appServerSocketIO.on('reverse_ssh_8872381747239', startReverseSshProcess)
appServerSocketIO.on('end_reverse_ssh_8872381747239', endReverseSshProcess)

#def myWait():
#  socketIO.wait()
#  thread.start_new_thread(myWait, ())


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
    chatSocket.emit('identify_robot_id', robotID);
    appServerSocketIO.emit('identify_robot_id', robotID);
    
waitCounter = 0

identifyRobotId()

if platform.system() == 'Darwin':
    pass
    #ipInfoUpdate()
elif platform.system() == 'Linux':
    ipInfoUpdate()

lastInternetStatus = False

def waitForAppServer():
    while True:
        appServerSocketIO.wait(seconds=1)

def waitForControlServer():
    while True:
        controlSocketIO.wait(seconds=1)        

def waitForChatServer():
    while True:
        chatSocket.wait(seconds=1)        
        
def startListenForAppServer():
   thread.start_new_thread(waitForAppServer, ())

def startListenForControlServer():
   thread.start_new_thread(waitForControlServer, ())

def startListenForChatServer():
   thread.start_new_thread(waitForChatServer, ())


startListenForControlServer()
startListenForAppServer()
startListenForChatServer()

while True:
    time.sleep(1)
    
    if (waitCounter % chargeCheckInterval) == 0:
        if commandArgs.type == 'motor_hat':
            chargeValue = module.updateChargeApproximation()
            sendChargeState()
            if commandArgs.slow_for_low_battery:
                module.setSpeedBasedOnCharge(chargeValue)

    if (waitCounter % 60) == 0:
        if robot_config.getboolean('misc', 'slow_for_low_battery'):
            if chargeValue < 30:
                say("battery low, %d percent" % int(chargeValue))

                
    if (waitCounter % 17) == 0:
        if not isCharging():
            if commandArgs.slow_for_low_battery:
                if chargeValue <= 25:
                    say("need to charge")
                
            
    if (waitCounter % 1000) == 0:
        
        internetStatus = isInternetConnected()
        if internetStatus != lastInternetStatus:
            if internetStatus:
                say("ok")
            else:
                say("missing internet connection")
        lastInternetStatus = internetStatus

        
    if (waitCounter % 10) == 0:
        if commandArgs.auto_wifi:
            if commandArgs.secret_key is not None:
                configWifiLogin(commandArgs.secret_key)

                
    if (waitCounter % 60) == 0:

        # tell the server what robot id is using this connection
        identifyRobotId()
        
        if platform.system() == 'Linux':
            ipInfoUpdate()

    waitCounter += 1
