######   LightGBM    ###### 

#import sys
#import logging
#from algorithms.algorithm import Algorithm

#class Algo2(Algorithm):
#    def __init__(self, name):
#        super().__init__(name)

    # Please implement the following functions
    # Concerning dataset, refer to the class TrainingSet
#    def learning(self, windows, step):
#        pass

#    def detection(self, window, step):
#        pass

### Basic CODE ------------------------------------------------------------------------------

import sys
import logging
import numpy as np
from sklearn.preprocessing import StandardScaler
from lightgbm import LGBMClassifier  # LightGBM 분류기 임포트
from algorithms.algorithm import Algorithm  # 부모 알고리즘 클래스 임포트

class Lightgbm(Algorithm):  # Algo2 클래스
    def __init__(self, name):
        super().__init__(name)  # 부모 클래스 초기화

    def learning(self, windows, step):
        # 학습 데이터를 가져오고, NumPy 배열로 변환
        self.scale, dataset = windows.get_dataset(step, scaler="standard")
        labels = windows.get_labels(step, dl=False)  # 라벨 데이터를 가져옴

        # LightGBM 분류기 초기화
        self.classifier[step] = LGBMClassifier(objective='binary', n_estimators=100, learning_rate=0.1)

        try:
            # LightGBM 모델 학습
            self.classifier[step].fit(dataset, labels)
            logging.info("  => {} {} classifier is generated".format(self.get_name(), step))
        except Exception as e:
            self.classifier[step] = None
            logging.error("  => {} {} classifier is not generated: {}".format(self.get_name(), step, e))

    def detection(self, window, step):
        # 예측할 데이터를 가져옵니다.
        test = window.get_code()  # NumPy 배열로 변환
        test = self.scale.transform(test.reshape(1, -1))  # 데이터를 2차원 배열로 변환 후 표준화

        if self.classifier[step]:
            # LightGBM 모델로 확률과 클래스를 예측
            pred_proba = self.classifier[step].predict_proba(test)
            pred_class = self.classifier[step].predict(test)

            logging.debug("{}> pred_proba: {}, pred_class: {}".format(self.get_name(), pred_proba, pred_class))

            # 예측된 클래스와 확률 반환
            return pred_class, list(pred_proba[0])
        else:
            logging.error("  => {} classifier not available for step {}".format(self.get_name(), step))
            return [0], [0.5, 0.5]


###-------------------------------------------------------------------------------------------------------
# modify code1_   code2

#import sys
#import logging
#import numpy as np
#from sklearn.preprocessing import StandardScaler
#from lightgbm import LGBMClassifier  # LightGBM 분류기 임포트
#from algorithms.algorithm import Algorithm  # 부모 알고리즘 클래스 임포트


#from sklearn.model_selection import GridSearchCV 

#class Algo2(Algorithm):
#    def __init__(self, name):
#        super().__init__(name)
#
#    def learning(self, windows, step):
#        dataset = np.array(windows.get_dataset(step))
#        labels = windows.get_labels(step)
#        self.scale = StandardScaler().fit(dataset)
#        dataset = self.scale.transform(dataset)
#
#        param_grid = {
#            'learning_rate': [0.01, 0.05, 0.1],
#            'n_estimators': [100, 200],
#            'max_depth': [5, 7, 10]
#        }
#
#        grid_search = GridSearchCV(LGBMClassifier(objective='binary'), param_grid, scoring='f1', cv=3)
#        grid_search.fit(dataset, labels)
#
#        self.classifier[step] = grid_search.best_estimator_
#        logging.info(f"Best parameters: {grid_search.best_params_}")
#
#
#    def detection(self, window, step):
#        # 예측할 데이터를 가져옵니다.
#        test = np.array(window.get_code())  # NumPy 배열로 변환
#        test = self.scale.transform(test.reshape(1, -1))  # 데이터를 2차원 배열로 변환 후 표준화
#
#        if self.classifier[step]:
#            # LightGBM 모델로 확률과 클래스를 예측
#            pred_proba = self.classifier[step].predict_proba(test)
#            pred_class = self.classifier[step].predict(test)
#
#            logging.debug("{}> pred_proba: {}, pred_class: {}".format(self.get_name(), pred_proba, pred_class))
#
#            # 예측된 클래스와 확률 반환
#            return pred_class, list(pred_proba[0])
#        else:
#            logging.error("  => {} classifier not available for step {}".format(self.get_name(), step))
#            return [0], [0.5, 0.5]

##-----------------------------------------------------------------------------------------------------------
# modify code2  --code3

