#!/usr/local/bin/python3

import random, cgi, cgitb, os, datetime, mysql.connector
from http import cookies
form = cgi.FieldStorage()
cgitb.enable()

def create_new_cookie():
	expiration = datetime.datetime.now() + datetime.timedelta(days=1)
	cookie = cookies.SimpleCookie()
	cookie["print"] = 0
	cookie["login"] = ""
	cookie["user_name"] = ""
	cookie["quiz_name"] = ""
	cookie["question"] = ""
	cookie["qn"] = 1
	cookie["an"] = 1
	return cookie

if "HTTP_COOKIE" in os.environ:
	cookie = cookies.SimpleCookie(os.getenv("HTTP_COOKIE"))
else:
	cookie = create_new_cookie()
	
def showMeYourMoves():
	
	if cookie["login"].value == "":
		logged_in = 0
	else:
		logged_in = 1
		
	db = mysql.connector.connect(host="silo.soic.indiana.edu", user="root", password="", database="quizes", port=16001)
	cursor = db.cursor()
	
	quizID = str(form.getvalue('quizID'))
	
	cursor.execute("SELECT q.text, a.text, a.point_value FROM question q INNER JOIN answer a ON q.id=a.question_id WHERE q.quiz_id = %s", (quizID, ))
	data = cursor.fetchall()
	
	cursor.execute("SELECT description FROM quiz WHERE id = %s", (quizID, ))
	data2 = cursor.fetchall()
	quiz_name = str(data2[0][0])
	html = "Quiz Name: " + quiz_name + "</h1>\n"
		
	an = 1 #answer number
	cur_question = data[0][0]
	html = html + "</p>\n<p>" + cur_question + "<br />\n"
	for row in data:	
		answer = str(row[1])
		value = str(row[2])
		
		#if new question:
		if row[0] != cur_question:
			cur_question = str(row[0])
			html = html + "</p>\n<p>" + cur_question + "<br />\n"
			html = html + "<input type='radio' name='ans" + str(an) + "' value='" + value + "'>"
			html = html + answer + "</input><br />\n"
			an += 1

		#if same question: put down answers and values
		else:
			html = html + "<input type='radio' name='ans" + str(an) + "' value='" + value + "'>"
			html = html + answer + "</input><br />\n"
			an += 1
		
	cursor.close()
	db.close()
	return html
	
	
html2 =  """Content-type: text/html
%(cookie)s\n
<!doctype html>
<html>
	<head>
		<title>Take A Quiz</title>
	</head>
	<body>
		<p>
		<form action='/cgi-bin/lab7/score_screen.py?quizID=%(quizID)s' method='post'>
		<h1>%(display)s
		<input type='submit' value='Done' name='done' />
		</form>
		</p>
	</body>
</html>""" % {
		"cookie": str(cookie),
		"quizID": str(form.getvalue('quizID')),
		"display": showMeYourMoves(),
	}

print(html2)
