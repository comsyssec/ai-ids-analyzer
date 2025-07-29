import sys
import copy
import logging
import numpy as np
from algorithms.algorithm import Algorithm
from keras.models import Sequential
from keras.layers import Input, Conv1D, GlobalMaxPooling1D, Dense
from keras.metrics import Recall, Precision
from sklearn.preprocessing import MinMaxScaler

THRESHOLD = 0.5
BATCH=256
EPOCHS=50

class Cnn(Algorithm):
    def __init__(self, name):
        super().__init__(name)
        self.num = {}
        self.num["training"] = {}
        self.num["testing"] = {}

    # Please implement the following functions
    # Concerning dataset, refer to the class TrainingSet
    def learning(self, windows, step):
        # 1) 데이터 복사 & numpy 배열 변환
        #dataset = copy.deepcopy(windows.get_dataset(step))
        self.scale, dataset = windows.get_dataset(step, scaler="minmax")

        # 3) CNN 입력 형태로 reshape
        #    Conv1D는 (samples, time_steps, channels) 형태를 기대합니다.
        #    여기서는 "features"를 time_steps로 보고, channels=1 로 지정.
        #    즉 (samples, features, 1)
        dataset = dataset.reshape((dataset.shape[0], dataset.shape[1], 1))

        # 라벨 준비
        features = len(windows.get_feature_names())
        labels = windows.get_labels(step, dl=True)

        # 4) CNN 모델 정의
        self.classifier[step] = Sequential()

        # Conv1D : 필터 수=32, 커널사이즈=3, relu 활성화
        # input_shape=(features, 1)
        self.classifier[step].add(Input(shape=(features,1)))
        self.classifier[step].add(Conv1D(filters=32, kernel_size=3, activation='relu'))
        # GlobalMaxPooling1D: Conv1D 출력 중 최댓값을 추출
        # (길이가 점차 줄어드는 대신 연산량이 적고 간단함)
        self.classifier[step].add(GlobalMaxPooling1D())

        # 분류를 위한 Dense
        self.classifier[step].add(Dense(32, activation='relu'))
        self.classifier[step].add(Dense(1, activation='sigmoid'))

        # 5) 모델 컴파일
        self.classifier[step].compile(
            loss='binary_crossentropy',
            optimizer='adam',
            metrics=['accuracy']
        )

        # 6) 모델 학습
        try:
            self.classifier[step].fit(dataset, labels, epochs=EPOCHS, batch_size=BATCH, verbose=1)
            logging.info(f"  => {self.get_name()} {step} classifier (CNN) is generated")
        except:
            self.classifier[step] = None
            logging.info(f"  => {self.get_name()} {step} classifier (CNN) is not generated")

    def detection(self, window, step):
        if step not in self.num["testing"]:
            self.num["testing"][step] = 0
        self.num["testing"][step] += 1
        total = self.get_num_of_windows(False)
        self.enqueue(step, window)
        if self.get_num_item(step) < BATCH and self.num["testing"][step] < total:
            return None
        else:
            windows = self.get_queue(step)
            tests = []
            labels = []
            if len(windows) > 0:
                nfeatures = len(windows[0].get_code())
                for window in windows:
                    label = window.get_label(step)
                    test = window.get_code()
                    test = np.array(test)
                    test = self.scale.transform(test.reshape(1, -1))
                    test = test.reshape((test.shape[0], test.shape[1], 1))
                    tests.append(test)
                    labels.append(label)

                rest = BATCH - len(tests)
                for _ in range(rest):
                    code = [-1] * nfeatures
                    code = np.array(code)
                    code = self.scale.transform(code.reshape(1, -1))
                    code = code.reshape((code.shape[0], code.shape[1], 1))
                    tests.append(code)
                    labels.append(-1)

                tests = np.concatenate(tests, axis=0)
                labels = np.array(labels)

                preds = self.classifier[step].predict(tests, batch_size=BATCH)

                if rest > 0:
                    preds = preds[:-1*rest]
                    labels = labels[:-1*rest]

                ret = []
                probs = []
                idx = 0
                for pred in preds:
                    val = float(pred[0])

                    prob = [1-val, val]
                    probs.append(prob)
                    ret.append(int(val > THRESHOLD))

                    logging.debug("label: {}, pred: {}, ret: {}".format(label, pred, ret))

                    idx += 1
                self.flush(step)
                return ret, probs
            else:
                return None
