# lando/examples.py

# Store each example’s code as a string

ex1 = """
import nltk
nltk.download('punkt',quiet=True)
nltk.download('punkt_tab',quiet=True)
nltk.download('averaged_perceptron_tagger',quiet=True)
nltk.download('maxent_ne_chunker_tab',quiet=True)
nltk.download('words',quiet=True)
nltk.download('gutenberg',quiet=True)
nltk.download('averaged_perceptron_tagger_eng',quiet=True)

import nltk
from nltk.tokenize import word_tokenize, PunktSentenceTokenizer
from nltk import pos_tag, ne_chunk, CFG, ChartParser
from nltk.corpus import gutenberg
from nltk.stem import PorterStemmer, LancasterStemmer, RegexpStemmer, SnowballStemmer

# load text
with open("drive/MyDrive/corpus (1).txt") as f:
  text = f.read()

# sentence and word tokenization
sentences = PunktSentenceTokenizer().tokenize(text)
words = word_tokenize(sentences[0])
print("\n sentence tokenization: \n", sentences, "\n")
print("\n word tokenization: \n", words, "\n")

# POS tagging and ne chunks
ptags = pos_tag(words)
print("\n POS tagging: \n", ptags, "\n")
ne_tags = ne_chunk(ptags)
print("\n NE tagging: \n", ne_tags, "\n")

# stemming
stemmers = {
  "Porter": PorterStemmer(),
  "Lancaster": LancasterStemmer(),
  "Regexp": RegexpStemmer('ing$|s$|e$|able$'), 
  "Snowball": SnowballStemmer('english') 
}
sample = ['running', 'jumps', 'easily', 'fairly', 'happiness'] 
print("Stemming examples:")
for word in sample:
  print(f"{word:10} ->", " , ".join(f"{k}: {s.stem(word)}" for k,s in stemmers.items()))
"""

ex2 = """
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from math import sqrt
import re

# --- Download required NLTK data ---
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# --- Load dataset and clean text ---
df = pd.read_excel('drive/MyDrive/SASTRA University (1).xlsx')

def clean_text(text):
    text = re.sub(r'[^A-Za-z\s]','',str(text))
    text = re.sub(r'\s+',' ',text)
    return text.lower()

# Fix: Correctly iterate over DataFrame content
reviews = [clean_text(t).lower() for t in df.astype(str).values.flatten()]

# --- Tokenize and remove stopwords ---
stops = set(stopwords.words('english'))
words = [w for r in reviews for w in nltk.word_tokenize(r) if w not in stops]

# --- Frequency and bigram calculation ---
word_freq = FreqDist(words)
bigrams = list(nltk.bigrams(words))
bigram_freq = FreqDist(bigrams)
N = len(words)

# --- Compute t-score and chi-square ---
t_scores, chi_sq = {}, {}
for (w1, w2), obs in bigram_freq.items():
    if obs < 4:
        continue
    exp = (word_freq[w1] * word_freq[w2]) / N
    t_scores[(w1, w2)] = (obs - exp) / sqrt(obs)
    chi_sq[(w1, w2)] = (obs - exp) ** 2 / exp

# --- Filter significant bigrams ---
crit = float(input("enter critical value: "))
sig_t = {b: s for b, s in t_scores.items() if s > crit} # default 2 for t test
sig_chi = {b: s for b, s in chi_sq.items() if s > crit} # default 3.841 for chi test

# --- Display results with collocation status ---
print("\n--- Collocation Results ---")

print(f"\nSignificant bigrams (t-score > {crit}):")
if not sig_t:
    print("No significant collocations found using t-test.")
else:
    for b, s in sig_t.items():
        print(f"{b}: t-score = {s:.2f} → Collocated ✅")

print(f"\nSignificant bigrams (chi-square > {crit}):")
if not sig_chi:
    print("No significant collocations found using chi-square test.")
else:
    for b, s in sig_chi.items():
        print(f"{b}: chi-square = {s:.2f} → Collocated ✅")
"""

ex3 = """
import pandas as pd
import re
import nltk
from nltk.classify import NaiveBayesClassifier

# --- Read & Clean Data ---
df = pd.read_csv("drive/MyDrive/Bank.csv")
df = df[~df['Word'].str.contains('Identify the sense', na=False)]
df['Class'] = df['Class'].fillna('?').str.strip()

# --- Feature Extractor ---
def feats(text):
    return {w: True for w in re.findall(r'\b\w+\b', text.lower())}

# --- Split Train/Test ---
train = [(feats(w), c) for w, c in zip(df['Word'], df['Class']) if c != '?']
test = df[df['Class'] == '?']['Word']

# --- Train Classifier ---
clf = NaiveBayesClassifier.train(train)

# --- Predict & Save Results ---
res = [{'Sentence': s, 'Predicted Sense': clf.classify(feats(s))} for s in test]
pd.DataFrame(res).to_csv("Bank_Predictions.csv", index=False)

# --- Display Output ---
print(pd.read_csv("Bank_Predictions.csv").to_string(index=False))
"""

