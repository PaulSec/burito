## Burito

Burito is a Hydra-like tool allowing you to audit Web applications using forms with server-side generated parameters. <br />
Feel free to use it (GPLv3) for non-commercial use and report any bug as soon as you experience it. <br />

## 1. Basic example

>(...)<br />
>< input type="text" name="login" value=""><br />
>< input type="password" name="password" value=""><br />
>(...)

_Command line_

>python burito.py --dico --file=passwords.txt --u="http://www.example.com/login.php" __login=admin__ --p=password

## 2. Burito and Cookies ?

_Same code as previous example._<br />
The actual login form is only accessible for authenticated users. 

>python burito.py --dico --file=passwords.txt --u="http://www.example.com/login.php" login=admin --p=password __--cookie="SESSIONID=ab7cde9c"__

## 3. Password is only digits. 

_Same code as previous example._<br />
If we know that the actual password only contains digits and the length of the password is 4 then : 

>python burito.py __--brute --min=4 --max=4__ -u "http://www.example.com/login.php" login=admin --p=password --cookie="SESSIONID=ab7cde9c" __--Charset="[0-9]"__

## 4. Web app checking User Agent

_Same code as previous example._<br />
Some web apps check the User-Agent and redirect scripts if it doesn't fit a proper User-Agent. 
Per default, User-Agent is : "Burito Scanner"

>python burito.py --dico --file=passwords.txt --u="http://www.example.com/login.php" login=admin --p=password __--user_agent=="My Specific User Agent"__

## 5. Generated values in form 

Imagine a form containing this :

>(...)<br />
>< input type="text" name="login" value=""><br />
>< input type="password" name="password" value=""><br />
>< input type="hidden" name="csrf_token" value="ab7def894bcd24"><br />
>(...)

Some parameters can be generated directly when form got loaded. 
Burito script is connecting to the page, gathering all the informations (cookies, forms inputs..) and creating the specified request. 

>python burito.py --dico --file=passwords.txt --u="http://www.example.com/login.php" login=admin --p=password --user_agent="My Specific User Agent" __--g__

## 6. Mastering the status code !

During my audits, I got confronted with some web applications redirecting people (HTTP Redirect 302) when the login failed. 
However, with Python, if the status code is not a 200, it's raised as an exception. 
An option has been implemented to manage those status code. 

>Use case : When login failed, redirect user to /loginForm


>python burito.py --dico --file=passwords.txt --u="http://www.example.com/login.php" login=admin --p=password --status-code=302

_If I want to continue with different status code, just separate them with a comma ','_

>python burito.py --dico --file=passwords.txt --u="http://www.example.com/login.php" login=admin --p=password __--status-code=302__

## 7. Gimme more threads !

If you're machine looks like a _Super Cosmic Monkey_, you can specify the number of threads you want to run on the machine. <br /><br />
_Example : 50 threads ?_
>python burito.py --dico --file=passwords.txt --u="http://www.example.com/login.php" login=admin --p=password __--t=50__

## 8. Log my session. 

You can specify a file where you want to log the ouput. <br />
If __none__, it will be displayed in the terminal itself. 

>python burito.py --dico --file=passwords.txt --u="http://www.example.com/login.php" login=admin --p=password --log=SessionExample.com.txt


