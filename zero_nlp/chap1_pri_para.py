# coding: utf-8
''' params, grads 更新を見てみる '''
import sys
import argparse
import numpy as np
from two_layers_net import TwoLayersNet
from optimizers import SGD
from dataset import spiral

def print_pg(model, ttl, cnt, flg):
    ''' params, grads print '''
    if flg:
        print('###', cnt, ttl, '----------------###')
        """
        for i, l in enumerate(model.layers):
            print('## layer:', i)
            print('# params:', l.params)
            print('# grads:', l.grads)
        """
        print('## model params ##')
        for j in range(len(model.params)):
            print(model.params[j])
        print('## model grads ##')
        for k in range(len(model.grads)):
            print(model.grads[k])

if __name__ == '__main__':

    psr = argparse.ArgumentParser()

    psr.add_argument('-p', help='print or not.', type=int, default=1, choices=[0,1])
    args = psr.parse_args()
    pflg = args.p

    #max_epoch = 300
    batch_size = 30
    hidden_size = 10
    learning_rate = 1.0

    x, t = spiral.load_data()
    model = TwoLayersNet(input_size=2, hidden_size=hidden_size, output_size=3)
    opt = SGD(learning_rate)

    it_per_epoch = - (- len(x) // batch_size)

    # データshuffle
    idx = np.random.permutation(len(x))
    x = x[idx]
    t = t[idx]

    for it in range(it_per_epoch):
        # ミニバッチデータ
        x_batch = x[batch_size * it: batch_size * (it+1)]
        t_batch = t[batch_size * it: batch_size * (it+1)]

        loss = model.forward(x_batch, t_batch)
        print('loss:', loss)
        print_pg(model, 'forward', it, pflg)

        model.backward(loss)
        print_pg(model, 'backward', it, pflg)

        opt.update(model.params, model.grads)
        print_pg(model, 'update', it, pflg)
