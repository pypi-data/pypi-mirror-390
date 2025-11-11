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