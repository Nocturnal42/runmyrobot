import time
import cozmo
import _thread as thread
import sys
import networking
import schedule
import extended_command
import cozmo_go_to_charger as autodocking
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes
import PIL

coz = None
video_port = ""
camera_id = 0
infoServer = None
annotated = False
flipped = 0
colour = False
cozmoChatSocket = None

def startListenForCozmoChatServer():
    thread.start_net_thread(waitForCozmoChatServer, ())

def waitForCozmoChatServer():
    while True:
        cozmoChatSocket.wait(seconds=1)

def cozmoChatConnect():
    global cozmoChatSocket
    print("connecting cozmo to chat")
    cozmoChatSocket = SocketIO('letsrobot.tv', 8000, LoggingNamespace)
    startListenForCozmoChatServer()
        
def cozmoChat(send_message):
    message = {}
    message['chat_message'] = { 'message': send_message,
                                'robot_name': 'CozmoTester',
                                'robot_id': 67202604,
                                'room': 'Nocturnal',
                                'secret': "iknowyourelookingatthisthatsfine"
                              }
    cozmoChatSocket.emit(message)
 
def set_colour(command, args):
    global colour 
    if extended_command.is_authed(args['name']) == 2:
        colour = not colour
        coz.camera.color_image_enabled = colour


def set_annotated(command, args):
    global annotated
    if extended_command.is_authed(args['name']) == 2:
        annotated = not annotated

def set_flipped(command, args):
    global flipped
    if extended_command.is_authed(args['name']) == 2:
        flipped = not flipped

def autodock(command, args):
    if extended_command.is_authed(args['name']) == 2:
        autodocking.drive_to_charger(coz, 5)


def setup(robot_config):
    global camera_id
    global infoServer
    global video_port
    global annotated
    global colour
    
    camera_id = robot_config.get('robot', 'camera_id')
    infoServer = robot_config.get('misc', 'info_server')
    video_port = getVideoPort()
    cozmo.setup_basic_logging()
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    
    extended_command.add_command('.annotate', set_annotated)
    extended_command.add_command('.autodock', autodock)
    extended_command.add_command('.color', set_colour)
    extended_command.add_command('.colour', set_colour)

    try:
        thread.start_new_thread(cozmo.run_program, (run,))
#        thread.start_new_thread(cozmo.run_program, (run,), {'use_3d_viewer':True})
    except KeyboardInterrupt as e:
        pass        
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)

    while not coz:
        try:
           time.sleep(0.5)
           print("not coz")
        except (KeyboardInterrupt, SystemExit):
           sys.exit()

    if robot_config.has_section('cozmo'):
        send_online_status = robot_config.getboolean('cozmo', 'send_online_status')
        annotated = robot_config.getboolean('cozmo', 'annotated')
        colour = robot_config.getboolean('cozmo', 'colour')
    else:
        send_online_status = True
    
    if send_online_status:
        print("Enabling online status")
        schedule.repeat_task(10, updateServer);

def getVideoPort():
    import robot_util
    import json
    url = 'https://%s/get_video_port/%s' % (infoServer, camera_id)
    response = robot_util.getWithRetry(url).decode('utf-8')
    return(json.loads(response)['mpeg_stream_port'])

# Tell the server we are online
def updateServer():
    print("Updating Server")
    try:
        networking.appServerSocketIO.emit('send_video_status', {'send_video_process_exists': True,
                               'ffmpeg_process_exists': True,
                               'camera_id':camera_id})
    except AttributeError:
        print("Error: No appServerSocketIO");

def getCozmo():
    return coz

def run(coz_conn):
    sdk_detect = 0
    
    def new_image(evt, **kwargs):
        nonlocal sdk_detect
        sdk_detect = 0        
        if p:
            image = coz.world.latest_image
            if image:
                if annotated:
                    image = image.annotate_image()
                else:
                    image = image.raw_image
                    
                if flipped:
                    image = image.transpose(PIL.Image.FLIP_LEFT_RIGHT)
                image.save(p.stdin, 'PNG')
            else:
                time.sleep(.1)

    def conn_closed(evt, **kwargs):
        print("Connection Closed")
        thread.interrupt_main()
        thread.exit()
              

    global coz
