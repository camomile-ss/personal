# coding: utf-8

import pickle
from util import most_similar, analogy, analogy_text

if __name__ == '__main__':
    #fname = 'cbow_params.pkl'
    fname = 'skip_gram_params.pkl'
    with open(fname, 'rb') as f:
        params = pickle.load(f)
    word_vecs = params['word_vecs']
    word_to_id = params['word_to_id']
    id_to_word = params['id_to_word']

    # most similar
    querys = ['you', 'year', 'car', 'toyota', 'cat', 'music']
    for query in querys:
        most_similar(query, word_to_id, id_to_word, word_vecs, top=5)

    # analogy
    print('\n-' + ' (distance) ' + '-' * 46)
    analogy('king', 'man', 'queen',  word_to_id, id_to_word, word_vecs, top=30)
    analogy('take', 'took', 'go',  word_to_id, id_to_word, word_vecs)
    analogy('car', 'cars', 'child',  word_to_id, id_to_word, word_vecs, top=10)
    analogy('good', 'better', 'bad',  word_to_id, id_to_word, word_vecs, top=30)
    print('\n-' + ' (text) ' + '-' * 50)
    analogy_text('king', 'man', 'queen',  word_to_id, id_to_word, word_vecs, top=30)
    analogy_text('take', 'took', 'go',  word_to_id, id_to_word, word_vecs, top=10)
    analogy_text('car', 'cars', 'child',  word_to_id, id_to_word, word_vecs, top=30)
    analogy_text('good', 'better', 'bad',  word_to_id, id_to_word, word_vecs)
