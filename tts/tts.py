import os
import tempfile
import uuid

type = 'none'
tts_module = None
tempDir = None
debug_messages = None

def setup(robot_config):
    global type
    global tts_module
    global tempDir
    global debug_messages
    
    type = robot_config.get('tts', 'type')
    debug_messages = robot_config.get('misc', 'debug_messages')
    
    if type != 'none':
        # set volume level

        # tested for 3.5mm audio jack
        if robot_config.getint(tts_volume) > 50:
            os.system("amixer set PCM -- -100")

        # tested for USB audio device
        os.system("amixer -c 2 cset numid=3 %d%%" % commandArgs.tts_volume)


    #import the appropriate tts handler module.
    if robot_config.getboolean('misc', 'custom_tts'):
        try:
            tts_module = __import__('tts.tts_custom', fromlist=['hardware_custom'])
        except ImportError:
            print "Unable to open custom tts handler"
            tts_module = __import__("tts."+type, fromlist=[type])
    else:    
        tts_module = __import__("tts."+type, fromlist=[type])    

    #set the location to write the temp file to
    tempDir = tempfile.gettempdir()
    if debug_messages:
       print "TTS temporary directory:", tempDir

    #call the tts handlers setup function
    tts_module.setup(robot_config)

def say(*args):
    message = args[0]

    tempFilePath = os.path.join(tempDir, "text_" + str(uuid.uuid4()))
    f = open(tempFilePath, "w")
    f.write(message)
    f.close()

    #check the number of arguments passed, and hand off as appropriate to the tts handler
    if len(args) == 1:
        tts_module.say(tempFilePath)
    else:
        tts_module.say(tempFilePath, args[1])
          
    #os.system('"C:\Program Files\Jampal\ptts.vbs" -u ' + tempFilePath) Whaa?
    
    #if commandArgs.festival_tts:
        # festival tts
    #    os.system('festival --tts < ' + tempFilePath)
    #os.system('espeak < /tmp/speech.txt')

    #else:
        # espeak tts
    #    for hardwareNumber in (2, 0, 3, 1, 4):
    #        if commandArgs.male:
    #            os.system('cat ' + tempFilePath + ' | espeak --stdout | aplay -D plughw:%d,0' % hardwareNumber)
    #        else:
    #            os.system('cat ' + tempFilePath + ' | espeak -ven-us+f%d -s170 --stdout | aplay -D plughw:%d,0' % (commandArgs.voice_number, hardwareNumber))

    os.remove(tempFilePath)    
    
