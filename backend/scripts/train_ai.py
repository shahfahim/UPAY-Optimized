import sys
import os

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hishab.ml_engine import train_model

def generate_data():
    base_data = [
        # status
        ('ami ki bhalo korchi', 'status'),
        ('amar obostha ki', 'status'),
        ('hisab thik ache', 'status'),
        ('amar financial condition kemon', 'status'),
        ('ami ki save korte parchhi', 'status'),
        ('am i doing ok', 'status'),
        ('kemon cholche amar', 'status'),
        ('amar ki khobor', 'status'),
        
        # advice
        ('ki korbo ekhon', 'advice'),
        ('ki korle bhalo hoy', 'advice'),
        ('ki kora uchit', 'advice'),
        ('poramorsho daw', 'advice'),
        ('suggestion lagbe', 'advice'),
        ('what should i do', 'advice'),
        ('taka bachate ki korbo', 'advice'),
        ('kharoch komabe kivabe', 'advice'),
        ('help me with money', 'advice'),
        
        # goal
        ('sanchoy korbo kivabe', 'goal'),
        ('taka jomate chai', 'goal'),
        ('jomate parbo ki', 'goal'),
        ('goal set korbo', 'goal'),
        ('target koto', 'goal'),
        ('50000 joma 6 mase', 'goal'),
        ('koto save kora jabe', 'goal'),
        ('ki vabe save korbo', 'goal'),
        
        # send_money
        ('karim ke 500 taka pathao', 'send_money'),
        ('send money to rahim', 'send_money'),
        ('taka pathabo', 'send_money'),
        ('taka send koro', 'send_money'),
        ('1000 tk pathao', 'send_money'),
        
        # cashout
        ('cash out korbo', 'cashout'),
        ('cashout fee koto', 'cashout'),
        ('agent theke taka tulbo', 'cashout'),
        ('kash aut koto', 'cashout'),
        ('taka tulte koto charge', 'cashout'),
        ('cash withdrawal fee', 'cashout'),
        
        # route_planner
        ('kivabe taka pathale fee kom', 'route_planner'),
        ('kon route e pathabo', 'route_planner'),
        ('kishe pathale kom khoroch', 'route_planner'),
        ('npsb naki bkash', 'route_planner'),
        ('bkashe pathabo naki bank e', 'route_planner'),
        ('npsb na agent', 'route_planner'),
        ('bkash na nagad konta sosta', 'route_planner'),
        ('npsb naki agent cashout', 'route_planner'),
        ('bank card na npsb', 'route_planner'),
        ('nagad na npsb konta valo', 'route_planner'),
        ('kon channel e charge kom', 'route_planner'),
        ('এনপিএসবি নাকি এজেন্ট', 'route_planner'),
        
        # emergency
        ('emergency taka lagbe', 'emergency'),
        ('urgent loan dorkar', 'emergency'),
        ('dhar lagbe', 'emergency'),
        ('ekhuni taka dorkar', 'emergency'),
        ('borrow some money', 'emergency'),
        ('udhar dorkar', 'emergency'),
        ('joruri taka chai', 'emergency'),
        
        # savings
        ('amar savings koto', 'savings'),
        ('koto jomlo', 'savings'),
        ('sanchoy dekhao', 'savings'),
        ('total savings', 'savings'),
        ('joma taka koto', 'savings'),
        
        # health
        ('amar health kemon', 'health'),
        ('financial health check', 'health'),
        ('amar arthik shastho kemon', 'health'),
        ('health score koto', 'health'),

        # balance
        ('balance koto', 'balance'),
        ('amar account e koto taka ache', 'balance'),
        ('baki koto ache', 'balance'),
        ('balance check', 'balance'),

        # ---- Casual phrasings real users typed (from testing) ----
        ('maa ke tk pathabo kishe', 'route_planner'),
        ('mayer kase 500 tk patabo kon vabe', 'route_planner'),
        ('bank card diye korle charge koto', 'route_planner'),
        ('npsb te 300 tk pathale koto katbe', 'route_planner'),
        ('bari te taka pathabo konta sosta', 'route_planner'),
        ('tour er jnno tk jomabo', 'goal'),
        ('porer masher tour er jnno kivabe tk save krbo', 'goal'),
        ('eid er jonno taka jomate chai', 'goal'),
        ('phone kinbo taka jomabo', 'goal'),
        ('trip er jonno save korbo', 'goal'),
        ('mash shesh e taka thakbe to', 'status'),
        ('ei mash e ki taka sesh hoye jabe', 'status'),

        # ---- Bangla script ----
        ('আমার অবস্থা কেমন', 'status'),
        ('আমি কি ঠিক আছি', 'status'),
        ('মাস শেষে টাকা থাকবে তো', 'status'),
        ('এখন কী করব', 'advice'),
        ('খরচ কমাব কিভাবে', 'advice'),
        ('পরামর্শ দাও', 'advice'),
        ('টাকা জমাতে চাই', 'goal'),
        ('ট্যুরের জন্য টাকা জমাবো', 'goal'),
        ('৬ মাসে ২০০০০ টাকা জমাবো', 'goal'),
        ('করিমকে ৫০০ টাকা পাঠাও', 'send_money'),
        ('টাকা পাঠাবো', 'send_money'),
        ('ক্যাশ আউট করবো', 'cashout'),
        ('ক্যাশ আউট চার্জ কত', 'cashout'),
        ('কোন পথে পাঠালে খরচ কম', 'route_planner'),
        ('মাকে টাকা পাঠাবো কিসে', 'route_planner'),
        ('জরুরি টাকা লাগবে', 'emergency'),
        ('ধার লাগবে', 'emergency'),
        ('আমার সঞ্চয় কত', 'savings'),
        ('পকেটে কত জমলো', 'savings'),
        ('আমার আর্থিক স্বাস্থ্য কেমন', 'health'),
        ('ব্যালেন্স কত', 'balance'),
    ]

    # Let's multiply by duplicating with some random spelling variations
    import random
    random.seed(42)  # reproducible training set

    variations = {
        'bhalo': ['valo', 'vlo', 'bhlo'],
        'korchi': ['korci', 'krchi', 'krc'],
        'amar': ['amr', 'amaar'],
        'obostha': ['obosta', 'oboshta', 'obosta'],
        'kemon': ['kmn', 'kemonn'],
        'ki': ['k', 'kii'],
        'korbo': ['krbo', 'korb', 'korvo'],
        'taka': ['tk', 'tka'],
        'pathao': ['patao', 'patha', 'ptha'],
        'pathabo': ['patabo', 'pathbo', 'ptabo'],
        'cashout': ['cash out', 'kashout', 'kash aut'],
        'fee': ['fi', 'charge'],
        'jomate': ['jomte', 'jomaite'],
        'jomabo': ['jomamu', 'jmabo'],
        'chai': ['cai', 'chi'],
        'emergency': ['imargency', 'emergncy'],
        'lagbe': ['lgbe', 'lagba'],
        'kivabe': ['kivbe', 'kemne', 'kmne'],
        'jnno': ['jonno', 'jnne', 'jnyo'],
        'kishe': ['kise', 'kiser maddhome'],
    }

    data = []

    # Every typo variant keeps its seed phrase as `group`, so evaluation can hold out whole
    # phrases (variants of a test phrase never appear in training).
    for text, intent in base_data:
        data.append({'text': text, 'intent': intent, 'group': text})

        for _ in range(10):
            words = text.split()
            new_words = []
            for w in words:
                if w in variations and random.random() > 0.3:
                    new_words.append(random.choice(variations[w]))
                else:
                    new_words.append(w)

            # also randomly drop some vowels to simulate extreme typos (Latin only)
            final_words = []
            for w in new_words:
                if w.isascii() and len(w) > 3 and random.random() > 0.7:
                    for v in 'aeiou':
                        w = w.replace(v, '', 1)
                final_words.append(w)

            data.append({'text': ' '.join(final_words), 'intent': intent, 'group': text})

    # "unknown": random letter strings, so gibberish is rejected instead of being forced into an intent.
    letters = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(GIBBERISH_N):
        words = [''.join(random.choice(letters) for _ in range(random.randint(3, 7)))
                 for _ in range(random.randint(1, 3))]
        data.append({'text': ' '.join(words), 'intent': 'unknown', 'group': f'gibberish-{i}'})

    print(f"Generated {len(data)} training samples from {len(base_data)} seed phrases.")
    return data


