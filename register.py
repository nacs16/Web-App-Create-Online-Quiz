#!/usr/local/bin/python3

#MySQL Server on port 16001
import random, cgi, cgitb, os, datetime, uuid, mysql.connector
from http import cookies
form = cgi.FieldStorage()
cgitb.enable()

def print1():
	if int(cookie["reg_fail"].value) == 1:
		cookie["reg_fail"] = 0
		try_again = "<h1>Registration Failed: Username taken or passwords do not match</h1><br>"
	else:
		try_again = "<h1>Register</h1><br>"
	
	html = """Content-type: text/html
	%(cookie)s\n
	<!doctype html>
	<html>
		<head>
			<title>Register</title>
		</head>
		<body>
			%(try_again)s
			<form action='/cgi-bin/lab7/register.py' method='post'>
			Username: <input type='text' name='user_name' /><br>
			Password: <input type='password' name='password' /><br>
			Re-Enter Password: <input type='password' name='re_password' /><br>
			<input type='submit' value='Register' name='register' />
			</form>
			<form action="http://silo.soic.indiana.edu:16000/cgi-bin/lab7/start_page.py">
				<input type="submit" value="Return to Start Page">
			</form>
		</body>
	</html>""" % {
			"cookie": str(cookie),
			"try_again": try_again,
		}
	print(html)

def print2():
	
	html = """Content-type: text/html
	%(cookie)s\n
	<!doctype html>
	<html>
		<head>
			<title>Registration Complete</title>
		</head>
		<body>
			<div align='center'>
				<h1>Registration Complete</h1>
				<form action="http://silo.soic.indiana.edu:16000/cgi-bin/lab7/start_page.py">
					<input type="submit" value="Return to Start Page">
				</form>
			</div>
		</body>
	</html>""" % {
			"cookie": str(cookie),
		}
	print(html)
	
def create_new_cookie():
	expiration = datetime.datetime.now() + datetime.timedelta(days=1)
	cookie = cookies.SimpleCookie()
	cookie["reg_print"] = 0
	cookie["reg_fail"] = 0
	cookie["login"] = ""
	return cookie
	
#Check cookie
if "HTTP_COOKIE" in os.environ:
	cookie = cookies.SimpleCookie(os.getenv("HTTP_COOKIE"))
	if "reg_print" in cookie:
		cookie["reg_print"] = int(cookie["reg_print"].value) + 1
	else:
		cookie = create_new_cookie()
else:
	cookie = create_new_cookie()	
display = int(cookie["reg_print"].value)

# 1: input username and password
if display == 1:
	print1()

# 2: First check for username/password errors. print2() otherwise
if display == 2:
	fail = 0
	#if passwords don't match:
	if str(form.getvalue('password')) != str(form.getvalue('re_password')):
		cookie["reg_print"] = 1
		cookie["reg_fail"] = 1
		print1()
		fail = 1
			
	# open the database connection
	db = mysql.connector.connect(host="silo.soic.indiana.edu", user="root", password="", database="quizes", port=16001)
	# create a cursor object with which to execute queries
	cursor = db.cursor()
	
	#if username is taken:
	#query MySQL server user table to see if inputed username exists.
	cursor.execute("SELECT email FROM user")
	data = cursor.fetchall()
	for x in data:
		if form.getvalue('user_name') in x:
			cookie["reg_print"] = 1
			cookie["reg_fail"] = 1
			print1()
			cursor.close()
			db.close()
			fail = 1
			break;
			
	# username and password are good, put them in database and reset cookies:
	if fail != 1:
		cookie["reg_print"] = 0
		cookie["reg_fail"] = 0
		cookie["login"] = form.getvalue('user_name')
		cursor.execute("INSERT INTO user VALUES (NULL, %s, SHA1(%s))", (str(form.getvalue('user_name')), str(form.getvalue('password'))))
		db.commit()
		cursor.close()
		db.close()
		print2()