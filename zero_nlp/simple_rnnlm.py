# coding: utf-8

import numpy as np
from time_layers import TimeEnbedding, TimeRNN, TimeAffine, TimeSoftmaxWithLoss

class SimpleRnnlm:
    def __init__(self, vocab_size, wordvec_size, hidden_size):

        embed_w = (np.random.randn(vocab_size, wordvec_size) / 100).astype('f')
        rnn_wx = (np.random.randn(wordvec_size, hidden_size) / np.sqrt(wordvec_size)).astype('f')
        rnn_wh = (np.random.randn(hidden_size, hidden_size) / np.sqrt(hidden_size)).astype('f')
        rnn_b = np.zeros(hidden_size).astype('f')
        affine_w = (np.random.randn(hidden_size, vocab_size) / np.sqrt(hidden_size)).astype('f')
        affine_b = np.zeros(vocab_size).astype('f')

        self.layers = [
                ]

