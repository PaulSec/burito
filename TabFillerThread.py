import threading
import sys

# developped for Burito
from GlobalVars import *
from LogHelper import *

#
# CLASS FillTabThread
#


class FillTabThread(threading.Thread):

    # init method
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    # run method, choosing the method to fill the tab
    def run(self):

        # fill the tab with the method.
        if (GlobalVars.opts.attack_brute is True):
            self.bruteforce()
        else:
            self.browseFile()

        # set the flag to advertise threads that we're not calculating anymore
        GlobalVars.FLAG_NO_MORE_PROCESSING = True

    def stop(self):
        self.running = False

    # method for bruteforce attack
    def bruteforce(self):
        val = GlobalVars.opts.min
        while (val <= GlobalVars.opts.max):
            self.recurse(val, 1, "")
            val = val + 1

    # method to browse the file
    def browseFile(self):

        f = open(GlobalVars.opts.file_dico)

        while (GlobalVars.FLAG_PASS_FOUND is False and self.running is True):
            line = f.readline()
            if not line:
                break
            # append the word into the tab
            GlobalVars.lock_access_tab.acquire()
            GlobalVars.TAB_PASSWORDS.append(line.strip())
            GlobalVars.lock_access_tab.release()
            self.waitForLimit()

    # waitForLimit method
    def waitForLimit(self):

        if ((not GlobalVars.FLAG_PASS_FOUND)
            and (self.running is True)
                and (len(GlobalVars.TAB_PASSWORDS) > 200)):
            GlobalVars.cond_tab_empty.acquire()
            # print "[++++] Je m'endors"
            GlobalVars.cond_tab_empty.wait()
            # print "Tab Filler reveille"
            GlobalVars.cond_tab_empty.release()

    # recurse method
    def recurse(self, width, position, baseString):
        # if pass found, stop filling tab
        if (GlobalVars.FLAG_PASS_FOUND is False and self.running is True):

            i = self.get_character_index(width, position)

            while i < len(GlobalVars.opts.charset):
            # for char in GlobalVars.opts.charset:
                if (GlobalVars.FLAG_PASS_FOUND is False and self.running is True):
                    if (position < width):
                        self.recurse(
                            width, position + 1, baseString + "%c" % GlobalVars.opts.charset[i])
                    else:
                        self.add_word_or_exit(i, position, baseString)
                else:
                    sys.exit(0)

                i = i + 1
        else:
            sys.exit(0)

    # add work to the tab or exit
    def add_word_or_exit(self, i, position, baseString):
        if (position <= GlobalVars.opts.max):
            # acquire the lock to append a new element
            self.waitForLimit()

            GlobalVars.lock_access_tab.acquire()
            GlobalVars.TAB_PASSWORDS.append(
                baseString + "%c" % GlobalVars.opts.charset[i])
            GlobalVars.lock_access_tab.release()
        else:
            # then whe try now new values > len(MAX_PASS)
            GlobalVars.FLAG_NO_MORE_PROCESSING = True
            sys.exit(0)

    def get_character_index(self, width, position):
        if(GlobalVars.opts.resume is not None and width == GlobalVars.opts.min):
            char = GlobalVars.opts.resume[position - 1]
            try:
                return GlobalVars.opts.charset.index(char)
            except:
                raise Exception(
                    'Password resume contains character not included in the charset !\n, kill process !')
        else:
            return 0
