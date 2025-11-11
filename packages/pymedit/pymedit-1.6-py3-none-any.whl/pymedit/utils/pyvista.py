import numpy as np 

def stack_cell(arr):
    return np.hstack((np.ones((arr.shape[0],1),dtype=int)*arr.shape[1],arr))

import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Tableau des couleurs Medit (repris de material.c)
medit_colors = np.array([
    [0.1, 0.4, 0.9],  # 0 - blue
    [1.0, 0.0, 0.0],  # 1 - red
    [0.0, 1.0, 0.0],  # 2 - green
    [1.0, 1.0, 0.0],  # 3 - yellow
    [0.0, 1.0, 1.0],  # 4 - cyan
    [1.0, 0.5, 0.0],  # 5 - orange
    [0.5, 0.0, 1.0],  # 6 - violet
    [0.0, 0.0, 0.4],  # 7 - dark blue
    [0.0, 0.4, 0.0],  # 8 - dark green
    [0.4, 0.0, 0.0],  # 9 - dark red
    [1.0, 1.0, 0.5],  # 10
    [1.0, 0.5, 1.0],  # 11
    [1.0, 0.5, 0.5],  # 12
    [1.0, 0.5, 0.0],  # 13 - orange
    [1.0, 0.0, 1.0],  # 14
    [1.0, 0.0, 0.5],  # 15
    [0.5, 1.0, 1.0],  # 16
    [0.5, 1.0, 0.5],  # 17
    [0.5, 1.0, 0.0],  # 18
    [0.5, 0.5, 1.0],  # 19
    [0.5, 0.5, 0.5],  # 20 - grey
    [0.5, 0.5, 0.0],  # 21
    [0.5, 0.0, 0.5],  # 22
    [0.5, 0.0, 0.0],  # 23
    [0.0, 1.0, 0.5],  # 24
    [0.0, 0.5, 1.0],  # 25
    [0.0, 0.5, 0.5],  # 26
    [0.0, 0.5, 0.0],  # 27
    [0.0, 0.0, 0.5],  # 28
    [0.4, 0.4, 0.0],  # 29 - dark yellow
    [0.0, 0.4, 0.4],  # 30 - dark cyan
    [0.3, 0.7, 0.9],  # 31 - default blue
])


def get_cmap_medit(n_colors):
    color_array = np.vstack([medit_colors[i % len(medit_colors)] for i in range(n_colors+1)])
    cmap_big = ListedColormap(color_array)
    return cmap_big
# Crée la colormap matplotlib
cmap_medit = ListedColormap(medit_colors)
