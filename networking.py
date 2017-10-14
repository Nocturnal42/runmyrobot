import thread
import robot_util
import json

from socketIO_client import SocketIO, LoggingNamespace

controlHostPort = None
chatHostPort = None
infoServer = None
robot_id = None

appServerSocketIO = None
controlSocketIO = None
chatSocket = None
no_chat_server = None

def getControlHostPort():
    url = 'https://%s/get_control_host_port/%s' % (infoServer, robot_id)
    response = robot_util.getWithRetry(url)
    return json.loads(response)

def getChatHostPort():
    url = 'https://%s/get_chat_host_port/%s' % (infoServer, robot_id)
    response = robot_util.getWithRetry(url)
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

def setupSocketIO(robot_config):
    global controlHostPort
    global chatHostPort
    global infoServer
    global robot_id
    global no_chat_server
    
    debug_messages = robot_config.get('misc', 'debug_messages') 
    robot_id = robot_config.getint('robot', 'robot_id')
    infoServer = robot_config.get('misc', 'info_server')
    no_chat_server = robot_config.getboolean('misc', 'no_chat_server')
    
    controlHostPort = getControlHostPort()
    chatHostPort = getChatHostPort()
    
    if debug_messages:   
        print "using socket io to connect to control", controlHostPort
        print "using socket io to connect to chat", chatHostPort

def setupControlSocket(on_handle_command):
    global controlSocketIO
    print "connecting to control socket.io"
    controlSocketIO = SocketIO(controlHostPort['host'], controlHostPort['port'], LoggingNamespace)
    print "finished using socket io to connect to control host port", controlHostPort
    startListenForControlServer()
    controlSocketIO.on('command_to_robot', on_handle_command)
    return controlSocketIO

def setupChatSocket(on_handle_chat_message):
    global chatSocket
    
    if not no_chat_server:
        print "connecting to chat socket.io"
        chatSocket = SocketIO(chatHostPort['host'], chatHostPort['port'], LoggingNamespace)
        print 'finished using socket io to connect to chat ', chatHostPort
        startListenForChatServer()
        chatSocket.on('chat_message_with_name', on_handle_chat_message)
        return chatSocket
    else:
        print "chat server connection disabled"

def setupAppSocket(on_handle_exclusive_control):
    global appServerSocketIO
    print "connecting to app server socket.io"
    appServerSocketIO = SocketIO('letsrobot.tv', 8022, LoggingNamespace)
    print "finished connecting to app server"
    startListenForAppServer()
    appServerSocketIO.on('exclusive_control', on_handle_exclusive_control)
    return appServerSocketIO

    