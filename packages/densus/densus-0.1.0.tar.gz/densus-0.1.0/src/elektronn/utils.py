# System and Basic Utilities
import sys
import os
import pickle
import math
import pickle
import torch
import argparse
import sys
import os
import pickle
import time
import numpy as np
import torch
from itertools import zip_longest
import periodictable as pt
from copy import deepcopy
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import spatial
import copy
import numpy as np
import torch
import torch_geometric.data
import sys
import os
import pickle
import time
import numpy as np
import torch
from itertools import zip_longest
import periodictable as pt
from copy import deepcopy
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import spatial
import copy
import numpy as np
import torch
import torch_geometric.data
import numpy as np
import numpy as np
from scipy.spatial import cKDTree
from collections import defaultdict
import re
import gau2grid
import multiprocessing as mp

# Numeric and Scientific Computing
import numpy as np
import torch
import torch_geometric
from torch_scatter import scatter
from torch_geometric.nn import radius_graph
from e3nn.nn.models.gate_points_2101 import Network
from e3nn import o3
import gau2grid
from scipy import spatial

# ML Tracking
import wandb
import random
import argparse

# Date and Time
from datetime import date

# Logging
import logging

# Data Visualization
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Text Processing and Data Structures
import re
from collections import defaultdict
import copy

def coeff_unperm_gau2grid_density_kdtree_ml_only_v2(
    x, y, z, data, ml_y, rs, ldepb=False, perm=False
):
    import numpy as np
    import gau2grid as g2g
    from scipy import spatial

    # Ensure grid arrays are float64
    x = np.asarray(x, dtype=np.float64).flatten()
    y = np.asarray(y, dtype=np.float64).flatten()
    z = np.asarray(z, dtype=np.float64).flatten()
    xyz = np.vstack([x, y, z])

    # KDTree for the 3D points
    tree = spatial.cKDTree(xyz.T)

    ml_density = np.zeros_like(x, dtype=np.float64)

    # l-indexed arrays to dump specific contributions to density
    ml_density_per_l = np.array([np.zeros_like(x, dtype=np.float64) for _ in range(5)])

    # Extract data as numpy arrays
    pos_array = np.asarray(data.pos_orig.cpu().detach().numpy(), dtype=np.float64)
    ml_array = np.asarray(ml_y.cpu().detach().numpy(), dtype=np.float64)
    alpha_array = np.asarray(data.exp.cpu().detach().numpy(), dtype=np.float64)
    norm_array = np.asarray(data.norm.cpu().detach().numpy(), dtype=np.float64)

    for coords, ml_coeffs, alpha, norm in zip(pos_array, ml_array, alpha_array, norm_array):
        center = np.asarray(coords, dtype=np.float64).flatten()
        counter = 0
        for mul, l in rs:
            for j in range(mul):
                normal = float(norm[counter])
                if normal != 0:
                    exp = [float(alpha[counter])]
                    small = 1e-50
                    angstrom2bohr = 1.8897259886
                    bohr2angstrom = 1 / angstrom2bohr

                    pop_ml = ml_coeffs[counter : counter + (2 * l + 1)]
                    c_ml = np.asarray(pop_ml, dtype=np.float64) * normal / (2 * np.sqrt(2))
                    ml_full_coeffs = c_ml

                    max_c_scalar = float(np.amax(np.abs(ml_full_coeffs)))

                    # Ensure cutoff is finite and positive
                    cutoff = np.sqrt((-1 / exp[0]) * np.log(small / np.abs(max_c_scalar * normal)))
                    cutoff = np.clip(cutoff, 1e-12, 1e3)

                    close_indices = tree.query_ball_point(center, cutoff)
                    if len(close_indices) == 0:
                        counter += 2 * l + 1
                        continue

                    points = np.require(xyz[:, close_indices], requirements=["C", "A"])

                    ret_target = gau2grid.collocation(
                        points * angstrom2bohr, l, [1], exp, center * angstrom2bohr
                    )

                    # Permutation mapping if needed
                    psi4_2_e3nn = [
                        [0], [2, 0, 1], [4, 2, 0, 1, 3], [6, 4, 2, 0, 1, 3, 5],
                        [8, 6, 4, 2, 0, 1, 3, 5, 7], [10, 8, 6, 4, 2, 0, 1, 3, 5, 7, 9],
                        [12, 10, 8, 6, 4, 2, 0, 1, 3, 5, 7, 9, 11]
                    ]
                    e3nn_2_psi4 = [
                        [0], [1, 2, 0], [2, 3, 1, 4, 0], [3, 4, 2, 5, 1, 6, 0],
                        [4, 5, 3, 6, 2, 7, 1, 8, 0], [5, 6, 4, 7, 3, 8, 2, 9, 1, 10, 0],
                        [6, 7, 5, 8, 4, 9, 3, 10, 2, 11, 1, 12, 0]
                    ]

                    if perm:
                        ml_full_coeffs = np.array([ml_full_coeffs[k] for k in e3nn_2_psi4[l]], dtype=np.float64)

                    ml_scaled_components = (ml_full_coeffs * normal * ret_target["PHI"].T).T
                    ml_tot = np.sum(ml_scaled_components, axis=0)

                    ml_density[close_indices] += ml_tot
                    ml_density_per_l[l][close_indices] += ml_tot

                counter += 2 * l + 1

    if ldepb:
        return None, ml_density, None, ml_density_per_l
    else:
        return ml_density

