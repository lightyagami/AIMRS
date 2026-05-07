import unittest
import pandas as pd
import pickle
import os
from main import rcmd, convert_to_list

class MovieSystemTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up resources for testing."""
        # Load the sentiment model and vectorizer
        # Using context managers for cleaner code
        with open('sentiment_model.pkl', 'rb') as f:
            cls.clf = pickle.load(f)
        with open('sentiment_vectorizer.pkl', 'rb') as f:
            cls.vectorizer = pickle.load(f)
        cls.data = pd.read_csv('main_data.csv')

    def test_recommendation_logic(self):
        """Test if the recommendation engine returns 10 movies for a known title."""
        recommendations = rcmd('The Avengers')
        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), 10)
        print("\n[PASS] Recommendation Logic: 'The Avengers' returned 10 similar movies.")

    def test_invalid_movie_handling(self):
        """Test if the system handles unknown movies gracefully."""
        result = rcmd('Some Non Existent Movie 12345')
        self.assertIsInstance(result, str)
        self.assertIn('not in our database', result)
        print("[PASS] Error Handling: System correctly identified an invalid movie title.")

    def test_sentiment_analysis_positive(self):
        """Test if a clearly positive review is classified correctly."""
        review = ["This movie was absolutely amazing! I loved every minute of it."]
        vector = self.vectorizer.transform(review)
        prediction = self.clf.predict(vector)[0]
        # In this model version, predictions might be 'positive' or 1
        self.assertTrue(str(prediction).lower() in ['1', 'positive', 'good'])
        print("[PASS] Sentiment Analysis: Positive review correctly classified.")

    def test_sentiment_analysis_negative(self):
        """Test if a clearly negative review is classified correctly."""
        review = ["Worst movie ever. A complete waste of time and money."]
        vector = self.vectorizer.transform(review)
        prediction = self.clf.predict(vector)[0]
        # In this model version, predictions might be 'negative' or 0
        self.assertTrue(str(prediction).lower() in ['0', 'negative', 'bad'])
        print("[PASS] Sentiment Analysis: Negative review correctly classified.")

if __name__ == '__main__':
    unittest.main()
