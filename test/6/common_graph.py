# coding: utf-8
'''
グラフ関係
（nisitetsu の common_meisai からコピーしたまま。後で直す。）
'''
from matplotlib.ticker import FuncFormatter

def barh_chart(ax, data, keys, tei_dic):
    ''' 棒グラフ（よこ） '''
    x = [-i for i in data.index]  # 多い順にしたいので -x
    y = data['count']
    # ラベル
    ticks = []
    for i, r in data.iterrows():
        if tei_dic:
            teis = ['{0} {1}'.format(r[k], tei_dic[r[k]]) for k in keys]
        else:
            teis = [r[k] for k in keys]
        ticks.append(' -> '.join(teis))

    ax.barh(x, y, tick_label=ticks)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.grid(axis='x')
    for x_, y_ in zip(x, y):
        ax.annotate('{:,}'.format(y_), xy=(y_, x_))

    return ax

def stack_bar_chart(ax, data, vals, anno=True, anno_thres=200000, ylim_max=None):
    '''
    積み上げ棒グラフ
    args  ax:   グラフaxes
          data: indexがx軸項目、columnsが積み上げ項目、の件数のdf
          val:  各積み上げ項目のラベル（legend用）
          anno_thres: 数値表示の閾値（これ以上なら表示）
          ylim_max: y軸範囲調整用（なぜか短くなる時があるので）
    '''
    data = data.fillna(0)

    ticks = data.index  # x軸ラベル
    datas = [data[x] for x in data.columns]  # 各積み上げのデータ
    stacks = [None] * len(data.columns)  # legend用に各stackを保存

    btms = [0] * len(ticks)  # 棒bottom位置
    for i in range(len(data.columns)):
        # 棒
        stacks[i] = ax.bar(ticks, datas[i], bottom=btms)
        # 数値表示
        y_anno = [a+b/2 for a, b in zip(btms, datas[i])]  # annotate位置
        for x_, y_, y in zip(list(range(len(ticks))), y_anno, datas[i]):
            if anno:
                if y != 0 and y >= anno_thres:
                    ax.annotate('{:,.0f}'.format(y), xy=(x_-0.4, y_-anno_thres/2))
        # bottom位置更新
        btms = [a+b for a, b in zip(btms, datas[i])]

    # 積み上げ合計値表示
    sums = data.sum(axis=1)
    for x_, y_ in zip(list(range(len(ticks))), sums):
        if anno or y_==0:
            ax.annotate('{:,.0f}'.format(y_), xy=(x_-0.4, y_+anno_thres/5))
    # y軸範囲調整
    if ylim_max:
        ax.set_ylim(0, ylim_max)

    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: '{:,}'.format(int(x))))  # y軸目盛書式
    ax.grid(axis='y')  # グリッド線
    ax.legend(vals, loc='lower left', bbox_to_anchor=(1.02, 0.5))  # 凡例
    return ax

