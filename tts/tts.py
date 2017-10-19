import os
import sys

if (sys.version_info > (3, 0)):
    import importlib

type = 'none'
tts_module = None
debug_messages = None

def setup(robot_config):
    global type
    global tts_module
    global debug_messages
    
    type = robot_config.get('tts', 'type')
    debug_messages = robot_config.get('misc', 'debug_messages')
    
    if type != 'none':
        # set volume level

        # tested for 3.5mm audio jack
        if robot_config.getint('tts', 'tts_volume') > 50:
            os.system("amixer set PCM -- -100")

        # tested for USB audio device
        os.system("amixer -c 2 cset numid=3 %d%%" % robot_config.getint('tts', 'tts_volume'))


    #import the appropriate tts handler module.
    if robot_config.getboolean('misc', 'custom_tts'):
        if (sys.version_info > (3, 0)):
            try:
                tts_module = importlib.import_module('tts.tts_custom')
            except ImportError:
        	    print("unable to load tts/tts_custom.py")
        	    tts_module = importlib.import_module('tts.'+type)
        else:
            try:
                tts_module = __import__('tts.tts_custom', fromlist=['tts_custom'])
            except ImportError:
                print("unable to load tts/tts_custom.py")
                tts_module = __import__("tts."+type, fromlist=[type])
    else:    
        if (sys.version_info > (3, 0)):
            tts_module = importlib.import_module('tts.'+type)
        else:
            tts_module = __import__("tts."+type, fromlist=[type])    

    #call the tts handlers setup function
    tts_module.setup(robot_config)

def say(*args):
    message = args[0]

    #check the number of arguments passed, and hand off as appropriate to the tts handler
    if len(args) == 1:
        tts_module.say(message)
    else:
        tts_module.say(message, args[1])
    
