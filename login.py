#!/usr/local/bin/python3

#MySQL Server on port 16001
import random, cgi, cgitb, os, datetime, uuid, mysql.connector
from http import cookies
form = cgi.FieldStorage()
cgitb.enable()

def print1():
	if int(cookie["reg_fail"].value) == 1:
		cookie["reg_fail"] = 0
		try_again = "<h1>Login Failed: Username doesn't exist or password is invalid</h1><br>"
	else:
		try_again = "<h1>Login</h1><br>"
	
	html = """Content-type: text/html
	%(cookie)s\n
	<!doctype html>
	<html>
		<head>
			<title>Login</title>
		</head>
		<body>
			%(try_again)s
			<form action='/cgi-bin/lab7/login.py' method='post'>
			Username: <input type='text' name='user_name' /><br>
			Password: <input type='password' name='password' /><br>
			<input type='submit' value='Login' name='login' />
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
			<title>Login Complete</title>
		</head>
		<body>
			<div align='center'>
				<h1>Login Complete</h1>
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
	
	# open the database connection
	db = mysql.connector.connect(host="silo.soic.indiana.edu", user="root", password="", database="quizes", port=16001)
	# create a cursor object with which to execute queries
	cursor = db.cursor()
	
	#if username doesn't exist:
	#query MySQL server user table to see if inputed username exists.
	cursor.execute("SELECT email FROM user")
	data = cursor.fetchall()
	fail = 1
	for x in data:	
		if form.getvalue('user_name') in x:
			fail = 0
			break;
	if fail == 1:
		cookie["reg_print"] = 1
		cookie["reg_fail"] = 1
		print1()
		cursor.close()
		db.close()
	
	if fail != 1:
		#if password isn't correct:
		cursor.execute("SELECT u.password FROM user u WHERE u.email = %s", (form.getvalue('user_name'), ))

		data = cursor.fetchall()
		pass1 = data[0][0]
		cursor.execute("SELECT SHA1(%s)", (form.getvalue('password'), ))
		data = cursor.fetchall()
		pass2 = data[0][0]
		if pass1 != pass2 and fail == 0:
			cookie["reg_print"] = 1
			cookie["reg_fail"] = 1
			fail = 1
			print1()
			cursor.close()
			db.close()
		
	# username and password are good, change cookie indicating user is logged in:
	if fail == 0:	
		cookie["reg_print"] = 0
		cookie["reg_fail"] = 0
		cookie["login"] = form.getvalue('user_name')
		cursor.close()
		db.close()
		print2()