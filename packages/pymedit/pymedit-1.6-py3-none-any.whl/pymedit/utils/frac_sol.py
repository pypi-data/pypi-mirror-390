# This file is part of pymedit.
#
# pymedit is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# pymedit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# A copy of the GNU General Public License is included below.
# For further information, see <http://www.gnu.org/licenses/>.
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
from pyfreefem import FreeFemRunner

from ..abstract import display
from .timing import tic, toc
from ..P1Frac import P1FracFunction
from ..mesh import Mesh


def invert_dict(
    d: dict[int, list[tuple[int, float]]],
) -> dict[int, list[tuple[int, float]]]:

    out = dict()
    for key, values in d.items():
        for partition, value in values:
            out.setdefault(partition, []).append((key, value))
    return out


def get_config_comp(p: int, fem_type: str, bd_cond: dict) -> dict:
    config = {
        "p": p,  # Component p
        "FEMTYPE": fem_type,
        "Ncond": 0,
        "bdLabels": [],
        "bdValues": [],
    }
    bd_cond_i = bd_cond.get(p)
    if bd_cond_i:
        bdLabels, bdValues = zip(*bd_cond_i)
        bdLabels = list(bdLabels)
        bdValues = list(bdValues)
        config.update(
            {
                "bdLabels": bdLabels,
                "bdValues": bdValues,
                "Ncond": len(bdLabels),
            }
        )
    return config


def create_Dp(genDof_p, ngdof: int, ndof: int) -> sp.csc_array:
    """
    Create the sparse mapping matrix Dp.
    """
    cols = np.flatnonzero(genDof_p != -1)
    rows = genDof_p[cols]
    Dmatrix = sp.coo_matrix(
        (np.ones_like(rows), (rows, cols)), shape=(ngdof, ndof), dtype=int
    )
    return Dmatrix.tocsc()


def get_func(dofmap: np.ndarray, ndof: int, P0_partition, chiMatrix: np.ndarray):
    P = len(chiMatrix)
    # Which dof in which partition
    compToDof = np.zeros((P, ndof), dtype=bool)

    for p, chi in enumerate(chiMatrix):
        I = chi.astype(bool)
        s = np.unique(dofmap[I, :])
        compToDof[p, s] = True

    sumDof = np.sum(compToDof, axis=0)
    sumDof[compToDof[0]] = 1

    mask = (sumDof == 1) & compToDof
    compToGenDof = np.full((P, ndof), -1, dtype=int)
    compToGenDof[mask] = np.tile(np.arange(ndof), (P, 1))[mask]

    indices = np.where(sumDof >= 2)[0]
    ngdof = ndof + sumDof[indices].sum() - len(indices)
    global_to_local = np.empty((ngdof, 1), dtype=int)
    global_to_local[:ndof, 0] = np.arange(ndof)

    max_gen_dof = ndof
    comp_indices, indices = np.where(~mask & compToDof)
    for p, i in zip(comp_indices, indices):
        if sumDof[i] == 1:
            gen_dof = i
        else:
            gen_dof = max_gen_dof
            max_gen_dof += 1
            sumDof[i] -= 1
        compToGenDof[p, i] = gen_dof
        global_to_local[gen_dof] = i

    # ngdof = max_gen_dof

    local_to_global = np.empty(shape=dofmap.shape, dtype=int)
    for i, p in enumerate(P0_partition.sol):
        dofs_in_elem = dofmap[i, :]
        local_to_global[i, :] = compToGenDof[int(p), dofs_in_elem]

    return compToGenDof, ngdof, local_to_global, global_to_local


def get_func_P1(gen_mesh, chiMatrix, partitionLabels):

    triangles = gen_mesh.triangles[:, :-1] - 1

    # ndof == nv here
    ndof = gen_mesh.nv

    P = len(chiMatrix)
    # Which dof in which partition
    compToDof = np.zeros((P, ndof), dtype=bool)

    for comp_i, chi in enumerate(chiMatrix):
        I = chi.astype(bool)
        s = np.unique(triangles[I, :])
        compToDof[comp_i, s] = True

    sumDof = np.sum(compToDof, axis=0)
    sumDof[compToDof[0]] = 1

    mask = (sumDof == 1) & compToDof
    compToGenIdx = np.full((P, ndof), -1, dtype=int)
    compToGenIdx[mask] = np.tile(np.arange(ndof), (P, 1))[mask]

    # `ngv` can also be calculated
    indices = np.where(sumDof >= 2)[0]
    ngv = ndof + sumDof[indices].sum() - len(indices)
    global_to_local = np.empty((ngv, 1), dtype=int)
    global_to_local[:ndof, 0] = np.arange(ndof)

    done = set()
    max_gen_vtx = ndof
    part_indices, indices = np.where(~mask & compToDof)
    for p, i in zip(part_indices, indices):
        if i in done:
            gen_vtx = max_gen_vtx
            max_gen_vtx += 1
        else:
            gen_vtx = i
            done.add(i)

        compToGenIdx[p, i] = gen_vtx
        global_to_local[gen_vtx] = i

    # ngv = max_gen_vtx

    return compToGenIdx, ngv


