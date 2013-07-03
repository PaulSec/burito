import optparse
import string

# developped for Burito
from GlobalVars import *
from HTTPHelper import *
import optparse

################################################################
########### FUNCTIONS
################################################################
def create_option_parser(parser):
    options_charset = """[a-z]       : lower cases characters
            [A-Z]       : upper cases characters
            [0-9]       : digits
            [hexdigits] : hex digits
            [punctuation]:ponctuation"""

    parser.add_option('--u', help='URL of the actual form', dest='url')
    parser.add_option('--brute', help='brute force attack', dest='attack_brute', default=False, action='store_true')
    parser.add_option('--min', help='minimum chars testing (default : 1)', dest='min', default=4)
    parser.add_option('--max', help='maximum chars testing (default : 1)', dest='max', default=6)
    parser.add_option('--Charset', help=options_charset, dest='charset', default="%s" % (string.ascii_letters))
    parser.add_option('--resume', help='Resume to a password attempt', dest='resume', default=None)
    parser.add_option('--dico', help='dictionnary force attack', dest='attack_dico', default=False, action='store_true')
    parser.add_option('--file', help='File for the dictionnary attack', dest='file_dico', default=None)
    parser.add_option('--id', help='id of the form', dest='form_id', default=None)
    parser.add_option('--name', help='name of the form', dest='form_name', default=None)
    parser.add_option('--action', help='URL action', dest='form_action', default=None)
    parser.add_option('--m', help='Fail message when login failed', dest='message_failed')
    parser.add_option('--p', help='Parameter to crack', dest='param_to_crack')
    parser.add_option('--cookie', help='Cookie that you want in the header', dest='cookie')
    parser.add_option('--t', help='Number of thread for all the attacks', dest='num_threads', default=10)
    parser.add_option('--g', help='Names of the generated inputs separated with commas', dest='generated', default=False, action='store_true')
    parser.add_option('--user_agent', help='Spoof the User-Agent', dest='user_agent', default="Burito Cracker v0.1")
    parser.add_option('--log', help='LOG file', dest='log_file')
    parser.add_option('--status-code', help='status code accepted for the response', dest='accepted_status_code')
    parser.add_option('--post-data', help='If generated value, POST params to access page', dest='post_params', default=None)
    parser.add_option('--v', help='Verbose mode', dest='verbose', default=False, action='store_true')


# check valid parameters
def check_valid_parameters():
    # exit program if no attack defined
    if (GlobalVars.opts.attack_dico is True and GlobalVars.opts.attack_brute is True):
        raise Exception("You should choose only one attack !")

    if (GlobalVars.opts.attack_dico is False and GlobalVars.opts.attack_brute is False):
        raise Exception("You should choose one attack !")

    check_common_args()
    check_mandatory_args()

    if (GlobalVars.opts.attack_dico is True):
        check_valid_parameters_dictionnary()
    else:
        check_valid_parameters_brute()

    get_action_form()


# check common arguments
def check_common_args():

    if (GlobalVars.opts.log_file is not None):
        GlobalVars.opts.LOG_FILE = open(GlobalVars.opts.log_file, 'a')
    else:
        GlobalVars.opts.LOG_FILE = None

    if (GlobalVars.opts.accepted_status_code is not None):
        GlobalVars.opts.accepted_status_code = GlobalVars.opts.accepted_status_code.split(',')

    # add the known parameters
    GlobalVars.opts.args = {}
    if (len(GlobalVars.args_command_line) > 0):
        for arg in GlobalVars.args_command_line:
            tmp = arg.split('=')
            GlobalVars.opts.args[tmp[0]] = tmp[1]


# verify that the mandatory fields are well set in the command line.
def check_mandatory_args():
    
    for m in GlobalVars.mandatories:
        if (GlobalVars.opts.__dict__[m] is None):
            print "mandatory " + m + " option is missing !\n"
            parser.print_help()
            exit(-1)



# check valid parameters for attack type
def check_valid_parameters_brute():
    # check the value of the charset
    GlobalVars.opts.charset = GlobalVars.opts.charset.replace('[0-9]', string.digits)
    GlobalVars.opts.charset = GlobalVars.opts.charset.replace('[a-z]', string.lowercase)
    GlobalVars.opts.charset = GlobalVars.opts.charset.replace('[A-Z]', string.uppercase)
    GlobalVars.opts.charset = GlobalVars.opts.charset.replace('[hexdigits]', string.hexdigits)
    GlobalVars.opts.charset = GlobalVars.opts.charset.replace('[punctuation]', string.punctuation)

    # if options resume is ON, check it
    if (GlobalVars.opts.resume is not None):
        if (len(GlobalVars.opts.resume) != GlobalVars.opts.min):
            raise Exception("Password resume should be same length than minimum !")


# check the valid parameter for a file
def check_valid_parameters_dictionnary():
    # check that there's a file
    if (GlobalVars.opts.__dict__["file_dico"] is None):
        print("Dictionnary file missing !")
        parser.print_help()
        sys.exit(-1)
