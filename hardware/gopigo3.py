sys.path.append("/home/pi/Dexter/GoPiGo3/Software/Python")
import easygopigo3

def setup(robot_config):
    easyGoPiGo3 = easygopigo3.EasyGoPiGo3()
    
def move(command):
    e = easyGoPiGo3
    if command == 'L':
        e.set_motor_dps(e.MOTOR_LEFT, -e.get_speed())
        e.set_motor_dps(e.MOTOR_RIGHT, e.get_speed())
        time.sleep(0.15)
        easyGoPiGo3.stop()
    if command == 'R':
        e.set_motor_dps(e.MOTOR_LEFT, e.get_speed())
        e.set_motor_dps(e.MOTOR_RIGHT, -e.get_speed())
        time.sleep(0.15)
        easyGoPiGo3.stop()
    if command == 'F':
        easyGoPiGo3.forward()
        time.sleep(0.35)
        easyGoPiGo3.stop()
    if command == 'B':
        easyGoPiGo3.backward()
        time.sleep(0.35)
        easyGoPiGo3.stop()

    