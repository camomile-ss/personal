# coding: utf-8
#from route_type import combi_rec

def combinations(table):
    '''
    リストのリストの、すべての組み合わせを返す。再帰処理。
    e. g.) input:  [[1,2,3], [4,5], [6,7], [8]]
           output: [[1, 4, 6, 8], [2, 4, 6, 8], [3, 4, 6, 8],
                    [1, 5, 6, 8], [2, 5, 6, 8], [3, 5, 6, 8],
                    [1, 4, 7, 8], [2, 4, 7, 8], [3, 4, 7, 8],
                    [1, 5, 7, 8], [2, 5, 7, 8], [3, 5, 7, 8]]
    '''
    if len(table)==1:
        return [[x] for x in table[0]]
    combis = []
    for a in table[-1]:
        for c in combinations(table[:-1]):
            c.append(a)
            combis.append(c)
    return combis

if __name__ == '__main__':
    #table = [[0,5], [4], [0,5], [6]]
    table = [[1,2,3], [4,5], [6,7], [8]]
    combis = combinations(table)
    print(combis)
