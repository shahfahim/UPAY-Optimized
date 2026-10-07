"""
ML Engine for Intent Classification

This module provides a robust, Machine Learning-based alternative to the 
current regex-based fallback mechanisms (like `fallback.py`). 
It uses a TF-IDF vectorizer (with char_wb ngrams for extreme typo robustness) 
and a LinearSVC (calibrated for probabilities) to predict intents.
"""

import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts", "intent_model.pkl")

class IntentClassifier:
    def __init__(self, load: bool = True):
        """
        Initialize the intent classifier with a TF-IDF vectorizer and a 
        LinearSVC model wrapped in a scikit-learn Pipeline.
        """
        # LinearSVC needs calibration to output probabilities
        svm = LinearSVC(dual="auto", max_iter=2000, random_state=42)
        calibrated_svc = CalibratedClassifierCV(svm, method='sigmoid', cv=3)
        
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), lowercase=True)),
            ('clf', calibrated_svc)
        ])
        self.is_trained = False
        if load:
            self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.pipeline = pickle.load(f)
                self.is_trained = True
                print(f"Model successfully loaded from {MODEL_PATH}")
            except Exception as e:
                print(f"Failed to load model: {e}")

    def train_model(self, data):
        """
        Train the intent classification model and save it.
        """
        if not data:
            raise ValueError("Training data cannot be empty.")
            
        texts = [item['text'] for item in data]
        labels = [item['intent'] for item in data]
        
        # Train the pipeline
        self.pipeline.fit(texts, labels)
        self.is_trained = True
        
        # Save model
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.pipeline, f)
        print(f"Model successfully trained on {len(data)} samples and saved to {MODEL_PATH}.")

    def predict_intent(self, text):
        """
        Predict the intent for a given user utterance.
        """
        text = text.strip() if text else ""
        if not text:
            return {'intent': 'unknown', 'confidence': 1.0, 'extracted_entities': {}}
            
        if not self.is_trained:
            # Fallback instead of raising an error
            print("Warning: ML model not trained, falling back to unknown intent.")
            return {'intent': 'unknown', 'confidence': 0.0, 'extracted_entities': _extract_entities(text)}

        # The pipeline handles vectorization and prediction automatically
        prediction = self.pipeline.predict([text])[0]

        # Get probability/confidence score
        probabilities = self.pipeline.predict_proba([text])[0]
        confidence = np.max(probabilities)

        return {
            'intent': prediction,
            'confidence': round(float(confidence), 3),
            'extracted_entities': _extract_entities(text),
        }


_BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def _extract_entities(text: str) -> dict:
    """Pull a taka amount out of the query (handles Bangla digits, 1,500, 2k)."""
    import re
    t = text.translate(_BN_DIGITS).lower().replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(k|হাজার|hajar|thousand)?", t)
    if not m:
        return {}
    amount = float(m.group(1)) * (1000 if m.group(2) else 1)
    return {"amount": int(amount) if amount.is_integer() else amount}

# Global instance for easier import and usage
_classifier_instance = IntentClassifier()

def train_model(data):
    return _classifier_instance.train_model(data)

def predict_intent(text):
    return _classifier_instance.predict_intent(text)
