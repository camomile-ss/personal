# coding: utf-8
import sys
import argparse
import numpy as np
from two_layers_net import TwoLayersNet
from optimizer import SGD
sys.path.append('../../deep-learning-from-scratch-2/dataset')
import spiral

def print_pg(model, ttl, cnt, flg):
    ''' params, grads 確認用 '''
    if flg:
        print('###', ttl, cnt, '----------------###')
        for cnt, l in enumerate(model.layers):
            print('## layer:', cnt)
            print('# params:', l.params)
            print('# grads:', l.grads)

        print('## model params ##')
        for j in range(len(model.params)):
            print(model.params[j])
        print('## model grads ##')
        for k in range(len(model.grads)):
            print(model.grads[k])

if __name__ == '__main__':

    psr = argparse.ArgumentParser()

    psr.add_argument('-p', help='print pram or not.', type=int, default=0, choices=[0,1])
    args = psr.parse_args()
    pflg = args.p

    #max_epoch = 300
    #batch_size = 30
    hidden_size = 10
    learning_rate = 0.01

    x, t = spiral.load_data()
    model = TwoLayersNet(input_size=2, hidden_size=hidden_size, output_size=3)
    opt = SGD(learning_rate)

    # データshuffle
    idx = np.random.permutation(len(x))
    x = x[idx]
    t = t[idx]

    # とりま10回
    for i in range(10):

        loss = model.forward(x, t)
        print('loss:', loss)
        print_pg(model, 'forward', i, pflg)

        dl = model.backward(loss)
        #print('dl:', dl)
        print_pg(model, 'backward', i, pflg)

        opt.update(model.params, model.grads)
        print_pg(model, 'update', i, pflg)
