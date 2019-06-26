# coding: utf-8
import numpy as np
from layers import Embedding

class EmbeddingDot:
    def __init__(self, w):
        self.emb = Embedding(w)
        self.params = self.emb.params
        self.grads = self.emb.grads
        self.cache = None

    def forward(self, h, idx):
        w_i = self.emb.forward(idx)
        s = np.sum(h * w_i, axis=1)
        self.cache = (h, w_i)
        return s

    def backward(self, ds):
        ds = ds.reshape(ds.shape[0], 1)  # ???
        h, w_i = self.cache
        dw_i = ds * h
        self.emb.backward(dw_i)
        dh = ds * w_i
        return dh
