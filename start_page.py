#!/usr/local/bin/python3

import random, cgi, cgitb, os, datetime, uuid, mysql.connector
from http import cookies
form = cgi.FieldStorage()
cgitb.enable()

def create_new_cookie():
	expiration = datetime.datetime.now() + datetime.timedelta(days=1)
	cookie = cookies.SimpleCookie()
	cookie["print"] = 0
	cookie["reg_print"] = 0
	cookie["reg_fail"] = 0
	cookie["quiz_fail"] = 0
	cookie["user_name"] = ""
	cookie["quiz_name"] = ""
	cookie["question"] = ""
	cookie["dat_path"] = ""
	cookie["qn"] = 1
	cookie["an"] = 1
	cookie["login"] = ""
	return cookie

if "HTTP_COOKIE" in os.environ:
	cookie = cookies.SimpleCookie(os.getenv("HTTP_COOKIE"))
	if "print" in cookie:
		cookie["print"] = 0
		cookie["reg_print"] = 0
		cookie["reg_fail"] = 0
		cookie["quiz_fail"] = 0
		cookie["qn"] = 1
		cookie["an"] = 1
		cookie["question"] = ""
		cookie["quiz_name"] = ""
	else:
		cookie = create_new_cookie()
else:
	cookie = create_new_cookie()
		
def makeShitHappen(cookie):
	if cookie["login"].value == "":
		logged_in = 0
	else:
		logged_in = 1
	
	db = mysql.connector.connect(host="silo.soic.indiana.edu", user="root", password="", database="quizes", port=16001)
	cursor = db.cursor()
	
	empty_list = []
	cursor.execute("SELECT description, id FROM quiz")
	data = cursor.fetchall()
	if logged_in == 1: #look through user_scores
		cursor.execute("SELECT id FROM user WHERE email = %s", (cookie["login"].value, ))
		data2 = cursor.fetchall()
		userID = data2[0][0]
	#elif logged_in == 0: #look through cookies	
	
	html = ""
	for x in data:
		quizID = x[1]
		quiz_name = x[0]
		
		if logged_in == 1:
			cursor.execute("SELECT score FROM user_scores WHERE quiz_id = %s and user_id = %s", (quizID, userID))
			data2 = cursor.fetchall()
			if data2 == empty_list:
				score = "N/A"
			else:
				score = data2[0][0]
		
		if logged_in == 0:
			if quiz_name.strip() in cookie:
				score = cookie[quiz_name.strip()].value
			else:
				score = "N/A"

		html = html + "<tr>\n" + "<td>" + "<a href='http://silo.soic.indiana.edu:16000/cgi-bin/lab7/take_quiz.py?quizID=" + str(quizID) + "'>" + str(quiz_name) + "</a>" + "</td>\n<td>" + str(score) + "</td>\n</tr>\n"
	
	return html
	
if form.getvalue('logout') == "Logout":
	cookie["login"] = ""
if cookie["login"].value != "":
	html_login = "<h2>Logged in as " + cookie["login"].value + "</h2>" + "<form action='/cgi-bin/lab7/start_page.py' method='post'>\n<input type='submit' value='Logout' name='logout' />\n</form>"
	create_quiz_link = " | <a href='quiz_creation.py'>Create Quiz</a>"
else:
	html_login = "<h2>Login to create a quiz</h2>"
	create_quiz_link = ""
	
html_table_fill = makeShitHappen(cookie)
	
html_code =  """Content-type: text/html
%(cookie)s\n
<!doctype html>
<html>
	<head>
		<title>List of Quizzes</title>
		<link rel="stylesheet" href="style.css" type="text/css" />
	</head>
	<body>
		<div id="wrapper">
		<div id="header" align='center'>
			<h1>Quiz Management</h1>
		</div>

		<div id="menu" align='center'>
			<a href="start_page.py">Home</a> |
			<a href="login.py">Login</a> |
			<a href="register.py">Register</a>
			%(create_quiz_link)s
		</div>
		
		<p>
		%(html_login)s
		</p>
		
		<div id="content">
			<div align='center'>
			<table width='300' border = '1'>
				<tr>
					<td>QUIZ</td>
					<td>SCORE</td>
				</tr>
					%(fill_table)s
			</table>
			</div>
		</div>
		
		<div id="footer" align='center'>
			<p>
				Nicholas Solano A290
			</p>
		</div>
		</div>
	</body>
</html>""" % {
		"cookie": str(cookie),
		"print_value": cookie["print"].value,
		"create_quiz_link": create_quiz_link,
		"html_login": html_login,
		"fill_table": html_table_fill,
	}

print(html_code)