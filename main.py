import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import bs4 as bs
import urllib.request
import pickle
import requests
import re

# load the nlp model and tfidf vectorizer from disk
filename = 'nlp_model.pkl'
clf = pickle.load(open(filename, 'rb'))
#importing tfidf transformer object using sentiment model training
vectorizer = pickle.load(open('tranform.pkl','rb'))

# Global variables for data and similarity
data = None
similarity = None

def create_similarity():
    global data
    data = pd.read_csv('main_data.csv')
    data['movie_title_clean'] = data['movie_title'].str.lower().str.replace(r'[^a-zA-Z0-9]', '', regex=True)
    # creating a count matrix
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    # creating a similarity score matrix
    sim = cosine_similarity(count_matrix)
    return data, sim

def rcmd(m):
    global data, similarity
    m = re.sub(r'[^a-zA-Z0-9]', '', m.lower())
    if data is None or similarity is None:
        data, similarity = create_similarity()
    
    if m not in data['movie_title_clean'].unique():
        return('Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies')
    else:
        movie_indx = data.loc[data['movie_title_clean']==m].index[0]
        lst = list(enumerate(similarity[movie_indx]))
        lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
        lst = lst[0:11] 
        l = []
        for i in range(len(lst)):
            if lst[i][0] != movie_indx:
                a = lst[i][0]
                l.append(data['movie_title'][a])
        return l
    
# converting list of string to list (eg. "["abc","def"]" to ["abc","def"])
def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["','')
    my_list[-1] = my_list[-1].replace('"]','')
    return my_list

def get_suggestions():
    global data
    if data is None:
        data, _ = create_similarity()
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

@app.route("/recommend",methods=["POST"])
def recommend():
    global data, similarity
    # getting data from AJAX request
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

    # Ensure data is loaded
    if data is None or similarity is None:
        data, similarity = create_similarity()

    # get movie suggestions for auto complete
    suggestions = get_suggestions()

    # call the convert_to_list function for every string that needs to be converted to list
    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)
    cast_bdays = convert_to_list(cast_bdays)
    cast_bios = convert_to_list(cast_bios)
    cast_places = convert_to_list(cast_places)
    
    # convert string to list (eg. "[1,2,3]" to [1,2,3])
    cast_ids = cast_ids.split(',')
    cast_ids[0] = cast_ids[0].replace("[","")
    cast_ids[-1] = cast_ids[-1].replace("]","")
    
    # rendering the string to python string
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"','\"')
    
    # combining multiple lists as a dictionary which can be passed to the html file so that it can be processed easily and the order of information will be preserved
    movie_cards = {rec_posters[i]: rec_movies[i] for i in range(len(rec_posters))}
    
    casts = {cast_names[i]:[cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}

    cast_details = {cast_names[i]:[cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in range(len(cast_places))}

    # Get reviews from TMDB API
    api_key = '71bdf22d8b06fde7b7b67d170d00b0c8'
    rev_url = f"http://3.165.239.72/3/movie/{movie_id}/reviews?api_key={api_key}&language=en-US"
    headers = {"Host": "api.themoviedb.org"}
    
    reviews_list = []
    reviews_status = []
    
    try:
        response = requests.get(rev_url, headers=headers, timeout=5)
        if response.status_code == 200:
            results = response.json().get('results', [])
            for rev in results:
                content = rev.get('content', '')
                if content:
                    reviews_list.append(content)
                    movie_review_list = np.array([content])
                    movie_vector = vectorizer.transform(movie_review_list)
                    if hasattr(clf, "predict_proba"):
                        prob = clf.predict_proba(movie_vector)[0][1]
                        reviews_status.append('Good' if prob > 0.55 else 'Bad')
                    else:
                        pred = clf.predict(movie_vector)
                        reviews_status.append('Good' if pred else 'Bad')
    except Exception as e:
        print(f"Error fetching reviews: {e}")

    movie_reviews = {reviews_list[i]: reviews_status[i] for i in range(len(reviews_list))}     

    return render_template('recommend.html',title=title,poster=poster,overview=overview,vote_average=vote_average,
        vote_count=vote_count,release_date=release_date,runtime=runtime,status=status,genres=genres,
        movie_cards=movie_cards,reviews=movie_reviews,casts=casts,cast_details=cast_details)

if __name__ == '__main__':
    app.run(debug=True)
