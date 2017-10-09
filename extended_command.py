# TODO 

# Impliment as many of these as possible.

#/mod username
#/unmod username
 
#Robocaster & Channel Mods:
 
#Channel admin Stuff:
 
#/ban username
#/unban username
#/timeout username
#/untimeout username
#/devmode on
#/devmode off
#/anon control on
#/anon control off
#/anon tts on
#/anon tts off
#/anon off
#/anon on
 
#Assign xcontrol manually. 
#/xcontrol username
#/xcontrol username (int time)
#/xcontrol off
 
 
#(block controls for specific users)
#/stop username
#/unstop username
 
#Robot Admin Stuff:
#/tts mute
#/tts unmute
#/tts volume (int)
#/mic mute
#/mic unmute
#/speed (int)
#/brightness (int)
#/contrast (int)
#/saturation (int)
 
#User level: 
 
#(blocking a user also bans them from your channel)
#/block username
#/unblock username

move_handler=None

def setup():
    return


def handler(args):
    print args

# This function checks the user sending the command, and if authorized
# call the move handler.
def auth_move(args):
    return