import RPi.GPIO as GPIO

def setup(robot_config):
    mode=GPIO.getmode()
    print " mode ="+str(mode)
    GPIO.cleanup()
    #Change the GPIO Pins to your connected motors in gpio.conf
    #visit http://bit.ly/1S5nQ4y for reference
    gpio_config = configparser.ConfigParser()
    gpio_config.read('gpio.conf')
    if str(robotID) in gpio_config.sections():
        config_id = str(robotID)
    else:
        config_id = 'default'		
    StepPinForward = int(str(gpio_config[config_id]['StepPinForward']).split(',')[0]),int(str(gpio_config[config_id]['StepPinForward']).split(',')[1])
    StepPinBackward = int(str(gpio_config[config_id]['StepPinBackward']).split(',')[0]),int(str(gpio_config[config_id]['StepPinBackward']).split(',')[1])
    StepPinLeft = int(str(gpio_config[config_id]['StepPinLeft']).split(',')[0]),int(str(gpio_config[config_id]['StepPinLeft']).split(',')[1])
    StepPinRight = int(str(gpio_config[config_id]['StepPinRight']).split(',')[0]),int(str(gpio_config[config_id]['StepPinRight']).split(',')[1])
	
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(StepPinForward, GPIO.OUT)
    GPIO.setup(StepPinBackward, GPIO.OUT)
    GPIO.setup(StepPinLeft, GPIO.OUT)
    GPIO.setup(StepPinRight, GPIO.OUT)

def move(direction):
    if direction == 'F':
        GPIO.output(StepPinForward, GPIO.HIGH)
        time.sleep(l298n_sleeptime * l298n_rotatetimes)
        GPIO.output(StepPinForward, GPIO.LOW)
    if direction == 'B':
        GPIO.output(StepPinBackward, GPIO.HIGH)
        time.sleep(l298n_sleeptime * l298n_rotatetimes)
        GPIO.output(StepPinBackward, GPIO.LOW)
    if direction == 'L':
        GPIO.output(StepPinLeft, GPIO.HIGH)
        time.sleep(l298n_sleeptime)
        GPIO.output(StepPinLeft, GPIO.LOW)
    if direction == 'R':
        GPIO.output(StepPinRight, GPIO.HIGH)
        time.sleep(l298n_sleeptime)
        GPIO.output(StepPinRight, GPIO.LOW)
       
