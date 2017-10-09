import serial

ser = None

def setup(robot_config):
    global ser
    serialDevice = robot_config.get('serial', 'serial_device')
    # initialize serial connection
#TODO add baud rate to config file
    serialBaud = 9600
    print "baud:", serialBaud
    try:
        ser = serial.Serial(serialDevice, serialBaud, timeout=1)  # open serial
    except:
        print "error: could not open serial port"
        try:
            ser = serial.Serial('/dev/ttyACM0', serialBaud, timeout=1)  # open serial
        except:
            print "error: could not open serial port /dev/ttyACM0"
            try:
                ser = serial.Serial('/dev/ttyUSB0', serialBaud, timeout=1)  # open serial
            except:
                print "error: could not open serial port /dev/ttyUSB0"
                try:
                    ser = serial.Serial('/dev/ttyUSB1', serialBaud, timeout=1)  # open serial
                except:
                    print "error: could not open serial port /dev/ttyUSB1"
                    try:
                        ser = serial.Serial('/dev/ttyUSB2', serialBaud, timeout=1)  # open serial
                    except:
                        print "error: could not open serial port /dev/ttyUSB2"

    if ser is None:
        print "error: could not find any valid serial port"
    else:
        telly.sendSettings(ser, commandArgs)

def move(args):
    command = args['command']
    
    sendSerialCommand(ser, command)
	