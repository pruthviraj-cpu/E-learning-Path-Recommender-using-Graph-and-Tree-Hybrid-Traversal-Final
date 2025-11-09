# quiz_logic.py
import json, os, random, torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, util
from nltk.corpus import wordnet
import nltk

nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

tokenizer = AutoTokenizer.from_pretrained("tuner007/pegasus_paraphrase", use_fast=False)
pegasus = AutoModelForSeq2SeqLM.from_pretrained("tuner007/pegasus_paraphrase")
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

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
        inputs = tokenizer(f"paraphrase: {text}", truncation=True, padding="longest", return_tensors="pt")
        with torch.no_grad():
            outputs = pegasus.generate(**inputs, max_new_tokens=80, num_beams=5, num_return_sequences=5)
        candidates = [tokenizer.decode(o, skip_special_tokens=True).strip() for o in outputs]

        orig_emb = semantic_model.encode(text, convert_to_tensor=True)
        best_para, best_sim = text, 0
        for c in candidates:
            if c.lower() == text.lower() or len(c.split()) <= 3:
                continue
            cand_emb = semantic_model.encode(c, convert_to_tensor=True)
            sim = util.cos_sim(orig_emb, cand_emb).item()
            if 0.85 <= sim < 0.98:
                best_para, best_sim = c, sim
                break
            elif sim > best_sim:
                best_para, best_sim = c, sim
        if best_sim < 0.75:
            best_para = synonym_replace(text)
        return best_para
    except Exception:
        return synonym_replace(text)

def load_questions(domain_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.abspath(os.path.join(base_dir, "..", "database", "learner_level.json"))
    data = json.load(open(data_path))
    # print("done") #for debugging
    domain_data = next((d for d in data["domains"] if d["name"].lower() == domain_name.lower()), None)
    if not domain_data:
        return None

    all_questions = []
    for level, qs in domain_data["levels"].items():
        for q in qs:
            q["level"] = level
            all_questions.append(q)
    # random.shuffle(all_questions)
    return all_questions[:6]