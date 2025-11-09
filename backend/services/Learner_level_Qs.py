# this is code of onboarding provided by Aryan as it is keep for reference then will delete it 
import json
import os
import random
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, util
from nltk.corpus import wordnet
import nltk

# --- Setup ---
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

# We are using paraphrasing models (Pegasus + Semantic Similarity)
tokenizer = AutoTokenizer.from_pretrained("tuner007/pegasus_paraphrase",use_fast=False)
pegasus = AutoModelForSeq2SeqLM.from_pretrained("tuner007/pegasus_paraphrase")
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Helper: synonym fallback ---
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

# --- Helper: Pegasus paraphrasing ---
def paraphrase_text(text):
    try:
        inputs = tokenizer(f"paraphrase: {text}", truncation=True, padding="longest", return_tensors="pt")
        with torch.no_grad():
            outputs = pegasus.generate(
                **inputs,
                max_new_tokens=80,
                num_beams=5,
                num_return_sequences=5,
                temperature=1.1,
                top_p=0.9,
                do_sample=True
            )
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

# --- Load learner-level JSON ---
base_dir = os.path.dirname(os.path.abspath(__file__))
# file_path = os.path.join(base_dir, "learner_level.json")
data_path = os.path.abspath(os.path.join(base_dir, "..", "database", "learner_level.json"))
data = json.load(open(data_path))

# with open(data, "r") as f:
#     data = json.load(f)

# --- Domain selection ---
domain = input("Choose your domain (Data Science / Web Development): ").strip()
domain_data = next((d for d in data["domains"] if d["name"].lower() == domain.lower()), None)

if not domain_data:
    print("Invalid domain! Exiting.")
    exit()

# --- Collect and randomize all domain questions ---
all_questions = []
for level, qs in domain_data["levels"].items():
    for q in qs:
        q["level"] = level
        all_questions.append(q)

random.shuffle(all_questions)
selected_questions = all_questions[:6]  # only 6 questions per quiz to ensure equal level distribution

score = 0

print("\nAdaptive Quiz Starting...\n")

# --- Ask rephrased questions ---
for idx, q in enumerate(selected_questions, start=1):
    q_text = paraphrase_text(q["text"])
    print(f"\nQ{idx}. {q_text}")

    rephrased_options = {}
    for key, val in q["options"].items():
        rephrased_options[key] = paraphrase_text(val)
        print(f"{key}. {rephrased_options[key]}")

    ans = input("Your choice (a/b/c/d): ").strip().lower()
    if ans == q["correct_answer"].lower():
        score += 1

# --- Determine learner level ---
if score >= 4:
    level = "Advanced"
elif (score >= 2 and score < 4):
    level = "Intermediate"
else:
    level = "Begginer"

print("\n Results")
print(f"Your score: {score}/6") # Keep this command optional and uncomment if needed
print(f"You are an {domain} {level} learner!")