# Movie Recommendation System - Exam/Viva Preparation Guide

This document contains potential questions and "perfect" answers for your project defense, categorized by domain.

---

## 1. Frontend & User Experience (UX)
*   **How does the autocomplete feature work?**
    *   It uses `autocomplete.js` to fetch the movie list from the backend and provides real-time suggestions as the user types, improving UX by preventing typos.
*   **How is data passed from Flask to HTML?**
    *   Via **Jinja2** templating. The backend sends variables (lists/dictionaries), and the HTML uses `{{ }}` for variables and `{% for %}` loops to render movie cards.
*   **What is the purpose of `recommend.js`?**
    *   It manages AJAX requests. This allows the "Recommend" button to fetch data and update the page without a full browser refresh.
*   **Why did you include a "Loader" (`loader.gif`)?**
    *   To provide visual feedback during the 2-3 seconds it takes to fetch TMDB API data and calculate similarity, preventing the user from thinking the app has crashed.

## 2. Backend & System Architecture
*   **Why Flask instead of Django?**
    *   Flask is a micro-framework, making it lightweight and ideal for ML prototypes where a complex built-in ORM or Admin panel isn't required.
*   **Explain the Request-Response Cycle.**
    *   User Search -> `recommend.js` (AJAX) -> Flask `main.py` -> ML Model (Similarity) -> TMDB API (Posters) -> JSON Response -> Frontend Update.
*   **What is the role of `pickle`?**
    *   It is used for **serialization**. It saves trained model objects (Similarity matrix, TF-IDF vectorizer) so they can be loaded instantly without retraining.

## 3. Machine Learning & Data Science
*   **What type of system is this?**
    *   **Content-Based Filtering**. It recommends items based on their features (genre, cast, director) rather than user behavior.
*   **What is the "comb" column in your dataset?**
    *   A concatenated string of metadata (Actor + Director + Genre + Keywords). This acts as the feature vector for each movie.
*   **Explain Cosine Similarity.**
    *   It measures the cosine of the angle between two vectors. It determines how similar two movies are regardless of the "length" of their metadata.
*   **Explain Sentiment Analysis logic.**
    *   It uses **TF-IDF Vectorization** (with bigrams) to turn review text into numerical features and a **Logistic Regression** classifier to predict sentiment.
    *   *Why Logistic Regression?* Because it is efficient, interprets probabilities well, and performs exceptionally well on high-dimensional sparse text data compared to more complex models.

## 4. Feature Engineering & Data Preprocessing
*   **What specific features are used for Recommendation?**
    *   The system uses a **metadata-fusion** approach. The primary features are:
        1. **Genres:** (e.g., Action, Sci-Fi) to capture the movie's category.
        2. **Director:** To capture the cinematic style associated with specific filmmakers.
        3. **Top 3 Cast Members:** To recommend movies with similar star power or acting styles.
        4. **Keywords/Plot Tags:** Extracted to capture the thematic essence of the movie.
    *   These are all concatenated into the **`comb`** (combination) feature.

*   **How was the data cleaned and preprocessed?**
    1. **Lowercasing:** All text was converted to lowercase to ensure "Action" and "action" are treated as the same feature.
    2. **Special Character Removal:** Using Regex (`[^a-zA-Z0-9]`) to remove punctuation that doesn't add semantic value.
    3. **Stopword Removal:** Words like "the", "is", and "at" were removed using NLTK to focus on meaningful keywords.
    4. **N-gram Modeling:** For sentiment analysis, I used **Bigrams** (pairs of words like "not good"). This helps the model understand negation which simple unigrams ("not", "good") would miss.

*   **What is the 'comb' column format?**
    *   It follows the pattern: `genre1 genre2 director_name actor1_name actor2_name actor3_name`.
    *   *Example:* For "The Avengers", the comb would be: `action adventure sci-fi joss whedon robert downey jr. chris evans mark ruffalo`.

---

## 5. Hard "Grilling" Questions (The Advanced Section)

### A. Algorithmic & Mathematical
*   **"The Cold Start Problem":** How do you handle a movie released yesterday that isn't in your CSV?
*   **"The Curse of Dimensionality":** How does having thousands of TF-IDF features affect the accuracy of Cosine Similarity?
*   **"Linearity of Similarity":** Why treat Cast and Genre with equal weight in a single string?
*   **"Why Content-Based instead of Collaborative Filtering?":** Why ignore user-rating patterns?
*   **"Why not use Word/Sentence Embeddings (Sentence-BERT)?":** Why use 'Bag-of-Words' instead of modern deep learning tensors?

