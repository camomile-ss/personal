# coding: utf-8

import numpy as np
from time_layers import TimeEmbedding, TimeRNN, TimeAffine, TimeSoftmaxWithLoss

class SimpleRnnlm:
    def __init__(self, vocab_size, wordvec_size, hidden_size):

        embed_w = (np.random.randn(vocab_size, wordvec_size) / 100).astype('f')
        rnn_wx = (np.random.randn(wordvec_size, hidden_size) / np.sqrt(wordvec_size)).astype('f')
        rnn_wh = (np.random.randn(hidden_size, hidden_size) / np.sqrt(hidden_size)).astype('f')
        rnn_b = np.zeros(hidden_size).astype('f')
        affine_w = (np.random.randn(hidden_size, vocab_size) / np.sqrt(hidden_size)).astype('f')
        affine_b = np.zeros(vocab_size).astype('f')

        self.layers = [
                TimeEmbedding(embed_w),
                TimeRNN(rnn_wx, rnn_wh, rnn_b, stateful=True),
                TimeAffine(affine_w, affine_b)
                ]
        self.loss_layer = TimeSoftmaxWithLoss()
        self.rnn_layer = self.layers[1]

        self.params, self.grads = [], []
        for l in self.layers:
            self.params += l.params
            self.grads += l.grads

    def forward(self, xs, ts):
        for l in self.layers:
            xs = l.forward(xs)
        loss = self.loss_layer.forward(xs, ts)
        return loss

    def backward(self, dl=1):
        dxs = self.loss_layer.backward(dl)
        for l in self.layers[::-1]:
            dxs = l.backward(dxs)
        return dxs

    def reset_state(self):
        self.rnn_layer.reset_state()