#import sys
#import logging
#import numpy as np
#from sklearn.preprocessing import StandardScaler
#from lightgbm import LGBMClassifier
#from algorithms.algorithm import Algorithm
#from sklearn.model_selection import GridSearchCV
#
#class Algo2(Algorithm):
#    def __init__(self, name):
#        super().__init__(name)
#
#    def learning(self, windows, step):
#        dataset = np.array(windows.get_dataset(step))
#        labels = windows.get_labels(step)
#        self.scale = StandardScaler().fit(dataset)
#        dataset = self.scale.transform(dataset)
#
#        param_grid = {
#            'learning_rate': [0.05, 0.1],  # 학습률을 0.05 ~ 0.1로 설정
#            'n_estimators': [100, 150],  # 트리 개수
#            'max_depth': [5, 7],  # 트리 깊이
#            'num_leaves': [20, 40],  # 리프 개수
#            'min_child_samples': [20, 30],  # 최소 리프 노드 데이터 수
#            'scale_pos_weight': [1, 2]  # 불균형 데이터에 대한 가중치 조정
#        }
#
#        grid_search = GridSearchCV(LGBMClassifier(objective='binary'), param_grid, scoring='f1', cv=3)
#        grid_search.fit(dataset, labels)
#
#        self.classifier[step] = grid_search.best_estimator_
#        logging.info(f"Best parameters: {grid_search.best_params_}")
#
#    def detection(self, window, step):
#        test = np.array(window.get_code())
#        test = self.scale.transform(test.reshape(1, -1))
#
#        if self.classifier[step]:
#            pred_proba = self.classifier[step].predict_proba(test)
#            pred_class = self.classifier[step].predict(test)
#            logging.debug("{}> pred_proba: {}, pred_class: {}".format(self.get_name(), pred_proba, pred_class))
#            return pred_class, list(pred_proba[0])
#        else:
#            logging.error("  => {} classifier not available for step {}".format(self.get_name(), step))
#            return [0], [0.5, 0.5]


##-------------------------------------------------------------------------------------------

# modify code3 --X

#import sys
#import logging
#import numpy as np
#from sklearn.preprocessing import StandardScaler
#from lightgbm import LGBMClassifier
#from algorithms.algorithm import Algorithm
#from sklearn.model_selection import GridSearchCV
#
#class Algo2(Algorithm):
#    def __init__(self, name):
#        super().__init__(name)
#
#    def learning(self, windows, step):
#        dataset = np.array(windows.get_dataset(step))
#        labels = windows.get_labels(step)
#        self.scale = StandardScaler().fit(dataset)
#        dataset = self.scale.transform(dataset)
#
#        param_grid = {
#            'learning_rate': [0.01, 0.05],  # 학습률 조정
#            'n_estimators': [100, 150],  # 트리 개수
#            'max_depth': [5, 6],  # 트리 깊이
#            'num_leaves': [30, 50],  # 리프 개수
#            'min_child_samples': [10, 20],  # 최소 리프 노드 샘플 수
#            'scale_pos_weight': [2, 3]  # 불균형 클래스에 대한 가중치
#        }
#
#        grid_search = GridSearchCV(LGBMClassifier(objective='binary'), param_grid, scoring='f1', cv=3)
#        grid_search.fit(dataset, labels)
#
#        self.classifier[step] = grid_search.best_estimator_
#        logging.info(f"Best parameters: {grid_search.best_params_}")
#
#    def detection(self, window, step):
#        test = np.array(window.get_code())
#        test = self.scale.transform(test.reshape(1, -1))
#
#        if self.classifier[step]:
#            pred_proba = self.classifier[step].predict_proba(test)
#            pred_class = self.classifier[step].predict(test)
#            logging.debug("{}> pred_proba: {}, pred_class: {}".format(self.get_name(), pred_proba, pred_class))
#            return pred_class, list(pred_proba[0])
#        else:
#            logging.error("  => {} classifier not available for step {}".format(self.get_name(), step))
#            return [0], [0.5, 0.5]


##------------------------------------------------


#import sys
#import logging
#import numpy as np
#from sklearn.preprocessing import StandardScaler
#from lightgbm import LGBMClassifier
#from algorithms.algorithm import Algorithm
#from sklearn.model_selection import GridSearchCV
#
#class Algo2(Algorithm):
#    def __init__(self, name):
#        super().__init__(name)
#
#    def learning(self, windows, step):
#        # 학습 데이터를 가져오고, NumPy 배열로 변환
#        dataset = np.array(windows.get_dataset(step))
#        labels = windows.get_labels(step)
#
#        # 데이터를 표준화합니다.
#        self.scale = StandardScaler().fit(dataset)
#        dataset = self.scale.transform(dataset)
#
#        # GridSearchCV를 사용
#        param_grid = {
#            'learning_rate': [0.04, 0.075],  # 학습률 조정
#            'n_estimators': [100],          #  트리 개수
#            'max_depth': [3, 5, 7]        # 트리 깊이
#          #  'num_leaves' : [30, 50]        # 리프 개수
#        }
#
#        # GridSearchCV로 하이퍼파라미터 탐색
#        grid_search = GridSearchCV(LGBMClassifier(objective='binary'), param_grid, scoring='f1', cv=3)
#        grid_search.fit(dataset, labels)
#
#        # 최적의 모델을 classifier에 저장
#        self.classifier[step] = grid_search.best_estimator_
#        logging.info(f"Best parameters: {grid_search.best_params_}")
#
#    def detection(self, window, step):
#        # 예측할 데이터를 가져옵니다.
#        test = np.array(window.get_code())  # NumPy 배열로 변환
#        test = self.scale.transform(test.reshape(1, -1))  # 데이터를 2차원 배열로 변환 후 표준화
#
#        if self.classifier[step]:
#            # LightGBM 모델로 확률과 클래스를 예측
#            pred_proba = self.classifier[step].predict_proba(test)
#            pred_class = self.classifier[step].predict(test)
#
#            logging.debug("{}> pred_proba: {}, pred_class: {}".format(self.get_name(), pred_proba, pred_class))
#
#            # 예측된 클래스와 확률 반환
#            return pred_class, list(pred_proba[0])
#        else:
#            logging.error("  => {} classifier not available for step {}".format(self.get_name(), step))
#            return [0], [0.5, 0.5]



