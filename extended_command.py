from __future__ import print_function
import os
import networking
import tts.tts as tts

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
owner = None
v4l2_ctl = None

def setup(robot_config):
    global owner
    global v4l2_ctl
    
    owner = robot_config.get('robot', 'owner')
    v4l2_ctl = robot_config.get('misc', 'v4l2-ctl')
    
    mods = networking.getOwnerDetails(owner)['moderators']
    print("Moderators :", mods)

# check if the user is the owner or moderator, 0 for not, 1 for moderator, 2 for owner
def is_authed(user):
    if user == owner:
        return(2)
    elif user in mods:
        return(1)
    else:
        return(0)


# add a new command handler, this will also allow for overriding existing ones.
def add_command(command, function):
    global commands
    commands[command] = function
    
def devmode_handler(command, args):
    global dev_mode
    global dev_mode_mods
    
    if len(command) > 2:
        if is_authed(args['name']) == 2: # Owner
            if command[2] == 'on':
                dev_mode = True
                dev_mode_mods = False
            elif command[2] == 'off':
                dev_mode = False
            elif command[2] == 'mods':
                dev_mode = True
                dev_mode_mods = True

def anon_handler(command, args):
    global anon_control

    if len(command) > 2:
        if is_authed(args['name']): # Moderator
            if command[2] == 'on':
                anon_control = True
                tts.unmute_anon_tts()
            elif command[2] == 'off':
                anon_control = False
                tts.mute_anon_tts()
            elif len(command) > 3:
                if command[2] == 'control':
                    if command[3] == 'on':
                        anon_control = True
                    elif command[3] == 'off':
                        anon_control = False
                elif command[2] == 'tts':
                    if command[3] == 'on':
                        tts.unmute_anon_tts()
                    elif command[3] == 'off':
                        tts.mute_anon_tts()

def tts_handler(command, args):
    print("tts :", tts)
    if len(command) > 2:
        if is_authed(args['name']) == 2: # Owner
            if command[2] == 'mute':
                print("mute")
                tts.mute_tts()
                return
            elif command[2] == 'unmute':
                tts.unmute_tts()
                return
            elif command[2] == 'vol':
                # TTS int volume command
                return

def mic_handler(command, args):
    if is_authed(args['name']) == 2: # Owner
        if len(command) > 2:
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
commands={    '.devmode'    :    devmode_handler,
	            '.anon'       :    anon_handler,
	            '.tts'        :    tts_handler,
	            '.mic'        :    mic_handler,
              '.brightness' :    brightness,
              '.contrast'   :    contrast,    
              '.saturation' :    saturation
	        }

def handler(args):  
    command = args['message']
# TODO : This will not work with robot names with spaces, update it to split on ']'
# [1:]
    command = command.split(' ')
    if command != None:
#        try:
            if command[1] in commands:
                commands[command[1]](command, args)
#        except:
#            print("Exception in extended command handler")
#            pass                

# This function checks the user sending the command, and if authorized
# call the move handler.
def move_auth(args):
    user = args['name']
    anon = args['anonymous']
    
    if anon_control == False and anon:
        exit()
    elif dev_mode_mods:
        if is_authed(user):
            move_handler(args)
        else:
            exit()
    elif dev_mode:
        if is_authed(user) == 2: # owner
            move_handler(args)
        else:
            exit()
    else:
        move_handler(args)
 
    return