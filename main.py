import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import bs4 as bs
import urllib.request
import pickle
import requests
import re
import os

# --- MODEL LOADING (Aligned with miniproj.docx) ---
# Sentiment Analysis Models
try:
    clf = pickle.load(open('sentiment_model.pkl', 'rb'))
    vectorizer = pickle.load(open('sentiment_vectorizer.pkl', 'rb'))
except FileNotFoundError:
    print("Sentiment models not found. Sentiment analysis will be disabled until retrain_sentiment.py is run.")
    clf = None
    vectorizer = None

# Recommendation Engine Data (Pre-computed)
similarity = None
tfidf_rec = None
if os.path.exists('transform.pkl'):
    similarity = pickle.load(open('transform.pkl', 'rb'))
if os.path.exists('nlp_model.pkl'):
    tfidf_rec = pickle.load(open('nlp_model.pkl', 'rb'))

data = pd.read_csv('main_data.csv')
data['movie_title_clean'] = data['movie_title'].str.lower().str.replace(r'[^a-zA-Z0-9]', '', regex=True)

def create_similarity():
    global similarity, tfidf_rec
    if similarity is None:
        if os.path.exists('transform.pkl'):
             similarity = pickle.load(open('transform.pkl', 'rb'))
        else:
            print("Similarity model not found. Generating in-memory (this may take a moment)...")
            from sklearn.feature_extraction.text import CountVectorizer
            cv = CountVectorizer(stop_words='english')
            tfidf_matrix = cv.fit_transform(data['comb'])
            similarity = cosine_similarity(tfidf_matrix)
    return similarity

def rcmd(m):
    global data, similarity
    m = re.sub(r'[^a-zA-Z0-9]', '', m.lower())
    if similarity is None:
        similarity = create_similarity()
    
    if m not in data['movie_title_clean'].unique():
        return 'Sorry! The movie you requested is not in our database.'
    else:
        movie_indx = data.loc[data['movie_title_clean']==m].index[0]
        base_comb = set(str(data['comb'][movie_indx]).split())
        
        lst = list(enumerate(similarity[movie_indx]))
        lst = sorted(lst, key=lambda x: x[1], reverse=True)
        
        # Get top 11 (including self)
        top_matches = lst[0:11] 
        results = []
        for i in range(len(top_matches)):
            idx = top_matches[i][0]
            if idx != movie_indx:
                score = round(top_matches[i][1] * 100, 2)
                title = data['movie_title'][idx]
                
                # Identify shared attributes
                rec_comb = set(str(data['comb'][idx]).split())
                shared = base_comb.intersection(rec_comb)
                shared = [word.capitalize() for word in shared if len(word) > 3][:3]
                shared_str = ", ".join(shared)
                
                results.append(f"{title} ({score}%)|||{shared_str}")
        return results
    
