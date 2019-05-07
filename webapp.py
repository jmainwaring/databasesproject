from flask import Flask, render_template, request, Response, url_for
import json
from json2html import *
import logging
import MySQLdb 
import re
import simplejson as json


app = Flask(__name__)


def connect(db="mydb"):
	db = MySQLdb.connect("mysql-server", "root", "secret", "mydb")
	cursor = db.cursor()
	return db, cursor


def format_voterate_result(result, col_to_format):
	'''
	Takes cursor result, reformats to JSON
	Assumes >1 row returned
	'''
	tasks = []
	for row in result:
		data = {}
		data[col_to_format] = row[0]
		data['voting_rate'] = row[1]
		tasks.append(data)
	return tasks



def format_county_result(result):
	'''
	Formats cursor result for the county search page 
	'''
	data = {}
	data['county'] = result[0][0]
	raw_percentage = result[0][1]
	data['voter_turnout'] = "{:.1%}".format(raw_percentage)
	return [data] 




@app.route('/')
def homepage():
	"""
	Homepage with link to three other areas         
	"""

	return render_template('homepage.html')



@app.route('/results')
def results():
	"""
	Page with results         
	"""

	return render_template('results.html')




@app.route('/query', methods=["GET", "POST"])
def query():
	"""
	Page with that allows users to enter their own query         
	"""

	# Getting the query
	user_text = request.form.get("textbox")




	db = MySQLdb.connect("mysql-server", "root", "secret", "mydb")
	cursor = db.cursor()




	####Tim#### - main thing I need help with here is figuring out exactly what comes
	# from this request.form.get() thing, and why it doesn't appear to only be the 
	# query. Seems to have additional info, e.g., "Submit", which is why query doesn't run 




	# Getting closer


	# Default for before a user enters their own query 
	if user_text is None:
		user_query = "SELECT ncid FROM voters LIMIT 1"
		user_answer = cursor.execute(user_query)


	# Running the query 
	else:
		user_query = user_text
		# user_query = re.findall(r'(SELECT[^;]*)', user_text)[0]
		user_answer = cursor.execute("%s", (user_query,))
		
	
	user_answer_table = cursor.fetchall()	

	return render_template('query.html', query_result=user_answer_table)
		






@app.route('/table_breakdown', methods=["GET"])
def table_breakdown():
	"""
	Tables with percentage breakdowns by race, gender, and election year         
	"""


	db = MySQLdb.connect("mysql-server", "root", "secret", "mydb")
	cursor = db.cursor()

	# Getting HTML table for race breakdown
	race_answer = cursor.execute("SELECT race, AVG(voted) FROM voters GROUP BY race")
	race_answer_table = cursor.fetchall()
	race_formatted_answers = format_voterate_result(race_answer_table, col_to_format='race')
	race_html_table = json2html.convert(json=race_formatted_answers)


	# Getting HTML table for gender breakdown
	gender_answer = cursor.execute("SELECT gender, AVG(voted) FROM voters GROUP BY gender")
	gender_answer_table = cursor.fetchall()
	gender_formatted_answers = format_voterate_result(gender_answer_table, col_to_format='gender')
	gender_html_table = json2html.convert(json=gender_formatted_answers)


	# Getting HTML table for year breakdown
	year_answer = cursor.execute("SELECT year, AVG(voted) FROM voters GROUP BY year")
	year_answer_table = cursor.fetchall()
	year_formatted_answers = format_voterate_result(year_answer_table, col_to_format='year')
	year_html_table = json2html.convert(json=year_formatted_answers)



	return render_template('breakdowntemplate.html', race_table_input=race_html_table, 
		gender_table_input=gender_html_table, year_table_input=year_html_table)






@app.route('/county_breakdown', methods=["GET", "POST"])
def county_breakdown():
	"""
	Tables with percentage breakdowns by race, gender, and election year         
	"""


	db = MySQLdb.connect("mysql-server", "root", "secret", "mydb")
	cursor = db.cursor()


	# Getting a list of all the counties
	all_counties = cursor.execute("SELECT DISTINCT county FROM voters ORDER BY county")
	all_counties_result = cursor.fetchall()

	county_list = []
	for count, elem in enumerate(all_counties_result):
		elem_to_add = all_counties_result[count][0]
		county_list.append(elem_to_add)

	dropdown_list = county_list   



	# Getting HTML table	
	# Change to Alamance
	specific_county = 'Haywood'
	specific_county_input = request.form.get('county_select')


	if specific_county_input != None:
	# Default, in the case that none are selected (should replace Haywood with the first NC county) 
		specific_county = specific_county_input

	county_answer = cursor.execute("SELECT county, AVG(voted) FROM voters WHERE county= %s", (specific_county,))
	county_answer_table = cursor.fetchall()
	county_formatted_answers = format_county_result(county_answer_table)
	county_html_table = json2html.convert(json=county_formatted_answers)	
	return render_template('countytemplate.html', county_table_input=county_html_table, dropdown_list=dropdown_list, 
							selected_county = specific_county)		





















@app.route('/questions', methods=["GET"])
def show_questions():
	"""
	Show a user all questions           
	"""


	db = MySQLdb.connect("mysql-server", "root", "secret", "mydb")
	cursor = db.cursor()
	answer = cursor.execute("SELECT * FROM questions")
	answer_table = cursor.fetchall()


	formatted_answers = format_result(answer_table)
	data = {"Questions": formatted_answers}
	resp = Response(json.dumps(data), mimetype='application/json', status=200)
	return resp






@app.route('/answer', methods=["POST"])
def answer():
	"""
	Takes user the input and lets them select/answer a question   
	"""


	question_id = request.json["question_id"] 
	user_query = request.json["user_query"]
	is_correct = False


	db = MySQLdb.connect("mysql-server", "root", "secret", "mydb")
	cursor = db.cursor()
	user_result = cursor.execute(user_query)

	# Error handling for results with no rows 
	if cursor.rowcount == 0:
		data = {"Is correct": is_correct, "Problem": "No rows returned"}
		resp = Response(json.dumps(data), mimetype='application/json', status=200)
		return resp


	user_full_table = cursor.fetchall()[0][0]



	correct_query_command = cursor.execute("SELECT correct_query FROM answers WHERE question_id = %s", (int(question_id),))
	correct_query = cursor.fetchall()[0][0]
	correct_result = cursor.execute(correct_query)
	correct_full_table = cursor.fetchall()[0][0]



	# Checking to see if the answers are equal 
	if user_full_table == correct_full_table:
		is_correct = True
		send_tweet(question_id)  



	# Updating the completion status table
	sql = "UPDATE questions SET completed = %s WHERE id = %s"
	args = ("true", int(question_id))
	cursor.execute(sql, args)
	db.commit()
	db.close()




	data = {"User answer": user_full_table, "Correct answer": correct_full_table, "Is correct": is_correct}
	resp = Response(json.dumps(data), mimetype='application/json', status=200)
	return resp


