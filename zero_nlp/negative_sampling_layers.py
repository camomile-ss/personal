# coding: utf-8
import numpy as np
from layers import Embedding

class EmbeddingDot:
    def __init__(self, w):
        self.embed = Embedding(w)
        self.params = self.embed.params
        self.grads = self.embed.grads
        self.cache = None

    def forward(self, h, idx):
        w_idx = self.embed.forward(idx)
        s = np.sum(h * w_idx, axis=1)
        self.cache = (h, w_idx)
        return s

    def backward(self, ds):
        ds = ds.reshape(ds.shape[0], 1)  # ???
        h, w_idx = self.cache
        dw_idx = ds * h
        self.embed.backward(dw_idx)
        dh = ds * w_idx
        return dh
