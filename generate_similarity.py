import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

print("Loading movie data...")
df = pd.read_csv('main_data.csv')

print("Vectorizing movie features (Tfidf)...")
# Using Tfidf as specified in the project documentation
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['comb'])

print("Computing cosine similarity matrix...")
# This corresponds to 'transform.pkl' in the documentation
sim = cosine_similarity(tfidf_matrix)

print("Saving models...")
# Based on miniproj.docx Appendix A naming:
# nlp_model.pkl -> vectorizer for recommendations
# transform.pkl -> similarity matrix
pickle.dump(tfidf, open('nlp_model.pkl', 'wb'))
pickle.dump(sim, open('transform.pkl', 'wb'))

print("Recommendation models generated successfully!")
