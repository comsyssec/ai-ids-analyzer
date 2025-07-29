import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from metrics.num_of_benign_windows import NumOfBenignWindows
from metrics.true_positive import TruePositive
from metrics.true_negative import TrueNegative
from metrics.learning_time import LearningTime
from metrics.precision import Precision
from metrics.num_of_step_windows import NumOfStepWindows
from metrics.feature_importance import FeatureImportance
from metrics.test_packets import TestPackets
from metrics.detection_time import DetectionTime
from metrics.recall import Recall
from metrics.false_negative import FalseNegative
from metrics.num_of_test_samples import NumOfTestSamples
from metrics.accuracy import Accuracy
from metrics.false_positive import FalsePositive
from metrics.f1_score import F1Score

def init_metrics(result_reporter):
    result_reporter.add_metric(NumOfBenignWindows("num_of_benign_windows"))
    result_reporter.add_metric(TruePositive("true_positive"))
    result_reporter.add_metric(TrueNegative("true_negative"))
    result_reporter.add_metric(LearningTime("learning_time"))
    result_reporter.add_metric(Precision("precision"))
    result_reporter.add_metric(NumOfStepWindows("num_of_step_windows"))
    result_reporter.add_metric(FeatureImportance("feature_importance"))
    result_reporter.add_metric(TestPackets("test_packets"))
    result_reporter.add_metric(DetectionTime("detection_time"))
    result_reporter.add_metric(Recall("recall"))
    result_reporter.add_metric(FalseNegative("false_negative"))
    result_reporter.add_metric(NumOfTestSamples("num_of_test_samples"))
    result_reporter.add_metric(Accuracy("accuracy"))
    result_reporter.add_metric(FalsePositive("false_positive"))
    result_reporter.add_metric(F1Score("f1_score"))

