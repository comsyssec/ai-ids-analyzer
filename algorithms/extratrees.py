import logging
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.preprocessing import StandardScaler
from algorithms.algorithm import Algorithm

class Extratrees(Algorithm):
    def __init__(self, name):
        super().__init__(name)  # 부모 클래스의 __init__ 메서드 호출
        self.scale = None  # 스케일러 변수 초기화

    def learning(self, windows, step):
        # Get the dataset for the current step
        self.scale, dataset = windows.get_dataset(step, scaler="standard")
        labels = windows.get_labels(step, dl=False)

        self.classifier[step] = ExtraTreesClassifier(n_estimators=100, random_state=42, n_jobs=-1)  # ExtraTreesClassifier 모델

        # Train the ExtraTrees classifier
        try:
            self.classifier[step] = self.classifier[step].fit(dataset, labels)
            logging.info("  => {} {} classifier is generated".format(self.get_name(), step))
        except:
            self.classifier[step] = None
            logging.info("  => {} {} classifier is not generated".format(self.get_name(), step))

    def detection(self, window, step):
        # Get the test data and standardize it
        test_data = window.get_code()
        test_data = self.scale.transform(test_data.reshape(1, -1))

        # Predict using the trained model
        if self.classifier[step]:
            prediction = self.classifier[step].predict(test_data)
            logging.debug("{}> pred: {}, ret: {}".format(self.get_name(), prediction[0], prediction[0]))
            return [prediction[0]], [prediction[0]]  # Returning prediction as both class and as a list for consistency
        else:
            return [0], [0, 1]
