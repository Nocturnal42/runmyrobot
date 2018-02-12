from threading import Thread

watches={}


def watch():
    global watches
    
    for (name, process) in watches.items():
        if not process[0].is_alive():
            print("Process "+name+" not running, restarting")
            start(name, process[1], *process[2], **process[3])
         
def start(name, startFunction, *args, **kwargs):
    global watches
    thread = Thread(target=startFunction, args=args, kwargs=kwargs)
    thread.setDaemon(True)
    thread.start()
    watches[name] = [thread, startFunction, args, kwargs]
