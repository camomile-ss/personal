# coding: utf-8
import numpy as np

class RNN:
    def __init__(self, wh, wx, b):
        self.params = [wh, wx, b]
        self.grads = [np.zeros_like(wh), np.zeros_like(wx), np.zeros_like(b)]
        self.cache = None

    def forward(self, x, h_prev):
        wh, wx, b = self.params
        t = np.dot(h_prev, wh) + np.dot(x, wx) + b
        h = np.tanh(t)
        self.cache = [x, h_prev, h]
        return h