def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["','')
    my_list[-1] = my_list[-1].replace('"]','')
    return my_list

def get_suggestions():
    return list(data['movie_title'].str.capitalize())

def get_trending_movies():
    api_key = '71bdf22d8b06fde7b7b67d170d00b0c8'
    url = f"http://3.165.239.72/3/trending/movie/day?api_key={api_key}&language=en-US"
    headers = {"Host": "api.themoviedb.org"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            results = response.json().get('results', [])[:15]
            trending = []
            for m in results:
                trending.append({
                    'title': m.get('title'), 
                    'poster': f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}"
                })
            return trending
    except Exception as e:
        print(f"Error fetching trending movies: {e}")
    return []

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    suggestions = get_suggestions()
    trending = get_trending_movies()
    return render_template('home.html', suggestions=suggestions, trending=trending)

@app.route("/similarity",methods=["POST"])
def similarity_route():
    movie = request.form['name']
    rc = rcmd(movie)
    if type(rc)==type('string'):
        return rc
    else:
        m_str="---".join(rc)
        return m_str

# --- GLOBAL REVIEWS STORAGE ---
REVIEWS_FILE = 'user_reviews.csv'
if not os.path.exists(REVIEWS_FILE):
    pd.DataFrame(columns=['movie_id', 'review', 'sentiment']).to_csv(REVIEWS_FILE, index=False)

@app.route("/recommend",methods=["POST"])
def recommend():
    import time
    start_time = time.time()
    global data, similarity
    title = request.form['title']
    cast_ids = request.form['cast_ids']
    cast_names = request.form['cast_names']
    cast_chars = request.form['cast_chars']
    cast_bdays = request.form['cast_bdays']
    cast_bios = request.form['cast_bios']
    cast_places = request.form['cast_places']
    cast_profiles = request.form['cast_profiles']
    imdb_id = request.form['imdb_id']
    poster = request.form['poster']
    genres = request.form['genres']
    overview = request.form['overview']
    vote_average = request.form['rating']
    vote_count = request.form['vote_count']
    release_date = request.form['release_date']
    runtime = request.form['runtime']
    status = request.form['status']
    movie_id = request.form['movie_id']
    rec_movies = request.form['rec_movies']
    rec_posters = request.form['rec_posters']

    if similarity is None:
        similarity = create_similarity()

    suggestions = get_suggestions()

    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)
    cast_bdays = convert_to_list(cast_bdays)
    cast_bios = convert_to_list(cast_bios)
    cast_places = convert_to_list(cast_places)
    
    cast_ids = cast_ids.split(',')
    cast_ids[0] = cast_ids[0].replace("[","")
    cast_ids[-1] = cast_ids[-1].replace("]","")
    
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"','\"')
    
    movie_cards = {rec_posters[i]: rec_movies[i] for i in range(len(rec_posters))}
    casts = {cast_names[i]:[cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}
    cast_details = {cast_names[i]:[cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in range(len(cast_places))}

    reviews_list = []
    reviews_status = []
    
    # 1. Load "Global" User Reviews from CSV
    try:
        if os.path.exists(REVIEWS_FILE):
            global_df = pd.read_csv(REVIEWS_FILE)
            movie_global_reviews = global_df[global_df['movie_id'].astype(str) == str(movie_id)]
            for _, row in movie_global_reviews.iterrows():
                reviews_list.append(row['review'])
                reviews_status.append(row['sentiment'])
    except Exception as e:
        print(f"Global Load Error: {e}")

    # 2. SMART CACHE: Scrape IMDB if we have no global data or very few reviews
    if len(reviews_list) < 5:
        try:
            target_id = None
            if imdb_id and str(imdb_id).lower() not in ['nan', 'none', 'null', '']:
                target_id = str(imdb_id)
            
            # FALLBACK: If no ID, try to find ID by searching IMDB with title
            if not target_id:
                try:
                    search_url = f'https://www.imdb.com/find?q={title.replace(" ","+")}&s=tt&ttype=ft'
                    search_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    s_resp = requests.get(search_url, headers=search_headers, timeout=5)
                    if s_resp.status_code == 200:
                        s_soup = bs.BeautifulSoup(s_resp.text, 'lxml')
                        # Find first title link
                        link = s_soup.find('a', href=re.compile(r'/title/tt\d+/'))
                        if link:
                            target_id = re.search(r'tt\d+', link['href']).group()
                except:
                    pass

            if target_id:
                imdb_rev_url = f'https://www.imdb.com/title/{target_id}/reviews'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.google.com/'
                }
                resp = requests.get(imdb_rev_url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    soup = bs.BeautifulSoup(resp.text, 'lxml')
                    # IMDB has multiple containers for reviews, let's try the common ones
                    imdb_reviews = soup.find_all("div", {"class": "text show-more__control"})
                    if not imdb_reviews:
                         # Fallback selector for different page versions
                         imdb_reviews = soup.select('.ipc-html-content-inner-div')
                    
                    new_persisted_reviews = []
                    for r in imdb_reviews:
                        content = r.get_text(separator=' ').strip()
                        if len(content) > 30 and content not in reviews_list:
                            # Analyze sentiment for persistence
                            sentiment = 'Good'
                            if clf and vectorizer:
                                try:
                                    movie_vector = vectorizer.transform([content])
                                    if hasattr(clf, "predict_proba"):
                                        prob = clf.predict_proba(movie_vector)[0][1]
                                        sentiment = 'Good' if prob > 0.5 else 'Bad'
                                    else:
                                        pred = clf.predict(movie_vector)
                                        sentiment = 'Good' if str(pred[0]).lower() in ['1', 'positive', 'good'] else 'Bad'
                                except:
                                    pass
                            
                            reviews_list.append(content)
                            reviews_status.append(sentiment)
                            new_persisted_reviews.append([str(movie_id), content, sentiment])
                            if len(reviews_list) >= 15: break
                    
                    if new_persisted_reviews:
                        persist_df = pd.DataFrame(new_persisted_reviews, columns=['movie_id', 'review', 'sentiment'])
                        persist_df.to_csv(REVIEWS_FILE, mode='a', header=False, index=False)
        except Exception as e:
            print(f"IMDB Scrape Note: {e}")

    # 3. Add Browser-passed reviews (TMDB) as fallback
    browser_reviews = request.form.get('browser_reviews')
    if browser_reviews:
        try:
            b_revs = json.loads(browser_reviews)
            for br in b_revs:
                clean_br = bs.BeautifulSoup(br, "lxml").get_text(separator=' ').strip()
                if clean_br and clean_br not in reviews_list:
                    reviews_list.append(clean_br)
        except:
            pass

    # Final preparation for display
    cleaned_reviews = []
    final_status = []
    
    for i, rev in enumerate(reviews_list):
        if rev not in cleaned_reviews:
            cleaned_reviews.append(rev)
            if i < len(reviews_status):
                final_status.append(reviews_status[i])
            else:
                # Perform inference for browser-only reviews
                if clf and vectorizer:
                    movie_vector = vectorizer.transform([rev])
                    prob = clf.predict_proba(movie_vector)[0][1] if hasattr(clf, "predict_proba") else 0.6
                    final_status.append('Good' if prob > 0.5 else 'Bad')
                else:
                    final_status.append('Good')

    movie_reviews = {cleaned_reviews[i]: final_status[i] for i in range(len(final_status))}     
    latency = round(time.time() - start_time, 4)

    return render_template('recommend.html',title=title,poster=poster,overview=overview,vote_average=vote_average,
        vote_count=vote_count,release_date=release_date,runtime=runtime,status=status,genres=genres,
        movie_cards=movie_cards,reviews=movie_reviews,casts=casts,cast_details=cast_details, latency=latency)

@app.route("/predict_sentiment", methods=["POST"])
def predict_sentiment():
    if clf is None or vectorizer is None:
        return jsonify({'error': 'Sentiment model not loaded'}), 500
    
    review = request.form.get('review')
    movie_id = request.form.get('movie_id')
    if not review:
        return jsonify({'error': 'No review provided'}), 400
    
    try:
        clean_text = bs.BeautifulSoup(review, "lxml").get_text()
        movie_vector = vectorizer.transform([clean_text])
        
        if hasattr(clf, "predict_proba"):
            prob = clf.predict_proba(movie_vector)[0][1]
            sentiment = 'Good' if prob > 0.5 else 'Bad'
        else:
            pred = clf.predict(movie_vector)
            sentiment = 'Good' if str(pred[0]).lower() in ['1', 'positive', 'good'] else 'Bad'
        
        # PERSIST GLOBALLY
        if movie_id:
            new_review = pd.DataFrame([[str(movie_id), clean_text, sentiment]], columns=['movie_id', 'review', 'sentiment'])
            new_review.to_csv(REVIEWS_FILE, mode='a', header=False, index=False)
            
        return jsonify({'sentiment': sentiment, 'cleaned_review': clean_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
