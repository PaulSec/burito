import httplib2
from bs4 import BeautifulSoup
from urllib import urlencode

# developped for Burito
from GlobalVars import *

#
# FUNCTIONS
#


def create_header(cookie=""):
    header = {}

    header['User-Agent'] = GlobalVars.opts.user_agent
    if (GlobalVars.opts.cookie is not None):
        header['Cookie'] = cookie + GlobalVars.opts.cookie
    else:
        header['Cookie'] = cookie

    return header


def send_http_request(h, url, header, is_get_request=True, data=None):
        # set the referer to the target url
    header['Referer'] = url

        # do the HTTP request
    if (is_get_request):
        # realize GET request
        if (data is not None):
            url = url + "?%s" % (urlencode(data))
        resp, response = h.request(url, headers=header)
    else:
        # realize POST request
        header['Content-type'] = 'application/x-www-form-urlencoded'

        resp, response = h.request(
            url, "POST", headers=header, body=urlencode(data))

    return resp, response


# get the action from the form we want to perform the attack.
def get_action_form():
    h = httplib2.Http(disable_ssl_certificate_validation=True)
    # send a request to get the html body

    if (GlobalVars.opts.post_params is not None):
        # POST param to access the form
        data = {}
        for arg in GlobalVars.opts.post_params.split('&'):
            tmp = arg.split('=')
            data[tmp[0]] = tmp[1]

        resp, response = send_http_request(
            h, GlobalVars.opts.url, create_header(), False, data)
    else:
        resp, response = send_http_request(
            h, GlobalVars.opts.url, create_header(), True, None)

    soup = BeautifulSoup(''.join(response))

    # generate selectors
    generate_selectors()

    # check if there are forms with those selectors
    form = soup.findAll('form', GlobalVars.opts.selectors)
    if (form is None):
        # if not, exception
        raise Exception('No form on this page !')
    else:
        # if there are some forms, let the user choose one
        if (len(form) > 1):
            iterate_on_all_forms(form)
        elif (len(form) == 0):
            raise Exception('No form with those specified options.')
        else:
            # there's only one result
            determine_HTTP_method(form[0])
            GlobalVars.opts.indice_form_page = 0
            GlobalVars.opts.action_form = generate_action_form(
                form[0]['action'])


# generate selectors to get the form
def generate_selectors():
    #
    # Selector priority :
    # id > name > action
    #

    GlobalVars.opts.selectors = {}
    # check if there's an id which has been set
    if (GlobalVars.opts.form_id is not None):
        GlobalVars.opts.selectors['id'] = opts.form_id
    else:
        if (GlobalVars.opts.form_name is not None):
            GlobalVars.opts.selectors['name'] = GlobalVars.opts.form_name
        else:
            if (GlobalVars.opts.form_action is not None):
                GlobalVars.opts.selectors[
                    'action'] = GlobalVars.opts.form_action


# iterate on all forms if after findAll (with selectors), len > 1
def iterate_on_all_forms(form):

    write_to_file("Multiple forms, choose one :")
    # disable the flag with the selectors
    # index of the form (used after with the other threads)
    i = 0
    notFound = False
    # iterate on all the forms
    while (i < len(form) and not notFound):
        # display the action form, and ask the user if that's the one
        res = raw_input(form[i]['action'] + " ? [Y/n] ")
        if (res == "Y"):
            GlobalVars.opts.indice_form_page = i
            GlobalVars.opts.action_form = generate_action_form(
                form[i]['action'])
            notFound = True

            # determine what kind of HTTP Request it is
            determine_HTTP_method(form[i])
        else:
            pass
        i = i + 1
    if (not notFound):
        raise Exception('You should have chosen a form !')


# determine http method using the form
def determine_HTTP_method(form):
    GlobalVars.opts.method_form = ""

    try:
        if (form['method'].lower() == "get"):
            GlobalVars.opts.method_form = "GET"
        else:
            GlobalVars.opts.method_form = "POST"
    except:
        GlobalVars.opts.method_form = "POST"


# function to generatz the action form
def generate_action_form(action):
    action = action.lower()
    # first case : http://www.example.com/
    if (action[:4] == "http"):
        return action
    # second case : /form/submit
    elif (action[:1] == "/"):
        if ("//" in GlobalVars.opts.url):
            res = GlobalVars.opts.url.split('/')
            return res[0] + '//' + res[2] + action
        else:
            res = GlobalVars.opts.url.split('/')
            return res[0] + action[:1]
    # third case : ./form/link
    elif (action[:2] == "./"):
        if (GlobalVars.opts.url[-1:] != "/"):
            raise('not implemented for this version. ')
        else:
            return GlobalVars.opts.url + action[2:]
    # fourth case : #
    elif (action == "#"):
        return GlobalVars.opts.url
    else:
        # else : action="test?"
        if (GlobalVars.opts.url[-1:] == "/"):
            return GlobalVars.opts.url + action
        else:
            string = GlobalVars.opts.url.split('/')
            string = string[::-1]
            string[0] = action
            string = string[::-1]
            res = ""
            for val in string:
                res += val + "/"
            res = res[:-1]
            return res
