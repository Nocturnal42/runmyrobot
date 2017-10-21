import tts.tts as tts
import os
# Example for adding custom code to the controller
hw_num - None

def setup(robot_config):
    global hw_num
    
    hw_num = robot_config.getint('tts', 'hw_num')
    # Your custom setup code goes here
    
 
    # call the default tts setup routine
    tts.setup(robot_config) 
       
def say(*args):
    message = args[0]

    # Check the username on the chat message, and play a sound before the tts
    # message for particular users.
    # check if we are doing a simple say, or a chat tts message
    if len(args) > 1:
        user = args[1]['username']
        if user == 'jill':
            prefix = "harken.mp3"
        elif user == 'theodore':
            prefix = "tremble.mp3"
        elif user == 'rick':
            prefix = "relax.mp3"
        elif user == 'roboempress':
            prefix = "run.mp3"
        elif user == 'mikey':
            prefix = "meander.mp3"
        else:
            tts.say(args)
            exit()
                
        if tts.mute:
            exit()
            
        os.system('/usr/bin/mpg123-alsa -a hw:%d,0 %s' % hw_num, prefix)
        tts.say(args)

    else:  # Simple Say
        tts/say(message)
        
    # Your custom tts interpreter code goes here

    
    
    # This code calls the default command interpreter function for your hardware.
    module.say(args)
    