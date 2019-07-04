# coding: utf-8

import pickle
from util import most_similar, analogy

if __name__ == '__main__':
    fname = 'pickle/cbow_params.pkl'
    with open(fname, 'rb') as f:
        params = pickle.load(f)
    word_vecs = params['word_vec']
    word_to_id = params['word_to_id']
    id_to_word = params['id_to_word']

    # most similar
    querys = ['you', 'year', 'car', 'toyota', 'cat', 'music']
    for query in querys:
        most_similar(query, word_to_id, id_to_word, word_vecs, top=5)

    # analogy
    print('-'*50)
    analogy('king', 'man', 'queen',  word_to_id, id_to_word, word_vecs)
    analogy('take', 'took', 'go',  word_to_id, id_to_word, word_vecs)
    analogy('car', 'cars', 'child',  word_to_id, id_to_word, word_vecs)
    analogy('good', 'better', 'bad',  word_to_id, id_to_word, word_vecs, top=10)