def coeff_unperm_gau2grid_density_kdtree_ml_only(
    x, y, z, data, ml_y, rs, ldepb=False, perm=False
):
    import numpy as np
    import gau2grid as g2g
    from scipy import spatial

    xyz = np.vstack([x, y, z])
    tree = spatial.cKDTree(xyz.T)

    ml_density = np.zeros_like(x)

    # l-indexed arrays to dump specific contributions to density
    ml_density_per_l = np.array(
        [
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
        ]
    )

    for coords, full_coeffs, ml_coeffs, alpha, norm in zip(
        data.pos_orig.cpu().detach().numpy(),
        ml_y.cpu().detach().numpy(),
        ml_y.cpu().detach().numpy(),
        data.exp.cpu().detach().numpy(),
        data.norm.cpu().detach().numpy(),
    ):

        center = coords
        counter = 0
        for mul, l in rs:
            # print("Rs",mul,l)
            for j in range(mul):
                normal = norm[counter]
                if normal != 0:
                    exp = [alpha[counter]]

                    small = 1e-50
                    angstrom2bohr = 1.8897259886
                    bohr2angstrom = 1 / angstrom2bohr

                    pop_ml = ml_coeffs[counter : counter + (2 * l + 1)]
                    c_ml = pop_ml * normal / (2 * np.sqrt(2))
                    ml_full_coeffs = c_ml

                    max_c = np.amax(np.abs(ml_full_coeffs))

                    cutoff = (
                        np.sqrt((-1 / exp[0]) * np.log(small / np.abs(max_c * normal)))
                        * bohr2angstrom
                    )

                    close_indices = tree.query_ball_point(center, cutoff)

                    points = np.require(xyz[:, close_indices], requirements=["C", "A"])
                    ret_target = gau2grid.collocation(
                        points * angstrom2bohr, l, [1], exp, center * angstrom2bohr
                    )

                    ret_ml = g2g.collocation(
                        points * angstrom2bohr, l, [1], exp, center * angstrom2bohr
                    )
                    # ret_ml = g2g.collocation(points*angstrom2bohr, l, [1], exp, center)

                    # Now permute back to psi4 ordering
                    ##              s     p         d             f                 g                      h                           i
                    psi4_2_e3nn = [
                        [0],
                        [2, 0, 1],
                        [4, 2, 0, 1, 3],
                        [6, 4, 2, 0, 1, 3, 5],
                        [8, 6, 4, 2, 0, 1, 3, 5, 7],
                        [10, 8, 6, 4, 2, 0, 1, 3, 5, 7, 9],
                        [12, 10, 8, 6, 4, 2, 0, 1, 3, 5, 7, 9, 11],
                    ]
                    e3nn_2_psi4 = [
                        [0],
                        [1, 2, 0],
                        [2, 3, 1, 4, 0],
                        [3, 4, 2, 5, 1, 6, 0],
                        [4, 5, 3, 6, 2, 7, 1, 8, 0],
                        [5, 6, 4, 7, 3, 8, 2, 9, 1, 10, 0],
                        [6, 7, 5, 8, 4, 9, 3, 10, 2, 11, 1, 12, 0],
                    ]
                    if perm == True:
                        ml_full_coeffs = np.array(
                            [ml_full_coeffs[k] for k in e3nn_2_psi4[l]]
                        )

                    ml_scaled_components = (
                        ml_full_coeffs * normal * ret_target["PHI"].T
                    ).T
                    ml_tot = np.sum(ml_scaled_components, axis=0)

                    ml_density[close_indices] += ml_tot

                    # dump l-dependent contributions

                    ml_density_per_l[l][close_indices] += ml_tot

                counter += 2 * l + 1

    if ldepb:
        return target_density, ml_density, target_density_per_l, ml_density_per_l
    else:
        return ml_density


def coeff_unperm_gau2grid_density_kdtree_target_only(x, y, z, data, rs):
    """
    Compute target density using gau2grid collocation with KDTree indexing without permutation.

    Parameters:
    x (numpy.ndarray): Array of x-coordinates for the grid points.
    y (numpy.ndarray): Array of y-coordinates for the grid points.
    z (numpy.ndarray): Array of z-coordinates for the grid points.
    data (torch.Tensor): Input data containing various coefficients and properties.
    rs (list): List of tuples representing radial and angular indices (mul, l).

    Returns:
    numpy.ndarray: Computed target density values.
    """

    xyz = np.vstack([x, y, z])
    tree = cKDTree(xyz.T)

    target_density = np.zeros_like(x)

    for coords, full_coeffs, alpha, norm in zip(
        data.pos_orig.cpu().detach().numpy(),
        data.full_c.cpu().detach().numpy(),
        data.exp.cpu().detach().numpy(),
        data.norm.cpu().detach().numpy(),
    ):
        center = coords
        counter = 0

        for mul, l in rs:
            for j in range(mul):
                normal = norm[counter]

                if normal != 0:
                    exp = [alpha[counter]]

                    # Calculate cutoff radius
                    small = 1e-50
                    angstrom2bohr = 1.8897259886
                    bohr2angstrom = 1 / angstrom2bohr
                    target_full_coeffs = full_coeffs[counter : counter + (2 * l + 1)]
                    max_c = np.amax(np.abs(target_full_coeffs))
                    cutoff = (
                        np.sqrt((-1 / exp[0]) * np.log(small / np.abs(max_c * normal)))
                        * bohr2angstrom
                    )

                    # Find close indices within the cutoff radius
                    close_indices = tree.query_ball_point(center, cutoff)

                    # Perform gau2grid collocation
                    points = np.require(xyz[:, close_indices], requirements=["C", "A"])
                    ret_target = gau2grid.collocation(
                        points * angstrom2bohr, l, [1], exp, center * angstrom2bohr
                    )

                    # Do not permute the coefficients back to psi4 ordering
                    target_full_coeffs = np.array(target_full_coeffs)
                    scaled_components = (
                        target_full_coeffs * normal * ret_target["PHI"].T
                    ).T
                    target_tot = np.sum(scaled_components, axis=0)

                    # Update target density
                    target_density[close_indices] += target_tot

                counter += 2 * l + 1

    return target_density


