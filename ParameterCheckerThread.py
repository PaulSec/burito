import threading
import sys
import httplib2
from urllib import urlencode
from bs4 import BeautifulSoup

# developped for Burito
from LogHelper import *
from GlobalVars import *
from HTTPHelper import *

#
# CLASS ParameterCheckerThread
#


class ParameterCheckerThread(threading.Thread):

    # init
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        self.h = httplib2.Http(disable_ssl_certificate_validation=True)
        self.cookie = ""

    # run method
    def run(self):

        # while pass not found and run is still on
        while (not GlobalVars.FLAG_PASS_FOUND and self.running is True):
            password = self.get_next_password()

            # gathering the data
            data = self.gathering_data()
            # insert the parameter to crack
            data[GlobalVars.opts.param_to_crack] = password

            write_to_file("Trying password " + password)

            # send data
            self.send_data(password, data)

    # stop method
    def stop(self):
        self.running = False

    # send HTTP Request method
    def send_HTTP_Request(self, url, isGETRequest=False, data=None):

        resp, response = send_http_request(
            self.h, url, create_header(self.cookie), isGETRequest, data)

        return resp, response

    # store loast password method.
    def store_last_password(self, password):

        GlobalVars.lock_last_password_tested.acquire()
        if (GlobalVars.LAST_PASSWORD_TESTED_MAX == ""):
            GlobalVars.LAST_PASSWORD_TESTED_MAX = password
        if (GlobalVars.LAST_PASSWORD_TESTED_MIN == ""):
            GlobalVars.LAST_PASSWORD_TESTED_MIN = password

        if (password > GlobalVars.LAST_PASSWORD_TESTED_MAX):
            GlobalVars.LAST_PASSWORD_TESTED_MAX = password
        else:
            if (password < GlobalVars.LAST_PASSWORD_TESTED_MAX and password > GlobalVars.LAST_PASSWORD_TESTED_MIN):
                GlobalVars.LAST_PASSWORD_TESTED_MIN = password
        GlobalVars.lock_last_password_tested.release()

    # get generated inputs from the form (if necessary)
    def get_generated_inputs(self, response, data):
        soup = BeautifulSoup(''.join(response))
        form = soup.findAll('form', GlobalVars.opts.selectors)

        for input in form[GlobalVars.opts.indice_form_page].findAll(['input']):
            try:
                if (input['name'] not in data):
                    data[str(input['name'])] = str(input['value'])
            except:
                pass
        return data

    # get next password method (using global variable in GlobalVars class)
    def get_next_password(self):
        password = ""

        while (password == ""):
            # lock to get the first element in the array
            GlobalVars.lock_access_tab.acquire()
            if (len(GlobalVars.TAB_PASSWORDS) > 0):
                password = GlobalVars.TAB_PASSWORDS[0]
                del GlobalVars.TAB_PASSWORDS[0]
                # increment the counter for password tested
                GlobalVars.NB_PASSWORD_TESTED = GlobalVars.NB_PASSWORD_TESTED + 1

            GlobalVars.lock_access_tab.release()

            # we do not really need the lock because
            # we only check a "potential" value of the tab
            if (len(GlobalVars.TAB_PASSWORDS) < 50):
                GlobalVars.cond_tab_empty.acquire()
                GlobalVars.cond_tab_empty.notify()
                GlobalVars.cond_tab_empty.release()
                # print "j'ai reveille le tab filler"

            self.stop_if_no_more_values(password)

        return password

    def stop_if_no_more_values(self, password):
        # if no more value and flag no more processing, we quit
        if (password == "" and GlobalVars.FLAG_NO_MORE_PROCESSING and (len(GlobalVars.TAB_PASSWORDS) == 0)):
            GlobalVars.cond_pass_not_found.acquire()
            GlobalVars.cond_pass_not_found.notify()
            GlobalVars.cond_pass_not_found.release()
            # no more results and the tab is empty
            sys.exit(1)

    # if problem (status code / connection / ..) then re-insert password
    def reinsert_value(self, password):
        GlobalVars.lock_last_password_tested.acquire()
        GlobalVars.TAB_PASSWORDS.append(password)
        GlobalVars.lock_last_password_tested.release()

    def gathering_data(self):
        # add the data to the request
        data = GlobalVars.opts.args.copy()

        if (GlobalVars.opts.generated):
            self.cookie = ""
            resp, response = self.send_HTTP_Request(GlobalVars.opts.url, True)

            try:
                self.cookie = resp['set-cookie']
            except:
                self.cookie = ""

            data = self.get_generated_inputs(response, data)

        return data

    def send_data(self, password, data):
        try:
            if (GlobalVars.opts.method_form == "POST"):
                resp, response = self.send_HTTP_Request(
                    GlobalVars.opts.action_form, False, data)
            else:
                resp, response = self.send_HTTP_Request(
                    GlobalVars.opts.action_form, True, data)

            if (int(resp['status']) == 200):  # ok status code

                #
                # Found password ?
                #
                if (GlobalVars.opts.message_failed not in response):
                    write_to_file("[*] Found Password : " + password)
                    GlobalVars.FOUND_PASSWORD = password
                    GlobalVars.FLAG_PASS_FOUND = True

                self.store_last_password(password)
            else:
                # if this is an other status code than 200
                if (resp['status'] in GlobalVars.opts.accepted_status_code):
                    # pass if it's an accepted status code
                    self.store_last_password(password)
                else:
                    # else, reInsert the value
                    self.reinsert_value(password)
        except Exception, e:
            print e
