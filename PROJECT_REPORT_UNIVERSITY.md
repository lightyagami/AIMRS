# Project Report: Content-Based Movie Recommendation System with Sentiment Analysis

## 1. Executive Summary
This project implements an intelligent movie recommendation system designed to enhance user engagement by providing personalized content suggestions. The system utilizes machine learning algorithms (Count and Cosine Similarity) to analyze movie attributes and a Logistic Regression model for user sentiment analysis. The architecture consists of a Flask backend and a responsive frontend integrated with The Movie Database (TMDB) API.

---

## 2. Introduction
### 2.1 Background
The growth of digital content has led to "choice paralysis." This system mitigates this by providing **Content-Based Filtering**, comparing attributes of a searched movie with a database of thousands of others to find the most relevant matches.

### 2.2 Objectives
*   Develop a web application for movie discovery and metadata viewing.
*   Implement a recommendation engine using Count and Cosine Similarity.
*   Integrate a sentiment analysis model to classify reviews as "Good" or "Bad."
*   Ensure low-latency responses through model pre-computation.

---

## 3. System Architecture
### 3.1 Tech Stack
*   **Frontend:** HTML5, CSS3, JavaScript (AJAX).
*   **Backend:** Python 3, Flask Web Framework.
*   **Machine Learning:** Scikit-learn, Pandas, NumPy, NLTK.
*   **Data Serialization:** Pickle (for pre-computed similarity and sentiment models).
*   **API Integration:** TMDB API for metadata, posters, and cast info.

### 3.2 System Components
1.  **Recommendation Engine:** Uses Cosine Similarity on Count vectors of movie attributes.
2.  **Sentiment Analyzer:** A Logistic Regression model trained on 50,000 IMDB reviews.
3.  **Data Persistence:** Uses `transform.pkl` for the similarity matrix and `sentiment_model.pkl` for NLP classification.

---

## 4. Machine Learning Implementation
### 4.1 Content-Based Recommendation
*   **Data Preparation:** The `main_data.csv` contains a "comb" column—a concatenation of movie genres, directors, lead actors, and keywords.
*   **Vectorization:** `CountVectorizer` converts text into a weighted numerical matrix, emphasizing unique keywords.
*   **Similarity Computation:** Cosine Similarity calculates the angle between movie vectors.
*   **Optimization:** The similarity matrix is pre-computed and stored in `transform.pkl` to ensure sub-second response times.

### 4.2 Sentiment Analysis (NLP)
*   **Dataset:** IMDB 50k dataset.
*   **Preprocessing:** Count vectorization with Bi-grams.
*   **Model:** Logistic Regression (Accuracy: ~90%).
*   **Files:** `sentiment_model.pkl` (Model) and `sentiment_vectorizer.pkl` (Vectorizer).

---

## 5. File Structure and Serialization
*   `main.py`: Core application logic and routing.
*   `generate_similarity.py`: Offline script to generate recommendation models.
*   `retrain_sentiment.py`: Pipeline for training the NLP sentiment model.
*   `transform.pkl`: Pre-computed Cosine Similarity matrix.
*   `nlp_model.pkl`: Recommendation vectorizer.
*   `sentiment_model.pkl`: Trained sentiment classifier.
*   `sentiment_vectorizer.pkl`: Count vectorizer for sentiment analysis.

---

## 6. Conclusion
The system successfully provides accurate, content-based recommendations with high performance. By utilizing pre-computed models and a streamlined NLP pipeline, it achieves sub-second latency while providing high-quality, genre-consistent movie suggestions.
