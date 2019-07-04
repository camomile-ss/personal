# coding: utf-8
import numpy as np
from layers import Embedding
from negative_sampling_layers import NegativeSamplingLoss

class CBOW:
    def __init__(self, vocab_size, hidden_size, window_size, corpus):
        # おもみ
        w_in = 0.01 * np.random.randn(vocab_size, hidden_size).astype('f')
        w_out = 0.01 * np.random.randn(vocab_size, hidden_size).astype('f')

        # layers
        self.embed_layers = [Embedding(w_in) for _ in range(2 * window_size)]
        self.ns_loss_layer = NegativeSamplingLoss(w_out, corpus)

        # おもみ, 勾配 まとめ
        layers = self.embed_layers + [self.ns_loss_layer]
        self.params, self.grads = [], []
        for l in layers:
            self.params += l.params
            self.grads += l.grads

        # 単語の分散表現
        self.word_vecs = w_in

    def forward(self, contexts, target):
        h = [l.forward(contexts[:, i]) for i, l in enumerate(self.embed_layers)]
        h = sum(h) / len(self.embed_layers)
        loss = self.ns_loss_layer.forward(h, target)
        return loss

    def backward(self, dl=1):
        dh = self.ns_loss_layer.backward(dl)
        dh /= len(self.embed_layers)
        for l in self.embed_layers:
            l.backward(dh)
