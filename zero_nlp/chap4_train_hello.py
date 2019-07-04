# coding: utf-8
from util import preprocess, create_contexts_target
from dataset import ptb
from trainers import Trainer
from cbow import CBOW
from optimizers import Adam

if __name__ == '__main__':

    window_size = 1
    hidden_size = 5
    batch_size = 3
    max_epoch = 1000

    text = 'You say goodbye and I say hello.'
    corpus, word_to_id, id_to_word = preprocess(text)
    vocab_size = len(word_to_id)
    contexts, target = create_contexts_target(corpus, window_size=window_size)

    # モデル
    model = CBOW(vocab_size, hidden_size, window_size, corpus)
    optimizer = Adam()

    # 学習
    trainer = Trainer(model, optimizer)
    trainer.fit(contexts, target, max_epoch=max_epoch, batch_size=batch_size)

    # plot
    trainer.plot('chap4_hello.png')

    # 単語の分散表現print
    for word, word_id in word_to_id.items():
        print('{0} {1}'.format(word, model.word_vecs[word_id]))
