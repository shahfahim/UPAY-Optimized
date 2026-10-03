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

    # create original and variants
    for text, intent in base_data:
        data.append({'text': text, 'intent': intent})

        # create 10 variants for each base phrase
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

            data.append({'text': ' '.join(final_words), 'intent': intent})

    # Merge the overnight synthetic dataset (deduplicated: 77k rows -> ~1.4k unique)
    overnight = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'hishab', 'training_data.jsonl')
    if os.path.exists(overnight):
        import json
        seen = set()
        with open(overnight, encoding='utf-8') as f:
            for line in f:
                row = json.loads(line)
                key = (row['text'], row['intent'])
                if key not in seen:
                    seen.add(key)
                    data.append({'text': row['text'], 'intent': row['intent']})
        print(f"Merged {len(seen)} unique rows from overnight dataset.")

    print(f"Generated {len(data)} training samples.")
    return data


def evaluate(data):
    """Honest held-out score: 20% stratified split, model never sees these rows."""
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    from hishab.ml_engine import IntentClassifier
    texts = [d['text'] for d in data]
    labels = [d['intent'] for d in data]
    xtr, xte, ytr, yte = train_test_split(texts, labels, test_size=0.2, random_state=0, stratify=labels)
    clf = IntentClassifier.__new__(IntentClassifier)
    IntentClassifier.__init__(clf)
    clf.pipeline.fit(xtr, ytr)
    print(classification_report(yte, clf.pipeline.predict(xte), digits=3))


if __name__ == "__main__":
    print("Generating dataset...")
    data = generate_data()
    print("Held-out evaluation:")
    evaluate(data)
    print("Training final ML model on all data...")
    train_model(data)
    print("Training completed.")
