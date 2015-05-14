#!/usr/local/bin/python3

import random, cgi, cgitb, os, datetime, mysql.connector
from http import cookies
form = cgi.FieldStorage()
cgitb.enable()

def print1():
	
	#check if logged in
	if cookie["login"].value == "":
		not_logged_in =  """Content-type: text/html
		%(cookie)s\n
		<!doctype html>
		<html>
			<head>
				<title>Quiz Creation Page</title>
			</head>
			<body>
				<div align='center'>
					<h2>Must Be Logged In To Create Quiz</h2>
					<form action='/cgi-bin/lab7/start_page.py'>
					<input type='submit' value='Home' name='submit' />
				</div>
			</body>
		</html>""" % {
				"cookie": str(cookie),
			}
		print(not_logged_in)
		return None
	else:
		display1 = "Quiz Name: <input type='text' name='quiz_name' /><br>"
	
	if int(cookie["quiz_fail"].value) == 1:
		fail_html = "Quiz Name Taken"
	else:
		fail_html = "Enter Quiz Name"
	
	html =  """Content-type: text/html
	%(cookie)s\n
	<!doctype html>
	<html>
		<head>
			<title>Quiz Creation Page</title>
		</head>
		<body>
			<h1>%(fail_html)s</h1>
			<form action='/cgi-bin/lab7/quiz_creation.py' method='post'>
			%(display1)s
			<input type='submit' value='Submit' name='submit' />
		</body>
	</html>""" % {
			"cookie": str(cookie),
			"fail_html": fail_html,
			"display1": display1,
		}
	print(html)

def print2():
	display2 = ""
	display2 = display2 + "Question " + str(cookie["qn"].value) + ": <input type='text' name='question' /><br>"
	
	html =  """Content-type: text/html
	%(cookie)s\n
	<!doctype html>
	<html>
		<head>
			<title>Quiz Creation Page</title>
		</head>
		<body>
			<h1>Stage = %(stage_num)d</h1>
			<form action='/cgi-bin/lab7/quiz_creation.py' method='post'>
			%(display2)s
			<input type='submit' value='Submit' name='submit' />
		</body>
	</html>""" % {
			"cookie": str(cookie),
			"stage_num": int(cookie["print"].value),
			"display2": display2,
		}
	print(html)

#answer textbox plus value textbox, each time submit is pressed, adds the question to quiz dictionary
#another submit buttom to indicate finished with question
#display3 is html code to take answers and values
def print3():
	question = cookie["question"].value
	display3 = ""
	display3 = display3 + "Answer " + str(cookie["an"].value) + ": <input type='text' name='answer' /><br>"
	display3 = display3 + "Value: " + "<input type='text' name='value' /><br>"
	
	html = """Content-type: text/html
	%(cookie)s\n
	<!doctype html>
	<html>
		<head>
			<title>Quiz Creation Page</title>
		</head>
		<body>
			<h1>Stage = %(stage_num)d</h1>
			<form action='/cgi-bin/lab7/quiz_creation.py' method='post'>
			%(display3)s
			<input type='submit' value='Add Answer' name='add_answer' />
			<input type='submit' value='Add Question' name='add_question' />
			</form>
			<form action='/cgi-bin/lab7/start_page.py' method='post'>
			<input type='submit' value='Finish Quiz' name='finish_quiz' />
			</form>
		</body>
	</html>""" % {
			"cookie": str(cookie),
			"stage_num": int(cookie["print"].value),
			"display3": display3,
		}
	print(html)

def create_new_cookie():
	expiration = datetime.datetime.now() + datetime.timedelta(days=1)
	cookie = cookies.SimpleCookie()
	cookie["print"] = 0
	cookie["user_name"] = ""
	cookie["quiz_name"] = ""
	cookie["question"] = ""
	cookie["quiz_fail"] = ""
	cookie["qn"] = 1
	cookie["an"] = 1
	return cookie

	
if "HTTP_COOKIE" in os.environ:
	cookie = cookies.SimpleCookie(os.getenv("HTTP_COOKIE"))
	if "print" in cookie:
		cookie["print"] = int(cookie["print"].value) + 1
	else:
		cookie = create_new_cookie()
else:
	cookie = create_new_cookie()
	
# if add question
if form.getvalue('add_question') == "Add Question":
	cookie["print"] = 3
	
# if finish quiz
if form.getvalue('finish_quiz') == "Finish Quiz":
	cookie["print"] = 1

display = int(cookie["print"].value)
if display == 1:
	print1()
elif display == 2:
	fail = 0
	db = mysql.connector.connect(host="silo.soic.indiana.edu", user="root", password="", database="quizes", port=16001)
	cursor = db.cursor()
	
	quiz_name = str(form.getvalue('quiz_name')).strip()
	
	cursor.execute("SELECT description FROM quiz")
	data = cursor.fetchall()
	for x in data:
		if quiz_name in x:
			cookie["print"] = 1
			cookie["quiz_fail"] = 1
			cursor.close()
			db.close()			
			print1()
			fail = 1
			break;	
	
	if fail == 0:	
		#input quiz_name into quiz table
		cursor.execute("INSERT INTO quiz VALUES (NULL, %s, NOW())", (quiz_name, ))
		cookie["quiz_id"] = cursor.lastrowid	
		
		db.commit()
		cursor.close()
		db.close()
		
		cookie["print"] = int(cookie["print"].value) + 1
		print2()	
	
elif display == 3:
	print2()
elif display == 4:
	
	db = mysql.connector.connect(host="silo.soic.indiana.edu", user="root", password="", database="quizes", port=16001)
	cursor = db.cursor()
	
	question = form.getvalue('question')
	
	cursor.execute("INSERT INTO question VALUES (NULL, %s, %s)", (question, cookie["quiz_id"].value))
	cookie["question_id"] = cursor.lastrowid
	
	cookie["qn"] = int(cookie["qn"].value) + 1
	
	db.commit()
	cursor.close()
	db.close()
	
	print3()
	
elif display > 4:
	cookie["answer"] = form.getvalue('answer')
	cookie["value"] = form.getvalue('value')
	cookie["an"] = int(cookie["an"].value) + 1
	
	db = mysql.connector.connect(host="silo.soic.indiana.edu", user="root", password="", database="quizes", port=16001)
	cursor = db.cursor()
	
	cursor.execute("INSERT INTO answer VALUES (NULL, %s, %s, %s)", (form.getvalue('answer'), form.getvalue('value'), cookie["question_id"].value))
	
	db.commit()
	cursor.close()
	db.close()
	
	print3()