# coding: utf-8
import numpy as np
from layers import MatMul, Embedding, softmax

class RNN:
    def __init__(self, wx, wh, b):
        self.matmul_x = MatMul(wx)
        self.matmul_h = MatMul(wh)
        self.params = self.matmul_x.params + self.matmul_h.params + [b]
        self.grads = self.matmul_x.grads + self.matmul_h.grads + [np.zeros_like(b)]
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

class TimeRNN:
    def __init__(self, wx, wh, b, stateful=False):
        self.params = [wx, wh, b]
        self.grads = [np.zeros_like(wx), np.zeros_like(wh), np.zeros_like(b)]
        self.layers = None
        self.h, self.dh = None, None
        self.stateful = stateful

    def set_state(self, h):
        self.h = h

    def reset_state(self):
        self.h = None

    def forward(self, xs):
        wx, wh, b = self.params
        N, T, D = xs.shape  # バッチサイズ, 時間サイズ, データの次元
        D, H = wx.shape  # データの次元, 隠れ状態の次元

        self.layers = []
        hs = np.empty((N, T, H), dtype='f')

        if not self.statefull or self.h is None:
            self.h = np.zeros((N, H), dtype='f')

        for t in range(T):
            layer = RNN(*self.params)
            self.h = layer.forward(xs[:, t, :], self.h)
            hs[:, t, :] = self.h
            self.layers.append(layer)

        return hs

    def backward(self, dhs):
        wx, wh, b = self.params
        N, T, H = dhs.shape  # バッチサイズ, 時間サイズ, 隠れ状態の次元
        D, H = wx.shape  # データの次元, 隠れ状態の次元

        dxs = np.empty((N, T, D), dtype='f')
        dh = 0
        grads = [0, 0, 0]  # 勾配加算用

        for t in range(T)[::-1]:
            layer = self.layers[t]
            dx, dh = layer.backward(dhs[:, t, :] + dh)
            dxs[:, t, :] = dx

            for i, grad in enumerate(layer.grads):
                grads[i] += grad

        for i, grad in enumerate(grads):
            self.grads[i][...] = grad

        self.dh = dh

        return dxs

class TimeEmbedding:
    def __init__(self, w):
        self.params = [w]
        self.grads = [np.zeros_like(w)]
        self.layers = None

    def forward(self, idxs):
        w, = self.params
        N, T = idxs.shape
        V, D = w.shape  # 語彙数, 分散表現の次元数

        self.layers = []
        ys = np.empty((N, T, D), dtype='f')

        for t in range(T):
            layer = Embedding(w)
            ys[:, t, :] = layer.forward(idxs[:, t])
            self.layers.append(layer)

        return ys

    def backward(self, dys):
        N, T, D = dys.shape

        grad = 0
        for t in range(T):
            layer = self.layer[t]
            layer.backward(dys[:, t, :])
            grad += layer.grads[0]
        self.grads[0][...] = grad

        return None

class TimeAffine:
    def __init__(self, w, b):
        self.params = [w, b]
        self.grads = [np.zeros_like(w), np.zeros_like(b)]
        self.xs = None

    def forward(self, xs):
        w, b = self.params
        N, T, D = xs.shape

        self.xs = xs
        xs_ = xs.reshape(N*T, -1)
        ys_ = np.dot(xs_, w) + b
        ys = ys_.reshape(N, T, -1)
        return ys

    def backward(self, dys):
        w, b = self.params
        N, T, D = self.xs.shape

        dys_ = dys.reshape(N*T, -1)
        xs_ = self.xs.reshape(N*T, -1)

        dxs_ = np.dot(dys_, w.T)
        dxs = dxs_.reshape(N, T, -1)
        dw = np.dot(xs_.T, dys_)
        db = np.sum(dys_, axis=0)

        self.grads[0][...] = dw
        self.grads[1][...] = db

        return dxs

class TimeSoftmaxWithLoss:
    ''' 著者さま提供のまま '''
    def __init__(self):
        self.params, self.grads = [], []
        self.cache = None
        self.ignore_label = -1

    def forward(self, xs, ts):
        N, T, V = xs.shape

        if ts.ndim == 3:  # 教師ラベルがone-hotベクトルの場合
            ts = ts.argmax(axis=2)

        mask = (ts != self.ignore_label)

        # バッチ分と時系列分をまとめる（reshape）
        xs = xs.reshape(N * T, V)
        ts = ts.reshape(N * T)
        mask = mask.reshape(N * T)

        ys = softmax(xs)
        ls = np.log(ys[np.arange(N * T), ts])
        ls *= mask  # ignore_labelに該当するデータは損失を0にする
        loss = -np.sum(ls)
        loss /= mask.sum()

        self.cache = (ts, ys, mask, (N, T, V))
        return loss

    def backward(self, dout=1):
        ts, ys, mask, (N, T, V) = self.cache

        dx = ys
        dx[np.arange(N * T), ts] -= 1
        dx *= dout
        dx /= mask.sum()
        dx *= mask[:, np.newaxis]  # ignore_labelに該当するデータは勾配を0にする

        dx = dx.reshape((N, T, V))

        return dx

