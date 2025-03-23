from flask import Blueprint, render_template, request, session, flash
from .models import Book, Rating, Users, db
import pandas as pd

# Blueprint for popularity-based filtering
popularity_bp = Blueprint("popularity_bp", __name__)

# Function to generate popularity-based recommendations
def get_popular_books_per_genre(top_n=3):
    # Fetch books and ratings
    books = Book.query.all()
    ratings = Rating.query.all()

    print(f"✅ Total Books: {len(books)}")
    print(f"✅ Total Ratings: {len(ratings)}")

    # Convert to DataFrame
    books_df = pd.DataFrame(
        [(b.ISBN, b.book_title, b.book_author, b.genre) for b in books],
        columns=["ISBN", "Title", "Author", "Genre"],
    )

    ratings_df = pd.DataFrame(
        [(r.ISBN) for r in ratings], columns=["ISBN"]
    )

    # Count number of ratings per book
    popular_books = ratings_df.groupby("ISBN").size().reset_index(name="rating_count")

    # Merge with books
    popular_books = popular_books.merge(books_df, on="ISBN", how="left")

    # Get unique genres
    genres = db.session.query(Book.genre).distinct().all()
    genres = [g[0] for g in genres]  # Extract genre values

    # Get top books per genre
    top_books_per_genre = {}
    for genre in genres:
        genre_books = popular_books[popular_books["Genre"] == genre].sort_values(
            by="rating_count", ascending=False
        ).head(top_n)
        if not genre_books.empty:
            top_books_per_genre[genre] = genre_books

    return top_books_per_genre

# **Route for Popularity-Based Filtering Page**
@popularity_bp.route("/popularity_based", methods=["GET"])
def popularity_based():
    if "user_id" not in session:
        flash("Please log in to access recommendations.", "warning")
        return render_template("signin.html")

    popular_books = get_popular_books_per_genre(top_n=3)

    print("DEBUG: Popular Books Data")
    for genre, books in popular_books.items():
        print(f"📚 {genre}: {books}")

    return render_template("popularity_based.html", popular_books=popular_books)
