# coding: utf-8
import re
import numpy as np

def preprocess(text):

    text = text.lower()

    #words = re.split(r'(\W+)?', text)  # <- これだとだめ
    # 単語間のスペースもリストに残る。カッコついてるから。
    # 最後の.もマッチするから最後に空文字列が入る。
    # ほんとうは各文字間もマッチするから将来は1文字ずつ分割されるようになる(FutureWarning出る)。

    words = [w for wk in re.split(r'\s', text) for w in re.split(r'(\W+)', wk) if w != '']

    word_to_id = {}
    id_to_word = {}

    for w in words:
        if not w in word_to_id:
            new_id = len(word_to_id)
            word_to_id[w] = new_id
            id_to_word[new_id] = w

    corpus = np.array([word_to_id[w] for w in words])

    return corpus, word_to_id, id_to_word

if __name__ == '__main__':

    corpus, word_to_id, id_to_word = preprocess('You say goodbye and I say hello.')

    print(corpus)
    print(word_to_id)
    print(id_to_word)