def gau2grid_density_kdtree_(x, y, z, data, ml_y, rs, ldepb=False):
    """
    Compute density using gau2grid collocation with KDTree indexing.

    This function computes the electron density using gau2grid collocation method,
    employing KDTree indexing for efficient neighbor searching. The density is computed
    based on the provided data, expansion coefficients, and radial basis functions.

    Parameters:
    x (numpy.ndarray): Array of x-coordinates for the grid points.
    y (numpy.ndarray): Array of y-coordinates for the grid points.
    z (numpy.ndarray): Array of z-coordinates for the grid points.
    data (torch.Tensor): Input data containing various coefficients and properties.
    ml_y (torch.Tensor): Machine-learning predicted coefficients.
    rs (list): List of tuples representing radial and angular indices (mul, l).
    ldepb (bool, optional): Whether to return l-dependent contributions. Default is False.

    Returns:
    tuple: A tuple containing the following elements:
        - target_density (numpy.ndarray): Computed target density values.
        - ml_density (numpy.ndarray): Computed machine-learning density values.
        - target_density_per_l (numpy.ndarray, optional): Array of l-dependent contributions to target density.
        - ml_density_per_l (numpy.ndarray, optional): Array of l-dependent contributions to machine-learning density.
    """

    # note, this takes x, y and z as flattened arrays
    # r = np.array(np.sqrt(np.square(x) + np.square(y) + np.square(z)))
    xyz = np.vstack([x, y, z])
    tree = spatial.cKDTree(xyz.T)

    ml_density = np.zeros_like(x)
    target_density = np.zeros_like(x)

    # l-indexed arrays to dump specific contributions to density
    ml_density_per_l = np.array(
        [
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
        ]
    )
    target_density_per_l = np.array(
        [
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
        ]
    )
    # rs = [(19, 0), (5, 1), (5, 2), (3, 3), (1, 3)]

    for coords, full_coeffs, iso_coeffs, ml_coeffs, alpha, norm in zip(
        data.pos_orig.cpu().detach().numpy(),
        data.full_c.cpu().detach().numpy(),
        data.iso_c.cpu().detach().numpy(),
        ml_y.cpu().detach().numpy(),
        data.exp.cpu().detach().numpy(),
        data.norm.cpu().detach().numpy(),
    ):
        center = coords
        counter = 0
        for mul, l in rs:  #!!!
            # print("Rs",mul,l)
            for j in range(mul):
                normal = norm[counter]
                if normal != 0:
                    exp = [alpha[counter]]

                    small = 1e-50
                    angstrom2bohr = 1.8897259886
                    bohr2angstrom = 1 / angstrom2bohr

                    target_full_coeffs = full_coeffs[counter : counter + (2 * l + 1)]

                    pop_ml = ml_coeffs[counter : counter + (2 * l + 1)]
                    c_ml = pop_ml * normal / (2 * np.sqrt(2))
                    ml_full_coeffs = c_ml + iso_coeffs[counter : counter + (2 * l + 1)]

                    target_max = np.amax(np.abs(target_full_coeffs))
                    ml_max = np.amax(np.abs(ml_full_coeffs))
                    max_c = np.amax(np.array([target_max, ml_max]))

                    cutoff = (
                        np.sqrt((-1 / exp[0]) * np.log(small / np.abs(max_c * normal)))
                        * bohr2angstrom
                    )

                    close_indices = tree.query_ball_point(center, cutoff)
                    # print("cutoff",cutoff)
                    # print(xyz.shape)
                    # print(l,len(close_indices))
                    points = np.require(xyz[:, close_indices], requirements=["C", "A"])

                    ret_target = gau2grid.collocation(
                        points * angstrom2bohr, l, [1], exp, center * angstrom2bohr
                    )
                    ret_ml = gau2grid.collocation(
                        points * angstrom2bohr, l, [1], exp, center * angstrom2bohr
                    )

                    # Now permute back to psi4 ordering
                    ##              s     p         d             f                 g                      h                           i
                    psi4_2_e3nn = [
                        [0],
                        [2, 0, 1],
                        [4, 2, 0, 1, 3],
                        [6, 4, 2, 0, 1, 3, 5],
                        [8, 6, 4, 2, 0, 1, 3, 5, 7],
                        [10, 8, 6, 4, 2, 0, 1, 3, 5, 7, 9],
                        [12, 10, 8, 6, 4, 2, 0, 1, 3, 5, 7, 9, 11],
                    ]
                    e3nn_2_psi4 = [
                        [0],
                        [1, 2, 0],
                        [2, 3, 1, 4, 0],
                        [3, 4, 2, 5, 1, 6, 0],
                        [4, 5, 3, 6, 2, 7, 1, 8, 0],
                        [5, 6, 4, 7, 3, 8, 2, 9, 1, 10, 0],
                        [6, 7, 5, 8, 4, 9, 3, 10, 2, 11, 1, 12, 0],
                    ]

                    target_full_coeffs = np.array(
                        [target_full_coeffs[k] for k in e3nn_2_psi4[l]]
                    )
                    ml_full_coeffs = np.array(
                        [ml_full_coeffs[k] for k in e3nn_2_psi4[l]]
                    )

                    # target_full_coeffs = full_coeffs[counter:counter+(2*l + 1)]
                    scaled_components = (
                        target_full_coeffs * normal * ret_target["PHI"].T
                    ).T
                    target_tot = np.sum(scaled_components, axis=0)

                    # pop_ml = ml_coeffs[counter:counter+(2*l + 1)]
                    # c_ml = pop_ml * normal / (2 * np.sqrt(2))
                    # target_delta_coeffs = delta_coeffs[counter:counter+(2*l + 1)]
                    # ml_full_coeffs = target_full_coeffs + c_ml - target_delta_coeffs
                    ml_scaled_components = (
                        ml_full_coeffs * normal * ret_target["PHI"].T
                    ).T
                    ml_tot = np.sum(ml_scaled_components, axis=0)

                    target_density[close_indices] += target_tot
                    ml_density[close_indices] += ml_tot

                    # dump l-dependent contributions

                    target_density_per_l[l][close_indices] += target_tot
                    ml_density_per_l[l][close_indices] += ml_tot

                counter += 2 * l + 1

    if ldepb:
        return target_density, ml_density, target_density_per_l, ml_density_per_l
    else:
        return target_density, ml_density


# I will assume that this is the old one and the one with DOCSTRINGS is the new one
# TODO: @luisa double check and remove this function
def _get_scalar_density_comparisons(
    data, y_ml, Rs, spacing=0.5, buffer=2.0, ldep=False
):
    """
    Compute various density comparison metrics between target and machine-learning densities.

    This function generates a grid of points based on input data, computes densities using gau2grid collocation,
    and then calculates several metrics to compare target and machine-learning densities. These metrics include
    electron population comparisons, relative error, and the Integral Similarity (I) index.

    Parameters:
    data (torch.Tensor): Input data containing various coefficients and properties.
    y_ml (torch.Tensor): Machine-learning predicted coefficients.
    Rs (list): List of tuples representing radial and angular indices (mul, l).
    spacing (float, optional): Spacing between grid points. Default is 0.5.
    buffer (float, optional): Additional buffer space around the data's bounding box. Default is 2.0.
    ldep (bool, optional): Whether to compute l-dependent contributions. Default is False.

    Returns:
    tuple: A tuple containing the following elements:
        - num_ele_target (float): Total number of electrons estimated from the target density.
        - num_ele_ml (float): Total number of electrons estimated from the machine-learning density.
        - bigI (float): Integral Similarity (I) index.
        - ep (float): Relative error in percentage between machine-learning and target densities.
        - ep_per_l (numpy.ndarray, optional): Array of l-dependent relative errors if ldep is True.
    """

    # generate grid in xyz input units (angstroms)
    x, y, z, vol, x_spacing, y_spacing, z_spacing = generate_grid(
        data, spacing=spacing, buffer=buffer
    )
    # get density on grid

    # l-dependent eps
    ep_per_l = np.zeros(len(Rs))

    if ldep:
        target_density, ml_density, target_density_per_l, ml_density_per_l = (
            gau2grid_density_kdtree_(
                x.flatten(), y.flatten(), z.flatten(), data, y_ml, Rs, ldepb=ldep
            )
        )
        # target_density, ml_density, target_density_per_l, ml_density_per_l = gau2grid_density_kdtree_lpop_scale(x.flatten(),y.flatten(),z.flatten(),data,y_ml,Rs, ldepb=ldep)
        # fill l-dependent eps in this case
        for l in range(len(Rs)):
            ep_per_l[l] = (
                100
                * np.sum(np.abs(ml_density_per_l[l] - target_density_per_l[l]))
                / np.sum(target_density)
            )

    else:
        target_density, ml_density = gau2grid_density_kdtree_(
            x.flatten(), y.flatten(), z.flatten(), data, y_ml, Rs, ldepb=ldep
        )

    # density is in e-/bohr**3
    angstrom2bohr = 1.8897259886
    bohr2angstrom = 1 / angstrom2bohr

    ep = 100 * np.sum(np.abs(ml_density - target_density)) / np.sum(target_density)

    num_ele_target = np.sum(target_density) * vol * angstrom2bohr**3
    num_ele_ml = np.sum(ml_density) * vol * angstrom2bohr**3

    numer = np.sum((ml_density - target_density) ** 2)
    denom = np.sum(ml_density**2) + np.sum(target_density**2)
    bigI = numer / denom

    if ldep:
        return num_ele_target, num_ele_ml, bigI, ep, ep_per_l

    else:
        return num_ele_target, num_ele_ml, bigI, ep


