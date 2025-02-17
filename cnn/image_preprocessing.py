import mxnet as mx
from mxnet import gluon, autograd, nd
import numpy as np
from sklearn.model_selection import train_test_split


class Preprocessing():
    def setdata(self, data_path, image_resize, test_size, batch_size):
        self.data_path = data_path
        self.image_resize = image_resize
        self.test_size = test_size
        self.batch_size = batch_size

    def image(self):
        data_path, image_resize, test_size, batch_size = self.data_path, self.image_resize, self.test_size, self.batch_size

        # 이미지 데이터 전처리
        def transformer(data, label):
            data = mx.image.imresize(data, image_resize, image_resize)
            data = mx.nd.transpose(data.astype('float32'), (2, 0, 1)) / 255
            label = np.float32(label)
            return data, label

        # ImageFolderDataset으로 폴더에 있는 이미지를 불러옴
        input_data = gluon.data.vision.datasets.ImageFolderDataset(data_path, transform=transformer)

        # 이미지 데이터와 레이블 데이터를 따로 리스트로 저장
        img_data = []
        img_label = []
        for d, l in input_data:
            img_data.append(d)
            img_label.append(l)

        # 이미지와 레이블 데이터를 trainset과 testset으로 구분
        train_data, test_data, train_label, test_label = train_test_split(img_data, img_label, test_size=test_size,
                                                                          shuffle=True)

        # DataLoader함수로 batch로 데이터를 불러옴
        train_iter = gluon.data.DataLoader(gluon.data.ArrayDataset(train_data, train_label), batch_size=batch_size,
                                           shuffle=False)
        test_iter = gluon.data.DataLoader(gluon.data.ArrayDataset(test_data, test_label), batch_size=batch_size,
                                          shuffle=False)

        return train_iter, test_iter


