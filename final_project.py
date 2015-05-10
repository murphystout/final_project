import urllib2
from flask import Flask, render_template, request, redirect, session, g, url_for, abort, flash
import pickle
import os.path
import time
import re
import json
import sqlite3

#configuration
DATABASE = 'bookcatalog.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'password'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
	g.db = connect_db()
	
@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()
		
@app.route('/lookup', methods=['POST','GET'])
def lookup():
	isbn = None
	urlslug = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
	if request.method == 'POST':
		isbn = request.form['ISBN']
		if isbn != "":
			try:
				fullurl = urlslug + isbn
				response = urllib2.urlopen(fullurl)
				data = response.read()
				data = json.loads(data)
				volumedata = data['items'][0]['volumeInfo']
				title = volumedata['title']
				authors = volumedata['authors'][0]
				pagecount = volumedata['pageCount']
				averagerating = volumedata['averageRating']
				thumbnail = volumedata['imageLinks']['smallThumbnail']
				return render_template('lookup.html',thumbnail = thumbnail, title=title, authors=authors,pagecount=pagecount,averagerating=averagerating,isbn=isbn)
			except:
				flash("Error on ISBN lookup, please try again")
				return redirect("/lookup")
		else: 
			flash("Please Enter an ISBN Number")
			return redirect("/lookup")
	elif request.method == 'GET':
		return render_template('lookup.html')
		
@app.route('/addbook', methods = ['POST'])
def addbook():
	try:
		querystring = "INSERT INTO bookcatalog (ISBN,TITLE,AUTHORS,PAGECOUNT,AVERAGERATING, THUMBNAIL) VALUES (?,?,?,?,?,?)"
		g.db.execute(querystring,(request.form['isbn'],request.form['title'],request.form['authors'],request.form['pagecount'],request.form['averagerating'],request.form['thumbnail']))
		g.db.commit()
		flash("Book Added to Catalog")
		return redirect("/")
	except():
		flash("Error Adding Book. Please Try Again")
		return redirect("/")
	
@app.route('/delete', methods = ['GET'])
def deletebook():
	id = request.args.get('id')
	querystring = "DELETE FROM bookcatalog WHERE ID = ?"
	g.db.execute(querystring,(id))
	g.db.commit()
	
	flash("Book Deleted with ID Number:"+id)
	return redirect("/")
	
@app.route('/')
def homepage():
	querystring = "SELECT ID, ISBN,TITLE,AUTHORS,PAGECOUNT,AVERAGERATING, THUMBNAIL FROM bookcatalog"
	cur = g.db.execute(querystring)
	books = [dict(id = row[0], isbn = row[1], title = row[2], authors = row[3], pagecount= row[4], averagerating = row[5], thumbnail = row[6]) for row in cur.fetchall()]
	return render_template('index.html',books = books)	
if __name__ == "__main__":
    app.run(debug=DEBUG)
	