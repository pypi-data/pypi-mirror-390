"""
Tests for DRUHG clustering algorithm
"""
import pickle
import numpy as np
import pandas as pd
from scipy.spatial import distance
from scipy import sparse
from scipy import stats
import pytest  #delete __init__.py or it wont work


from druhg import (DRUHG,
                   druhg)

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# from sklearn.cluster.tests.common import generate_clustered_data
import sklearn.datasets as datasets
from sklearn.datasets import make_blobs
from sklearn.utils import shuffle
from sklearn.preprocessing import StandardScaler
from scipy.stats import mode
from sklearn.metrics import adjusted_rand_score

from tempfile import mkdtemp
from functools import wraps

import warnings

_plot_graph = True
_not_fail_all = False

blobs, _ = datasets.make_blobs(n_samples=30, centers=[(-1., -1.), (1.0, 1.0)], cluster_std=0.25)
X = np.vstack([blobs])

X = [[ 0.92106143 , 0.90547575],
 [ 0.77740108,  0.74381424],
 [-0.54707238, -0.93632275],
 [ 1.14528332,  0.47395599],
 [-1.18154265, -0.86885681],
 [-0.99693863, -1.534588  ],
 [-0.6993809,  -1.18147767],
 [ 1.28328471,  0.77446717],
 [-0.69767129, -0.70035315],
 [ 1.0087693 ,  1.0576548 ],
 [ 0.6074741 ,  1.37124275],
 [ 1.27818319,  1.33145458],
 [ 1.16809938,  1.05568675],
 [-0.96391345, -0.76431969],
 [-0.97849489, -0.64393941],
 [-0.76445103, -0.92221768],
 [-0.66520734, -1.33962011],
 [-0.82256141, -1.23753227],
 [ 0.96583008,  0.87435429],
 [-1.46553152, -0.96775917],
 [-0.7730766 , -1.1289692 ],
 [ 1.37473563,  0.99939175],
 [ 1.45518458,  0.75611808],
 [ 1.145298  ,  0.91818625],
 [-1.04021956, -1.02153293],
 [ 1.23676014,  1.45337014],
 [ 1.02380103,  0.91979054],
 [-1.13063934, -1.43201801],
 [ 0.9759653 ,  1.19603341],
 [-0.82044957, -1.20135226]]

def test_splashes(filename=None):
    if filename is None:
        filename = test_splashes.__name__
    XX = np.array(X)
    for i in range(1, 15):
        print('HELLO', i)
        print(XX)
        dr = DRUHG(max_ranking=60, verbose=False)
        dr.fit(XX)
        dr.develop(XX)
        print('labels_', dr.labels_)

        if _plot_graph:
            plt.close('all')
            axis = dr.minimum_spanning_tree_.plot()
            axis.axhline(0, color='gray')
            axis.axvline(0, color='gray')
            axis.set_xlim(-20.0, 20.0)
            axis.set_ylim(-20.0, 20.0)
            plt.savefig(filename+str(i)+'.png')
        print('dr.new_data_', dr.new_data_)
        XX = np.array(dr.new_data_)


    assert _not_fail_all
