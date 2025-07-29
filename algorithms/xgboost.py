######   XGBoost    ###### 


#import sys
#import logging
#from algorithms.algorithm import Algorithm

#class Algo1(Algorithm):
#    def __init__(self, name):
#        super().__init__(name)

#    # Please implement the following functions
#    # Concerning dataset, refer to the class TrainingSet
#    def learning(self, windows, step):
#        pass

#    def detection(self, window, step):
#        pass


############################################################

#import sys
#import logging
#import numpy as np
#from sklearn.preprocessing import StandardScaler
#from xgboost import XGBClassifier
#from algorithms.algorithm import Algorithm
#
#
#class Algo1(Algorithm):
#    def __init__(self, name):
#        super().__init__(name)
#
#    def learning(self, windows, step):
#        # Get the dataset for the current step
#        dataset = np.array(windows.get_dataset(step))
#       
#        # Standardize the features
#        self.scale = StandardScaler().fit(dataset)
#        dataset = self.scale.transform(dataset)
#       
#        # Get the labels
#        labels = windows.get_labels(step)
#       
#        # Initialize the XGBoost classifier
#        self.classifier[step] = XGBClassifier(objective='binary:logistic', n_estimators=100, learning_rate=0.1)
#
#        try:
#            # Train the model
#            self.classifier[step].fit(dataset, labels)
#            logging.info("  => {} {} classifier is generated".format(self.get_name(), step))
#        except Exception as e:
#            # Handle exceptions during training
#            self.classifier[step] = None
#            logging.error("  => {} {} classifier is not generated: {}".format(self.get_name(), step, e))
#
#    def detection(self, window, step):
#        # Get the test data and standardize it
#        test = np.array(window.get_code())
#        test = self.scale.transform(test.reshape(1, -1))
#
#        if self.classifier[step]:
#            # Predict probabilities and class
#            pred_proba = self.classifier[step].predict_proba(test)
#            pred_class = self.classifier[step].predict(test)
#           
#            logging.debug("{}> pred_proba: {}, pred_class: {}".format(self.get_name(), pred_proba, pred_class))
#           
#            # Return the predicted class and the probabilities
#            return pred_class, list(pred_proba[0])
#        else:
#            logging.error("  => {} classifier not available for step {}".format(self.get_name(), step))
#            return [0], [0.5, 0.5]

###--------------------------------------------------------------------------------------------------


import sys
import logging
import numpy as np
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from algorithms.algorithm import Algorithm


class Xgboost(Algorithm):
    def __init__(self, name):
        super().__init__(name)

    def learning(self, windows, step):
        # Get the dataset for the current step
        self.scale, dataset = windows.get_dataset(step, scaler="standard")
        labels = windows.get_labels(step, dl=False)
        
        # Calculate scale_pos_weight
        num_positive = np.sum(labels)
        num_negative = len(labels) - num_positive
        scale_pos_weight = num_negative / num_positive if num_positive > 0 else 1

       
        # Initialize the XGBoost classifier with updated hyperparameters
        self.classifier[step] = XGBClassifier(
            objective='binary:logistic',
            n_estimators=300,
            learning_rate=0.05,
            scale_pos_weight = scale_pos_weight
            
            
       #     max_depth=8,  
       #     min_child_weight=0.5  
        )

        try:
            # Train the model
            self.classifier[step].fit(dataset, labels)
            logging.info("  => {} {} classifier is generated".format(self.get_name(), step))
        except Exception as e:
            # Handle exceptions during training
            self.classifier[step] = None
            logging.error("  => {} {} classifier is not generated: {}".format(self.get_name(), step, e))

    def detection(self, window, step):
        # Get the test data and standardize it
        test = window.get_code()
        test = self.scale.transform(test.reshape(1, -1))

        if self.classifier[step]:
            # Predict probabilities and class
            pred_proba = self.classifier[step].predict_proba(test)
            pred_class = self.classifier[step].predict(test)
           
            logging.debug("{}> pred_proba: {}, pred_class: {}".format(self.get_name(), pred_proba, pred_class))
           
            # Return the predicted class and the probabilities
            return pred_class, list(pred_proba[0])
        else:
            logging.error("  => {} classifier not available for step {}".format(self.get_name(), step))
            return [0], [0.5, 0.5]


