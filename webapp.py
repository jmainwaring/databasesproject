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
	Homepage with link to four other pages         
	"""

	return render_template('homepage.html')



@app.route('/results')
def results():
	"""
	Page with results from our study        
	"""

	return render_template('results.html')




@app.route('/query', methods=["GET", "POST"])
def query():
	"""
	Page that allows users to execute their own query         
	"""

	# Getting the query text
	user_text = request.form.get("description")


	db = MySQLdb.connect("mysql-server", "root", "secret", "mydb")
	cursor = db.cursor()


	# Default for before a user enters their own query 
	if user_text is None:
		user_query = "SELECT ncid FROM voters LIMIT 1"
		user_answer = cursor.execute(user_query)


	# Running the query 
	else:
		user_answer = cursor.execute(user_text)
		
	
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
	race_answer = cursor.execute("""
		WITH voted_table AS (
			SELECT voters.ncid, 
				CASE WHEN voting_method IS NULL THEN 0 ELSE 1 END AS voted,
				CASE 
					WHEN race_code = 'W' THEN 'White' 
					WHEN race_code = 'B' THEN 'African American/Black'
					WHEN race_code = 'M' THEN 'Multiracial' 
					WHEN race_code = 'I' THEN 'American Indian/Alaska Native' 
					WHEN race_code = 'A' THEN 'Asian' 
					WHEN race_code = 'U' THEN 'Native Hawaiian/Pacific Islander' 
					ELSE 'Other' END AS race     
			FROM voters 
			LEFT JOIN vhist
				ON voters.ncid=vhist.ncid)

			SELECT race, CONCAT(ROUND(AVG(voted)*100, 1), '%')   
			FROM voted_table
			GROUP BY race
			ORDER BY race;""")

	race_answer_table = cursor.fetchall()
	race_formatted_answers = format_voterate_result(race_answer_table, col_to_format='race')
	race_html_table = json2html.convert(json=race_formatted_answers)


	# Getting HTML table for gender breakdown
	gender_answer = cursor.execute("""
		WITH voted_table AS (
			SELECT voters.ncid, 
				CASE WHEN voting_method IS NULL THEN 0 ELSE 1 END AS voted, 
				CASE WHEN gender_code = 'f' THEN 'Female' ELSE 'Male' END AS gender   
			FROM voters 
			LEFT JOIN vhist
				ON voters.ncid=vhist.ncid)

			SELECT gender, CONCAT(ROUND(AVG(voted)*100, 1), '%')    
			FROM voted_table
			GROUP BY gender
			ORDER BY gender;""")

	gender_answer_table = cursor.fetchall()
	gender_formatted_answers = format_voterate_result(gender_answer_table, col_to_format='gender')
	gender_html_table = json2html.convert(json=gender_formatted_answers)


	# Getting HTML table for age breakdown
	year_answer = cursor.execute("""
		WITH voted_table AS (
			SELECT voters.ncid, 
				CASE WHEN voting_method IS NULL THEN 0 ELSE 1 END AS voted,
				CASE 
					WHEN birth_year < 1944 THEN '70+' 
					WHEN birth_year >= 1944 AND birth_year < 1964 THEN '50-69' 
					WHEN birth_year >= 1964 AND birth_year < 1984 THEN '30-49'
					ELSE '30 or younger' END AS age
			FROM voters 
			LEFT JOIN vhist
				ON voters.ncid=vhist.ncid)

			SELECT age, CONCAT(ROUND(AVG(voted)*100, 1), '%')  
			FROM voted_table
			GROUP BY age
			ORDER BY age;""")

	year_answer_table = cursor.fetchall()
	year_formatted_answers = format_voterate_result(year_answer_table, col_to_format='age')
	year_html_table = json2html.convert(json=year_formatted_answers)


	return render_template('breakdowntemplate.html', race_table_input=race_html_table, 
		gender_table_input=gender_html_table, year_table_input=year_html_table)





@app.route('/county_breakdown', methods=["GET", "POST"])
def county_breakdown():
	"""
	Tables with percentage breakdowns by county         
	"""


	db = MySQLdb.connect("mysql-server", "root", "secret", "mydb")
	cursor = db.cursor()


	# Getting a list of all the counties
	all_counties = cursor.execute("SELECT DISTINCT name FROM counties ORDER BY name")
	all_counties_result = cursor.fetchall()

	county_list = []
	for count, elem in enumerate(all_counties_result):
		elem_to_add = all_counties_result[count][0]
		county_list.append(elem_to_add)

	dropdown_list = county_list   



	# Getting HTML table	
	specific_county = 'ALAMANCE'
	specific_county_input = request.form.get('county_select')


	# Default, in the case that none are selected 
	if specific_county_input != None:
		specific_county = specific_county_input

	county_answer = cursor.execute("""
					WITH voted_table AS (
						SELECT voters.ncid, c.county_id, name, CASE WHEN voting_method IS NULL THEN 0 ELSE 1 END AS voted 
						FROM voters 
						LEFT JOIN vhist
							ON voters.ncid=vhist.ncid
						JOIN counties c
							ON voters.county_id = c.county_id
						WHERE name = %s)

					SELECT name AS county, AVG(voted)   
					FROM voted_table
					GROUP BY name
					ORDER BY name""", (specific_county,))

	county_answer_table = cursor.fetchall()
	county_formatted_answers = format_county_result(county_answer_table)
	county_html_table = json2html.convert(json=county_formatted_answers)	

	
	return render_template('countytemplate.html', county_table_input=county_html_table, dropdown_list=dropdown_list, 
							selected_county = specific_county)		
