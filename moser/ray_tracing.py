import numpy as np
from core.index_heapq import IndexPq
from collections import deque
from itertools import product
from core import grd
import os

vp_grd = grd.from_ascii_grd(r'G:\毕设数据\模型-3-23\倾斜地层\incline_layervp.grd')

vp_data: np.ndarray = vp_grd.data

source_x = 0
source_y = 0
s = (source_x, source_y)

rows = vp_data.shape[0]
cols = vp_data.shape[1]
dx = vp_grd.x_size
dy = vp_grd.y_size

# tt, 计算最小走时
tt = np.empty_like(vp_data)
tt.fill(np.inf)
tt[s[0], s[1]] = 0

prev = np.empty_like(tt, dtype='O')
prev[s[0], s[1]] = s

# P set, 已知旅行时数据集
P = set()

# Q set, 未知旅行时数据集
Q = [(tt[i, j], (i, j)) for i in range(0, tt.shape[0]) for j in range(0, tt.shape[1])]
Q = IndexPq(Q)


def neighbor(node):
    i = node[0]
    j = node[1]

    def get_tt_value(i, j):
        if i < 0 or i >= tt.shape[0] or j < 0 or j >= tt.shape[1]:
            return None
        else:
            return tt[i, j]

    r = []

    def add_no_p(lst, i, j, flag=False):
        if flag == True:
            v = get_tt_value(i, j)
            if v is not None and v not in P:
                lst.append((v, (i, j)))
        else:
            v = tt[i, j]
            if v not in P:
                lst.append((v, (i, j)))

    if i == 0 or i == tt.shape[0] - 1 or j == 0 or j == tt.shape[1] - 1:
        add_no_p(r, i - 1, j, True)
        add_no_p(r, i - 1, j + 1, True)
        add_no_p(r, i, j + 1, True)
        add_no_p(r, i + 1, j + 1, True)
        add_no_p(r, i + 1, j, True)
        add_no_p(r, i + 1, j - 1, True)
        add_no_p(r, i, j - 1, True)
        add_no_p(r, i - 1, j - 1, True)
    else:
        add_no_p(r, i - 1, j)
        add_no_p(r, i - 1, j + 1)
        add_no_p(r, i, j + 1)
        add_no_p(r, i + 1, j + 1)
        add_no_p(r, i + 1, j)
        add_no_p(r, i + 1, j - 1)
        add_no_p(r, i, j - 1)
        add_no_p(r, i - 1, j - 1)
    return r


while Q:
    u = Q.pop()

    u = u[1]
    ns = neighbor(u)

    for node in ns:

        node = node[1]

        d = np.sqrt((u[0] - node[0])**2 + (u[1] - node[1])**2)
        v = vp_data[u[0], u[1]] + vp_data[node[0], node[1]]
        alt = tt[u[0], u[1]] + d / v
        if alt < tt[node[0], node[1]]:
            old = tt[node[0], node[1]]
            tt[node[0], node[1]] = alt
            prev[node[0], node[1]] = u
            Q.update((old, (node[0], node[1])), (alt, (node[0], node[1])))


dat = [(i, -j, tt[i, j]) for i in range(0, tt.shape[0]) for j in range(0, tt.shape[1])]

dat = list(map(lambda x: str(float(x[0])) + "   " + str(float(x[1])) + "   " + str(float(x[2])) + "\n", dat))

with open(r'../resource/incline_layer.dat', 'w+') as wf:
    wf.writelines(dat)







