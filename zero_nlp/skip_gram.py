# coding: utf-8
import numpy as np
from layers import Embedding
from negative_sampling_layers import NegativeSamplingLoss

class SkipGram:
    def __init__(self, vocab_size, hidden_size, window_size, corpus):
        # おもみ
        w_in = 0.01 * np.random.randn(vocab_size, hidden_size).astype('f')
        w_out = 0.01 * np.random.randn(vocab_size, hidden_size).astype('f')

        # layers
        self.embed_layer = Embedding(w_in)
        self.ns_loss_layers = [NegativeSamplingLoss(w_out, corpus) for _ in range(2 * window_size)]

        # おもみ, 勾配まとめ
        layers = [self.embed_layer] + self.ns_loss_layers
        self.params, self.grads = [], []
        for l in layers:
            self.params += l.params
            self.grads += l.grads

        # 単語の分散表現
        self.word_vecs = w_in

    def forward(self, contexts, target):
        h = self.embed_layer.forward(target)
        loss = sum([l.forward(h, contexts[:, i]) for i, l in enumerate(self.ns_loss_layers)])
        return loss

    def backward(self, dl=1):
        dh = sum([l.backward(dl) for i, l in enumerate(self.ns_loss_layers)])
        self.embed_layer.backward(dh)
