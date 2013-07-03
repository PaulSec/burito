from GlobalVars import *

# function to log output
def write_to_file(string):
    if (GlobalVars.opts.LOG_FILE is not None):
        GlobalVars.lock_access_file.acquire()
        GlobalVars.opts.LOG_FILE.write(string + '\n')
        GlobalVars.lock_access_file.release()
    else:
        print string
