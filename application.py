from flask import Flask, url_for, redirect, render_template, request, g
import sqlite3
import collections
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "thomasambrose76@gmail.com"
app.config['MAIL_PASSWORD'] = 'Thomas123456789'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = ("Boys Brigade", "thomasambrose76@gmail.com")
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)

def connect_db():
    sql = sqlite3.connect('data.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route("/")
def home():
    return render_template('HOME.html')

@app.route("/ABOUT")
def about():
    return render_template("ABOUT.html")

@app.route("/NEWSLETTER")
def newsletter():
    return render_template("NEWSLETTER.html")

@app.route("/VOLUNTEER", methods=["GET", "POST"])
def volunteer():

    if request.method == "POST":
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        db = get_db()
        db.execute("insert into volunteers (firstname, lastname, email) values(?, ?, ?)", [firstname, lastname, email])
        db.commit()
        return redirect(url_for('home'))
    else:
        return render_template("Volunteer.html")

@app.route("/admin", methods=["POST"])
def admin():

    if request.method == "POST":

        x = request.form['x']

        if x == "0":
            password = request.form['password']
            if password == "password":
                db = get_db()
                cur = db.execute('select id, firstname, lastname, email from volunteers')
                results = cur.fetchall()
                return render_template("admin.html", results = results)
            else:
                return redirect(url_for('home'))

        if x == "1":
            Subject = request.form['Subject']
            Body = request.form['Body']
            recipients = collections.defaultdict(list)
            for id in query_db('select email from volunteers'):
                a = [id['email']]
                separator = ', '
                a = separator.join(a)
                recipients["email"].append(a)

            msg = Message(Subject, recipients=recipients['email'])
            msg.body = Body
            mail.send(msg)
            db = get_db()
            cur = db.execute('select id, firstname, lastname, email from volunteers')
            results = cur.fetchall()
            return render_template("admin.html", results = results)
