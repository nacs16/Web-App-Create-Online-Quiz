#!/usr/local/bin/python3

import random, cgi, cgitb, os, datetime, mysql.connector
from http import cookies
form = cgi.FieldStorage()
cgitb.enable()

db = mysql.connector.connect(host="silo.soic.indiana.edu", user="root", password="", database="quizes", port=16001)
cursor = db.cursor()
quizID = str(form.getvalue('quizID'))
cursor.execute("SELECT description FROM quiz WHERE id = %s", (quizID, ))
data2 = cursor.fetchall()
quiz_name = str(data2[0][0])
quiz_name = ''.join(quiz_name.split())

def dragon():
	ans = "ans"
	num = 1
	score = 0
	while (ans + str(num)) in form:
		s = ans + str(num)
		score += int(form.getvalue(s))
		num += 1
	return score

score = dragon()
cookie = cookies.SimpleCookie(os.getenv("HTTP_COOKIE"))
if quiz_name in cookie:
	if int(cookie[quiz_name].value) < score:
		cookie[quiz_name] = score
else:
	cookie[quiz_name] = score

empty_list = []
if cookie["login"].value == "":
		logged_in = 0
else:
	logged_in = 1
		
if logged_in == 1:
	cursor.execute("SELECT id FROM user WHERE email = %s", ((cookie["login"].value), ))
	data = cursor.fetchall()
	userID = str(data[0][0])
	
	#check if quiz already taken:
	cursor.execute("SELECT score FROM user_scores WHERE user_id = %s and quiz_id = %s", (userID, quizID))
	data = cursor.fetchall()
	if data == empty_list or int(data[0][0]) < score:
		cursor.execute("INSERT INTO user_scores VALUES (%s, %s, %s, NOW())", (userID, quizID, str(score)))
		db.commit()
	cursor.close()
	db.close()

html2 =  """Content-type: text/html
%(cookie)s\n
<!doctype html>
<html>
	<head>
		<title>Score Screen</title>
	</head>
	<body>
		<p>
		<form action='/cgi-bin/lab7/start_page.py' method='post'>
		<h1>%(quiz_name)s Score: %(score)d
		<input type='submit' value='Return' name='return' />
		</form>
		</p>
	</body>
</html>""" % {
		"cookie": str(cookie),
		"quiz_name": quiz_name,
		"score": score,
	}

print(html2)