import json
import os
import random
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from nltk.corpus import wordnet
import nltk
from sentence_transformers import SentenceTransformer, util

nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

# --- Load models once ---
print("⏳ Loading advanced models (Pegasus + Semantic Encoder)...")
tokenizer = AutoTokenizer.from_pretrained("tuner007/pegasus_paraphrase")
model = AutoModelForSeq2SeqLM.from_pretrained("tuner007/pegasus_paraphrase")
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')


def synonym_replace(text):
    words = text.split()
    new_words = []
    for w in words:
        syns = wordnet.synsets(w)
        if syns:
            lemmas = [l.name().replace("_", " ") for l in syns[0].lemmas() if l.name().lower() != w.lower()]
            new_words.append(random.choice(lemmas) if lemmas else w)
        else:
            new_words.append(w)
    return " ".join(new_words)


def paraphrase_text(text):
    try:
        torch.manual_seed(random.randint(0, 99999)) 
        inputs = tokenizer(
            f"paraphrase: {text}",
            truncation=True,
            padding="longest",
            return_tensors="pt"
        )
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=80,
                do_sample=True,        
                top_k=50,
                top_p=0.95,
                temperature=1.3,
                num_return_sequences=5  
            )

        candidates = [tokenizer.decode(o, skip_special_tokens=True).strip() for o in outputs]
        orig_emb = semantic_model.encode(text, convert_to_tensor=True)
        best_para, best_sim = text, 0

        for c in candidates:
            if c.lower() == text.lower() or len(c.split()) <= 3:
                continue
            cand_emb = semantic_model.encode(c, convert_to_tensor=True)
            sim = util.cos_sim(orig_emb, cand_emb).item()
            if 0.8 <= sim < 0.98:
                best_para, best_sim = c, sim
                break
            elif sim > best_sim:
                best_para, best_sim = c, sim

        if best_sim < 0.7:
            best_para = synonym_replace(text)

        return best_para
    except Exception:
        return synonym_replace(text)



def load_and_paraphrase_quiz():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # file_path = os.path.join(base_dir, '../data/learner_quiz.json')
    file_path = os.path.join(base_dir, "..", "database", "learner_quiz.json")
    # print("done")

    with open(file_path, 'r') as f:
        quiz_data = json.load(f)

    new_data = {"questions": []}
    for q in quiz_data["questions"]:
        new_q = {
            "question": paraphrase_text(q["question"]),
            "options": [paraphrase_text(opt) for opt in q["options"]],
            "weights": q["weights"]
        }
        new_data["questions"].append(new_q)

    return new_data


def evaluate_learner_type(quiz_data, answers):
    scores = {"visual": 0, "auditory": 0, "kinesthetic": 0}

    for i, q in enumerate(quiz_data["questions"]):
        if i < len(answers):
            ans = answers[i]
            if ans == 1:
                scores["visual"] += q["weights"]["visual"]
            elif ans == 2:
                scores["auditory"] += q["weights"]["auditory"]
            else:
                scores["kinesthetic"] += q["weights"]["kinesthetic"]

    learner_type = max(scores, key=scores.get)
    return {
        "visual": scores["visual"],
        "auditory": scores["auditory"],
        "kinesthetic": scores["kinesthetic"],
        "learner_type": learner_type
    }