ex4 = """
import math
from nltk.tokenize import word_tokenize
from nltk import bigrams

# --- Load Corpus ---
with open('drive/MyDrive/corpus (1).txt', 'r', encoding='latin-1') as f:
    tokens = word_tokenize(f.read().lower())

# --- Count Unigrams & Bigrams ---
unigrams, bigrams_list = {}, list(bigrams(tokens))
for t in tokens: unigrams[t] = unigrams.get(t, 0) + 1
bigrams_freq = {}
for b in bigrams_list: bigrams_freq[b] = bigrams_freq.get(b, 0) + 1

# --- Inputs ---
noun = input("Enter the Noun: ").lower()
verb = input("Enter the Verb: ").lower()
prep = input("Enter the Preposition: ").lower()

# --- Probabilities ---
p_v = bigrams_freq.get((prep, verb), 0)
p_n = bigrams_freq.get((prep, noun), 0)
v, n = unigrams.get(verb, 1), unigrams.get(noun, 1)
prob_v, prob_n = p_v / v, p_n / n

# --- Smoothing & Safe Log ---
prob_v = max(prob_v, 1e-10)
prob_n = max(min(prob_n, 1 - 1e-10), 1e-10)  # keep within (0,1)
ratio = (prob_v * (1 - prob_n)) / prob_n
ratio = max(ratio, 1e-10)  # avoid log(0)
_lambda = math.log(ratio, 2)

# --- Output ---
print(f"\nP(prep|verb)={prob_v:.6f},  \nP(prep|noun)={prob_n:.6f}, \nP(noun|verb)={n/v}")
print(f"Lambda = {_lambda:.4f}")
if _lambda > 0:
    print("→ The Preposition attaches with the Verb.")
elif _lambda < 0:
    print("→ The Preposition attaches with the Noun.")
else:
    print("→ Attachment cannot be determined.")
"""

ex5 = """
import math

print("=== Trellis Algorithm (Forward–Backward) ===\n")

# --- Input HMM Parameters ---
n = int(input("Enter number of states: "))
states = [input(f"State {i+1}: ") for i in range(n)]
init = [float(input(f"P({s}) = ")) for s in states]

emissions = input("\nEmission symbols (space separated): ").split()
emit = {(i, e): float(input(f"P({e}|{states[i]}) = ")) for i in range(n) for e in emissions}

print("\nEnter transition probabilities:")
trans = {(i, j): float(input(f"P({states[j]}|{states[i]}) = ")) for i in range(n) for j in range(n)}

obs = input("\nEnter observed sequence: ").split()

# --- Forward Procedure ---
def forward():
    a = [init]
    for o in obs:
        a.append([sum(a[-1][j] * trans[j, i] * emit[i, o] for j in range(n)) for i in range(n)])
    return a

# --- Backward Procedure ---
def backward():
    b = [[1.0]*n]
    for o in reversed(obs):
        b.append([sum(b[-1][j] * trans[i, j] * emit[j, o] for j in range(n)) for i in range(n)])
    return list(reversed(b))

# --- Run Forward & Backward ---
alpha, beta = forward(), backward()

# --- Probabilities ---
P_fwd = sum(alpha[-1])
P_bwd = sum(alpha[0][i] * beta[0][i] for i in range(n))
print(f"\nForward Prob = {P_fwd:.6f}\nBackward Prob = {P_bwd:.6f}")

# --- Gamma (State Probabilities) ---
def gamma(a_t, b_t):
    tot = sum(a_t[i]*b_t[i] for i in range(n))
    return [round((a_t[i]*b_t[i])/tot, 4) for i in range(n)]

gammas = [gamma(alpha[t], beta[t]) for t in range(1, len(obs)+1)]
print("\nGamma values:")
for t, g in enumerate(gammas, 1):
    print(f"t{t}: {g}")

# --- Most Likely State Sequence ---
seq = [states[max(range(n), key=lambda i: g[i])] for g in gammas]
print("\nMost likely state sequence:\n" + " → ".join(seq))
"""

