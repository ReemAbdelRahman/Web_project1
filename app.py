import os
import requests
from flask import Flask, render_template, request, session
from flask_session import Session


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
user_name = ""
@app.route("/")
def page1():
    return render_template("page1.html")

@app.route("/page1_register", methods=["GET", "POST"])
def page1_register():
    return render_template("page1_register.html", exists_u = 0, exists_p = 0)

@app.route("/page1_login", methods=["GET", "POST"])
def page1_login():
    return render_template("page1_login.html" , exists = 1)

@app.route("/register", methods=["POST"])
def register():
    global user_name
    Name = request.form.get("Name")
    username = request.form.get("username")
    user_name = username
    password = request.form.get("password")
    exists_u = db.execute("SELECT username FROM users WHERE username =  :username",{"username":username}).rowcount
    print (f"exists_u :{exists_u}")
    exists_p = db.execute("SELECT password FROM users WHERE password =  :password",{"password":password}).rowcount
    print (f"exists_p :{exists_p}")

    if exists_u == 0 and exists_p == 0:
        db.execute("INSERT INTO users (name,username, password) VALUES (:name, :username, :password)",{"name":Name,"username":username,"password":password})
        db.commit()
        return render_template("logged.html", found = -1 , books = [])

    else:
        return render_template("page1_register.html",exists_u = exists_u, exists_p = exists_p)



@app.route("/login", methods=["POST"])
def login():
    global user_name
    username = request.form.get("username")
    user_name = username
    password = request.form.get("password")
    exists = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",{"username":username, "password":password}).rowcount
    print(f"exists = {exists}")
    if exists == 0:
        return render_template("page1_login.html", exists = exists)
    else:
        return render_template("logged.html", found = -1 , books = [])

@app.route("/search", methods = ["POST"])
def search():
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    author = request.form.get("author")
    books_found = db.execute("SELECT * FROM kotob WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author",{"isbn":isbn, "title":title,"author":author}).fetchall()
    return render_template("logged.html",found = len(books_found), books_found = books_found)

@app.route("/book/<string:book_title>/<string:book_isbn>")
def book(book_title,book_isbn):
    #global book
    #global rev
    #global average_rating
    #global work_ratings_count
    book = db.execute(" SELECT * FROM kotob WHERE isbn = :isbn",{"isbn":book_isbn}).fetchone()
    rev = db.execute("SELECT * FROM reviews WHERE book_isbn = :book_isbn",{"book_isbn":book_isbn}).fetchall()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "ABTCFGHYe1o2naQrLOBaA", "isbns": {book_isbn}})
    info = res.json()['books'][0]
    average_rating = info ['average_rating']
    print(f"type of average_rating {type(average_rating)}")
    work_ratings_count = info['work_ratings_count']
    print(f"rev: {rev}")
    return render_template("book.html", book = book, average_rating = average_rating, work_ratings_count = work_ratings_count, rev = rev)

@app.route("/post_review/<string:book_title>/<string:book_isbn>", methods =["POST"])
def post_review(book_title,book_isbn):
    rating = request.form.get("points")
    review = request.form.get("review")
    print(f"review : {review}")
    db.execute("INSERT INTO reviews (book_isbn,user_username,review,rating) VALUES (:book_isbn, :user_username, :review, :rating)",{"book_isbn":book_isbn,"user_username":user_name,"review":review, "rating":rating})
    db.commit()
    return book(book_title,book_isbn)

@app.route("/api/<string:isbn>")
def api(isbn):
    try:
        book = db.execute(" SELECT * FROM kotob WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "ABTCFGHYe1o2naQrLOBaA", "isbns": {isbn}})
        info = res.json()['books'][0]
        return render_template("api.html",book = book, info = info)
    except ValueError:
        return render_template("error.html", message = "Sorry! This book does not exist in our database")
