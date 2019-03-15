# coding: utf-8
import pickle
import numpy as np

filepath = 'dataset/ptb/'
infnames = {'train': 'ptb.train.txt',
            'test': 'ptb.test.txt',
            'valid': 'ptb.valid.txt'}
npfnames = {'train': 'ptb.train.npy',
             'test': 'ptb.test.npy',
             'valid': 'ptb.valid.npy'}
vocabfname = 'dataset/ptb/ptb.vocab.pkl'

def save_vocab():
    trainfname = filepath + infnames['train']
    with open(trainfname, 'r', encoding='utf-8') as inf:
        words = inf.read().replace('\n', '<eos>').strip().split()

    word_to_id = {}
    id_to_word = {}
    for word in words:
        if not word in word_to_id:
            word_id = len(word_to_id)
            word_to_id[word] = word_id
            id_to_word[word_id] = word

    with open(vocabfname, 'wb') as vf:
        pickle.dump((word_to_id, id_to_word), vf)

def load_vocab():

    with open(vocabfname, 'rb') as vf:
        word_to_id, id_to_word = pickle.load(vf)
    return word_to_id, id_to_word

def save_corpus():

    word_to_id, _ = load_vocab()

    for dt in infnames:
        infn = filepath + infnames[dt]
        with open(infn, 'r', encoding='utf-8') as inf:
            words = inf.read().replace('\n', '<eos>').strip().split()
        corpus = np.array([word_to_id[w] for w in words])

        outfn = filepath + npfnames[dt]
        np.save(outfn, corpus)

def load_data(data_type='train'):
    '''data_type: train, test, valid(val)
    '''
    if data_type == 'val':
        data_type = 'valid'
    word_to_id, id_to_word = load_vocab()

    fn = filepath + npfnames[data_type]
    corpus = np.load(fn)

    return corpus, word_to_id, id_to_word

if __name__ == '__main__':

    #save_vocab()
    #word_to_id, id_to_word = load_vocab()
    #save_corpus()

    for dt in npfnames.keys():
        corpus, word_to_id, id_to_word = load_data(data_type=dt)

        print('[{0} corpus size: {1}'.format(dt, len(corpus)))
        print('[{0} corpus[:30]: {1}'.format(dt, corpus[:30]))

        print('id_to_word[0]: {0}'.format(id_to_word[0]))
        print('id_to_word[1]: {0}'.format(id_to_word[1]))
        print('id_to_word[2]: {0}'.format(id_to_word[2]))
        print("word_to_id['car']: {0}".format(word_to_id['car']))
        print("word_to_id['happy']: {0}".format(word_to_id['happy']))
        print("word_to_id['lexus']: {0}".format(word_to_id['lexus']))