ex6 = """
# --- Simple Viterbi Algorithm (Exam-friendly) ---
print("=== Viterbi Algorithm ===\n")

# --- Input ---
n = int(input("Number of states: "))
states = [input(f"State {i+1}: ") for i in range(n)]
start = [float(input(f"Initial P({s}): ")) for s in states]

emissions = input("\nEmission symbols (space separated): ").split()
emit = [{e: float(input(f"P({e}|{s}) = ")) for e in emissions} for s in states]

print("\nEnter transition probabilities P(next|current):")
trans = [[float(input(f"P({states[j]}|{states[i]}) = ")) for j in range(n)] for i in range(n)]

obs = input("\nEnter observed sequence: ").split()
print("\nObserved sequence:", obs)

# --- Viterbi Computation ---
T = len(obs)
V = [[0]*n for _ in range(T)]
back = [[0]*n for _ in range(T)]

# Initialization
for i in range(n):
    V[0][i] = start[i] * emit[i].get(obs[0], 0)

# Recursion
for t in range(1, T):
    for j in range(n):
        probs = [V[t-1][i]*trans[i][j]*emit[j].get(obs[t], 0) for i in range(n)]
        V[t][j] = max(probs)
        back[t][j] = probs.index(V[t][j])

# Termination & Backtracking
last = max(range(n), key=lambda i: V[-1][i])
path = [last]
for t in range(T-1, 0, -1):
    path.insert(0, back[t][path[0]])

print("\nMost likely state sequence:")
print(" -> ".join(states[i] for i in path))
print(f"\nSequence Probability = {V[-1][last]:.6f}")
"""
ex7 = """
import nltk
from nltk.grammar import PCFG

# --- PCFG Grammar (from question) ---
grammar = PCFG.fromstring('
S -> NN VP [0.50] | VP NP [0.50]
NP -> NN PP [0.60] | PP NN [0.40]
VP -> VB NP [0.30] | VP NP [0.25] | VB NN [0.25] | VB PP [0.20]
PP -> P VP [0.45] | P NN [0.55]
P -> 'with' [0.75] | 'beside' [0.25]
VB -> 'play' [0.15] | 'watch' [0.20] | 'draw' [0.20] | 'enjoy' [0.15] | 'listen' [0.10] | 'admire' [0.20]
NN -> 'children' [0.15] | 'students' [0.15] | 'painting' [0.25] | 'football' [0.15] | 'cricket' [0.10] | 'friends' [0.20]
')

# --- Sentence ---
sentence = "children watch painting with students".split()

# --- CYK Algorithm with Probabilities ---
def cyk_prob(pcfg, words):
    n = len(words)
    table = [[set() for _ in range(n)] for _ in range(n)]

    # Fill diagonal (terminals)
    for i, w in enumerate(words):
        for prod in pcfg.productions(rhs=w):
            table[i][i].add((prod.lhs(), prod.prob()))

    # Fill table
    for l in range(2, n+1):
        for i in range(n-l+1):
            j = i+l-1
            for k in range(i, j):
                for A, pA in table[i][k]:
                    for B, pB in table[k+1][j]:
                        for prod in pcfg.productions():
                            if prod.rhs() == (A, B):
                                table[i][j].add((prod.lhs(), prod.prob() * pA * pB))

    # Display CYK Table
    print("\n--- CYK Table (Non-terminals & Probabilities) ---")
    for i in range(n):
        for j in range(n):
            if table[i][j]:
                print(f"[{i},{j}] -> {table[i][j]}")

    # Inside probability (S in last cell)
    for lhs, p in table[0][n-1]:
        if lhs == pcfg.start():
            return p
    return 0.0

# --- Run CYK ---
prob = cyk_prob(grammar, sentence)
print(f"\nInside Probability of '{' '.join(sentence)}': {prob:.6f}")

# --- Grammar Check ---
if prob > 0:
    print("✅ The sequence is grammatically correct according to the PCFG.")
else:
    print("❌ The sequence is NOT grammatically correct according to the PCFG.")

# --- Parse Tree using Viterbi Parser ---
print("\n--- Most Probable Parse Tree ---")
parser = nltk.ViterbiParser(grammar)
for tree in parser.parse(sentence):
    print(tree)
    tree.pretty_print()
    break
"""

