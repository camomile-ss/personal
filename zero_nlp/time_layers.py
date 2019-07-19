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
