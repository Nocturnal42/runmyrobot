# Example for adding custom code to the controller
module = None

def setup(robot_config):
    # Your custom setup code goes here
    
 
    # This code calls the default setup function for your tts.
    # global module
    module = __import__("tts."+robot_config.get('robot', 'type'), fromlist=[robot_config.get('robot', 'type')])
    module.setup(robot_config)
    
def move(args):
    # Your custom tts interpreter code goes here
    
    
    
    # This code calls the default command interpreter function for your hardware.
    module.say(args)
    