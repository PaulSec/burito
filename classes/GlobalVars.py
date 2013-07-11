import threading


class GlobalVars(object):

    lock_last_password_tested = threading.Lock()
    lock_access_tab = threading.Lock()
    lock_access_file = threading.Lock()

    cond_tab_empty = threading.Condition()
    cond_pass_not_found = threading.Condition()

    LAST_PASSWORD_TESTED_MIN = ""
    LAST_PASSWORD_TESTED_MAX = ""
    FOUND_PASSWORD = ""
    TAB_PASSWORDS = []

    # number of passwords tested
    NB_PASSWORD_TESTED = 0

    #
    # FLAGS
    #
    FLAG_PASS_FOUND = False
    FLAG_NO_MORE_PROCESSING = False

    #
    # Options
    #
    options = None

    # mandatories args
    mandatories = ['url', 'param_to_crack']

    args_command_line = []
