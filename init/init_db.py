from flask import Flask, request, Response
import MySQLdb 

app = Flask(__name__)

def connect(db="mydb"):
    db = MySQLdb.connect("mysql-server", "root", "secret", db)
    cursor = db.cursor()
    return db, cursor

def initialize(sql_list):
    db, cursor = connect('sys')
    for sql in sql_list:
        cursor.execute(sql)
    db.commit()
    db.close()


sql = ['''CREATE DATABASE mydb;''',
 '''USE mydb;''', 
 '''CREATE TABLE voters (ncid BIGINT, race VARCHAR(255), gender VARCHAR(255), year BIGINT, county VARCHAR(255), voted BIGINT, PRIMARY KEY (ncid));''',
'''INSERT INTO voters (ncid, race, gender, year, county, voted) VALUES (777, "White", "Male", 2012, "Haywood", 1);''', 
'''INSERT INTO voters (ncid, race, gender, year, county, voted) VALUES (778, "Black", "Female", 2012, "Haywood", 1);''', 
'''INSERT INTO voters (ncid, race, gender, year, county, voted) VALUES (779, "White", "Male", 2016, "Haywood", 1);''', 
'''INSERT INTO voters (ncid, race, gender, year, county, voted) VALUES (780, "Black", "Female", 2016, "Haywood", 0);''', 
'''INSERT INTO voters (ncid, race, gender, year, county, voted) VALUES (781, "White", "Male", 2012, "Surry", 0);''', 
'''INSERT INTO voters (ncid, race, gender, year, county, voted) VALUES (782, "White", "Female", 2012, "Surry", 0);''',
'''INSERT INTO voters (ncid, race, gender, year, county, voted) VALUES (783, "White", "Male", 2016, "Surry", 1);''', 
'''INSERT INTO voters (ncid, race, gender, year, county, voted) VALUES (784, "Black", "Female", 2012, "Surry", 0);''']

initialize(sql)