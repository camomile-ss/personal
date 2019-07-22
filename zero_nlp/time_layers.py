# coding: utf-8
import numpy as np
from layers import MatMul

class RNN:
    def __init__(self, wh, wx, b):
        self.matmul_h = MatMul(wh)
        self.matmul_x = MatMul(wx)
        self.params = self.matmul_h.params + self.matmul_x.params + [b]
        self.grads = self.matmul_h.grads + self.matmul_x.grads + [np.zeros_like(b)]
        self.h = None

    def forward(self, x, h_prev):
        b = self.params[2]
        t = self.matmul_h.forward(h_prev) + self.matmul_x.forward(x) + b
        h = np.tanh(t)
        self.h = h
        return h

    def backward(self, dh):
        dt = dh * (1 - self.h ** 2)
        db = np.sum(dt, axis=0)

        dh_prev = self.matmul_h.backward(dt)
        dx = self.matmul_x.badkward(dt)

        self.grads[2][...] = db

        return dx, dh_prev

class timeRNN:
    def __init__(self, wh, wx, b, stateful=False):
        self.params = [wh, wx, b]
        self.grads = [np.zeros_like(wh), np.zeros_like(wx), np.zeros_like(b)]
        self.layers = None
        self.h, self.dh = None, None
        self.stateful = stateful

    def forward(self, xs):
        wh, wx, b = self.params
        N, T, D = xs.shape  # バッチサイズ, 時間サイズ, データの次元
        D, H = wh.shape  # データの次元, 隠れ状態の次元

        self.layers = []
        hs = np.empty((N, T, H), drype='f')

        if not self.statefull or self.h is None:
            self.h = np.zeros((N, H), dtype='f')

        for t in range(T):
            layer = RNN(*self.params)
            self.h = layer.forward(xs[:, t, :], self.h)
            hs [:, t, :] = self.h
            self.layers.append(layer)

        return hs
