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
        cls.clf = pickle.load(open('nlp_model.pkl', 'rb'))
        cls.vectorizer = pickle.load(open('tranform.pkl', 'rb'))
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
        # Adjusting expectation to 'positive' string
        self.assertEqual(prediction.lower(), 'positive') 
        print("[PASS] Sentiment Analysis: Positive review correctly classified.")

    def test_sentiment_analysis_negative(self):
        """Test if a clearly negative review is classified correctly."""
        review = ["Worst movie ever. A complete waste of time and money."]
        vector = self.vectorizer.transform(review)
        prediction = self.clf.predict(vector)[0]
        # Adjusting expectation to 'negative' string
        self.assertEqual(prediction.lower(), 'negative') 
        print("[PASS] Sentiment Analysis: Negative review correctly classified.")

    def test_data_utility_function(self):
        """Test the string-to-list conversion utility."""
        raw_list = '["Action","Adventure","Sci-Fi"]'
        processed = convert_to_list(raw_list)
        self.assertEqual(len(processed), 3)
        self.assertEqual(processed[0], 'Action')
        print("[PASS] Utility Function: String-to-list conversion is accurate.")

if __name__ == '__main__':
    print("Starting Movie Recommendation System Test Suite...")
    print("="*50)
    unittest.main()
