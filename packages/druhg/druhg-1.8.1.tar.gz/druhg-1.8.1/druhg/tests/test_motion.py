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
import matplotlib.animation as animation

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


_test_motion = True
_plot_graph = 1

def test_motion_triangle(length=10., delta = -1., filename=None):
    if not _test_motion:
        return
    if filename is None:
        filename = test_motion_triangle.__name__

    # XX = [[0.,0.+delta],[0.,length+delta],[2.,length+delta]]
    XX = [[ 0.57735027,  0.],[-0.56735027,  0.],[ 0., 0.5]]
    XX = np.array(XX)
    dr = DRUHG(max_ranking=200, verbose=False)
    dr.develop(XX)
    np.set_printoptions(precision=2, suppress=True)
    i = 200
    while True:
        print(XX)
        print('new dp ' + str(i))
        print(dr.new_data_)
        print("{:.2f}".format(np.linalg.norm(dr.new_data_[1]-dr.new_data_[0])),
              "{:.2f}".format(np.linalg.norm(dr.new_data_[2]-dr.new_data_[0])),
              "{:.2f}".format(np.linalg.norm(dr.new_data_[1]-dr.new_data_[2])))
        if i == 0:
            break
        i -= 1
        XX = np.array(dr.new_data_)
        dr = DRUHG(max_ranking=200, verbose=False)
        dr.develop(XX)

    assert False
    return dr.new_data_

def test_motion_rectangle(length = 10., delta = -1., filename=None):
    if not _test_motion:
        return
    if filename is None:
        filename = test_motion_rectangle.__name__

    XX = [[0.,0.+delta],[1.,0.+delta],[0.,length+delta],[1.,length+delta],]
    XX = np.array(XX)
    dr = DRUHG(max_ranking=200, verbose=False)
    dr.develop(XX)
    print(XX)
    print ('new dp')
    print (dr.new_data_)

    assert False

def test_motion_speed(filename=None):
    if not _test_motion:
        return
    if filename is None:
        filename = test_motion_speed.__name__

    d2 = test_motion_triangle(2.)
    # d4 = test_motion_triangle(4.)

    # print(d4[0], 'and', d2[0], 'ratio', d4[0][1]/ d2[0][1])
    # assert d4[0][1] >= d2[0][1]

    assert False

def test_motion_collision(length=20.,filename=None):
    if not _test_motion:
        return
    if filename is None:
        filename = test_motion_collision.__name__

    XX = [[0.,0.],[1.,0.],[0.,-4.],
          [0., length], [1., length], [0., length+4.],
          ]
    XX = np.array(XX)
    dr = DRUHG(max_ranking=200, verbose=False)
    dr.frames_.animate(XX, frames=10, interval_ms=500, ylim=[-100,200])
    print('SUCCESS!!!!')
    assert False

def test_motion_animate_triangle(length=1.5, delta = -1.,filename=None):
    if not _test_motion:
        return
    if filename is None:
        filename = test_motion_animate_triangle.__name__

    XX = [[0.,0.+delta],[0.,length+delta],[1.,length+delta]]
    XX = np.array(XX)
    dr = DRUHG(max_ranking=200, verbose=False)
    dr.frames_.animate(XX, frames=100, interval_ms=500, xlim=[-20,20], ylim=[-20,20])
    print('SUCCESS!!!!')
    assert False

def test_motion_animate_rectangle(length=1.1, delta = -1.,filename=None):
    if not _test_motion:
        return
    if filename is None:
        filename = test_motion_animate_rectangle.__name__

    XX = [[0., 0.5 + delta], [1., 0. + delta], [0., length + delta], [1., length + delta], ]
    XX = np.array(XX)
    dr = DRUHG(max_ranking=200, verbose=False)
    dr.frames_.animate(XX, frames=100, interval_ms=500, xlim=[-20,20], ylim=[-20,20])
    print('SUCCESS!!!!')
    assert False

def test_motion_animate_1(length=3., delta = -1.,filename=None):
    if not _test_motion:
        return
    if filename is None:
        filename = test_motion_animate_triangle.__name__

    XX = [[0., 0. + delta], [0., length + delta], [2., length + delta]]
    XX = np.array(XX)
    dr = DRUHG(max_ranking=200, verbose=False)
    dr.frames_.animate(XX, frames=500, interval_ms=100, ylim=[-50,50])
    print('SUCCESS!!!!')
    assert False