GIBBERISH_N = 150
METRICS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'artifacts', 'intent_metrics.json')


def evaluate(data, n_splits=5):
    """Grouped K-fold: all typo variants of a seed phrase sit in the same fold, so the score
    measures generalisation to unseen phrasings, not memorised duplicates."""
    import json
    from sklearn.model_selection import GroupKFold
    from sklearn.metrics import accuracy_score, classification_report, f1_score
    from hishab.ml_engine import IntentClassifier
    texts = [d['text'] for d in data]
    labels = [d['intent'] for d in data]
    groups = [d['group'] for d in data]
    y_true, y_pred = [], []
    for tr, te in GroupKFold(n_splits=n_splits).split(texts, labels, groups):
        clf = IntentClassifier.__new__(IntentClassifier)
        IntentClassifier.__init__(clf, load=False)
        clf.pipeline.fit([texts[i] for i in tr], [labels[i] for i in tr])
        y_true += [labels[i] for i in te]
        y_pred += list(clf.pipeline.predict([texts[i] for i in te]))
    report = classification_report(y_true, y_pred, digits=3, output_dict=True, zero_division=0)
    metrics = {
        "method": f"GroupKFold(n_splits={n_splits}) by seed phrase; typo variants never cross folds",
        "n_samples": len(data),
        "n_groups": len(set(groups)),
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "macro_f1": round(f1_score(y_true, y_pred, average='macro'), 4),
        "per_class_f1": {k: round(v['f1-score'], 4) for k, v in report.items() if isinstance(v, dict) and k not in ('macro avg', 'weighted avg')},
    }
    print(classification_report(y_true, y_pred, digits=3, zero_division=0))
    os.makedirs(os.path.dirname(METRICS_PATH), exist_ok=True)
    with open(METRICS_PATH, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"Saved grouped CV metrics to {METRICS_PATH}")
    return metrics


if __name__ == "__main__":
    print("Generating dataset...")
    data = generate_data()
    print("Grouped cross-validation (seed phrase held out):")
    evaluate(data)
    print("Training final ML model on all data...")
    train_model(data)
    print("Training completed.")