def get_iso_permuted_dataset(picklefile, **atm_iso):

    dataset = []

    for molecule in pickle.load(open(picklefile, "rb")):
        pos = molecule["pos"]
        z = molecule["type"].unsqueeze(1)
        x = molecule["onehot"]
        c = molecule["coefficients"]
        n = molecule["norms"]
        exp = molecule["exponents"]

        full_c = copy.deepcopy(c)
        iso_c = torch.zeros_like(c)

        # Extract atomic number information
        atomic_numbers = z.squeeze().tolist()

        pop = torch.where(n != 0, c * 2 * np.sqrt(2) / n, n)

        # Permute positions: YZX -> XYZ
        p_pos = copy.deepcopy(pos)
        p_pos[:, 0] = pos[:, 1]
        p_pos[:, 1] = pos[:, 2]
        p_pos[:, 2] = pos[:, 0]

        dataset += [
            torch_geometric.data.Data(
                pos=p_pos.to(torch.float32),
                pos_orig=pos.to(torch.float32),
                z=z.to(torch.float32),
                x=x.to(torch.float32),
                y=pop.to(torch.float32),
                c=c.to(torch.float32),
                full_c=full_c.to(torch.float32),
                iso_c=iso_c.to(torch.float32),
                exp=exp.to(torch.float32),
                norm=n.to(torch.float32),
                atomic_numbers=atomic_numbers,
            )
        ]

    return dataset


def lossPerChannel(y_ml, y_target, Rs):
    """
    Compute loss and percentage deviation per channel.

    This function computes the loss and percentage deviation per channel for the predicted machine-learning coefficients
    (`y_ml`) compared to the target coefficients (`y_target`). The channels are defined by a list of radial and angular
    indices (Rs) that specify the number of terms per angular momentum level.

    Parameters:
    y_ml (torch.Tensor): Predicted machine-learning coefficients.
    y_target (torch.Tensor): Target coefficients for comparison.
    Rs (list, optional): List of tuples representing radial and angular indices (mul, l). Default is [(12, 0), (5, 1), (4, 2), (2, 3), (1, 4)].

    Returns:
    tuple: A tuple containing the following elements:
        - loss_perChannel_list (numpy.ndarray): Array of loss values per channel.
        - pct_deviation_list (numpy.ndarray): Array of percentage deviation values per channel.
    """
    err = y_ml - y_target
    pct_dev = torch.div(err.abs(), y_target)
    loss_perChannel_list = np.zeros(len(Rs))
    pct_deviation_list = np.zeros(len(Rs))
    normalization = err.sum() / err.mean()

    counter = 0
    for mul, l in Rs:
        if l == 0:
            temp_loss = err[:, :mul].pow(2).sum().abs() / normalization
        else:
            temp_loss = (
                err[:, counter : counter + mul * (2 * l + 1)].pow(2).sum().abs()
                / normalization
            )

        loss_perChannel_list[l] += temp_loss.detach().cpu().numpy()
        pct_deviation_list[l] += (
            pct_dev[:, counter : counter + mul * (2 * l + 1)]
            .sum()
            .detach()
            .cpu()
            .numpy()
        )

        counter += mul * (2 * l + 1)

    return loss_perChannel_list, pct_deviation_list


