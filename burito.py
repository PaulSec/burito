# default libs
import httplib2
from bs4 import BeautifulSoup
import time
import optparse
import string

# developed for burito
from classes.ParameterCheckerThread import *
from classes.TabFillerThread import *
from classes.GlobalVars import *
from classes.HTTPHelper import *
from classes.OptionsValidator import *
from classes.LogHelper import *

THREADS_LIST = []

# stop thread function


def stop_threads():
    GlobalVars.cond_tab_empty.acquire()
    GlobalVars.cond_tab_empty.notify()
    GlobalVars.cond_tab_empty.release()

    for curThread in THREADS_LIST:
        curThread.stop()


# launch thread function
def launch_threads():

    # launch a thread for filling the tab
    currentThread = FillTabThread()
    currentThread.start()
    THREADS_LIST.append(currentThread)

    i = 0
    # start the threads
    while (i < GlobalVars.opts.num_threads):
        currentThread = ParameterCheckerThread()
        currentThread.start()
        THREADS_LIST.append(currentThread)
        i = i + 1


def wait_during_processing():

    while (not GlobalVars.FLAG_PASS_FOUND):
        time.sleep(0.5)
        if ((GlobalVars.FLAG_NO_MORE_PROCESSING and len(GlobalVars.TAB_PASSWORDS) == 0)):
            break

    # this solution will be after some code fixing in Python 2.7

    # GlobalVars.cond_pass_not_found.acquire()
    # GlobalVars.cond_pass_not_found.wait()
    # GlobalVars.cond_pass_not_found.release()


#
# MAIN PROGRAM
#
parser = optparse.OptionParser()
create_option_parser(parser)

if (len(sys.argv) <= 3):

    parser.print_help()

else:
    (opts, GlobalVars.args_command_line) = parser.parse_args()

    startTime = time.time()

    # declare some options for the Globals class
    opts.num_threads = int(opts.num_threads)
    opts.min = int(opts.min)
    opts.max = int(opts.max)

    # set the globals options in file
    GlobalVars.opts = opts
    # if no exception were raised, launch the attack

    # Verify params given by the user
    check_valid_parameters()

    # print args
    write_to_file(str(opts))

    try:
        # launch the threads
        launch_threads()

        # wait until it's finished
        wait_during_processing()
    except (KeyboardInterrupt, SystemExit):
        # if Ctrl-C occured, then stop all threads
        stop_threads()

     # waiting for all threads to finish
    for curThread in THREADS_LIST:
        curThread.join()

    # execution time
    write_to_file("Execution in : " + str(
        time.time() - startTime) + "seconds.")
    # number password tested
    write_to_file("Number of passwords tested : " +
                  str(GlobalVars.NB_PASSWORD_TESTED))

    # if pass found
    if (GlobalVars.FLAG_PASS_FOUND):
        write_to_file("[!] Pass found : " + GlobalVars.FOUND_PASSWORD)
        sys.exit(0)
    else:
        # pass not found
        write_to_file("Pass not found.")
        write_to_file(
            "Last password tested : " + GlobalVars.LAST_PASSWORD_TESTED_MIN)
        sys.exit(1)
