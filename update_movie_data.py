import pandas as pd
import requests
import time

# Use the API key found in the project's javascript
API_KEY = '71bdf22d8b06fde7b7b67d170d00b0c8'

# Using direct IP and Host header to bypass DNS issues
BASE_URL = "http://3.165.239.72/3"
HEADERS = {"Host": "api.themoviedb.org"}

def get_genres():
    url = f"{BASE_URL}/genre/movie/list?api_key={API_KEY}&language=en-US"
    response = requests.get(url, headers=HEADERS).json()
    return {g['id']: g['name'] for g in response['genres']}

def get_movie_data(year):
    movies = []
    # Fetching top 2 pages (40 popular movies) for each year
    for page in range(1, 3):
        url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&language=en-US&sort_by=popularity.desc&primary_release_year={year}&page={page}"
        response = requests.get(url, headers=HEADERS).json()
        
        for m in response.get('results', []):
            movie_id = m['id']
            title = m['original_title'].lower()
            
            # Get Cast and Director
            credits_url = f"{BASE_URL}/movie/{movie_id}/credits?api_key={API_KEY}"
            creds = requests.get(credits_url, headers=HEADERS).json()
            
            cast = " ".join([c['name'].replace(" ", "").lower() for c in creds.get('cast', [])[:3]])
            director = ""
            for crew in creds.get('crew', []):
                if crew['job'] == 'Director':
                    director = crew['name'].replace(" ", "").lower()
                    break
            
            genres = " ".join([genre_map.get(gi, "").lower() for gi in m['genre_ids']])
            
            # Create the 'comb' string
            comb = f"{genres} {director} {cast}"
            movies.append({'movie_title': title, 'comb': comb})
            
            # Small sleep to be nice to the API
            time.sleep(0.1)
        print(f"Finished page {page} for year {year}")
    return movies

print("Starting data update...")
genre_map = get_genres()
all_new_movies = []

for year in range(2021, 2025):
    all_new_movies.extend(get_movie_data(year))

# Load existing data
main_df = pd.read_csv('main_data.csv')

# Convert to DataFrame and append
new_df = pd.DataFrame(all_new_movies)

# Deduplicate (incase movie already exists)
combined_df = pd.concat([main_df, new_df]).drop_duplicates(subset=['movie_title'], keep='last')

combined_df.to_csv('main_data.csv', index=False)
print(f"Successfully added {len(all_new_movies)} new movies from 2021-2024 to main_data.csv!")
