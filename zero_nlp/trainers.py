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
                # 複数layer共有の重みをひとつに （model.params, model.grads の並びはくずさない）
                params, grads = remove_duplicate(self.model.params, self.model.grads)
                # (未実装) 勾配クリッピング RNNのときみたい
                self.opt.update(params, grads)

                total_loss.append(loss)

                # 評価
                if (it + 1) % eval_interval == 0 or \
                   (it_per_epoch < eval_interval and it == it_per_epoch - 1):
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

def remove_duplicate(params, grads):
    ''' 複数layer共有の重み、勾配をひとつに。勾配は加算。 '''

    params, grads = params[:], grads[:]  # リストをcopy -> 各パラメータの場所は不変。

    while True:
        find_flg = False

        for i in range(0, len(params)-1):
            for j in range(i+1, len(params)):
                # 重みを共有
                if params[i] is params[j]:
                    grads[i] += grads[j]
                    find_flg = True
                    params.pop(j)
                    grads.pop(j)
                # 転置行列として重みを共有
                elif params[i].ndim == 2 and params[j].ndim == 2 and \
                     params[i].T.shape == params[j].shape and np.all(params[i].T == params[j]):
                    grads[i] += grads[j].T
                    find_flg = True
                    params.pop(j)
                    grads.pop(j)

                # 1個見つけたら最初に戻る
                if find_flg: break
            if find_flg: break

        # 全部べつになったら終了
        if not find_flg: break

    return params, grads
