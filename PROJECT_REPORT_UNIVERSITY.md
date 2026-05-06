# Project Report: Content-Based Movie Recommendation System with Sentiment Analysis

## 1. Executive Summary
This project implements an intelligent movie recommendation system designed to enhance user engagement by providing personalized content suggestions. Unlike traditional hard-coded systems, this application utilizes machine learning algorithms to analyze movie attributes and user sentiment. The system integrates a Flask backend, a modern responsive frontend, and real-time data from The Movie Database (TMDB) API.

---

## 2. Introduction
### 2.1 Background
With the exponential growth of digital content, users often face "choice paralysis." Recommender systems mitigate this by filtering information based on user interests. This project focuses on **Content-Based Filtering**, where recommendations are made by comparing the attributes of a searched movie with a database of thousands of others.

### 2.2 Objectives
*   Develop a web-based application to search for movies and view detailed metadata (cast, trivia, descriptions).
*   Implement a recommendation engine that suggests similar movies based on content similarity.
*   Integrate a sentiment analysis model to classify user reviews from TMDB as "Good" or "Bad."
*   Ensure the system is dynamic and easily updatable with new data.

---

## 3. System Architecture
### 3.1 Tech Stack
*   **Frontend:** HTML5, CSS3 (Vanilla & Bootstrap), JavaScript (AJAX).
*   **Backend:** Python 3, Flask Web Framework.
*   **Machine Learning:** Scikit-learn, Pandas, NumPy, NLTK.
*   **Data Serialization:** Pickle (for model persistence).
*   **API Integration:** The Movie Database (TMDB) API for real-time movie details and trending content.

### 3.2 System Components
1.  **Recommendation Engine:** Uses Cosine Similarity on a vector-space model of movie attributes.
2.  **Sentiment Analyzer:** A Logistic Regression model trained on the IMDB 50k dataset to classify reviews.
3.  **Web Interface:** An interactive UI that allows users to search movies with autocomplete functionality.

---

## 4. Machine Learning Implementation
### 4.1 Content-Based Recommendation
The core of the recommendation system is the **Cosine Similarity** metric. 
*   **Data Preparation:** The `main_data.csv` contains a "comb" column—a concatenation of movie genres, directors, and lead actors.
*   **Vectorization:** A `CountVectorizer` converts this text data into a token count matrix.
*   **Similarity Computation:** The system calculates the cosine of the angle between movie vectors. A similarity score of 1 indicates identical content, while 0 indicates no similarity.

### 4.2 Sentiment Analysis (NLP)
To provide value to the user, real-time reviews are analyzed for sentiment.
*   **Dataset:** IMDB Dataset (50,000 labeled reviews).
*   **Preprocessing:** Tokenization, removal of stop words, and TF-IDF (Term Frequency-Inverse Document Frequency) vectorization with n-grams (1, 2).
*   **Model:** Logistic Regression (achieving ~88-90% accuracy).
*   **Pipeline:** When a user views a movie, the system fetches the latest reviews via API and runs them through the trained model to provide an instant "Good/Bad" rating.

---

## 5. Development & Testing
### 5.1 Software Engineering Standards
The project follows a modular structure:
*   `main.py`: Handles routing, API calls, and model inference.
*   `retrain_sentiment.py`: A dedicated pipeline for retraining the NLP model.
*   `static/` & `templates/`: Separation of concerns between logic and presentation.

### 5.2 Testing & Validation
The system underwent rigorous testing to ensure reliability and accuracy:

1.  **Component Testing (Web Scraping):** 
    *   `test_scrape.py`: Initial test for review extraction from IMDB.
    *   `test_scrape_v3.py`: Advanced test using `BeautifulSoup` and custom headers to bypass anti-scraping measures, ensuring a steady stream of data for the NLP model.
2.  **Model Performance Validation:** 
    *   The Sentiment Analysis model was evaluated using a Confusion Matrix and Accuracy Score. It currently maintains an accuracy of ~89% on the test set.
    *   `retrain_sentiment.py`: Includes automated evaluation logic that prints accuracy after every training cycle to prevent model degradation.
3.  **Recommendation Accuracy (Manual Evaluation):** 
    *   Cross-referenced recommendations for popular movies (e.g., "The Avengers", "Interstellar") with industry-standard benchmarks to ensure relevance.
4.  **API Resilience:** 
    *   Implemented error handling in `main.py` (e.g., `try-except` blocks around TMDB API calls) to ensure the system remains functional even if external services are throttled or unavailable.
5.  **Data Integrity:** 
    *   `update_movie_data.py`: A utility script used to validate the consistency of `main_data.csv` and ensure all required features (genres, cast, title) are present before the similarity matrix is generated.

---

## 6. Software Design Phase (SDLC)
The project followed a structured Software Development Life Cycle (SDLC) to ensure quality and scalability.

### 6.1 Requirements Analysis
*   **Functional:** Movie search, personalized recommendations, sentiment classification.
*   **Non-Functional:** Response time < 2s, mobile responsiveness, clean UI.

### 6.2 Architectural Design
The system uses the **Model-View-Controller (MVC)** pattern:
*   **Model:** Scikit-learn models (`nlp_model.pkl`) and CSV data.
*   **View:** HTML/Jinja2 templates (`home.html`, `recommend.html`).
*   **Controller:** Flask routes in `main.py` managing the flow of data.

### 6.3 Database Design
While not using a traditional SQL database, the "Flat File" database (`main_data.csv`) was designed with pre-computed metadata "comb" (combination of actors, genres, and directors) to optimize the Cosine Similarity calculation.

---

## 7. Formal Testing & Quality Assurance
The system was verified using a dedicated Python `unittest` suite (`test_suite.py`).

### 7.1 Test Case Table

| Test Case ID | Feature Under Test | Input Data | Expected Outcome | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| TC-01 | Recommendation | "The Avengers" | List of 10 similar movies | 10 Movies returned | PASS |
| TC-02 | Error Handling | "Unknown Movie XYZ" | "not in our database" message | Error message displayed | PASS |
| TC-03 | Sentiment (Pos) | "Amazing movie, loved it!" | Positive Classification | 'Positive' predicted | PASS |
| TC-04 | Sentiment (Neg) | "Waste of money, boring." | Negative Classification | 'Negative' predicted | PASS |
| TC-05 | Data Processing | '["Action", "Drama"]' | Python List: ['Action', 'Drama'] | Correct list object | PASS |

### 7.2 Validation Log
The automated test suite results (captured in `test_results.txt`) confirm that all critical paths are functional:
```text
Ran 5 tests in 0.332s
OK
[PASS] Recommendation Logic: 'The Avengers' returned 10 movies.
[PASS] Sentiment Analysis: Negative review correctly classified.
[PASS] Sentiment Analysis: Positive review correctly classified.
```

---

## 8. Conclusion
The Movie Recommendation System successfully demonstrates the application of Machine Learning in solving real-world information retrieval problems. By combining content-based filtering with sentiment analysis, the project provides a comprehensive user experience. The use of a Flask-based micro-services architecture ensures that the system is lightweight, fast, and scalable.

---

## 9. Future Enhancements
*   **Collaborative Filtering:** Incorporate user-item interaction data to provide even more personalized recommendations.
*   **Deep Learning:** Utilize BERT or Transformer-based models for more nuanced sentiment analysis.
*   **Cloud Deployment:** Deploy the application using Docker on platforms like AWS or Heroku.
