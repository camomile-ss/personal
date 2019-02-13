# coding: utf-8
'''
Created on Thu Jan 31 15:11:34 2019

@author: otani
'''
import sys
import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def softmax(x):
    if x.ndim == 1:
        x = x.reshape(1, x.size)
    x = x - x.max(axis=1, keepdims=True)
    return np.exp(x)/np.sum(np.exp(x), axis=1, keepdims=True)

def cross_entropy_error(y, t):
    if y.ndim == 1:  # batchデータじゃないときも2階にする
        if t.ndim != 1:
            print('[err] dim diff. y:', y.ndim, ', t:', t.ndim, '. (cross_entropy_error)')
            sys.exit()
        y = y.reshape(1, y.size)
        t = t.reshape(1, t.size)
    if y.ndim == 2 and t.ndim == 1:  # 教師データがラベルだったらone-hotに
        t_ = np.zeros((t.size, y.shape[1]))
        t_[range(t.size), t] = 1
        t = t_
    if y.ndim != 2 or t.ndim != 2:
        print('[err] dim ne 2. y:', y.ndim, ', t:', t.ndim, '. (cross_entropy_error)')
        sys.exit()

    n = len(y)  # batch size
    return - np.sum(np.sum(t * np.log(y + 1e-7), axis=1)) / n

def cross_entropy_error_text(y, t):
    ''' 著者提供のほう '''
    if y.ndim == 1:
        t = t.reshape(1, t.size)
        y = y.reshape(1, y.size)

    # 教師データがone-hot-vectorの場合、正解ラベルのインデックスに変換
    if t.size == y.size:
        t = t.argmax(axis=1)

    batch_size = y.shape[0]

    return -np.sum(np.log(y[np.arange(batch_size), t] + 1e-7)) / batch_size

class Sigmoid:
    def __init__(self):
        self.params = []
        self.y = None

    def forward(self, x):
        y = sigmoid(x)
        self.y = y
        return y

    def backward(self, dy):
        dx = self.y * (1 - self.y) * dy
        return dx

class Relu:
    def __init__(self):
        self.params = []
        self.mask = None

    def forward(self, x):
        self.mask = (x <= 0)  # x<=0 -> True を保持
        y = x
        y[self.mask] = 0
        return y

    def backward(self, dy):
        dx = dy
        dx[self.mask] = 0
        return dx

class Affine:
    ''' 全結合層 '''
    def __init__(self, w, b):
        self.params = [w, b]

    def forward(self, x):
        w, b = self.params
        return np.dot(x, w) + b

class Softmax:
    def __init__(self):
        self.params = []

    def forward(self, x):
        return softmax(x)

class SoftmaxWithLoss:
    def __init__(self):
        self.params = []
        self.y = None  # softmax出力
        self.t = None  # 教師ラベル

    def forward(self, x, t):
        self.y = softmax(x)
        self.t = t
        loss = cross_entropy_error(self.y, self.t)
        return loss

class TwoLayersNet:
    def __init__(self, input_size, hidden_size, output_size):
        i, h, o = input_size, hidden_size, output_size

        w1 = np.random.randn(i, h)
        b1 = np.random.randn(h)
        w2 = np.random.randn(h, o)
        b2 = np.random.randn(o)

        self.layers = [
            Affine(w1, b1),
            Sigmoid(),
            Affine(w2, b2)
        ]

        self.params = []
        for l in self.layers:
            self.params += l.params

    def predict(self, x):
        for l in self.layers:
            x = l.forward(x)
        return x

if __name__=='__main__':

    x = np.random.randn(10,3)
    print(x)

    relu_layer = Relu()

    y = relu_layer.forward(x)
    print(y)

    dy = np.ones((10,3))

    dx = relu_layer.backward(dy)
    print(dx)

    """
    x = np.random.randn(10,3)
    y = softmax(x)
    t_oh = np.array([0]*30).reshape(10,3)
    for i in range(10):
        t_oh[i, np.random.randint(0,3)] = 1
    t = np.random.randn(10,3)
    t = softmax(t)

    t_lbl = np.random.randint(0,3,10)

    print('x:', x)
    print('y:', y)
    print('tがone hot:', t_oh)
    print('自作    :', cross_entropy_error(y, t_oh))
    print('テキスト:', cross_entropy_error_text(y, t_oh))
    print('tが確率->テキストは対応してない:', t)
    print('自作    :', cross_entropy_error(y, t))
    print('テキスト:', cross_entropy_error_text(y, t))
    print('tがラベル:', t_lbl)
    print('自作    :', cross_entropy_error(y, t_lbl))
    print('テキスト:', cross_entropy_error_text(y, t_lbl))
    #x = np.random.randn(10, 2)
    #model = TwoLayersNet(2, 4, 3)
    #result = model.predict(x)
    #print(result)
    """

