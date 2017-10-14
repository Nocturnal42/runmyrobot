import os

# TODO 

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
    

def handler(args):
    global dev_mode
    global anon_control
    global anon_tts

    
    user = args['name']
    command = args['message']
    command = command.split(' ')
    if command != None:
        try:
            if command[1][0] == '\\':
# TODO load mods with a robocasters mods, and update this check to include them
                if user == owner:
                    if command[1] == '\\devmode':
                        if command[2] == 'on':
                            dev_mode = True
                        elif command[2] == 'off':
                            dev_mode = False
                    elif command[1] == '\\anon':
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
                    elif command[1] == '\\tts':
                        if command[2] == 'mute':
                            # TTS Mute command
                            return
                        elif command[2] == 'unmute':
                            # TTS Unmute command
                            return
                        elif command[2] == 'vol':
                            # TTS int volume command
                            return
                    elif command[1] == '\\mic':
                        if command[2] == 'mute':
                            # Mic Mute
                            return
                        elif command[2] == 'unmute':
                            # Mic Unmute
                            return
                    elif command[1] == 'brightness':
                        # Set brightness
                        os.system(v4l2_ctl + " --set-ctrl brightness=" . command[2])
                        return
                    elif command[1] == 'contrast':
                        # Set contrast
                        os.system(v4l2_ctl + " --set-ctrl contrast=" . command[2])
                        return
                    elif command[1] == 'saturation':
                        # Set saturation
                        os.system(v4l2_ctl + " --set-ctrl saturation=" . command[2])
                        return
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