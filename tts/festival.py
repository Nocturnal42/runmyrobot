import os
import tempfile
import uuid

tempDir = None
debug_messages = None

def setup(robot_config):
    global debug_messages
    global tempDir
        
    debug_messages = robot_config.get('misc', 'debug_messages')

    #set the location to write the temp file to
    tempDir = tempfile.gettempdir()
    if debug_messages:
       print "TTS temporary directory:", tempDir

def say(message, args):

    tempFilePath = os.path.join(tempDir, "text_" + str(uuid.uuid4()))
    f = open(tempFilePath, "w")
    f.write(message)
    f.close()

    os.system('festival --tts < ' + tempFilePath)

    os.remove(tempFilePath)    
    
