import os

with open('backend/hishab/ml_engine.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix empty string
target_predict = '''    def predict_intent(self, text):
        \"\"\"
        Predict the intent for a given user utterance.
        \"\"\"
        if not self.is_trained:'''

new_predict = '''    def predict_intent(self, text):
        \"\"\"
        Predict the intent for a given user utterance.
        \"\"\"
        text = text.strip() if text else ""
        if not text:
            return {'intent': 'unknown', 'confidence': 1.0, 'extracted_entities': {}}
            
        if not self.is_trained:'''

code = code.replace(target_predict, new_predict)

# Fix missing pkl / silent failure
target_not_trained = '''        if not self.is_trained:
            raise RuntimeError("Model must be trained before predicting. Call train_model() first.")'''

new_not_trained = '''        if not self.is_trained:
            # Fallback instead of raising an error
            print("Warning: ML model not trained, falling back to unknown intent.")
            return {'intent': 'unknown', 'confidence': 0.0, 'extracted_entities': _extract_entities(text)}'''

code = code.replace(target_not_trained, new_not_trained)

with open('backend/hishab/ml_engine.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('ml_engine fixed')
