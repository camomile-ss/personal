# coding: utf-8

import numpy as np
import pandas as pd

def minInull(a, b):
    """
    引数   a, b: ふたつの値
    戻り値 a, bの小さいほうを返す。
           ただし、どちらかがnullのときはnullじゃないほうを返す。
           両方nullならnullを返す
    """
    if a!=a:
        if b!=b:
            return np.nan
        else:
            return b
    else:
        if b!=b:
            return a
        else:
            return min(a, b)

def errInull(dt, mn):
    """
    引数   dt :値
           mn :平均
    戻り値 誤差
           |平均-値|/値
           ただし、どちらかがnullのときはnull
    """
    if dt!=dt:
        return np.nan
    elif mn!=mn:
        return np.nan
    elif dt==0:
        return 0
    else:
        return abs(mn-dt)/dt

def float2int_cha(ser):
    """
    nullを含むためfloatになっているseriesを、出力用に整数にする
    引数   ser: pandas series (dtype: float)
    戻り値 ser_out: pandas series (dtype: object)
    """
    ser = ser.astype('object')
    ser[ser.isnull()==False] = ser[ser.isnull()==False].apply(lambda x: str(int(x)))
    return(ser)

if __name__ == '__main__':
    ser1 = pd.Series([1.0, np.nan, 2.0, 3.0])
    print(ser1.dtype)
    print(ser1)

    ser2 = float2int_cha(ser1)
    print(ser2.dtype)
    print(ser2)
