from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import random, datetime, re, md5
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'ThisIsSecret'
mysql = MySQLConnector(app, 'mydb')

def check_name(var):
    if len(request.form[var]) < 1:
        flash("Name cannot be blank!")
        return False
    if any(char.isdigit() for char in request.form[var]) == True:
        flash("Name must not contain numbers")
        return False

def check_email():
    if len(request.form['email']) < 1:
        flash("Email cannot be blank!")
        return False
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")
        return False
    
def check_password():
    if len(request.form['password']) < 1:
        flash("Password cannot be blank!")
        return False
    if len(request.form['password']) < 8:
        flash("Password must be more than 8 characters!")
        return False

def check_message():
    if len(request.form['msg']) < 1:
        flash("Cannot post a blank message!")
        return False

def check_comment():
    if len(request.form['cmt']) < 1:
        flash("Cannot post a blank comment!")
        return False
    
@app.route('/')
def main():
    query = "SELECT * FROM users"
    users = mysql.query_db(query)   
    return render_template("login_and_registration.html")

@app.route('/login', methods=['POST'])
def login():
    hashed_password = md5.new(request.form['password']).hexdigest()

    if check_email() == False:
        return redirect('/')
    
    email = "SELECT email FROM users WHERE email='{}'".format(request.form['email'])
    email_check = len(mysql.query_db(email))
    if email_check < 1 :
        flash("That Email is not Registered")
        return redirect('/')

    if check_password() == False:
        return redirect('/')
    
    password = "SELECT password FROM users WHERE password='{}'".format(hashed_password)
    password_check = len(mysql.query_db(password))
    if password_check < 1 :
        flash("That Password is incorrect")
        return redirect('/')

    user = "SELECT * FROM users WHERE email='{}'".format(request.form['email'])
    session['user_info'] = mysql.query_db(user)
    session['msgs'] = {}
    session['cmts'] = {}

    return redirect('/the_wall')

@app.route('/the_wall')
def the_wall():
    info = session['user_info']
    
    msgs = "SELECT users.first_name, users.last_name,messages.users_id, messages.id, messages.message, messages.created_at AS message_created, messages.updated_at AS message_update FROM messages JOIN users ON messages.users_id = users.id ORDER BY message_created;"
    session['msgs'] = mysql.query_db(msgs)
    
    msg = session['msgs']
   
    cmts = "SELECT users.first_name, users.last_name, messages.message,comments.id, comments.messages_id, comments.users_id, comments.comment, comments.created_at AS comment_created, comments.updated_at AS comment_updated FROM comments JOIN users ON comments.users_id = users.id JOIN messages ON comments.messages_id = messages.id ORDER BY comment_created;"
    session['cmts'] = mysql.query_db(cmts)

    cmt = session['cmts']
    return render_template("the_wall.html", the_user = info, messages=msg, comments=cmt)
    

@app.route('/registration')
def reg_page():
    return render_template('registration.html')

@app.route('/register', methods=['POST'])
def register():
    if check_name('first_name') == False:
        return redirect('/registration')
    session['first_name'] = request.form['first_name']

    if check_name('last_name') == False:
        return redirect('/registration')
    session['last_name'] = request.form['last_name']

    if check_email() == False:
        return redirect('/registration')
    
    email = "SELECT email FROM users WHERE email='{}'".format(request.form['email'])
    email_check = len(mysql.query_db(email))
    if email_check >= 1 :
        flash("That Email is Already Added")
        return redirect('/registration')
    session['email'] = request.form['email']

    if check_password() == False:
        return redirect('/registration')

    if request.form['password'] != request.form['confirm_password']:
        flash("Password must Match confirm-password!")
        return redirect('/registration')
 
    session['password'] = md5.new(request.form['password']).hexdigest()
        
    return redirect('/valid')

@app.route('/valid')
def valid():
    user = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW() )"
    info = {
        'first_name': session['first_name'],
        'last_name': session['last_name'],
        'email': session['email'],
        'password': session['password']
    }
    mysql.query_db(user, info)

    return redirect('/')


# @app.route('/delete', methods=['POST'])
# def delete():
#     idn = int(request.form['hidden'])
#     query = "DELETE FROM users WHERE id = '{}'".format(idn)
#     mysql.query_db(query)
#     return redirect('/valid')

@app.route('/post_msg', methods=['POST'])
def post_msg():
    if check_message() == False:
        return redirect('/the_wall')

    post = "INSERT INTO messages(users_id, message, created_at, updated_at) VALUES (:user_id, :message, NOW(), NOW())"
    message = {
        'message': request.form['msg'],
        'user_id': int(request.form['user_id'])
    }
    mysql.query_db(post, message)
    return redirect('/the_wall')

@app.route('/delete_msg', methods=['POST'])
def delete_msg():
    idn = request.form['delete_msg']
    query2 = "DELETE FROM comments WHERE messages_id = '{}'".format(idn)
    mysql.query_db(query2)
    query = "DELETE FROM messages WHERE id = '{}'".format(idn)
    mysql.query_db(query)
    
    return redirect('/the_wall')

@app.route('/post_cmt', methods=['POST'])
def post_cmt():
    if check_comment() == False:
        return redirect('/the_wall')

    print "WHAT WHAT", request.form['msg_id']

    post = "INSERT INTO comments(messages_id, users_id, comment, created_at, updated_at) VALUES (:message_id, :user_id, :comment, NOW(), NOW())"
    comment = {
        'message_id': int(request.form['msg_id']),
        'user_id': int(request.form['user_id']),
        'comment': request.form['cmt']
    }
    mysql.query_db(post, comment)
    return redirect('/the_wall')

@app.route('/delete_cmt', methods=['POST'])
def delete_cmt():
    idn = request.form['delete_cmt']
    query2 = "DELETE FROM comments WHERE id = '{}'".format(idn)
    mysql.query_db(query2)
    
    return redirect('/the_wall')



print mysql.query_db("SELECT * FROM users")

app.run(debug=True)