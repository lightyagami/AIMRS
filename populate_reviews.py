import pandas as pd
import requests
import bs4 as bs
import time
import os
import json

# Configuration
API_KEY = '71bdf22d8b06fde7b7b67d170d00b0c8'
DATA_FILE = 'main_data.csv'
REVIEWS_FILE = 'user_reviews.csv'
BATCH_SIZE = 10  # Set small for demonstration, can be increased by user

def get_imdb_id(title):
    url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}'
    try:
        res = requests.get(url, timeout=5).json()
        if res['results']:
            movie_id = res['results'][0]['id']
            # Get external IDs
            ext_url = f'https://api.themoviedb.org/3/movie/{movie_id}/external_ids?api_key={API_KEY}'
            ext_res = requests.get(ext_url, timeout=5).json()
            return ext_res.get('imdb_id'), movie_id
    except Exception as e:
        print(f"Error getting ID for {title}: {e}")
    return None, None

def scrape_reviews(imdb_id, movie_id):
    if not imdb_id: return []
    url = f'https://www.imdb.com/title/{imdb_id}/reviews'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = bs.BeautifulSoup(resp.text, 'lxml')
            review_divs = soup.find_all("div", {"class": "text show-more__control"})
            reviews = []
            for r in review_divs[:5]: # Take top 5
                reviews.append({
                    'movie_id': str(movie_id),
                    'review': r.get_text(separator=' ').strip(),
                    'sentiment': 'Good' # Initial placeholder, app will re-analyze if needed
                })
            return reviews
    except Exception as e:
        print(f"Error scraping {imdb_id}: {e}")
    return []

def main(limit=None):
    df = pd.read_csv(DATA_FILE)
    if limit:
        df = df.head(limit)
    
    all_new_reviews = []
    
    print(f"Starting population for {len(df)} movies...")
    
    for i, row in df.iterrows():
        title = row['movie_title']
        print(f"[{i+1}/{len(df)}] Processing: {title}")
        
        imdb_id, tmdb_id = get_imdb_id(title)
        if imdb_id and tmdb_id:
            reviews = scrape_reviews(imdb_id, tmdb_id)
            if reviews:
                all_new_reviews.extend(reviews)
                print(f"  - Found {len(reviews)} reviews")
            else:
                print(f"  - No reviews found")
        
        # Respectful delay
        time.sleep(1)

    if all_new_reviews:
        new_df = pd.DataFrame(all_new_reviews)
        header = not os.path.exists(REVIEWS_FILE)
        new_df.to_csv(REVIEWS_FILE, mode='a', header=header, index=False)
        print(f"\nSuccessfully added {len(all_new_reviews)} reviews to {REVIEWS_FILE}")
    else:
        print("\nNo new reviews were collected.")

if __name__ == "__main__":
    # To run for the full dataset, remove the argument: main()
    # Running for a small batch now to demonstrate.
    main(limit=10)
