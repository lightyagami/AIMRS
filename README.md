# Advanced Movie Recommendation Engine with Sentiment Analysis

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/framework-Flask-red.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📊 Overview
This project implements a sophisticated **Content-Based Recommendation Engine** integrated with an **NLP-driven Sentiment Analysis** pipeline. It leverages vector-space modeling and Cosine Similarity to suggest cinematic content and utilizes a Logistic Regression model to analyze real-time user feedback.

## 🚀 Key Features
- **Explainable AI (XAI):** Real-time display of similarity confidence scores for every recommendation.
- **Hybrid Data Pipeline:** Seamless integration of TMDB API for metadata and high-fidelity web scraping for IMDB reviews.
- **Sentiment Classification:** On-the-fly sentiment analysis of user reviews using TF-IDF vectorization.
- **Performance Optimized:** Low-latency inference ($<50ms$) achieved via optimized Scikit-learn matrices.
- **Glassmorphism UI:** Modern, responsive interface built with Apple-inspired design principles.

## 🛠️ Technical Architecture
### 1. Recommendation Engine
- **Vectorization:** `CountVectorizer` (N-gram range: 1, 1).
- **Similarity Metric:** Cosine Similarity.
- **Feature Set:** Genre, Director, Lead Cast, and Keywords.

### 2. Sentiment Analysis (NLP)
- **Algorithm:** Logistic Regression (trained on 50,000 IMDB records).
- **Vectorization:** TF-IDF with Bi-grams.
- **Accuracy:** ~89% on validation sets.

## 📂 Project Structure
```text
├── main.py                 # Core Flask Controller & ML Logic
├── retrain_sentiment.py    # NLP Model Training Pipeline
├── test_suite.py           # Unit Testing & QA Framework
├── static/                 # CSS, JavaScript & Assets
├── templates/              # Jinja2 HTML Templates
└── data-preprocessing/     # Experimental Jupyter Notebooks
```

## 📝 Academic Documentation
For detailed architectural analysis, testing results, and the Software Development Life Cycle (SDLC) report, please refer to:
👉 [**PROJECT_REPORT_UNIVERSITY.md**](./PROJECT_REPORT_UNIVERSITY.md)

## ⚡ Quick Start
1. **Initialize Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Execute Application:**
   ```bash
   python main.py
   ```

---
*Developed as part of a Master's Level Software Engineering Thesis Project.*