def read_basis_data(filename, marker="****"):

    element_counts = defaultdict(lambda: defaultdict(int))

    with open(filename, "r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith(marker):
            try:
                current_element = lines[i + 1].strip().split()[0]
            except:
                pass
        else:
            match = re.match(r"([SPDFG])\s+(\d+)", line)
            if match:
                letter, number = match.groups()
                element_counts[current_element][letter] += int(number)

    element_sum_dict = {
        element: list(data.items()) for element, data in element_counts.items()
    }

    return element_sum_dict


def read_files_in_directory(directory, file_extension):
    targetdir = os.getcwd() if directory == "current" else directory
    valid_atom_symbols = set()

    for filename in os.listdir(targetdir):
        if filename.endswith(file_extension):
            full_path = os.path.join(targetdir, filename)
            with open(full_path, "r") as file:
                valid_atom_symbols.update(
                    match.group(1).upper() + match.group(2).lower()
                    for line in file
                    if (match := re.match(r"^\s*([A-Za-z]{1})([A-Za-z]{0,1})\s", line))
                )

    return list(valid_atom_symbols)



def flatten_list(nested_list):
    """Flatten an arbitrarily nested list, without recursion (to avoid
    stack overflows). Returns a new list, the original list is unchanged.
    >> list(flatten_list([1, 2, 3, [4], [], [[[[[[[[[5]]]]]]]]]]))
    [1, 2, 3, 4, 5]
    >> list(flatten_list([[1, 2], 3]))
    [1, 2, 3]
    """
    nested_list = deepcopy(nested_list)

    while nested_list:
        sublist = nested_list.pop(0)

        if isinstance(sublist, list):
            nested_list = sublist + nested_list
        else:
            yield sublist


def get_densities(filepath, dens_file, elements, num_atoms):
    """
    inputs:
    - density file
    - number of atoms

    returns:
    - shape [N, X] list of basis function coefficients, where X is the number of basis functions per atom
    """
    ## get density coefficients for each atom
    ## ordered in ascending l order
    ## also get Rs_out for each atom
    dens_file = filepath + "/" + dens_file

    basis_coeffs = []
    basis_exponents = []
    basis_norms = []
    num_basis_func = []
    Rs_outs = []
    for l in range(0, 20):
        flag = 0
        atom_index = -1
        counter = 0
        multiplicity = 0
        with open(dens_file, "r") as density_file:
            for line in density_file:
                if flag == 1:
                    split = line.split()
                    if int(split[0]) == l:
                        basis_coeffs[atom_index].append(float(split[1]))
                        basis_exponents[atom_index].append(float(split[2]))
                        basis_norms[atom_index].append(float(split[3]))
                        multiplicity += 1
                    counter += 1
                    if counter == num_lines:
                        flag = 0
                        if multiplicity != 0:
                            Rs_outs[atom_index].append((multiplicity // (2 * l + 1), l))
                if "functions" in line:
                    num_lines = int(line.split()[3])
                    num_basis_func.append(num_lines)
                    counter = 0
                    multiplicity = 0
                    flag = 1
                    atom_index += 1
                    # if (l == l):
                    if l == 0:
                        basis_coeffs.append([])
                        basis_exponents.append([])
                        basis_norms.append([])
                        Rs_outs.append([])

    # break coefficients list up into l-based vectors
    newbasis_coeffs = []
    newbasis_exponents = []
    newbasis_norms = []
    atom_index = -1
    for atom in Rs_outs:
        atom_index += 1
        counter = 0
        newbasis_coeffs.append([])
        newbasis_exponents.append([])
        newbasis_norms.append([])
        for Rs in atom:
            number = Rs[0]
            l = Rs[1]
            for i in range(0, number):
                newbasis_coeffs[atom_index].append(
                    basis_coeffs[atom_index][counter : counter + (2 * l + 1)]
                )
                newbasis_exponents[atom_index].append(
                    basis_exponents[atom_index][counter : counter + (2 * l + 1)]
                )
                newbasis_norms[atom_index].append(
                    basis_norms[atom_index][counter : counter + (2 * l + 1)]
                )
                counter += 2 * l + 1

    Rs_out_list = []
    elementdict = {}
    for i, elem in enumerate(elements):
        if elem not in elementdict:
            elementdict[elem] = Rs_outs[i]
            Rs_out_list.append(Rs_outs[i])

    """
    #psi4
    S: 0	
    P: 0, +1, -1	
    D: 0, +1, -1, +2, -2	
    F: 0, +1, -1, +2, -2, +3, -3	
    G: 0, +1, -1, +2, -2, +3, -3, +4, -4
    H: 0, +1, -1, +2, -2, +3, -3, +4, -4, +5, -5
    I: 0, +1, -1, +2, -2, +3, -3, +4, -4, +5, -5, +6, -6

    #e3nn (wikipedia)
    S: 0	
    P: -1, 0, +1	
    D: -2, -1, 0, +1, +2	
    F: -3, -2, -1, 0, +1, +2, +3	
    G: -4, -3, -2, -1, 0, +1, +2, +3, +4
    H: -5, -4, -3, -2, -1, 0, +1, +2, +3, +4, +5
    I: -6, -5, -4, -3, -2, -1, 0, +1, +2, +3, +4, +5, +6
    """

    ##              s     p         d             f                 g                      h                           i
    psi4_2_e3nn = [
        [0],
        [2, 0, 1],
        [4, 2, 0, 1, 3],
        [6, 4, 2, 0, 1, 3, 5],
        [8, 6, 4, 2, 0, 1, 3, 5, 7],
        [10, 8, 6, 4, 2, 0, 1, 3, 5, 7, 9],
        [12, 10, 8, 6, 4, 2, 0, 1, 3, 5, 7, 9, 11],
    ]

    """
    test = [[0],[0, +1, -1],[0, +1, -1, +2, -2],[0, +1, -1, +2, -2, +3, -3],	
            [0, +1, -1, +2, -2, +3, -3, +4, -4]]
    for i, item in enumerate(test):
        l = (len(item)-1)//2
        print (l)
        test[i] = [item[i] for i in psi4_2_e3nn[l]]
    """

    # change convention from psi4 to e3nn
    for i, atom in enumerate(newbasis_coeffs):
        for j, item in enumerate(atom):
            l = (len(item) - 1) // 2
            if l > 6:
                raise ValueError("L is too high. Currently only supports L<7")
            newbasis_coeffs[i][j] = [item[k] for k in psi4_2_e3nn[l]]

    return newbasis_coeffs, newbasis_exponents, newbasis_norms, Rs_outs


def get_coordinates(filepath, inputfile):
    """
    reads in coordinates and atomic number from psi4 input file

    returns:
    -shape [N, 3] numpy array of points
    -shape [N] numpy array of masses
    -shape [N] list of element symbols
    """
    # read in coords and atomic numbers
    inputfile = filepath + "/" + inputfile

    if not os.path.exists(inputfile):
        inputfile = inputfile + ".xyz"

    points = np.loadtxt(inputfile, skiprows=2, usecols=range(1, 4))
    numatoms = len(points)
    elements = np.genfromtxt(inputfile, skip_header=2, usecols=0, dtype="str")
    atomic_numbers = [getattr(pt, i).number for i in elements]
    unique_elements = len(np.unique(atomic_numbers))
    onehot = np.zeros((numatoms, unique_elements))

    # get one hot vector
    weighted_onehot = onehot
    typedict = {}
    counter = -1
    for i, num in enumerate(atomic_numbers):
        if num not in typedict:
            # dictionary: key = atomic number
            # value = 0,1,2,3 (ascending types)
            counter += 1
            typedict[num] = counter
        weighted_onehot[i, typedict[num]] = num

    # print(weighted_onehot)

    return points, numatoms, atomic_numbers, elements, weighted_onehot


def generate_grid(data, spacing=0.5, buffer=2.0):
    """
    Generate a 3D grid based on input data's position information.

    This function generates a 3D grid of points within a specified volume.
    The grid is defined based on the minimum and maximum coordinates of the input data's positions,
    with optional additional buffer space.

    Parameters:
    data (torch.Tensor): Input data containing positions (assumed to be a tensor with 'pos_orig' attribute).
    spacing (float, optional): Spacing between grid points. Default is 0.5.
    buffer (float, optional): Additional buffer space around the data's bounding box. Default is 2.0.

    Returns:
    tuple: A tuple containing the following elements:
        - x (numpy.ndarray): Array of x-coordinates of the grid points.
        - y (numpy.ndarray): Array of y-coordinates of the grid points.
        - z (numpy.ndarray): Array of z-coordinates of the grid points.
        - vol (float): Volume of each grid cell.
        - x_spacing (float): Spacing between x-coordinates of adjacent grid points.
        - y_spacing (float): Spacing between y-coordinates of adjacent grid points.
        - z_spacing (float): Spacing between z-coordinates of adjacent grid points.
    """
    buf = buffer
    xmin, xmax, ymin, ymax, zmin, zmax = find_min_max(
        data.pos_orig.cpu().detach().numpy()
    )

    x_points = 2*(int((xmax - xmin + 2 * buf) / spacing) + 1)
    y_points = 2*(int((ymax - ymin + 2 * buf) / spacing) + 1)
    z_points = 2*(int((zmax - zmin + 2 * buf) / spacing) + 1)

    npoints = int((x_points + y_points + z_points) / 3)

    xlin = np.linspace(xmin - buf, xmax + buf, npoints)
    ylin = np.linspace(ymin - buf, ymax + buf, npoints)
    zlin = np.linspace(zmin - buf, zmax + buf, npoints)

    x_spacing = xlin[1] - xlin[0]
    y_spacing = ylin[1] - ylin[0]
    z_spacing = zlin[1] - zlin[0]
    vol = x_spacing * y_spacing * z_spacing

    x, y, z = np.meshgrid(xlin, ylin, zlin, indexing="ij")

    return x, y, z, vol, x_spacing, y_spacing, z_spacing


def find_min_max(coords):
    xmin, xmax = coords[0, 0], coords[0, 0]
    ymin, ymax = coords[0, 1], coords[0, 1]
    zmin, zmax = coords[0, 2], coords[0, 2]

    for coord in coords:
        if coord[0] < xmin:
            xmin = coord[0]
        if coord[0] > xmax:
            xmax = coord[0]
        if coord[1] < ymin:
            ymin = coord[1]
        if coord[1] > ymax:
            ymax = coord[1]
        if coord[2] < zmin:
            zmin = coord[2]
        if coord[2] > zmax:
            zmax = coord[2]

    return xmin, xmax, ymin, ymax, zmin, zmax


def unperm_gau2grid_density_kdtree_target_only(x, y, z, data, rs):
    """
    Compute target density using gau2grid collocation with KDTree indexing without permutation.

    Parameters:
    x (numpy.ndarray): Array of x-coordinates for the grid points.
    y (numpy.ndarray): Array of y-coordinates for the grid points.
    z (numpy.ndarray): Array of z-coordinates for the grid points.
    data (torch.Tensor): Input data containing various coefficients and properties.
    rs (list): List of tuples representing radial and angular indices (mul, l).

    Returns:
    numpy.ndarray: Computed target density values.
    """

    xyz = np.vstack([x, y, z])
    tree = cKDTree(xyz.T)

    target_density = np.zeros_like(x)

    for coords, full_coeffs, iso_coeffs, alpha, norm in zip(
        data.pos_orig.cpu().detach().numpy(),
        data.full_c.cpu().detach().numpy(),
        data.iso_c.cpu().detach().numpy(),
        data.exp.cpu().detach().numpy(),
        data.norm.cpu().detach().numpy(),
    ):
        center = coords
        counter = 0

        for mul, l in rs:
            for j in range(mul):
                normal = norm[counter]

                if normal != 0:
                    exp = [alpha[counter]]

                    # Calculate cutoff radius
                    small = 1e-50
                    angstrom2bohr = 1.8897259886
                    bohr2angstrom = 1 / angstrom2bohr
                    target_full_coeffs = full_coeffs[counter : counter + (2 * l + 1)]
                    max_c = np.amax(np.abs(target_full_coeffs))
                    cutoff = (
                        np.sqrt((-1 / exp[0]) * np.log(small / np.abs(max_c * normal)))
                        * bohr2angstrom
                    )

                    # Find close indices within the cutoff radius
                    close_indices = tree.query_ball_point(center, cutoff)

                    # Perform gau2grid collocation
                    points = np.require(xyz[:, close_indices], requirements=["C", "A"])
                    ret_target = gau2grid.collocation(
                        points * angstrom2bohr, l, [1], exp, center * angstrom2bohr
                    )

                    # Do not permute the coefficients back to psi4 ordering
                    target_full_coeffs = np.array(target_full_coeffs)
                    scaled_components = (
                        target_full_coeffs * normal * ret_target["PHI"].T
                    ).T
                    target_tot = np.sum(scaled_components, axis=0)

                    # Update target density
                    target_density[close_indices] += target_tot

                counter += 2 * l + 1

    return target_density


def visualize_target_density(x, y, z, target_density, points):
    rows = 1
    cols = 2
    specs = [[{"is_3d": True} for i in range(cols)] for j in range(rows)]

    fig = make_subplots(
        rows=rows, cols=cols, specs=specs, subplot_titles=("Target Density",)
    )

    fig.update_layout(
        height=600,
        width=1200,
    )

    traces = []
    traces.append(
        go.Volume(
            x=x.flatten(),
            y=y.flatten(),
            z=z.flatten(),
            value=target_density.flatten(),
            isomin=0.15,
            isomax=0.2,
            colorscale="Blues",
            opacity=0.1,  # needs to be small to see through all surfaces
            surface_count=10,  # needs to be a large number for good volume rendering
            name="Target Density",
        )
    )

    fig.add_trace(traces[0], row=1, col=1)

    xs = points.cpu().numpy()[:, 0]
    ys = points.cpu().numpy()[:, 1]
    zs = points.cpu().numpy()[:, 2]
    geom = go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="markers",
        marker=dict(size=3, color="Black", opacity=1.0),
    )
    fig.add_trace(geom, row=1, col=1)

    fig.update_layout(showlegend=True)
    fig.write_html("newest_testdensity.html")
    fig.show()


def get_scalar_density_comparisons(data, y_ml, Rs, spacing=0.5, buffer=2.0, ldep=False):
    import numpy as np

    # generate grid in xyz input units (angstroms)
    x, y, z, vol, x_spacing, y_spacing, z_spacing = generate_grid(
        data, spacing=spacing, buffer=buffer
    )
    # get density on grid

    # l-dependent eps
    ep_per_l = np.zeros(len(Rs))

    if ldep:
        target_density, ml_density, target_density_per_l, ml_density_per_l = (
            unperm_gau2grid_density_kdtree(
                x.flatten(), y.flatten(), z.flatten(), data, y_ml, Rs, ldepb=ldep
            )
        )
        # target_density, ml_density, target_density_per_l, ml_density_per_l = gau2grid_density_kdtree_lpop_scale(x.flatten(),y.flatten(),z.flatten(),data,y_ml,Rs, ldepb=ldep)
        # fill l-dependent eps in this case
        for l in range(len(Rs)):
            ep_per_l[l] = (
                100
                * np.sum(np.abs(ml_density_per_l[l] - target_density_per_l[l]))
                / np.sum(target_density)
            )

    else:
        target_density, ml_density = unperm_gau2grid_density_kdtree(
            x.flatten(), y.flatten(), z.flatten(), data, y_ml, Rs, ldepb=ldep
        )
        # target_density, ml_density = gau2grid_density_kdtree_lpop_scale(x.flatten(),y.flatten(),z.flatten(),data,y_ml,Rs,ldepb=ldep)

    # density is in e-/bohr**3
    angstrom2bohr = 1.8897259886
    bohr2angstrom = 1 / angstrom2bohr

    # n_ele = np.sum(data.z.cpu().detach().numpy())
    # ep = 100 * vol * (angstrom2bohr**3) * np.sum(np.abs(target_density - ml_density)) / n_ele
    ep = 100 * np.sum(np.abs(ml_density - target_density)) / np.sum(target_density)

    num_ele_target = np.sum(target_density) * vol * angstrom2bohr**3
    num_ele_ml = np.sum(ml_density) * vol * angstrom2bohr**3

    numer = np.sum((ml_density - target_density) ** 2)
    denom = np.sum(ml_density**2) + np.sum(target_density**2)
    bigI = numer / denom

    if ldep:
        return num_ele_target, num_ele_ml, bigI, ep, ep_per_l

    else:
        return num_ele_target, num_ele_ml, bigI, ep


def get_scalar_density_comparisons_human_readble(
    data, y_ml, Rs, spacing=0.5, buffer=2.0, ldep=False
):
    """
    Compute various density comparison metrics between target and machine-learning densities.

    This function generates a grid of points based on input data, computes densities using gau2grid collocation,
    and then calculates several metrics to compare target and machine-learning densities. These metrics include
    electron population comparisons, relative error, and the Integral Similarity (I) index.

    Parameters:
    data (torch.Tensor): Input data containing various coefficients and properties.
    y_ml (torch.Tensor): Machine-learning predicted coefficients.
    Rs (list): List of tuples representing radial and angular indices (mul, l).
    spacing (float, optional): Spacing between grid points. Default is 0.5.
    buffer (float, optional): Additional buffer space around the data's bounding box. Default is 2.0.
    ldep (bool, optional): Whether to compute angular momentum. Default is False.

    Returns:
    tuple: A tuple containing the following elements:
        - target_electron_count (float): Total number of electrons estimated from the target density.
        - ml_electron_count (float): Total number of electrons estimated from the machine-learning density.
        - integral_similarity_index (float): Integral Similarity (I) index.
        - relative_error_percentage (float): Relative error in percentage between machine-learning and target densities.
        - relative_error_per_angular_momentum (numpy.ndarray, optional): Array of l-dependent relative errors if ldep is True.
    """
    import numpy as np

    # generate grid in xyz input units (angstroms)
    x, y, z, vol, x_spacing, y_spacing, z_spacing = generate_grid(
        data, spacing=spacing, buffer=buffer
    )
    # get density on grid

    # l-dependent eps
    relative_error_per_angular_momentum = np.zeros(len(Rs))

    if ldep:
        target_density, ml_density, target_density_per_l, ml_density_per_l = (
            unperm_gau2grid_density_kdtree(
                x.flatten(), y.flatten(), z.flatten(), data, y_ml, Rs, ldepb=ldep
            )
        )
        # Fill l-dependent eps in this case
        for l in range(len(Rs)):
            relative_error_per_angular_momentum[l] = (
                100
                * np.sum(np.abs(ml_density_per_l[l] - target_density_per_l[l]))
                / np.sum(target_density)
            )
    else:
        target_density = coeff_unperm_gau2grid_density_kdtree_target_only(
            x.flatten(), y.flatten(), z.flatten(), data, Rs
        )
        ml_density = coeff_unperm_gau2grid_density_kdtree_ml_only(
            x.flatten(),
            y.flatten(),
            z.flatten(),
            data,
            y_ml,
            Rs,
            ldepb=False,
            perm=False,
        )

    # Density is in e-/bohr**3
    angstrom2bohr = 1.8897259886
    bohr2angstrom = 1 / angstrom2bohr

    relative_error_percentage = (
        100 * np.sum(np.abs(ml_density - target_density)) / np.sum(target_density)
    )

    target_electron_count = np.sum(target_density) * vol * angstrom2bohr**3
    ml_electron_count = np.sum(ml_density) * vol * angstrom2bohr**3

    numer = np.sum((ml_density - target_density) ** 2)
    denom = np.sum(ml_density**2) + np.sum(target_density**2)
    integral_similarity_index = numer / denom

    if ldep:
        return (
            target_electron_count,
            ml_electron_count,
            integral_similarity_index,
            relative_error_percentage,
            relative_error_per_angular_momentum,
        )
    else:
        return (
            target_electron_count,
            ml_electron_count,
            integral_similarity_index,
            relative_error_percentage,
        )


def unperm_gau2grid_density_kdtree(x, y, z, data, ml_y, rs, ldepb=False):
    import numpy as np
    import gau2grid as g2g
    from scipy import spatial

    # note, this takes x, y and z as flattened arrays
    # r = np.array(np.sqrt(np.square(x) + np.square(y) + np.square(z)))
    xyz = np.vstack([x, y, z])
    tree = spatial.cKDTree(xyz.T)

    ml_density = np.zeros_like(x)
    target_density = np.zeros_like(x)

    # l-indexed arrays to dump specific contributions to density
    ml_density_per_l = np.array(
        [
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
        ]
    )
    target_density_per_l = np.array(
        [
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
        ]
    )

    for coords, full_coeffs, iso_coeffs, ml_coeffs, alpha, norm in zip(
        data.pos_orig.cpu().detach().numpy(),
        data.full_c.cpu().detach().numpy(),
        data.iso_c.cpu().detach().numpy(),
        ml_y.cpu().detach().numpy(),
        data.exp.cpu().detach().numpy(),
        data.norm.cpu().detach().numpy(),
    ):
        center = coords
        counter = 0
        for mul, l in rs:
            # print("Rs",mul,l)
            for j in range(mul):
                normal = norm[counter]
                if normal != 0:
                    exp = [alpha[counter]]

                    small = 1e-5
                    angstrom2bohr = 1.8897259886
                    bohr2angstrom = 1 / angstrom2bohr

                    target_full_coeffs = full_coeffs[counter : counter + (2 * l + 1)]

                    pop_ml = ml_coeffs[counter : counter + (2 * l + 1)]
                    c_ml = pop_ml * normal / (2 * np.sqrt(2))
                    ml_full_coeffs = c_ml + iso_coeffs[counter : counter + (2 * l + 1)]

                    target_max = np.amax(np.abs(target_full_coeffs))
                    ml_max = np.amax(np.abs(ml_full_coeffs))
                    max_c = np.amax(np.array([target_max, ml_max]))

                    cutoff = (
                        np.sqrt((-1 / exp[0]) * np.log(small / np.abs(max_c * normal)))
                        * bohr2angstrom
                    )

                    close_indices = tree.query_ball_point(center, cutoff)
                    # print("cutoff",cutoff)
                    # print(xyz.shape)
                    # print(l,len(close_indices))
                    points = np.require(xyz[:, close_indices], requirements=["C", "A"])

                    ret_target = g2g.collocation(
                        points * angstrom2bohr, l, [1], exp, center * angstrom2bohr
                    )
                    ret_ml = g2g.collocation(
                        points * angstrom2bohr, l, [1], exp, center * angstrom2bohr
                    )  # old
                    # ret_ml = g2g.collocation(points*angstrom2bohr, l, [1], exp, center)

                    # Now permute back to psi4 ordering
                    ##              s     p         d             f                 g                      h                           i
                    psi4_2_e3nn = [
                        [0],
                        [2, 0, 1],
                        [4, 2, 0, 1, 3],
                        [6, 4, 2, 0, 1, 3, 5],
                        [8, 6, 4, 2, 0, 1, 3, 5, 7],
                        [10, 8, 6, 4, 2, 0, 1, 3, 5, 7, 9],
                        [12, 10, 8, 6, 4, 2, 0, 1, 3, 5, 7, 9, 11],
                    ]
                    e3nn_2_psi4 = [
                        [0],
                        [1, 2, 0],
                        [2, 3, 1, 4, 0],
                        [3, 4, 2, 5, 1, 6, 0],
                        [4, 5, 3, 6, 2, 7, 1, 8, 0],
                        [5, 6, 4, 7, 3, 8, 2, 9, 1, 10, 0],
                        [6, 7, 5, 8, 4, 9, 3, 10, 2, 11, 1, 12, 0],
                    ]

                    # target_full_coeffs = np.array([target_full_coeffs[k] for k in e3nn_2_psi4[l]])
                    # ml_full_coeffs = np.array([ml_full_coeffs[k] for k in e3nn_2_psi4[l]])

                    # target_full_coeffs = full_coeffs[counter:counter+(2*l + 1)]
                    scaled_components = (
                        target_full_coeffs * normal * ret_target["PHI"].T
                    ).T
                    target_tot = np.sum(scaled_components, axis=0)

                    # pop_ml = ml_coeffs[counter:counter+(2*l + 1)]
                    # c_ml = pop_ml * normal / (2 * np.sqrt(2))
                    # target_delta_coeffs = delta_coeffs[counter:counter+(2*l + 1)]
                    # ml_full_coeffs = target_full_coeffs + c_ml - target_delta_coeffs
                    ml_scaled_components = (
                        ml_full_coeffs * normal * ret_target["PHI"].T
                    ).T
                    ml_tot = np.sum(ml_scaled_components, axis=0)

                    target_density[close_indices] += target_tot
                    ml_density[close_indices] += ml_tot

                    # dump l-dependent contributions

                    target_density_per_l[l][close_indices] += target_tot
                    ml_density_per_l[l][close_indices] += ml_tot

                counter += 2 * l + 1

    if ldepb:
        return target_density, ml_density, target_density_per_l, ml_density_per_l
    else:
        return target_density, ml_density


def visualize_target_density(x, y, z, target_density, points):
    rows = 1
    cols = 2
    specs = [[{"is_3d": True} for i in range(cols)] for j in range(rows)]

    fig = make_subplots(
        rows=rows, cols=cols, specs=specs, subplot_titles=("Target Density",)
    )

    fig.update_layout(
        height=600,
        width=1200,
    )

    traces = []
    traces.append(
        go.Volume(
            x=x.flatten(),
            y=y.flatten(),
            z=z.flatten(),
            value=target_density.flatten(),
            isomin=0.15,
            isomax=0.2,
            colorscale="Blues",
            opacity=0.1,  # needs to be small to see through all surfaces
            surface_count=10,  # needs to be a large number for good volume rendering
            name="Target Density",
        )
    )

    fig.add_trace(traces[0], row=1, col=1)

    xs = points.cpu().numpy()[:, 0]
    ys = points.cpu().numpy()[:, 1]
    zs = points.cpu().numpy()[:, 2]
    geom = go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="markers",
        marker=dict(size=3, color="Black", opacity=1.0),
    )
    fig.add_trace(geom, row=1, col=1)

    fig.update_layout(showlegend=True)
    fig.write_html("newest_testdensity.html")
    fig.show()


def visualize_target_density(x, y, z, target_density, points, filename):
    rows = 1
    cols = 2
    specs = [[{"is_3d": True} for i in range(cols)] for j in range(rows)]

    fig = make_subplots(
        rows=rows, cols=cols, specs=specs, subplot_titles=("Target Density",)
    )

    fig.update_layout(
        height=600,
        width=1200,
    )

    traces = []
    traces.append(
        go.Volume(
            x=x.flatten(),
            y=y.flatten(),
            z=z.flatten(),
            value=target_density.flatten(),
            isomin=0.15,
            isomax=0.2,
            colorscale="Blues",
            opacity=0.1,  # needs to be small to see through all surfaces
            surface_count=10,  # needs to be a large number for good volume rendering
            name="Target Density",
        )
    )

    fig.add_trace(traces[0], row=1, col=1)

    xs = points.cpu().numpy()[:, 0]
    ys = points.cpu().numpy()[:, 1]
    zs = points.cpu().numpy()[:, 2]
    geom = go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="markers",
        marker=dict(size=3, color="Black", opacity=1.0),
    )
    fig.add_trace(geom, row=1, col=1)

    fig.update_layout(showlegend=True)
    fig.write_html(filename)
    fig.show()


