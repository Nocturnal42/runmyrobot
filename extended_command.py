from __future__ import print_function
import os
import networking
import tts.tts as tts
import schedule

# TODO 
# If I pull the send_video stuff into controller, the ability to restart the ffmpeg process would
# be useful

# /stationary only able to move left and right.
#/mod username
#/unmod username
#/stop username
#/unstop username
#/tts volume (int)
#/mic mute
#/mic unmute
#/xcontrol username
#/xcontrol username (int time)
#/xcontrol off
#/speed (int)


# Cant DO
# Can't do anything that requires server side stuff. Ban and timoue are do-able, 
# only on at the bot level.
#(blocking a user also bans them from your channel)
#/block username
#/unblock username


# Done
#/devmode on
#/devmode off
#/anon control on
#/anon control off
#/anon tts on
#/anon tts off
#/anon off
#/anon on
#/tts mute
#/tts unmute
#/brightness (int)
#/contrast (int)
#/saturation (int)
#/ban username
#/unban username
#/timeout username
#/untimeout username

move_handler = None
mods=[]
dev_mode = None
dev_mode_mods = False
anon_control = True
owner = None
v4l2_ctl = None
banned=[]

def setup(robot_config):
    global owner
    global v4l2_ctl
    
    owner = robot_config.get('robot', 'owner')
    v4l2_ctl = robot_config.get('misc', 'v4l2-ctl')
    
    mods = networking.getOwnerDetails(owner)['moderators']
#    mods = networking.getOwnerDetails(owner)['robocaster']['moderators']
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
    
def anon_handler(command, args):
    global anon_control

    if len(command) > 1:
        if is_authed(args['name']): # Moderator
            if command[1] == 'on':
                anon_control = True
                tts.unmute_anon_tts()
            elif command[1] == 'off':
                anon_control = False
                tts.mute_anon_tts()
            elif len(command) > 3:
                if command[1] == 'control':
                    if command[2] == 'on':
                        anon_control = True
                    elif command[2] == 'off':
                        anon_control = False
                elif command[1] == 'tts':
                    if command[2] == 'on':
                        tts.unmute_anon_tts()
                    elif command[2] == 'off':
                        tts.mute_anon_tts()
    print("anon_control : " + str(anon_control))

def ban_handler(command, args):
    global banned
    
    if len(command) > 1:
        user = command[1]
        if is_authed(args['name']): # Moderator
            banned.append(user)
            print(user + " added to ban list")
            tts.mute_user_tts(user)            

def unban_handler(command, args):
    global banned

    if len(command) > 1:
        user = command[1]
        if is_authed(args['name']): # Moderator
            if user in banned:
                banned.remove(user)
                print(user + " removed from ban list")
                tts.unmute_user_tts(user)            

def timeout_handler(command, args):
    global banned

    if len(command) > 1:
        user = command[1]
        if is_authed(args['name']): # Moderator
            banned.append(user)
            schedule.single_task(5, untimeout_user, user)
            print(user + " added to timeout list")
            tts.mute_user_tts(user)            
            
    
def untimeout_user(user):
    global banned

    if user in banned:  
        banned.remove(user)
        print(user + " timeout expired")
        tts.unmute_user_tts(user)            


def untimeout_handler(command, args):
    global banned

    if len(command) > 1:
        user = command[1]
        if is_authed(args['name']): # Moderator
            if user in banned:
                banned.remove(user)
                print(user = " removed from timeout list")
                tts.unmute_user_tts(user)            
    
    
def devmode_handler(command, args):
    global dev_mode
    global dev_mode_mods
   
    if len(command) > 1:
        if is_authed(args['name']) == 2: # Owner
            if command[1] == 'on':
                dev_mode = True
                dev_mode_mods = False
            elif command[1] == 'off':
                dev_mode = False
            elif command[1] == 'mods':
                dev_mode = True
                dev_mode_mods = True
    print("dev_mode : " + str(dev_mode))
    print("dev_mode_mods : " + str(dev_mode_mods))

def mic_handler(command, args):
    if is_authed(args['name']) == 1: # Owner
        if len(command) > 1:
            if command[1] == 'mute':
                # Mic Mute
                return
            elif command[1] == 'unmute':
                # Mic Unmute
                return

def tts_handler(command, args):
    print("tts :", tts)
    if len(command) > 1:
        if is_authed(args['name']) == 2: # Owner
            if command[1] == 'mute':
                print("mute")
                tts.mute_tts()
                return
            elif command[1] == 'unmute':
                tts.unmute_tts()
                return
            elif command[1] == 'vol':
                # TTS int volume command
                return

def brightness(command, args):
    if len(command) > 1:
        if is_authed(args['name']): # Moderator
            os.system(v4l2_ctl + " --set-ctrl brightness=" + command[1])
            print("brightness set to " + command[1])

def contrast(command, args):
    if len(command) > 1:
        if is_authed(args['name']): # Moderator
            os.system(v4l2_ctl + " --set-ctrl contrast=" + command[1])
            print("contrast set to " + command[1])

def saturation(command, args):
    if len(command) > 2:
        if is_authed(args['name']): # Moderator
            os.system(v4l2_ctl + " --set-ctrl saturation=" + command[1])
            print("saturation set to " + command[1])
	


# This is a dictionary of commands and their handler functions
commands={    '.anon'       :    anon_handler,
	            '.ban'        :    ban_handler,
	            '.unban'      :    unban_handler,
	            '.timeout'    :    timeout_handler,
	            '.untimout'   :    untimeout_handler,
              '.devmode'    :    devmode_handler,
	            '.mic'        :    mic_handler,
	            '.tts'        :    tts_handler,
              '.brightness' :    brightness,
              '.contrast'   :    contrast,    
              '.saturation' :    saturation
	        }

def handler(args):  
    command = args['message']
# TODO : This will not work with robot names with spaces, update it to split on ']'
# [1:]
    command = command.split(']')[1:][0].split(' ')[1:]
    print(command)
    
    if command != None:
        if command[0] in commands:
            commands[command[0]](command, args)

# This function checks the user sending the command, and if authorized
# call the move handler.
def move_auth(args):
    user = args['user']
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
    elif user not in banned: # Check for banned and timed out users
        move_handler(args)
 
    return
