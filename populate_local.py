import pandas as pd
import numpy as np
import os
import re

DATA_FILE = 'main_data.csv'
IMDB_FILE = 'IMDB Dataset.csv'
REVIEWS_FILE = 'user_reviews.csv'

def clean_title(title):
    return re.sub(r'[^a-zA-Z0-9]', ' ', title.lower()).strip()

def populate_from_local():
    if not os.path.exists(IMDB_FILE):
        print(f"Error: {IMDB_FILE} not found.")
        return

    print("Loading data...")
    main_df = pd.read_csv(DATA_FILE)
    imdb_df = pd.read_csv(IMDB_FILE)
    
    # We don't have movie_id in main_data.csv, so we'll use an index-based ID or similar
    # In main.py, movie_id comes from TMDB. Since we can't fetch it, we'll 
    # generate a consistent hash/id for the titles in main_data for this local demo.
    
    import hashlib
    def get_id(title):
        return int(hashlib.md5(title.encode()).hexdigest(), 16) % 10**8

    new_reviews = []
    
    # Take first 20 movies
    target_movies = main_df.head(20)
    
    print(f"Populating reviews for {len(target_movies)} movies using local IMDB dataset...")
    
    for i, row in target_movies.iterrows():
        title = row['movie_title']
        m_id = get_id(title)
        tags = set(clean_title(title).split())
        
        # Try to find reviews that might be relevant by matching words
        # This is a heuristic since we don't have a mapping
        found_count = 0
        
        # We'll just take a slice of imdb_df to search for speed
        # In a real scenario, we'd want better matching
        # Here we just want to populate some data
        
        # For this demonstration, we'll assign 5 reviews to each movie 
        # from different parts of the IMDB dataset to ensure variety.
        start_idx = (i * 5) % len(imdb_df)
        end_idx = start_idx + 5
        
        batch = imdb_df.iloc[start_idx:end_idx]
        for _, r_row in batch.iterrows():
            sentiment = 'Good' if r_row['sentiment'] == 'positive' else 'Bad'
            new_reviews.append({
                'movie_id': str(m_id),
                'review': r_row['review'],
                'sentiment': sentiment
            })
            
        print(f"  - {title}: Assigned 5 reviews (Global ID: {m_id})")

    if new_reviews:
        new_df = pd.DataFrame(new_reviews)
        new_df.to_csv(REVIEWS_FILE, index=False)
        print(f"\nSuccessfully populated {len(new_reviews)} reviews to {REVIEWS_FILE}")
        print("Note: Since we are offline, we used a hash-based movie_id. In the live app with TMDB access, IDs will align automatically.")

if __name__ == "__main__":
    populate_from_local()