import multiprocessing as mp
from tqdm import tqdm


def process_atom(args):
    import numpy as np
    import gau2grid as g2g
    from scipy import spatial

    x, y, z, coords, full_coeffs, ml_coeffs, alpha, norm, rs, tree, perm = args
    center = coords
    counter = 0
    atom_ml_density = np.zeros_like(x)
    atom_ml_density_per_l = np.zeros_like(
        np.array(
            [
                np.zeros_like(x),
                np.zeros_like(x),
                np.zeros_like(x),
                np.zeros_like(x),
                np.zeros_like(x),
            ]
        )
    )

    xyz = np.vstack([x, y, z])

    for mul, l in rs:
        for j in range(mul):
            normal = norm[counter]
            if normal != 0:
                exp = [alpha[counter]]

                small = 1e-50
                angstrom2bohr = 1.8897259886
                bohr2angstrom = 1 / angstrom2bohr

                pop_ml = ml_coeffs[counter : counter + (2 * l + 1)]
                c_ml = pop_ml * normal / (2 * np.sqrt(2))
                ml_full_coeffs = c_ml

                max_c = np.amax(np.abs(ml_full_coeffs))

                cutoff = (
                    np.sqrt((-1 / exp[0]) * np.log(small / np.abs(max_c * normal)))
                    * bohr2angstrom
                )

                close_indices = tree.query_ball_point(center, cutoff)

                points = np.require(xyz[:, close_indices], requirements=["C", "A"])
                ret_target = g2g.collocation(
                    points * angstrom2bohr, l, [1], exp, center * angstrom2bohr
                )

                ret_ml = g2g.collocation(
                    points * angstrom2bohr, l, [1], exp, center * angstrom2bohr
                )

                psi4_2_e3nn = [
                    [0],
                    [2, 0, 1],
                    [4, 2, 0, 1, 3],
                    [6, 4, 2, 0, 1, 3, 5],
                    [8, 6, 4, 2, 0, 1, 3, 5, 7],
                    [10, 8, 6, 4, 2, 0, 1, 3, 5, 7, 9],
                    [12, 10, 8, 6, 4, 2, 0, 1, 3, 5, 7, 9, 11],
                ]
                e3nn_2_psi4 = [
                    [0],
                    [1, 2, 0],
                    [2, 3, 1, 4, 0],
                    [3, 4, 2, 5, 1, 6, 0],
                    [4, 5, 3, 6, 2, 7, 1, 8, 0],
                    [5, 6, 4, 7, 3, 8, 2, 9, 1, 10, 0],
                    [6, 7, 5, 8, 4, 9, 3, 10, 2, 11, 1, 12, 0],
                ]
                if perm == True:
                    ml_full_coeffs = np.array(
                        [ml_full_coeffs[k] for k in e3nn_2_psi4[l]]
                    )

                ml_scaled_components = (ml_full_coeffs * normal * ret_target["PHI"].T).T
                ml_tot = np.sum(ml_scaled_components, axis=0)

                atom_ml_density[close_indices] += ml_tot
                atom_ml_density_per_l[l][close_indices] += ml_tot

            counter += 2 * l + 1

    return atom_ml_density, atom_ml_density_per_l


