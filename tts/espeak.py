import os
#import tempfile
#import uuid

#tempDir = None
debug_messages = None
male = None
voice_number = None
hw_num = None

def setup(robot_config):
    global debug_messages
#    global tempDir
    global male
    global voice_number
        
    debug_messages = robot_config.get('misc', 'debug_messages')
    male = robot_config.getboolean('espeak', 'male')
    voice_number = robot_config.get('espeak', 'voice_number')

    #set the location to write the temp file to
#    tempDir = tempfile.gettempdir()
    if debug_messages:
       print "TTS temporary directory:", tempDir

def say(message, args):

#    tempFilePath = os.path.join(tempDir, "text_" + str(uuid.uuid4()))
#    f = open(tempFilePath, "w")
#    f.write(message)
#    f.close()

    for hardwareNumber in (2, 0, 3, 1, 4):
        if male:
            os.system('echo ' + message + ' | espeak --stdout | aplay -D plughw:%d,0' % hardwareNumber)
        else:
            os.system('echo ' + message + ' | espeak -ven-us+f%d -s170 --stdout | aplay -D plughw:%d,0' % voice_number, hardwareNumber))
    os.remove(tempFilePath)    
