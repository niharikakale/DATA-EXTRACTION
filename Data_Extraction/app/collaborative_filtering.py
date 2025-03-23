from flask import Blueprint, render_template, request, session, flash
from .models import Book, Rating, Users, db
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pandas as pd

# Blueprint for collaborative filtering
collaborative_bp = Blueprint("collaborative_bp", __name__)

# Function to generate collaborative filtering recommendations
def get_collaborative_recommendations(user_id, top_n=5):
    # Fetch books and ratings
    books = Book.query.all()
    ratings = Rating.query.all()
    users = Users.query.all()

    print(f"✅ Total Books: {len(books)}")
    print(f"✅ Total Ratings: {len(ratings)}")
    print(f"✅ Total Users: {len(users)}")

    # Convert data to DataFrame
    books_df = pd.DataFrame(
        [(b.ISBN, b.book_title, b.book_author, b.genre) for b in books],
        columns=["ISBN", "Title", "Author", "Genre"],
    )

    ratings_df = pd.DataFrame(
        [(r.user_id, r.ISBN, r.book_rating) for r in ratings],
        columns=["User_ID", "ISBN", "Book_Rating"],
    )

    # Create user-item matrix
    if ratings_df.empty:
        print("❌ No ratings found in database!")
        return pd.DataFrame(columns=["Title", "Author", "Genre"])

    user_item_matrix = ratings_df.pivot(index="User_ID", columns="ISBN", values="Book_Rating").fillna(0)

    # Convert to sparse matrix
    matrix_sparse = csr_matrix(user_item_matrix)

    # Train KNN model
    model = NearestNeighbors(metric="cosine", algorithm="brute")
    model.fit(matrix_sparse)

    # Get similar users
    user_id_to_index = {uid: i for i, uid in enumerate(user_item_matrix.index)}

    if user_id not in user_id_to_index:
        print("⚠️ New user detected, recommending popular books.")
        return get_popular_books(top_n)

    user_idx = user_id_to_index[user_id]
    distances, indices = model.kneighbors(matrix_sparse[user_idx].reshape(1, -1), n_neighbors=top_n + 1)
    similar_users = indices.flatten()[1:]

    recommended_books = ratings_df[ratings_df["User_ID"].isin(user_item_matrix.index[similar_users])]
    recommendations = recommended_books.groupby("ISBN").mean().sort_values("Book_Rating", ascending=False).head(20)
    recommendations = recommendations.merge(books_df, on="ISBN", how="left")

    return recommendations[["Title", "Author", "Genre"]].head(top_n)

# Function to suggest popular books
def get_popular_books(top_n=5):
    popular_books = db.session.query(
        Rating.ISBN, db.func.avg(Rating.book_rating).label("avg_rating")
    ).group_by(Rating.ISBN).order_by(db.func.avg(Rating.book_rating).desc()).limit(top_n).all()

    books_data = []
    for book in popular_books:
        book_details = Book.query.filter_by(ISBN=book.ISBN).first()
        books_data.append((book_details.book_title, book_details.book_author, book_details.genre))

    return pd.DataFrame(books_data, columns=["Title", "Author", "Genre"])

# **Route for Collaborative Filtering Page**
@collaborative_bp.route("/collaborative_based", methods=["GET"])
def collaborative_based():
    if "user_id" not in session:
        flash("Please log in to access recommendations.", "warning")
        return render_template("signin.html")

    user_id = session["user_id"]
    recommendations = get_collaborative_recommendations(user_id, top_n=5)

    print("DEBUG: Collaborative Recommendations Data")
    print(recommendations)

    return render_template("collaborative_based.html", recommendations=recommendations)
