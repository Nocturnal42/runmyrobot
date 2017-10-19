import os

# TODO 

# Pull list of moderators


# If I pull the send_video stuff into controller, the ability to restart the ffmpeg process would
# be useful

# /stationary only able to move left and right.

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

move_handler = None
mods=[]
dev_mode = None
anon_control = None
anon_tts = None
owner = None
v4l2_ctl = None

def setup(robot_config):
    global owner
    global v4l2_ctl
    
    owner = robot_config.get('robot', 'owner')
    v4l2_ctl = robot_config.get('misc', 'v4l2-ctl')

# check if the user is the owner or moderator, 0 for not, 1 for moderator, 2 for owner
def is_authed(user):
    if user == owner:
        return(2)
    else:
        return(0)


# add a new command handler, this will also allow for overriding existing ones.
def add_command(command, function):
    global commands
    commands[command] = function
    
def devmode(command, args):
    global dev_mode

    if is_authed(args['name']) == 2: # Owner
        if command[2] == 'on':
            dev_mode = True
        elif command[2] == 'off':
            dev_mode = False

def anon(command, args):
    global anon_control
    global anon_tts

    if is_authed(args['name']): # Moderator
        if command[2] == 'on':
            anon_control = True
            anon_tts = True
        elif command[2] == 'off':
            anon_control = False
            anon_tts = False
        elif command[2] == 'control':
            if command[3] == 'on':
                anon_control = True
            elif command[3] == 'off':
                anon_control = False
        elif command[2] == 'tts':
            if command[3] == 'on':
                anon_tts = True
            elif command[3] == 'off':
                anon_tts = False

def tts(command, args):
    if is_authed(args['name']) == 2: # Owner

        if command[2] == 'mute':
            # TTS Mute command
            return
        elif command[2] == 'unmute':
            # TTS Unmute command
            return
        elif command[2] == 'vol':
            # TTS int volume command
            return

def mio(command, args):
    if is_authed(args['name']) == 2: # Owner
        if command[2] == 'mute':
            # Mic Mute
            return
        elif command[2] == 'unmute':
            # Mic Unmute
            return

def brightness(command, args):
    if is_authed(args['name']): # Moderator
        os.system(v4l2_ctl + " --set-ctrl brightness=" . int(command[2]))
        return

def contrast(command, args):
    if is_authed(args['name']): # Moderator
        os.system(v4l2_ctl + " --set-ctrl contrast=" . int(command[2]))
        return

def saturation(command, args):
    if is_authed(args['name']): # Moderator
        os.system(v4l2_ctl + " --set-ctrl saturation=" . int(command[2]))
	


# This is a dictionary of commands and their handler functions
commands={    '.devmode'    :    devmode,
	            '.anon'       :    anon,
	            '.tts'        :    tts,
	            '.mic'        :    mic,
              '.brightness' :    brightness,
              '.contrast'   :    contrast,    
              '.saturation' :    saturation
	        }

def handler(args):  
    user = args['name']
    command = args['message']
# TODO : This will not work with robot names with spaces, update it to split on ']'
# [1:]
    command = command.split(' ')
    if command != None:
        try:
            if command[1] in commands:
                commands[command[1]](command, args)
        except:
            pass                

# This function checks the user sending the command, and if authorized
# call the move handler.
def move_auth(args):
    move_user = args['name']
    anon = args['anonymous']
    
    if auth_mode == None:
        move_handler(args)
    return