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
def main():
    query = "SELECT * FROM emails"
    tmpEmail = mysql.query_db(query)   
    return render_template("email_validation.html")

@app.route('/email', methods=['POST'])
def validation():
    session['email'] = request.form['email']
    if len(request.form['email']) < 1:
        flash("Email cannot be blank!")
        return redirect('/')
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")
        return redirect('/')
    
    double = "SELECT email FROM emails WHERE email='{}'".format(request.form['email'])
    check = len(mysql.query_db(double))
    if check >= 1 :
        flash("That Email is Already Added")
        return redirect('/')

    else:    
        query = "INSERT INTO emails (email, date_added) VALUES (:email, NOW() )"
        data = {
            'email': request.form['email']
        }
        mysql.query_db(query, data)
        
    return redirect('/valid')

@app.route('/valid')
def valid():
    query2 = "SELECT * FROM emails"
    emails = mysql.query_db(query2) 
    return render_template('valid.html', email = session['email'], all_emails=emails)

@app.route('/delete', methods=['POST'])
def delete():
    idn = int(request.form['hidden'])
    query = "DELETE FROM emails WHERE id = '{}'".format(idn)
    mysql.query_db(query)
    return redirect('/valid')

print mysql.query_db("SELECT * FROM emails")

app.run(debug=True)