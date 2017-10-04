# Example for adding custom code to the controller
module = None

def setup(robot_config):
    # Your custom setup code goes here


    
    # Call the setup handler for max7219 LEDs
    # import hardware.max7219
    # max7219.setup(robot_config)
 
    # This code calls the default setup function for your hardware.
    # global module
    module = __import__("hardware."+robot_config.get('robot', 'type'), fromlist=[robot_config.get('robot', 'type')])
    print dir(module)
    module.setup(robot_config)

    
def move(command):
    # Your custom command interpreter code goes here
    
    
    
    # Call the command handler for max7219 LEDs
    # hardware.max7219.move(command)
    
    # This code calls the default command interpreter function for your hardware.
    module.move(command)
    