def get_dofs(M: Mesh, fem_type: str) -> tuple[np.ndarray, int, sp.csc_matrix]:

    # TODO load correct element based on fem_type
    script = """
    IMPORT "io.edp"
    load "Element_P3"

    mesh Th = importMesh("Th");
    fespace Uh(Th, $FEMTYPE);

    int nt = Uh.nt;
    int kdf = Uh.ndofK;
    int ndof = Uh.ndof;
    exportVar(ndof);
    
    // TODO use this when fixed
    //int[int,int] dofmap(nt, kdf); 
    // This loop does not work when dofmap is a matrix
    // because then dofmap is emtpy and the loop does not start
    //for [i,j,v:dofmap] {
    //    v = Uh(i, j);
    //}
    //export2DArray(dofmap);

    // TODO delete this workaround
    matrix dofmap(nt, kdf);
    for (int i = 0; i < nt; i++) {
        for (int j = 0; j < kdf; j++) {
            dofmap(i, j) = Uh(i, j);
        }
    }
    exportMatrix(dofmap);

    fespace Wh(Th, P1);
    matrix Intp = interpolate(Wh, Uh);
    exportMatrix(Intp);
    """

    runner = FreeFemRunner(script, run_dir="code_run0", debug=3)
    runner.import_variables(Th=M)

    config = {"FEMTYPE": fem_type}
    exports = runner.execute(config, verbosity=0)

    ndof = int(exports.get("ndof"))

    # like mesh.triangles, but for higher order
    dofmap_csc: sp.csc_matrix = exports.get("dofmap")
    dofmap: np.ndarray = dofmap_csc.astype(int).toarray()

    Intp: sp.csc_matrix = exports.get("Intp")
    Intp: sp.csc_matrix = Intp.astype(int)

    return dofmap, ndof, Intp


def construct_freefem(
    M: Mesh,
    P0_partition,
    chiMatrix: np.ndarray,
    runner: FreeFemRunner,
    fem_type: str = "P1",
    bd_cond: dict[int, list[int]] | None = None,
    doPlotFreeFEM: bool = False,
    **kwargs: int | float | str,
):
    """TODO"""

    if bd_cond:
        display(f"Dirichlet boundary conditions {bd_cond}")
        bd_cond = invert_dict(bd_cond)
    else:
        bd_cond = dict()

    # Use FreeFEM to get dofs
    dofmap, ndof, Intp = get_dofs(M, fem_type)

    # Determine which generlized dofs lie in which component
    compToGenDof, ngdof, _, _ = get_func(dofmap, ndof, P0_partition, chiMatrix)
    display(f"Number of gen-dofs for {fem_type} is {ngdof}.")

    # Determine which generlized vertices lie in which component
    compToGenVtx, ngv, local_to_global, global_to_local = get_func(
        M.triangles[:, :-1] - 1, M.nv, P0_partition, chiMatrix
    )
    display(f"Number of gen-vertices is {ngv}.")

    A = sp.csc_matrix(([], ([], [])), (ngdof, ngdof))
    b = np.zeros(ngdof, dtype=float)
    GenIntp = sp.csc_matrix(([], ([], [])), (ngv, ngdof), dtype=int)

    imports = {f"chi{p}": chi for p, chi in enumerate(chiMatrix)}
    runner.import_variables(Th=M, **imports, **kwargs)

    P = len(chiMatrix)
    # Loop over components p = 0, 1, ..., P-1
    for p in range(P):
        config = get_config_comp(p, fem_type, bd_cond)
        exports = runner.execute(config, plot=doPlotFreeFEM, verbosity=0)

        Dp_P1 = create_Dp(compToGenVtx[p, :], ngv, M.nv)
        Dp = create_Dp(compToGenDof[p, :], ngdof, ndof)

        Ap = exports.get("Ap")
        A += Dp @ Ap @ Dp.T

        bp = exports.get("bp")
        b += Dp @ bp

        GenIntp += Dp_P1 @ Intp @ Dp.T

    GenIntp.data[:] = 1
    U = spsolve(A, b)
    P1_frac_func = P1FracFunction(M, GenIntp @ U)

    P1_frac_func.ngv = ngv
    P1_frac_func.local_to_global = local_to_global
    P1_frac_func.global_to_local = global_to_local

    return P1_frac_func