ex8 = """
import pandas as pd
import nltk
nltk.download('stopwords',quiet=True)
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re, tensorflow as tf
from tensorflow.keras import layers, models

# --- Clean function ---
def clean_tweet(text, stop_rm=True, stem=False):
    if not isinstance(text, str): return ""
    text = re.sub(r'http\S+|@\w+|#|\W', ' ', text.lower())
    words = text.split()
    if stop_rm:
        sw = set(stopwords.words('english')) | {'rt','amp','im','get','got','like','would'}
        words = [w for w in words if w not in sw and len(w) > 2]
    if stem:
        ps = PorterStemmer()
        words = [ps.stem(w) for w in words]
    return ' '.join(words)

# --- Load + preprocess ---
data = pd.read_csv('drive/MyDrive/TweetSentimentAnalysis.csv', encoding='latin')[['text', 'sentiment']]
data['clean'] = data['text'].apply(clean_tweet)
X_train, X_test, y_train, y_test = train_test_split(
    data['clean'], LabelEncoder().fit_transform(data['sentiment']),
    test_size=0.25, random_state=42)

# --- TF-IDF ---
tfidf = TfidfVectorizer(max_features=5000)
X_train = tfidf.fit_transform(X_train).toarray()
X_test = tfidf.transform(X_test).toarray()

# --- Model ---
model = models.Sequential([
    layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    layers.Dropout(0.5),
    layers.Dense(64, activation='relu'),
    layers.Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=5, batch_size=16, verbose=1)

print("Test Accuracy:", model.evaluate(X_test, y_test)[1])
"""

ex9 = """
from gensim.models import Word2Vec
import gensim,nltk
from nltk.tokenize import sent_tokenize,word_tokenize

data = [
    'Alice Wonderland is the main character of the story',
    'Wonderland Alice discovered a magical new world',
    'Alice from Wonderland had amazing adventures daily',
    'Wonderland was explored thoroughly by curious Alice',
    'Alice Wonderland met strange creatures in Wonderland',
    'The adventures of Alice in Wonderland are famous',
    'Alice explored every part of magical Wonderland',
    'Wonderland fascinated young Alice from the start',
    'Alice Wonderland attended tea parties in Wonderland',
    'Throughout Wonderland Alice became quite famous',
    'Alice journey through Wonderland was spectacular',
    'Wonderland magic transformed Alice perspective',
    'Alice of Wonderland challenged the Queen wisely',
    'Wonderland creatures helped Alice find her way',
    'Alice memories of Wonderland lasted forever',
    'Wonderland adventures made Alice more confident',
    'Alice returned from Wonderle with open arms',
    'Alice love for Wonderlanand much wiser',
    'Wonderland lessons stayed with Alice always',
    'Alice courage in Wonderland was remarkable',
    'Wonderland experiences shaped Alice character',
    'Alice became a legend throughout Wonderland',
    'Wonderland welcomed Alicd never faded',
    'Wonderland without Alice seems incomplete',
    'Alice and Wonderland are forever linked',

    # Machines sentences (25 sentences - completely separate context)
    'Industrial machines manufacture products efficiently',
    'Computer machines process data very quickly',
    'Digital machines perform calculations accurately',
    'Automated machines assemble components precisely',
    'Robotic machines handle dangerous tasks safely',
    'Modern machines improve productivity significantly',
    'Advanced machines require regular maintenance',
    'Electronic machines consume electrical power',
    'Manufacturing machines operate continuously',
    'Precision machines create tiny components',
    'Heavy machines move large materials easily',
    'Smart machines learn from their experiences',
    'Complex machines have many moving parts',
    'Technical machines need expert operators',
    'Innovative machines solve difficult problems',
    'Powerful machines generate substantial force',
    'Reliable machines work for long periods',
    'Sophisticated machines use advanced technology',
    'Mechanical machines convert energy to motion',
    'Efficient machines reduce energy consumption',
    'Specialized machines perform specific functions',
    'High-tech machines incorporate computers',
    'Productive machines increase output rates',
    'Durable machines withstand harsh conditions',
    'Versatile machines handle multiple tasks'
]

# Tokenize the data
tokenized_data = [sentence.split() for sentence in data]

# Then use tokenized_data for training
model1 = gensim.models.Word2Vec(sentences=tokenized_data, min_count=1, vector_size=100, window=5, sg=0,epochs=30)
model2 = gensim.models.Word2Vec(sentences=tokenized_data, min_count=1, vector_size=100, window=5, sg=1,epochs=30)
print("=== SIMILARITY RESULTS ===")

# Similarity between Alice and Wonderland (using words present in the training data)
a_cbow = model1.wv.similarity('Alice', 'Wonderland')
a_skipgram = model2.wv.similarity('Alice', 'Wonderland')

print(f"\nAlice - Wonderland Similarity:")
print(f"CBOW:      {a_cbow:.4f}")
print(f"Skip-gram: {a_skipgram:.4f}")

# You can also try other words from your corpus, for example:
m_cbow = model1.wv.similarity('Industrial', 'machines')
m_skipgram = model2.wv.similarity('Industrial', 'machines')

print(f"\nIndustrial - machines Similarity:")
print(f"CBOW:      {m_cbow:.4f}")
print(f"Skip-gram: {m_skipgram:.4f}")
"""

