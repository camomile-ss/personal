# coding: utf-8
from util import create_contexts_target
from dataset import ptb
from trainers import Trainer
#from cbow import CBOW
from skip_gram import SkipGram
from optimizers import Adam
import numpy as np
import pickle

if __name__ == '__main__':

    window_size = 5
    hidden_size = 100
    batch_size = 100
    max_epoch = 10

    corpus, word_to_id, id_to_word = ptb.load_data('train')
    vocab_size = len(word_to_id)
    contexts, target = create_contexts_target(corpus, window_size=window_size)

    # モデル
    #model = CBOW(vocab_size, hidden_size, window_size, corpus)
    model = SkipGram(vocab_size, hidden_size, window_size, corpus)
    optimizer = Adam()

    # 学習
    trainer = Trainer(model, optimizer)
    trainer.fit(contexts, target, max_epoch=max_epoch, batch_size=batch_size)

    # plot
    trainer.plot('chap4_ptb.png')

    # 単語の分散表現保存
    params = {}
    params['word_vecs'] = model.word_vecs.astype(np.float16)
    params['word_to_id'] = word_to_id
    params['id_to_word'] = id_to_word
    #fname = 'cbow_params.pkl'
    fname = 'skip_gram_params.pkl'
    with open(fname, 'wb') as f:
        pickle.dump(params, f, -1)
