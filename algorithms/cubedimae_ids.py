from copy import deepcopy as copy
import os, sys
import types
import logging
import numpy as np

import tensorflow as tf
from tensorflow.keras import layers
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm
from algorithms.algorithm import Algorithm

THRESHOLD = 0.2


from copy import deepcopy as copy
import logging
import numpy as np
from scipy.spatial.distance import pdist, cdist

from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from tqdm import tqdm


class DimensionEstimator:
    def __repr__(self):
        return 'dimension estimator'
    
    def __call__(
            self,
            X,
            batch_count = 1000,
            exact = False,
            trim = False,
            truncate = False,
            divisions = 10
            ):
        if type(X) != np.ndarray:
            raise TypeError('Input must be a \'numpy.ndarray\'.')
        if X.dtype != np.float64:
            X = X.astype('float64')
        if X.ndim != 2:
            raise ValueError('The shape must be the dataset standard.')
        if not isinstance(batch_count, int):
            raise TypeError('\'batch_count\' should be an integer.')
        if batch_count < 1:
            raise ValueError('\'batch_count\' must be positive.')
        if not isinstance(exact, bool):
            raise TypeError('\'exact\' should be boolean.')
        if not isinstance(trim, bool):
            raise TypeError('\'trim\' should be boolean.')
        if not isinstance(truncate, bool):
            raise TypeError('\'truncate\' should be boolean.')
        if not isinstance(divisions, int):
            raise TypeError('\'divisions\' should be an integer.')
        if divisions < 2:
            raise ValueError('\'divisions\' must be greater than 1.')
        if divisions > 10000:
            raise ValueError('\'divisions\' greater than 10000 is not supported.')
        if truncate:
            retained_variance = 0.9
            logging.warning('The dataset is truncated at 90% total variance for faster computation. It may overtruncate those of few features.')
        else:
            retained_variance = None
        
        #trimmed
        if trim:
            logging.info('The dataset is trimmed by the isolation forest.')
            forest = IsolationForest()
            forest.fit(X)
            valid = forest.predict(X)
            valid = np.where(valid == 1, True, False)
            X = X[valid]
        
        #oriented
        pca = PCA(n_components = retained_variance, svd_solver = 'full')
        pca.fit(X)
        X = pca.transform(X)
        
        # A tile is always adjacent to all the others in the case of two divisions.
        if divisions == 2:
            binary = np.where(X >= 0, 1, -1)
            binary = binary.astype('int8')

            occupied = np.unique(binary, axis = 0)
            dimension = np.log(occupied.shape[0], dtype = 'float64') / np.log(2, dtype = 'float64')
            if exact:
                dimension = dimension.tolist()
            else:
                dimension = dimension.round().astype('int64')
                dimension = dimension.tolist()
            return dimension
            
        
        #quantized
        width = (X[:, 0].max(axis = 0) - X[:, 0].min(axis = 0)) / np.float64(divisions)
        if divisions % 2 != 0:
            tile = X / width
        else:
            tile = X / width - np.float64(0.5)
        tile = tile.round().astype('int64')
        tile = np.unique(tile, axis = 0)
        
        
        # - counted -

        batch = copy(np.array_split(tile, batch_count, axis = 0))
        if batch_count > tile.shape[0]:
            batch = batch[:tile.shape[0]]
        
        adjacency = []
        for l in tqdm(batch, colour = 'magenta'):
            
            distance = cdist(l, tile, metric = 'chebyshev')
            is_adjacent = np.isclose(distance, 1, atol = 0)
            
            adjacency_batch = is_adjacent.astype('int64')
            adjacency_batch = adjacency_batch.sum(axis = 1, dtype = 'int64')
            adjacency.append(adjacency_batch)
            
        adjacency = np.concatenate(adjacency, axis = 0)
        
        
        dimension = np.log(adjacency.mean(axis = 0) + 1, dtype = 'float64') / np.log(3, dtype = 'float64')
        if exact:
            dimension = dimension.tolist()
        else:
            dimension = dimension.round().astype('int64')
            dimension = dimension.tolist()
        return dimension



class CubedimaeIds(Algorithm):
    def __init__(self, name):
        super().__init__(name)

    def learning(self, windows, step):
        labels = windows.get_labels(step)
        features = len(windows.get_feature_names())
        
        #data
        self.scale, dataset = windows.get_dataset(step = 'all', select = 'benign', scaler="minmax")
        
        #dimension estimation
        estimator = DimensionEstimator()
        intrinsic_dim = estimator(dataset, trim = True)
        logging.info("intrinsic_dim: {}".format(intrinsic_dim))

        
        #model

        self.classifier[step] = tf.keras.Sequential()

        #encoder
        for lll in range(dataset.shape[1] - 3, intrinsic_dim, -3):
            self.classifier[step].add(layers.Dense(lll, activation = 'gelu', kernel_initializer = 'he_uniform'))
        self.classifier[step].add(layers.Dense(intrinsic_dim, activation='tanh', kernel_initializer = 'glorot_uniform'))
        
        #decoder
        for lll in range(intrinsic_dim + 3, dataset.shape[1], 3):
            self.classifier[step].add(layers.Dense(lll, activation='gelu', kernel_initializer = 'he_uniform'))
        self.classifier[step].add(layers.Dense(dataset.shape[1], activation='tanh', kernel_initializer = 'glorot_uniform'))
        
        #configure
        self.classifier[step].compile(
                optimizer = tf.keras.optimizers.Adam(learning_rate = 0.0001),
                loss = 'mse'
                )

        #train
        dataset_tf = tf.constant(dataset, dtype = 'float32')
        
        try:
            self.classifier[step].fit(
                    dataset_tf, dataset_tf,
                    epochs = 100,
                    shuffle = True
                    )
            logging.info("  => {} {} classifier is generated".format(self.get_name(), step))
        except:
            self.classifier[step] = None
            logging.info("  => {} {} classifier is not generated".format(self.get_name(), step))


    def detection(self, window, step):
        ret = 0    #necessary
        label = window.get_label(step)
        
        #data
        test = window.get_code()
        test = test.reshape([1, test.shape[0]])
        
        #processed
        test = self.scale.transform(test)

        test_tf = tf.constant(test, dtype = 'float32')
        if self.classifier[step]:

            pred_tf = self.classifier[step](test_tf)
            diff = score(pred_tf, test_tf)

            if diff >= THRESHOLD:
                ret = 1
            #logging.debug("{}> pred: {}, ret: {}".format(self.get_name(), pred_tf.numpy().tolist(), ret))
            return [ret], pred_tf[0].numpy().tolist()
        else:
            return [0], [0, 1]

def score(a, b):
    ret = None
    
    if a.shape[1] != b.shape[1]:
        ret = -1
    else:
        ret = tf.math.reduce_sum((a - b) ** 2, axis = 1)
        ret = tf.math.sqrt(ret)
    ret = ret[0]

    #logging.debug("ret: {}".format(ret.numpy().tolist()))
    return ret
