# coding: utf-8
#from route_type import combi_rec

def combination(table):
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
    new_combi = []
    for add in table[-1]:
        for combi in combination(table[:-1]):
            combi.append(add)
            new_combi.append(combi)
    return new_combi

#table = [[0,5], [4], [0,5], [6]]
table = [[1,2,3], [4,5], [6,7], [8]]
combinations = combination(table)
print(combinations)
