# =============================================================
# CBOW (Continuous Bag of Words) — Word Embedding Model (Keras)
# Sequential version — matches your MNIST FFNN syntax style
# =============================================================
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical

# --- b) PREPARE TEXT DATA ---
corpus = [
    """The speed of transmission is an important point of difference between the two viruses. 
    Influenza has a shorter median incubation period (the time from infection to appearance of symptoms) 
    and a shorter serial interval (the time between successive cases) than COVID-19 virus. 
    The serial interval for COVID-19 virus is estimated to be 5-6 days, while for influenza virus, 
    the serial interval is 3 days. This means that influenza can spread faster than COVID-19. 

    Further, transmission in the first 3-5 days of illness, or potentially pre-symptomatic transmission – 
    transmission of the virus before the appearance of symptoms – is a major driver of transmission for influenza. 
    In contrast, while we are learning that there are people who can shed COVID-19 virus 24-48 hours prior to symptom onset, 
    at present, this does not appear to be a major driver of transmission. 

    The reproductive number – the number of secondary infections generated from one infected individual – 
    is understood to be between 2 and 2.5 for COVID-19 virus, higher than for influenza. 
    However, estimates for both COVID-19 and influenza viruses are very context and time-specific, 
    making direct comparisons more difficult."""
]

# Tokenize → integer sequences
tokenizer = Tokenizer()
tokenizer.fit_on_texts(corpus)
sequences = tokenizer.texts_to_sequences(corpus)
vocab_size = len(tokenizer.word_index) + 1  # +1 for padding

print("✅ Loaded Corpus & Vocabulary")
print("Vocab Size:", vocab_size)
print("Example Sequence (first 30 tokens):", sequences[0][:30])

# --- c) BUILD CONTEXT–TARGET PAIRS ---
window = 2
contexts, targets = [], []

for seq in sequences:
    for i in range(window, len(seq) - window):
        ctx = seq[i - window:i] + seq[i + 1:i + window + 1]
        contexts.append(ctx)
        targets.append(seq[i])

x_train = np.array(contexts)
y_train = to_categorical(targets, num_classes=vocab_size)

print("\n✅ Training Data Shapes")
print("x_train:", x_train.shape)
print("y_train:", y_train.shape)

# --- d) DEFINE CBOW MODEL ---
embedding_dim = 40  # <--- changed from 10 to 40

model = keras.Sequential([
    layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=2 * window),
    layers.GlobalAveragePooling1D(),
    layers.Dense(vocab_size, activation="softmax")
])

model.summary()

# --- e) COMPILE MODEL ---
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# --- f) TRAIN MODEL ---
history = model.fit(
    x_train, y_train,
    epochs=100,
    batch_size=8,
    validation_split=0.1,
    verbose=2
)

# --- g) OPTIONAL: CHECK WORD EMBEDDINGS ---
embeddings = model.layers[0].get_weights()[0]
print("\n✅ Embedding matrix shape:", embeddings.shape)

# Example: Get embedding for a specific word
word = "virus"
word_index = tokenizer.word_index.get(word)
if word_index:
    print(f"Embedding for '{word}':\n", embeddings[word_index])
else:
    print(f"'{word}' not in vocabulary.")