### B. Engineering & Production
*   **"The O(N²) Problem":** If you have 1 million movies, how will you handle the memory explosion of a similarity matrix?
*   **"Global Interpreter Lock (GIL)":** How does Flask handle multiple users performing heavy ML calculations simultaneously?
*   **"State Management":** Why is using `global similarity` a bad idea for a multi-worker production server (Gunicorn)?

### C. Security & Integrity
*   **"Pickle Security":** Are you aware that `pickle.load()` can execute arbitrary code? How would you secure this?
*   **"Hardcoded Secrets":** Why is your TMDB API key visible in the source code, and how would you fix it?

---

## 5. The "Perfect" Strategic Answers

### Q1: The Cold Start Problem
**Answer:** "Currently, this is a known limitation. In a production environment, I would solve this by implementing a **Hybrid Model**. I would use the TMDB API to fetch 'Trending' movies as a fallback for new titles and set up a **data pipeline** that automatically scrapes and vectorizes new releases every 24 hours to keep the local database updated."

### Q2: Why Content-Based instead of Collaborative Filtering?
**Answer:** "Collaborative Filtering requires a massive **User-Item Interaction Matrix** (millions of ratings from thousands of unique users). My project focuses on the **attributes of the movie** itself. Content-based filtering is superior for this use case because:
1. It doesn't suffer from the 'User Cold Start' problem (it works for a first-time user who hasn't rated anything).
2. It is more transparent—we can tell the user *exactly* why a movie was recommended (e.g., 'because it shares the same director').
3. It doesn't require storing sensitive user profile data, making it more privacy-friendly for a public tool."

### Q3: Why not use Sentence Tensors or Transformers (SBERT/USE)?
**Answer:** "While Sentence Tensors (like SBERT) provide deep semantic understanding, they come with a high **computational cost**.
1. **Inference Speed:** Running a BERT-based model on every search would require a GPU to maintain the low latency I currently have with CountVectorizer on a CPU.
2. **Domain Specificity:** Movie metadata consists mostly of proper nouns (Actors, Directors) and categorical tags (Genres). These don't have 'synonyms' or complex grammar that a Transformer needs to decode. In this specific domain, 'Bag-of-Words' is often as accurate as deep learning but 100x faster.
3. **Model Size:** A TF-IDF pickle is a few MBs; a Transformer model is 400MB+. For a lightweight Flask deployment, the simpler model is more architecturally sound."

### Q4: Why Logistic Regression for Sentiment instead of Random Forest or SVM?
**Answer:** "Logistic Regression is a linear model that performs exceptionally well on **high-dimensional sparse data** like TF-IDF vectors. It is less prone to overfitting than a Deep Decision Tree (Random Forest) when the number of features is greater than the number of samples. It also provides a probability score, which allows us to see how 'confident' the model is in its sentiment prediction."

### Q5: Why Cosine Similarity over Euclidean Distance?
**Answer:** "I chose Cosine Similarity because it is **magnitude-independent**. In text analysis, one movie might have a much longer plot summary than another. Euclidean distance would penalize the shorter vector, whereas Cosine Similarity only looks at the *angle* (the presence of shared keywords), making it much more accurate for 'bag-of-words' comparisons."

### Q6: Scaling to 1 Million Movies (The O(N²) Problem)
**Answer:** "Calculating an exact $N \times N$ matrix for 1 million movies is impossible in RAM. To scale, I would use **Approximate Nearest Neighbors (ANN)** libraries like **FAISS** or **Annoy**. These use tree-based indexing to find similar vectors in $O(\log N)$ time rather than $O(N^2)$, allowing the system to scale to millions of movies efficiently."

### Q7: Handling Sarcasm in Sentiment Analysis
**Answer:** "My current Logistic Regression model relies on word frequencies and n-grams, so it often misses sarcasm (e.g., 'This movie was a total masterpiece... NOT!'). To fix this, I would replace the current classifier with a **Transformer-based model like BERT**, which understands bidirectional context and semantic nuances far better than simple frequency-based models."

### Q8: Architectural Weakness (Global Variables & CSVs)
**Answer:** "In this prototype, global variables and CSVs were used for simplicity. However, for a production-grade app, I would move the metadata to a **PostgreSQL database** with indexing. I would also wrap the ML logic in a separate **Microservice** (using FastAPI) to decouple the heavy computation from the user-facing web server."

### Q9: Security & API Keys
**Answer:** "Hardcoding the API key was for ease of testing during development. For production, I would use **Environment Variables** (stored in a `.env` file) and ensure that file is added to `.gitignore`. This prevents secrets from being leaked in version control."
