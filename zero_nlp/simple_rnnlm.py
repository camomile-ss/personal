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
                TimeRNN(rnn_wx, rnn_wh, rnn_b),
                TimeAffine(affine_w, affine_b)
                ]
        self.loss_layer = TimeSoftmaxWithLoss()

        self.params, self.grads = [], []
        for l in self.layers:
            self.params += l.params
            self.grads += l.grads

    def forward(self, idxs, ts):
        time_embedding_layer, time_rnn_layer, time_affine_layer = self.layers
        xs = time_embedding_layer.forward(idxs)
        hs = time_rnn_layer.forward(xs)
        ys = time_affine_layer.forward(hs)
        loss = self.loss_layer.forward(ys)
        return loss

    def backward(self, dl):
        time_embedding_layer, time_rnn_layer, time_affine_layer = self.layers
        dys = self.loss_layer.backward(dl)
        dhs = time_affine_layer.backward(dys)
        dxs = time_rnn_layer.backward(dhs)
        time_embedding_layer.backward(dxs)
        return None
