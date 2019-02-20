# coding: utf-8
from decimal import Decimal

def dec(x):
    ''' float -> decimal '''
    return Decimal(str(x))

class MulLayer:
    ''' 乗算ノード '''
    def __init__(self):
        self.x = None
        self.y = None

    def forward(self, x, y):
        self.x = x
        self.y = y
        return float(dec(x) * dec(y))

    def backward(self, dz):
        dx = float(dec(dz) * dec(self.y))
        dy = float(dec(dz) * dec(self.x))
        return dx, dy

class AddLayer:
    ''' 加算ノード '''
    def __init__(self):
        pass

    def forward(self, x, y):
        return float(dec(x) + dec(y))

    def backward(self, dz):
        dx = dz
        dy = dz
        return dx, dy

if __name__ == '__main__':

    # りんごとみかん
    apple_p = 100
    orange_p = 150
    apple_n = 2
    orange_n = 3
    ctax_ratio = 1.1

    apple_layer = MulLayer()
    orange_layer = MulLayer()
    total_layer = AddLayer()
    ctax_layer = MulLayer()

    # forward propagation
    apple_total = apple_layer.forward(apple_p, apple_n)
    orange_total = orange_layer.forward(orange_p, orange_n)
    total = total_layer.forward(apple_total, orange_total)
    bill = ctax_layer.forward(total, ctax_ratio)

    print(bill)

    # backward propagation
    dbill = 1
    dtotal, dctax_ratio = ctax_layer.backward(dbill)
    dapple_total, dorange_total = total_layer.backward(dtotal)
    dapple_p, dapple_n = apple_layer.backward(dapple_total)
    dorange_p, dorange_n = orange_layer.backward(dorange_total)

    print(dapple_p, dapple_n, dorange_p, dorange_n, dapple_total, dorange_total, dtotal, dctax_ratio, dbill)
