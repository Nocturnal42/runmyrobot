from threading import Timer

def task(wait, task_handler):
    task_handler();
    t=Timer(wait, task, [wait, task_handler])
    t.daemon = True
    t.start()

def repeat_task(wait, task_handler):
    t=Timer(wait, task, [wait, task_handler])
    t.daemon = True
    t.start()
    
def single_task(wait, task_handler):
    t=Timer(wait, task_handler)
    t.daemon = True
    t.start()