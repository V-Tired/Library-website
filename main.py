from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

"""A web-based library database for keeping track of things you've read."""


class Base(DeclarativeBase):
    pass


# Creation of Flask app and linking database
app = Flask(__name__)
db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///book-list.db"
db.init_app(app)

all_books = []


class User(db.Model):
    """Database template"""
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    blurb: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    """Home page. Shows entries if there are any."""
    books = db.session.execute(db.select(User).order_by(User.id)).scalars().all()
    return render_template('index.html', books=books)


@app.route("/add", methods=["GET", "POST"])
def add():
    """Adds new entries to database by pulling information from the forms."""
    if request.method == "POST":
        with app.app_context():
            book = User(
                title=request.form['title'],
                author=request.form['author'],
                rating=float(request.form['rating']),
                blurb=request.form['blurb'],
                category=request.form['category']
            )
            db.session.add(book)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('add.html')


@app.route('/edit', methods=["GET", "POST"])
def edit():
    """Allows editing of rating"""
    if request.method == "POST":
        book_id = request.form['id']
        book_to_update = db.get_or_404(User, book_id)
        book_to_update.rating = request.form["rating"]
        db.session.commit()
        return redirect(url_for('home'))
    book_id = request.args.get('id')
    book_selected = db.get_or_404(User, book_id)
    return render_template("edit.html", book=book_selected)


@app.route("/delete")
def delete():
    """Deletes entr from database"""
    book_id = request.args.get('id')
    book_to_delete = db.get_or_404(User, book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

