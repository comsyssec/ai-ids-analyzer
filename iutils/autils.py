import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from algorithms.lightgbm import Lightgbm
from algorithms.xgboost import Xgboost
from algorithms.lstm import Lstm
from algorithms.cubedimae_ids import CubedimaeIds
from algorithms.cnn import Cnn
from algorithms.decision_tree import DecisionTree
from algorithms.naive_bayes import NaiveBayes
from algorithms.svm import Svm
from algorithms.extratrees import Extratrees
from algorithms.catboost import Catboost
from algorithms.random_forest import RandomForest
from algorithms.feedforward import Feedforward
from algorithms.rnn import Rnn
from algorithms.logistic_regression import LogisticRegression

def init_algorithms(model_manager):
    model_manager.add_algorithm(Lightgbm("lightgbm"))
    model_manager.add_algorithm(Xgboost("xgboost"))
    model_manager.add_algorithm(Lstm("lstm"))
    model_manager.add_algorithm(CubedimaeIds("cubedimae_ids"))
    model_manager.add_algorithm(Cnn("cnn"))
    model_manager.add_algorithm(DecisionTree("decision_tree"))
    model_manager.add_algorithm(NaiveBayes("naive_bayes"))
    model_manager.add_algorithm(Svm("svm"))
    model_manager.add_algorithm(Extratrees("extratrees"))
    model_manager.add_algorithm(Catboost("catboost"))
    model_manager.add_algorithm(RandomForest("random_forest"))
    model_manager.add_algorithm(Feedforward("feedforward"))
    model_manager.add_algorithm(Rnn("rnn"))
    model_manager.add_algorithm(LogisticRegression("logistic_regression"))

