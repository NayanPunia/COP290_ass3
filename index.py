from flask import Flask, render_template , request , redirect , url_for , session , send_file , jsonify , make_response
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import MySQLdb.cursors
from flask_bootstrap import Bootstrap5
import re
import os

app =  Flask(__name__, static_folder=os.path.join(os.getcwd(), 'static'), template_folder=os.path.join(os.getcwd(),'templates'))

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'pythonlogin'

mysql = MySQL(app)

bootstrap = Bootstrap5(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/booking.html')
def booking():
    return render_template('booking.html')

@app.route('/most-popular.html')
def popular():
    return render_template('most-popular.html')

@app.route('/guides.html', methods =['GET', 'POST'])
def guide():
    msg=''
    if request.method == 'POST' and 'destination' in request.form :
        destination = request.form['destination']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tour_guides WHERE specialty = % s' , (destination,))
        account = cursor.fetchall()
        if account :
            return render_template('guides.html', account = account)
        else :
            msg = 'No guides for this area'
            return render_template('guides.html',msg=msg)



@app.route('/personal-tour-guide.html')
def tour_guide():
    return render_template('personal-tour-guide.html')

@app.route('/loginsign-up.html', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username / password !'
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return render_template('loginsign-up.html', msg = msg)

@app.route('/logout', methods = ['POST'])
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('index'))

@app.route('/register.html', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)

if __name__ == '__main__':
    app.run(debug=True)
