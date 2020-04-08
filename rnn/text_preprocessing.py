# -*- coding: utf-8 -*-

from __future__ import print_function
import mxnet as mx
from mxnet import gluon, nd, autograd
from string import punctuation
import numpy as np
import pandas as pd
import gluonnlp as nlp
from sklearn.model_selection import train_test_split
from gluonnlp.data import SacreMosesTokenizer


########################################################################################################################
# 데이터 읽기, 구분자로 뭘로 해야할지 정해야 할듯

class Preprocessing():
    def setdata(self, path, sep, test_size, batch_size):
        self.path = path
        self.sep = sep
        self.test_size = test_size
        self.batch_size = batch_size

    def text(self):
        path, sep, test_size, batch_size = self.path, self.sep, self.test_size, self.batch_size

        path = 'dataset/nlp/timemachine.txt'
        sep = '\\'
        data = pd.read_csv(path, header=None, sep=sep)

        # 한 문장을 하나의 리스트로 저장
        text = []
        text.extend(list(data[0].values))

        # 구두점 제거와 동시에 소문자화
        def repreprocessing(s):
            s = s.encode('utf8').decode('ascii', 'ignore')
            return ''.join(c for c in s if c not in punctuation).lower() # 구두점 제거와 동시에 소문자화

        text = [repreprocessing(x) for x in text]

        # vocab_size
        tokenizer = nlp.data.SacreMosesTokenizer()
        counter = nlp.data.count_tokens(tokenizer(text))

        vocab = nlp.Vocab(counter)
        vocab_size = len(vocab.token_to_idx)

        sequences = list()
        for line in text:                                # 샘플에 대해서 샘플을 1개씩 가져온다.
            encoded = vocab.to_indices(tokenizer(line))  # 문자열을 정수 인덱스로 변환
            for i in range(1, len(encoded)):
                sequence = encoded[:i+1]
                sequences.append(sequence)

        # sequence의 최대 길이
        max_len = max(len(l) for l in sequences)

        a = sequences[:100]
        max = max(len(l) for l in a)
        datasets = nlp.data.PadSequence(length=max, pad_val=0)
        a.transform(nlp.data.PadSequence(length=max, pad_val=0))

        ################################################################################################################
        # pad처리(gluonnlp로는 못찾음-일단 케라스를 이용해서 padding)
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        sequences = pad_sequences(sequences,
                                  maxlen=max_len,  # 최대 길이를 설정
                                  padding='pre')   # pre: 앞으로 값을 채움, post: 뒤로 값을 채움
        ################################################################################################################

        # 입력값과 출력값 분리
        X = sequences[:, :-1].astype('float32')
        y = sequences[:,-1]

        a = y[:5]
        a = mx.nd.array(a)

        # one-hot encoding
        mx.nd.one_hot(a, depth=5)


        # 트레이닝셋과 테스트셋 분리
        train_data, test_data, train_label, test_label = train_test_split(X, y, test_size = test_size, shuffle=False)

        train_iter = gluon.data.DataLoader(gluon.data.ArrayDataset(train_data, train_label), batch_size=batch_size, shuffle=False)
        test_iter = gluon.data.DataLoader(gluon.data.ArrayDataset(test_data, test_label), batch_size=batch_size, shuffle=False)

        return train_iter, test_iter
