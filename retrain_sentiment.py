import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pickle
import os

# Download stopwords if not already present
print("Downloading stopwords...")
nltk.download('stopwords')
stop = set(stopwords.words('english'))

print("Loading dataset...")
df = pd.read_csv('IMDB Dataset.csv')

# Preprocessing: convert sentiment to binary
if df['sentiment'].dtype == 'O':
    df['sentiment'] = df['sentiment'].apply(lambda x: 1 if x.lower() == 'positive' else 0)

print("Vectorizing data...")
# Initialize TfidfVectorizer with improved parameters
vectorizer = TfidfVectorizer(
    use_idf=True, 
    lowercase=True, 
    strip_accents='ascii', 
    stop_words=list(stop),
    ngram_range=(1,2),
    max_df=0.7,
    min_df=5
)

# Fit and transform the reviews
X = vectorizer.fit_transform(df.review)
y = df.sentiment

# Save the vectorizer
print("Saving tranform.pkl...")
pickle.dump(vectorizer, open('tranform.pkl', 'wb'))

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

print("Training LogisticRegression model...")
# Initialize and train the model
clf = LogisticRegression(max_iter=1000)
clf.fit(X_train, y_train)

# Check accuracy
y_pred = clf.predict(X_test)
print(f"Model Accuracy: {accuracy_score(y_test, y_pred):.2f}")

# Save the model
print("Saving nlp_model.pkl...")
pickle.dump(clf, open('nlp_model.pkl', 'wb'))

print("Retraining complete! New models have been saved to the project root.")
