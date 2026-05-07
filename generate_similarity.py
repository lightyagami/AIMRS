import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

print("Loading movie data...")
df = pd.read_csv('main_data.csv')

print("Vectorizing movie features (CountVectorizer)...")
# Using CountVectorizer as it is more robust for short metadata strings
cv = CountVectorizer(stop_words='english')
count_matrix = cv.fit_transform(df['comb'])

print("Computing cosine similarity matrix...")
sim = cosine_similarity(count_matrix)

print("Saving models...")
# We keep the same filenames for compatibility
pickle.dump(cv, open('nlp_model.pkl', 'wb'))
pickle.dump(sim, open('transform.pkl', 'wb'))

print("Recommendation models regenerated successfully with CountVectorizer!")
