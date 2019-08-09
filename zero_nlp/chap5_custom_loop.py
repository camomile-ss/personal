# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
from simple_rnnlm import SimpleRnnlm
from optimizers import SGD
from dataset import ptb

if __name__ == '__main__':
    # ハイパーパラメータ
    batch_size = 10
    wordvec_size = 100
    hidden_size = 100
    time_size = 5
    lr = 0.1
    max_epoch = 100

    # 学習データ
    corpus, word_to_id, id_to_word = ptb.load_data('train')
    corpus_size = 1000  # データセットを小さくする
    corpus = corpus[:corpus_size]
    vocab_size = int(max(corpus) + 1)

    xs = corpus[:-1]  # 入力
    ts = corpus[1:]  # 教師
    data_size = len(xs)
    print('corpus size: {0}, vocabulary size: {1}'.format(corpus_size, vocab_size))

    #
    max_iters = data_size // (batch_size * time_size)
    time_idx = 0
    total_loss = 0
    loss_count = 0
    ppl_list = []

    # モデル
    model = SimpleRnnlm(vocab_size, wordvec_size, hidden_size)
    optimizer = SGD(lr)

    # ミニバッチの各サンプル読込開始位置を計算
    jump = (corpus_size-1) // batch_size
    offsets = [i * jump for i in range(batch_size)]

    for epoch in range(max_epoch):
        for iter in range(max_iters):

            # ミニバッチ取得
            batch_x = np.empty((batch_size, time_size), dtype='i')
            batch_t = np.empty((batch_size, time_size), dtype='i')
            for t in range(time_size):
                for i, offset in enumerate(offsets):
                    batch_x[i, t] = xs[(offset + time_idx) % data_size]
                    batch_t[i, t] = ts[(offset + time_idx) % data_size]
                time_idx += 1

            # 学習
            loss = model.forward(batch_x, batch_t)
            model.backward()
            optimizer.update(model.params, model.grads)
            total_loss += loss
            loss_count += 1

        # perplexity の評価
        ppl = np.exp(total_loss / loss_count)
        print('| epoch {0} | perplexity {1:1.2f}'.format(epoch+1, ppl))
        ppl_list.append(float(ppl))
        total_loss, loss_count = 0, 0

    # グラフ
    x = np.arange(len(ppl_list))
    plt.plot(x, ppl_list, label='train')
    plt.xlabel('epochs')
    plt.ylabel('perplexity')
    plt.savefig('chap5.png')
