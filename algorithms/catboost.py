######    CatBoost    ######


#import sys
#import logging
#from algorithms.algorithm import Algorithm

#class Algo3(Algorithm):
#    def __init__(self, name):
#        super().__init__(name)

    # Please implement the following functions
    # Concerning dataset, refer to the class TrainingSet
#    def learning(self, windows, step):
#        pass

#    def detection(self, window, step):
#        pass

import sys
import logging
import numpy as np
from sklearn.preprocessing import StandardScaler
from catboost import CatBoostClassifier  # CatBoost 분류기 임포트
from algorithms.algorithm import Algorithm  # 부모 알고리즘 클래스 임포트

class Catboost(Algorithm):  # Algo3 클래스
    def __init__(self, name):
        super().__init__(name)  # 부모 클래스 초기화

    def learning(self, windows, step):
        # 학습 데이터를 가져오고, NumPy 배열로 변환
        self.scale, dataset = windows.get_dataset(step, scaler="standard")
        labels = windows.get_labels(step, dl=False)  # 라벨 데이터를 가져옵니다.

        # CatBoost 분류기 초기화
        self.classifier[step] = CatBoostClassifier(
            iterations=200,
            learning_rate=0.01,
            depth=8,
            loss_function='Logloss',
            verbose=0  # 학습 중 출력을 끄기 위해 설정
        )

        try:
            # CatBoost 모델 학습
            self.classifier[step].fit(dataset, labels)
            logging.info("  => {} {} classifier is generated".format(self.get_name(), step))
        except Exception as e:
            self.classifier[step] = None
            logging.error("  => {} {} classifier is not generated: {}".format(self.get_name(), step, e))

    def detection(self, window, step):
        # 예측할 데이터를 가져옵니다.
        test = window.get_code()
        test = self.scale.transform(test.reshape(1, -1))  # 데이터를 2차원 배열로 변환 후 표준화

        if self.classifier[step]:
            # CatBoost 모델로 확률과 클래스를 예측
            pred_proba = self.classifier[step].predict_proba(test)
            pred_class = self.classifier[step].predict(test)

            logging.debug("{}> pred_proba: {}, pred_class: {}".format(self.get_name(), pred_proba, pred_class))

            # 예측된 클래스와 확률 반환
            return pred_class, list(pred_proba[0])
        else:
            logging.error("  => {} classifier not available for step {}".format(self.get_name(), step))
            return [0], [0.5, 0.5]
