from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import random
import datetime
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'ThisIsSecret'
mysql = MySQLConnector(app, 'mydb')

@app.route('/')
def friends():
    query = "SELECT * FROM friends"
    friends = mysql.query_db(query)
    # time = mysql.query_db("SELECT MONTHNAME(friend_since) FROM friends")
        
    return render_template("full_friends.html", all_friends=friends)

@app.route('/add_friend', methods=['POST'])
def add_friend():
    query = "INSERT INTO friends (name, age, friend_since) VALUES (:name,:age, NOW() )"
    data = {
        'name': request.form['name'],
        'age': int(request.form['age'])
    }
    mysql.query_db(query, data)
    return redirect('/')


print mysql.query_db("SELECT * FROM friends")

app.run(debug=True)