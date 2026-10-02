"""
ML Engine for Intent Classification

This module provides a robust, Machine Learning-based alternative to the 
current regex-based fallback mechanisms (like `fallback.py`). 

Currently, `fallback.py` handles user queries by matching hardcoded regular 
expressions. While this works for a limited set of pre-defined patterns, it 
fails to generalize to the diverse ways low-income Bangladeshi users might 
express their financial needs (e.g., mixing Bengali, English, and regional dialects).

Once we collect sufficient training data (pairs of user utterances and their 
corresponding intents), this ML engine will replace the regex logic. It uses 
a TF-IDF vectorizer to extract features from text and a Multinomial Naive Bayes 
classifier (or LightGBM for more complex patterns) to probabilistically determine 
the user's intent.

Future steps for production:
1. Data collection & annotation (utterance -> intent).
2. Preprocessing pipeline (handling Bangla-lish, spell correction).
3. Hyperparameter tuning.
4. Model serialization (saving/loading models via joblib or pickle).
5. Seamless integration with the main router to fallback here instead of `fallback.py`.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
# from lightgbm import LGBMClassifier # Alternative for better performance on larger datasets

class IntentClassifier:
    def __init__(self):
        """
        Initialize the intent classifier with a TF-IDF vectorizer and a 
        MultinomialNB model wrapped in a scikit-learn Pipeline.
        """
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
            ('clf', MultinomialNB())
            # For LightGBM, replace the above line with:
            # ('clf', LGBMClassifier(n_estimators=100, learning_rate=0.1))
        ])
        self.is_trained = False

    def train_model(self, data):
        """
        Train the intent classification model.

        Args:
            data (list of dict): A list containing dictionaries with 'text' and 'intent' keys.
                                 Example: [{'text': 'Send money to Karim', 'intent': 'send_money'}, ...]
        """
        if not data:
            raise ValueError("Training data cannot be empty.")
            
        texts = [item['text'] for item in data]
        labels = [item['intent'] for item in data]
        
        # Train the pipeline (vectorizer + classifier)
        self.pipeline.fit(texts, labels)
        self.is_trained = True
        print(f"Model successfully trained on {len(data)} samples.")

    def predict_intent(self, text):
        """
        Predict the intent for a given user utterance.

        Args:
            text (str): The user's input string.

        Returns:
            dict: A dictionary containing the predicted intent and its confidence score.
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before predicting. Call train_model() first.")
            
        # The pipeline handles vectorization and prediction automatically
        prediction = self.pipeline.predict([text])[0]
        
        # Get probability/confidence score
        probabilities = self.pipeline.predict_proba([text])[0]
        confidence = np.max(probabilities)
        
        return {
            'intent': prediction,
            'confidence': float(confidence)
        }

# Global instance for easier import and usage
_classifier_instance = IntentClassifier()

def train_model(data):
    """
    Module-level function to train the global model instance.
    This will eventually replace the rule-based configuration in `fallback.py`.
    """
    return _classifier_instance.train_model(data)

def predict_intent(text):
    """
    Module-level function to predict intent using the global model instance.
    Once trained, the system should route unknown queries here instead of `fallback.py`.
    """
    return _classifier_instance.predict_intent(text)

if __name__ == "__main__":
    # Example usage for testing the skeleton
    sample_data = [
        {'text': 'amar account e koto ache', 'intent': 'check_balance'},
        {'text': 'balance check korbo', 'intent': 'check_balance'},
        {'text': 'karim ke 500 taka pathao', 'intent': 'send_money'},
        {'text': 'send 500 tk to 01711111111', 'intent': 'send_money'},
        {'text': 'mobile recharge korbo', 'intent': 'mobile_recharge'}
    ]
    
    train_model(sample_data)
    
    test_query = "500 taka send koro"
    result = predict_intent(test_query)
    print(f"Query: '{test_query}' -> Prediction: {result}")
