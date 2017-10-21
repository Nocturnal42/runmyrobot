import os
import sys
import re

if (sys.version_info > (3, 0)):
    import importlib

type = 'none'
tts_module = None
debug_messages = None
mute = False
mute_anon = None
urlRegExp = "(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"
url_filter = None

def setup(robot_config):
    global type
    global tts_module
    global debug_messages
    global mute_anon
    global url_filter
    
    type = robot_config.get('tts', 'type')
    debug_messages = robot_config.get('misc', 'debug_messages')
    mute_anon = robot_config.getboolean('tts', 'anon_tts')
    url_filter = robot_config.getboolean('tts', 'filter_url_tts')
    
    if type != 'none':
        # set volume level

        # tested for 3.5mm audio jack
        if robot_config.getint('tts', 'tts_volume') > 50:
            os.system("amixer set PCM -- -100")

        # tested for USB audio device
        os.system("amixer -c 2 cset numid=3 %d%%" % robot_config.getint('tts', 'tts_volume'))


    #import the appropriate tts handler module.
    if robot_config.getboolean('misc', 'custom_tts'):
        if os.path.exists('tts/tts_custom.py'):
            if (sys.version_info > (3, 0)):
                tts_module = importlib.import_module('tts.tts_custom')
            else:
                tts_module = __import__('tts.tts_custom', fromlist=['tts_custom'])
        else:
            print("Unable to find tts/tts_custom.py")    
            if (sys.version_info > (3, 0)):
                tts_module = importlib.import_module('tts.'+type)
            else:
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

    if mute:
        exit()
    else:
        #check the number of arguments passed, and hand off as appropriate to the tts handler
        if len(args) == 1:
            tts_module.say(message)
        else:
            if mute_anon and args[1]['anonymous'] == True:
                exit()
            if url_filter:
                if re.search(urlRegExp, message):
                    exit()
            else:
                tts_module.say(message, args[1])
    
def mute_tts():
    global mute
    mute = True
    if debug_messages:
        print ("TTS muted")    

def unmute_tts():
    global mute
    mute = False
    if debug_messages:
        print ("TTS unmuted")    
    
def mute_anon_tts():
    global mute_anon
    mute_anon = True
    if debug_messages:
        print ("Anonymous TTS muted")    
    
def unmute_anon_tts():
    global mute_anon
    mute_anon = False
    if debug_messages:
        print ("Anonymous TTS unmuted")    
    