ex10 = """
import numpy as np, pandas as pd
from tensorflow import keras

# --- Load data ---
eng, tam = [], []
for ln in open('drive/MyDrive/MT Eng Tam Dataset.txt', encoding='utf-8'):
    if '\t' in ln:
        e, t = ln.strip().split('\t')[:2]
        eng.append(e); tam.append(t)
df = pd.DataFrame({'en': eng, 'ta': tam})

# --- Tokenize & pad ---
tok_en, tok_ta = [keras.preprocessing.text.Tokenizer(oov_token='<OOV>', filters='') for _ in range(2)]
tok_en.fit_on_texts(df.en); tok_ta.fit_on_texts(df.ta)
X = tok_en.texts_to_sequences(df.en); Y = tok_ta.texts_to_sequences(df.ta)
max_len = max(max(map(len, X)), max(map(len, Y)))
X = keras.preprocessing.sequence.pad_sequences(X, maxlen=max_len, padding='post')
Y = keras.preprocessing.sequence.pad_sequences(Y, maxlen=max_len, padding='post')
Y = np.expand_dims(Y, -1)

# --- Model ---
model = keras.Sequential([
    keras.layers.Embedding(len(tok_en.word_index)+1, 64, input_length=max_len),
    keras.layers.SimpleRNN(128, return_sequences=True),
    keras.layers.TimeDistributed(keras.layers.Dense(len(tok_ta.word_index)+1, activation='softmax'))
])
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X, Y, epochs=100, batch_size=64, verbose=1)

# --- Translate ---
def translate(s):
    seq = tok_en.texts_to_sequences([s])
    seq = keras.preprocessing.sequence.pad_sequences(seq, maxlen=max_len, padding='post')
    pred = np.argmax(model.predict(seq, verbose=0)[0], axis=-1)
    return ' '.join(tok_ta.index_word.get(i, '') for i in pred if i>0)

print("Tamil:", translate(input("Enter English: ")))
"""

ex11 = """
import string
import numpy as np
import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dropout, Dense

# ---- Load headlines ----
df = pd.read_csv('drive/MyDrive/ArticlesApril2017.csv')
lines = [h for h in df.headline.astype(str).tolist() if h != "Unknown"]

# ---- Simple cleaning ----
def clean(s):
    s = "".join(ch for ch in s if ch not in string.punctuation).lower()
    return s.encode('utf8').decode('ascii', 'ignore')

corpus = [clean(s) for s in lines]

# ---- Tokenize & create n-gram sequences ----
tokenizer = Tokenizer()
tokenizer.fit_on_texts(corpus)
total_words = len(tokenizer.word_index) + 1

sequences = []
for line in corpus:
    token_ids = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_ids)):
        sequences.append(token_ids[: i + 1])

# ---- Prepare predictors (X) and one-hot labels (y) ----
max_len = max(len(seq) for seq in sequences)
sequences = pad_sequences(sequences, maxlen=max_len, padding='pre')
X, y = sequences[:, :-1], sequences[:, -1]
y = to_categorical(y, num_classes=total_words)

# ---- Model ----
def build_model(total_words, input_len, embed_dim=10, lstm_units=100):
    model = Sequential([
        Embedding(input_dim=total_words, output_dim=embed_dim, input_length=input_len),
        LSTM(lstm_units),
        Dropout(0.2),
        Dense(total_words, activation='softmax')
    ])
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model

model = build_model(total_words, X.shape[1])
model.summary()

# ---- Train (adjust epochs for real runs) ----
model.fit(X, y, epochs=30, batch_size=128, verbose=2)

# ---- Fast generator (greedy) ----
index_to_word = {i: w for w, i in tokenizer.word_index.items()}

def generate_text(seed, next_words=5):
    out = seed
    for _ in range(next_words):
        seq = tokenizer.texts_to_sequences([out])[0]
        seq = pad_sequences([seq], maxlen=X.shape[1], padding='pre')
        pred = model.predict(seq, verbose=0)[0]
        next_id = int(np.argmax(pred))
        next_word = index_to_word.get(next_id, '')
        if not next_word: break
        out += " " + next_word
    return out.title()

# ---- Examples ----
print("Generated:", generate_text("united states", 5))
print("Generated:", generate_text("president trump", 4))
"""

