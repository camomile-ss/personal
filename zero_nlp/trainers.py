# coding: utf-8
import sys
import numpy as np
import matplotlib.pyplot as plt
from time import time

class Trainer:
    def __init__(self, model, opt):
        self.model = model
        self.opt = opt
        self.loss_list = []
        self.eval_interval = 10

    def fit(self, x, t, max_epoch=10, batch_size=32, eval_interval=20):
        self.eval_interval = eval_interval
        it_per_epoch = - (- len(x) // batch_size)
        total_loss = []  # print用

        start_time = time()
        for e in range(max_epoch):

            # データshuffle
            idx = np.random.permutation(len(x))
            x = x[idx]
            t = t[idx]

            for it in range(it_per_epoch):
                # ミニバッチデータ
                x_batch = x[batch_size * it: batch_size * (it+1)]
                t_batch = t[batch_size * it: batch_size * (it+1)]

                # 学習
                loss = self.model.forward(x_batch, t_batch)
                self.model.backward(loss)
                # (未実装) 共有された重みをひとつに集約
                # (未実装) 勾配クリッピング RNNのときみたい
                self.opt.update(self.model.params, self.model.grads)

                total_loss.append(loss)

                # 評価
                if (it + 1) % eval_interval == 0:
                    avg_loss = np.mean(total_loss)
                    elapsed_time = time() - start_time
                    print('epoch: {0}, iter: {1}/{2}, time: {3:.3f}[s], avg loss: {4}'.format( \
                          e+1, it+1, it_per_epoch, elapsed_time, avg_loss))
                    self.loss_list.append(avg_loss)
                    total_loss = []

    def plot(self, fname):
        fig = plt.figure()
        plt.plot(self.loss_list)
        plt.xlabel('iter / {0}'.format(self.eval_interval))
        plt.ylabel('avg loss')
        fig.savefig(fname)
