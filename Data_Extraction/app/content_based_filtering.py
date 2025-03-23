from flask import Blueprint, render_template, request, session, flash
from .models import Book, Rating, Users, db
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Blueprint for content-based filtering
content_bp = Blueprint("content_bp", __name__)

# Function to generate recommendations
def get_recommendations(user_id, genre=None, top_n=5):
    # Fetch books and ratings
    books = Book.query.all()
    ratings = Rating.query.all()
    users = Users.query.all()

    print(f"✅ Total Books Fetched: {len(books)}")  # Debugging print
    print(f"✅ Total Ratings Fetched: {len(ratings)}")  # Debugging print
    print(f"✅ Total Users Fetched: {len(users)}")  # Debugging print

    # Convert to DataFrame with correct field names from models.py
    books_df = pd.DataFrame(
        [(b.ISBN, b.book_title, b.book_author, b.publisher, b.genre) for b in books],
        columns=["ISBN", "Title", "Author", "Publisher", "Genre"],
    )

    ratings_df = pd.DataFrame(
        [(r.user_id, r.ISBN) for r in ratings], columns=["User_ID", "ISBN"]
    )

    # Handle cases where no books exist
    if books_df.empty:
        print("❌ No books found in the database!")
        return []

    # Merge books with ratings (if ratings exist)
    if not ratings_df.empty:
        ratings_books_df = ratings_df.merge(books_df, on="ISBN", how="inner")

        # Create user profiles (books they have rated)
        user_profiles = (
            ratings_books_df.groupby("User_ID")["Title"]
            .apply(lambda x: " ".join(x))
            .reset_index()
        )
        user_profiles.rename(columns={"Title": "user_profile"}, inplace=True)

        # Get active users
        users_df = pd.DataFrame(
            [(u.user_id,) for u in users], columns=["User_ID"]
        )
        users_df = users_df.merge(user_profiles, on="User_ID", how="left")
    else:
        users_df = pd.DataFrame(columns=["User_ID", "user_profile"])

    # Create book profiles using correct column names
    books_df["book_profile"] = books_df.apply(
        lambda x: f"{x['Title']} {x['Author']} {x['Publisher']} {x['Genre']}", axis=1
    )

    # Handle missing profiles
    users_df["user_profile"] = users_df["user_profile"].fillna("")
    books_df.dropna(subset=["book_profile"], inplace=True)

    print(f"✅ Total User Profiles: {len(users_df)}")
    print(f"✅ Total Book Profiles: {len(books_df)}")

    # TF-IDF Vectorization
    tfidf_vectorizer = TfidfVectorizer(max_features=5000)
    tfidf_books = tfidf_vectorizer.fit_transform(books_df["book_profile"])

    # If the user has never rated any books, recommend random books
    if users_df["user_profile"].isnull().all():
        print("⚠️ No user ratings found. Recommending random books.")
        return books_df.sample(n=top_n)[["Title", "Author", "Genre"]]

    tfidf_users = tfidf_vectorizer.transform(users_df["user_profile"])

    # Compute similarity
    cosine_sim = cosine_similarity(tfidf_users, tfidf_books)
    user_id_to_index = {int(row["User_ID"]): idx for idx, row in users_df.iterrows()}

    if user_id in user_id_to_index:
        user_idx = user_id_to_index[user_id]
        sim_scores = list(enumerate(cosine_sim[user_idx]))
        sim_scores_df = pd.DataFrame(sim_scores, columns=["Index", "Similarity"])
        sim_scores_df = sim_scores_df.sort_values(by="Similarity", ascending=False)

        recommended_books = books_df.iloc[sim_scores_df["Index"]][["Title", "Author", "Genre"]]
        if genre:
            recommended_books = recommended_books[recommended_books["Genre"].str.lower() == genre.lower()]
        return recommended_books.head(top_n)
    else:
        # If new user, recommend books strictly from the selected genre
        if genre:
            genre_books = books_df[books_df["Genre"].str.lower() == genre.lower()]
            return genre_books.head(top_n) if len(genre_books) >= top_n else genre_books
        return books_df.sample(n=top_n)[["Title", "Author", "Genre"]]

# **Route for Content-Based Filtering Page**
@content_bp.route("/content_based", methods=["GET"])
def content_based():
    if "user_id" not in session:
        flash("Please log in to access recommendations.", "warning")
        return render_template("signin.html")

    user_id = session["user_id"]
    genre = request.args.get("genre", None)

    # Get unique genres from the database
    genres = db.session.query(Book.genre).distinct().all()
    genres = [g[0] for g in genres]  # Extract genre values

    recommendations = get_recommendations(user_id, genre, top_n=5)

    # Debugging print statements
    print("DEBUG: Recommendations Data:")
    print(recommendations)

    print("DEBUG: Book Recommendations (First 5)")
    print(recommendations.head(5))  # Ensure ISBN is present

    return render_template("content_based.html", recommendations=recommendations)

