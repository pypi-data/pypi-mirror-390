# Auto-generated from notebook: Assignment5_(1).ipynb
# a. Data Preparation
import pandas as pd
from tensorflow.keras.preprocessing import text, sequence
from tensorflow.keras.utils import to_categorical, pad_sequences
import numpy as np
#for building CBOW model
import tensorflow.keras.backend as K
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, Lambda

from sklearn.metrics.pairwise import euclidean_distances

data = [
    "Natural Language Processing is a field of Artificial Intelligence.",
    "Word embeddings help computers understand human language.",
    "The CBOW model is a part of Word2Vec technique.",
    "CBOW predicts the target word using surrounding context words.",
    "Skip Gram is another architecture of Word2Vec.",
    "Word2Vec is widely used in NLP applications.",
    "Embedding layers in deep learning are used to represent words.",
    "CBOW is faster and works better with frequent words."
]

#Tokenize and build vocabulary
tokenizer = text.Tokenizer()
tokenizer.fit_on_texts(data)

word2id = tokenizer.word_index
word2id['PAD'] = 0   # padding token
id2word = {v: k for k, v in word2id.items()}

# Convert sentences into sequences of IDs
wids = [[word2id[w] for w in text.text_to_word_sequence(doc)] for doc in data]

vocab_size = len(word2id)
embed_size = 100
window_size = 2  # context window size

print("Vocabulary Size:", vocab_size)
print("Sample Vocabulary:", list(word2id.items())[:10])

# Generate training data (context -> target)
def generate_context_word_pairs(corpus, window_size, vocab_size):
    context_length = window_size * 2
    for words in corpus:
        sentence_length = len(words)
        for index, word in enumerate(words):
            context_words = []
            label_word = []
            start = index - window_size
            end = index + window_size + 1

            # pick context (excluding target word)
            context_words.append([words[i]
                                  for i in range(start, end)
                                  if 0 <= i < sentence_length and i != index])
            label_word.append(word)

            # pad context & one-hot target
            x = pad_sequences(context_words, maxlen=context_length)
            y = to_categorical(label_word, vocab_size)
            yield (x, y)

# Show few examples
i = 0
for x, y in generate_context_word_pairs(wids, window_size, vocab_size):
    if 0 not in x[0]:  # skip padded ones
        print("Context (X):", [id2word[w] for w in x[0]], "-> Target (Y):", id2word[np.argmax(y[0])])
        i += 1
        if i == 5:
            break

#Build CBOW model
cbow = Sequential()
cbow.add(Embedding(input_dim=vocab_size, output_dim=embed_size, input_shape=(window_size*2,)))
cbow.add(Lambda(lambda x: K.mean(x, axis=1), output_shape=(embed_size,)))
cbow.add(Dense(vocab_size, activation="softmax"))
cbow.compile(loss="categorical_crossentropy", optimizer="adam")

print(cbow.summary())

#Train Model
for epoch in range(1, 10):  # run fewer epochs for demo
    loss = 0.
    i = 0
    for x, y in generate_context_word_pairs(wids, window_size, vocab_size):
        loss += cbow.train_on_batch(x, y)
        i += 1
    print("Epoch:", epoch, "Loss:", loss)

#Save trained word embeddings to a file
weights = cbow.get_weights()[0]
weights = weights[1:]
print(weights.shape)

pd.DataFrame(weights, index=list(id2word.values())[1:]).head()

#Find similar words using Euclidean distance
distance_matrix = euclidean_distances(weights)

similar_words = {
    search: [id2word[idx] for idx in distance_matrix[word2id[search]-1].argsort()[1:6]+1]
    for search in ["deep", "cbow"]
}

print("Similar Words:", similar_words)