#    coz = coz_conn.wait_for_robot()
    coz = coz_conn

    coz.enable_stop_on_cliff(True)

    # Turn on image receiving by the camera
    coz.camera.image_stream_enabled = True

    # Enable anotators
    coz.world.image_annotator.enable_annotator('objects')
    coz.world.define_custom_wall(CustomObjectTypes.CustomType01,
                                              CustomObjectMarkers.Hexagons5,
                                              120, 150,
                                              64, 64, True)
    coz.world.define_custom_cube(CustomObjectTypes.CustomType02,
                                              CustomObjectMarkers.Diamonds3,
                                              25,
                                              25, 25, True)
    coz.world.define_custom_cube(CustomObjectTypes.CustomType03,
                                              CustomObjectMarkers.Circles2,
                                              25,
                                              25, 25, True)

    coz.say_text( "hey everyone, lets robot!", in_parallel=True)

    while True:
        time.sleep(0.25)

        from subprocess import Popen, PIPE
        from sys import platform

        #Frames to file
        #p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'png', '-r', '25', '-i', '-', '-vcodec', 'mpeg1video', '-qscale', '5', '-r', '25', 'outtest.mpg'], stdin=PIPE)
        
        if platform.startswith('linux') or platform == "darwin":
            #MacOS/Linux
            p = Popen(['/usr/local/bin/ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'png', '-r', '25', '-i', '-', '-vcodec', 'mpeg1video', '-r', '25', "-f","mpegts","http://letsrobot.tv:"+str(video_port)+"/hello/320/240/"], stdin=PIPE)
        elif platform.startswith('win'):
            #Windows
            import os
            if not os.path.isfile('c:/ffmpeg/bin/ffmpeg.exe'):
               print("Error: cannot find c:\\ffmpeg\\bin\\ffmpeg.exe check ffmpeg is installed. Terminating controller")
               thread.interrupt_main()
               thread.exit()
#            videoCommand = ['c:/ffmpeg/bin/ffmpeg.exe', '-nostats', '-loglevel', 'panic', '-y', '-f', 'image2pipe', '-rtbufsize', '200k', '-vcodec', 'png', '-r', '25', '-i', '-', '-f', 'dshow', '-video_size', '640x480', '-r', '25', '-rtbufsize', '10000k', '-i', 'video=Logitech QuickCam Pro 9000', '-filter_complex', '[1:v]setpts=PTS-STARTPTS[pip];[pip][0]overlay=main_w-overlay_w-10:10', '-vcodec', 'mpeg1video', '-b:v', '400k', '-f', 'mpegts', 'http://letsrobot.tv:'+str(video_port)+'/BlahBlah/640/480']
#           p = Popen(videoCommand, stdin=PIPE)
            p = Popen(['c:/ffmpeg/bin/ffmpeg.exe', '-nostats', '-y', '-f', 'image2pipe', '-vcodec', 'png', '-r', '25', '-i', '-', '-vcodec', 'mpeg1video', '-r', '25','-b:v', '400k', "-f","mpegts","http://letsrobot.tv:"+str(video_port)+"/BlahBlah/320/240/"], stdin=PIPE)
        
#        coz.world.add_event_handler(cozmo.world.EvtNewCameraImage, new_image)
        coz.world.add_event_handler(cozmo.camera.EvtNewRawCameraImage, new_image)

        time.sleep(10)
        while True:
            time.sleep(1)
            if sdk_detect < 5:
                sdk_detect = sdk_detect + 1
#            else: # More than 2 seconds without a new image, sdk has disconnected.
#                thread.interrupt_main()
#                thread.exit()       
#        try:
#            while True:
#                if coz:
#                    image = coz.world.latest_image
#                    if image:
#                        if annotated:
#                            image = image.annotate_image()
#                        else:
#                            image = image.raw_image
#                        image.save(p.stdin, 'PNG')
#                else:
#                    time.sleep(.1)
#            p.stdin.close()
#            p.wait()
#        except cozmo.exceptions.SDKShutdown:
#            p.stdin.close()
#            p.wait()
#            thread.interrupt_main()
#            thread.exit()
#            pass               

def say(*args):
    global coz
    message = args[0]

    try:
        coz.say_text(message, duration_scalar=0.75)
    except cozmo.exceptions.RobotBusy:
        return False

