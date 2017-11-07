from __future__ import print_function

import sys
import robot_util
import json
import schedule
import platform
import subprocess
import tts.tts as tts

from socketIO_client import SocketIO, LoggingNamespace

if (sys.version_info > (3, 0)):
    import _thread as thread
    import urllib.request as urllib2
else:
    import thread
    import urllib2

controlHostPort = None
chatHostPort = None
infoServer = None
robot_id = None

appServerSocketIO = None
controlSocketIO = None
chatSocket = None
no_chat_server = None
secure_cert = None

def getControlHostPort():
    url = 'https://%s/get_control_host_port/%s' % (infoServer, robot_id)
    response = robot_util.getWithRetry(url, secure=secure_cert).decode('utf-8')
    return json.loads(response)

def getChatHostPort():
    url = 'https://%s/get_chat_host_port/%s' % (infoServer, robot_id)
    response = robot_util.getWithRetry(url, secure=secure_cert).decode('utf-8')
    return json.loads(response)
    
def getOwnerDetails(username):
    url = 'https://api.letsrobot.tv/api/v1/accounts/%s' % (username)
    response = robot_util.getWithRetry(url, secure=secure_cert).decode('utf-8')
    return json.loads(response)
    

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

def onHandleAppServerConnect(*args):
    print
    print("chat socket.io connect")
    print
    identifyRobotID()


def onHandleAppServerReconnect(*args):
    print
    print("app server socket.io reconnect")
    print
    identifyRobotID()    
    
def onHandleAppServerDisconnect(*args):
    print
    print("app server socket.io disconnect")
    print
 
def onHandleChatConnect(*args):
    print
    print("chat socket.io connect")
    print
    identifyRobotID()

def onHandleChatReconnect(*args):
    print
    print("chat socket.io reconnect")
    print
    identifyRobotID()
    
def onHandleChatDisconnect(*args):
    print
    print("chat socket.io disconnect")
    print

def setupSocketIO(robot_config):
    global controlHostPort
    global chatHostPort
    global infoServer
    global robot_id
    global no_chat_server
    global secure_cert

    debug_messages = robot_config.get('misc', 'debug_messages') 
    robot_id = robot_config.getint('robot', 'robot_id')
    infoServer = robot_config.get('misc', 'info_server')
    no_chat_server = robot_config.getboolean('misc', 'no_chat_server')
    secure_cert = robot_config.getboolean('misc', 'secure_cert')
    
    controlHostPort = getControlHostPort()
    chatHostPort = getChatHostPort()

    schedule.repeat_task(60, identifyRobot_task)
    
    if debug_messages:   
        print("using socket io to connect to control", controlHostPort)
        print("using socket io to connect to chat", chatHostPort)

    if robot_config.getboolean('misc', 'check_internet'):
        #schedule a task to check internet status
        schedule.task(robot_config.getint('misc', 'check_freq'), internetStatus_task)


def setupControlSocket(on_handle_command):
    global controlSocketIO
    print("connecting to control socket.io")
    controlSocketIO = SocketIO(controlHostPort['host'], controlHostPort['port'], LoggingNamespace)
    print("finished using socket io to connect to control host port", controlHostPort)
    startListenForControlServer()
    controlSocketIO.on('command_to_robot', on_handle_command)
    return controlSocketIO

def setupChatSocket(on_handle_chat_message):
    global chatSocket
    
    if not no_chat_server:
        print("connecting to chat socket.io")
        chatSocket = SocketIO(chatHostPort['host'], chatHostPort['port'], LoggingNamespace)
        print('finished using socket io to connect to chat ', chatHostPort)
        startListenForChatServer()
        chatSocket.on('chat_message_with_name', on_handle_chat_message)
        chatSocket.on('connect', onHandleChatConnect)
        chatSocket.on('reconnect', onHandleChatReconnect)    
        chatSocket.on('disconnect', onHandleChatDisconnect)
        return chatSocket
    else:
        print("chat server connection disabled")

def setupAppSocket(on_handle_exclusive_control):
    global appServerSocketIO
    print("connecting to app server socket.io")
    appServerSocketIO = SocketIO('letsrobot.tv', 8022, LoggingNamespace)
    print("finished connecting to app server")
    startListenForAppServer()
    appServerSocketIO.on('exclusive_control', on_handle_exclusive_control)
    appServerSocketIO.on('connect', onHandleAppServerConnect)
    appServerSocketIO.on('reconnect', onHandleAppServerReconnect)
    appServerSocketIO.on('disconnect', onHandleAppServerDisconnect)
    return appServerSocketIO

def sendChargeState(charging):
    chargeState = {'robot_id': robot_id, 'charging': charging}
    appServerSocketIO.emit('charge_state', chargeState)
    print("charge state:", chargeState)


def ipInfoUpdate():
    appServerSocketIO.emit('ip_information',
                  {'ip': subprocess.check_output(["hostname", "-I"]).decode('utf-8'), 'robot_id': robot_id})

def identifyRobotId():
    """tells the server which robot is using the connection"""
    print("sending identify robot id messages")
    if not no_chat_server:
        chatSocket.emit('identify_robot_id', robot_id);
    appServerSocketIO.emit('identify_robot_id', robot_id);
   
#schedule a task to tell the server our robot it.
def identifyRobot_task():
    # tell the server what robot id is using this connection
    identifyRobotId()
    
    if platform.system() == 'Linux':
        ipInfoUpdate()
    
def isInternetConnected():
    try:
        urllib2.urlopen('https://www.google.com', timeout=1)
        return True
    except urllib2.URLError as err:
        return False

lastInternetStatus = False
def internetStatus_task():
    global lastInternetStatus
    internetStatus = isInternetConnected()
    if internetStatus != lastInternetStatus:
        if internetStatus:
            tts.say("ok")
        else:
            tts.say("missing internet connection")
    lastInternetStatus = internetStatus