def coeff_unperm_gau2grid_density_kdtree_ml_only_parallel(
    x, y, z, data, ml_y, rs, ldepb=False, perm=False
):
    import numpy as np
    import gau2grid as g2g
    from scipy import spatial

    xyz = np.vstack([x, y, z])
    tree = spatial.cKDTree(xyz.T)

    ml_density = np.zeros_like(x)

    # l-indexed arrays to dump specific contributions to density
    ml_density_per_l = np.array(
        [
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
            np.zeros_like(x),
        ]
    )

    # Create a pool of worker processes
    pool = mp.Pool(processes=mp.cpu_count())

    # Prepare the arguments for each atom
    atom_args = [
        (x, y, z, coords, full_coeffs, ml_coeffs, alpha, norm, rs, tree, perm)
        for coords, full_coeffs, ml_coeffs, alpha, norm in zip(
            data.pos_orig.cpu().detach().numpy(),
            data.full_c.cpu().detach().numpy(),
            ml_y.cpu().detach().numpy(),
            data.exp.cpu().detach().numpy(),
            data.norm.cpu().detach().numpy(),
        )
    ]

    # Process atoms in parallel with tqdm progress bar
    results = []
    with tqdm(total=len(atom_args), desc="Processing atoms") as pbar:
        for result in pool.imap_unordered(process_atom, atom_args):
            results.append(result)
            pbar.update()

    # Close the pool
    pool.close()
    pool.join()

    # Combine the results from all atoms
    for atom_ml_density, atom_ml_density_per_l in results:
        ml_density += atom_ml_density
        ml_density_per_l += atom_ml_density_per_l

    if ldepb:
        return ml_density, ml_density_per_l
    else:
        return ml_density

