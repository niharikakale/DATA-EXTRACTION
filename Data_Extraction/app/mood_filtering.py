from flask import Blueprint, render_template, request, session, flash
from .models import Book, db
import pandas as pd
import random

mood_bp = Blueprint("mood_bp", __name__)

# Mood Mapping
mood_mapping = {
    "Cheerful": "Happy", "Moody": "Sad", "Calm": "Calm", "Tired": "Tired",
    "Laugh and have fun": "Happy", "Reflect and relax": "Sad",
    "Go on an adventure": "Happy", "Read something emotional": "Sad",
    "High energy": "Happy", "Low energy": "Sad", "Balanced energy": "Calm", "Very low energy": "Tired",
    "Happy, excited": "Happy", "Sad, nostalgic": "Sad", "Peaceful, content": "Calm", "Motivated, adventurous": "Happy",
    "Action-packed stories": "Happy", "Deep emotional stories": "Sad",
    "Relaxing and slow-paced": "Calm", "Short and light reads": "Tired"
}

# Mood-based keyword mapping
mood_to_keywords = {
    "Happy": ["adventure", "fun", "joy", "excitement"],
    "Sad": ["nostalgic", "reflective", "deep"],
    "Calm": ["peaceful", "relaxing", "soothing"],
    "Tired": ["light", "easy", "gentle"]
}

def recommend_books(mood, top_n=5):
    """Recommend books based on the predicted mood."""
    keywords = mood_to_keywords.get(mood, [])
    
    # Fetch books from the database
    books = Book.query.all()
    books_df = pd.DataFrame(
        [(b.book_title, b.book_author, b.genre) for b in books],
        columns=["Book-Title", "Book-Author", "Genre"]
    )
    
    if books_df.empty:
        return pd.DataFrame({"Error": ["No books available in database"]})
    
    # Filter books based on mood
    recommended_books = books_df[books_df['Genre'].str.contains('|'.join(keywords), case=False, na=False)]
    
    if recommended_books.empty:
        recommended_books = books_df.sample(n=min(top_n, len(books_df)))  # Random books if no exact match

    return recommended_books.head(top_n)

@mood_bp.route("/mood_based", methods=["GET", "POST"])
def mood_based():
    if request.method == "POST":
        # Get selected moods from form
        selected_moods = [
            mood_mapping.get(request.form.get("mood1"), "Happy"),
            mood_mapping.get(request.form.get("mood2"), "Happy"),
            mood_mapping.get(request.form.get("mood3"), "Happy"),
            mood_mapping.get(request.form.get("mood4"), "Happy"),
            mood_mapping.get(request.form.get("mood5"), "Happy"),
        ]

        # Count mood occurrences
        mood_counts = {}
        for mood in selected_moods:
            mood_counts[mood] = mood_counts.get(mood, 0) + 1

        # Select the most common mood, or choose randomly if there's a tie
        max_count = max(mood_counts.values())
        most_common_moods = [m for m, count in mood_counts.items() if count == max_count]
        final_mood = random.choice(most_common_moods)  # Random selection in case of tie

        # Get recommendations based on final mood
        recommendations = recommend_books(final_mood)

        return render_template("mood_based.html", recommendations=recommendations, final_mood=final_mood)

    return render_template("mood_based.html", recommendations=None, final_mood=None)
