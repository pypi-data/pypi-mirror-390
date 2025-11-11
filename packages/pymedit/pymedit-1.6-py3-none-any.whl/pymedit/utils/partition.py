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

from ..P0 import P0Function
from ..P0_3D import P0Function3D
from ..mesh import Mesh, trunc, mesh_boundary
from ..mesh3D import Mesh3D, trunc3DMesh, eliminate_duplicates
from .graphs import UnionFind, Graph, partition
from .timing import tic, toc
from ..abstract import display
from scipy.sparse.csgraph import connected_components
import scipy.sparse as sp

def select(A, value):
    I, J, D = sp.find(A)
    indices = np.where(D==value)[0]
    I, J, D = I[indices], J[indices], np.ones_like(indices)
    return sp.coo_matrix((D,(I,J)),shape=A.shape)

def get_tris_adjacent_to_fracture(M : Mesh, frac):
    edges_on_fracture = np.where(np.isin(M.edges[:,-1],frac))[0]
    edges_to_tris = (M.verticesToEdges[:,edges_on_fracture]).T @ M.verticesToTriangles
    _, triangles, _ = sp.find(edges_to_tris)
    triangles = np.unique(triangles)
    return triangles

def get_tris_adjacent_to_internal_nodes_fracture(M : Mesh, frac):
    edges_on_fracture = np.where(np.isin(M.edges[:,-1],frac))[0]
    boundary = np.where(M.verticesToEdges[:,edges_on_fracture].sum(axis=1)==1)[0]
    internal_nodes = np.setdiff1d(np.unique(M.edges[edges_on_fracture,:2])-1,boundary)

    # Add triangles adjacent to boundary points that are on the boundary of the global mesh 
    boundary_M = np.unique(mesh_boundary(M)) - 1
    nodes_to_keep = np.intersect1d(boundary_M,boundary)

    internal_nodes = np.concatenate((internal_nodes, nodes_to_keep))
    _, triangles, _ = sp.find(M.verticesToTriangles[internal_nodes,:])


    return triangles

def boundary_fracture(M : Mesh3D, frac : list[int]) -> np.ndarray: 
    triangles_on_fracture = np.where(np.isin(M.triangles[:,-1],frac))[0]
    # Calculer la frontière de la fracture
    verticesToVertices = M.verticesToTriangles[:,triangles_on_fracture] \
        @ M.verticesToTriangles[:,triangles_on_fracture].T
    I, J, D = sp.find(verticesToVertices) 
    indices = np.where(D==1)[0]
    edges = np.vstack((J[indices]+1,I[indices]+1)).T
    ## Orienter les arêtes conformément à l'orientation des triangles
    tris = sp.find(M.verticesToTriangles[I[indices],:].multiply(M.verticesToTriangles[J[indices],:]))[1]
    triangles = M.triangles[tris,:3] 
    match0 = (triangles[:, 0] == I[indices]+1) & (triangles[:, 1] == J[indices]+1)
    match1 = (triangles[:, 1] == I[indices]+1) & (triangles[:, 2] == J[indices]+1)
    match2 = (triangles[:, 2] == I[indices]+1) & (triangles[:, 0] == J[indices]+1)
    same_orientation = match0 | match1 | match2
    edges = edges[same_orientation,:]

    return edges

def compute_boundary_fracture(M : Mesh3D, frac, boundary_label = 100): 
    edges = boundary_fracture(M,frac)
    ### Ajouter le label 100
    edges = np.hstack((edges,boundary_label*np.ones(edges.shape[0],dtype=int)[:,None]))
    if hasattr(M,'edges'):
        M.edges = np.vstack((M.edges,edges))
    else: 
        M.edges = edges
    M.edges = eliminate_duplicates(M.edges)


def get_tetras_adjacent_to_faces_fracture(M : Mesh3D, frac : np.ndarray | list[int] | int):
    triangles_on_fracture = np.where(np.isin(M.triangles[:,-1],frac))[0]
    vtx_to_tetras = M.verticesToTriangles[:,triangles_on_fracture].T @ M.verticesToTetra
    tetras = sp.find(vtx_to_tetras==3)[1]
    return np.unique(tetras)

def get_tetras_adjacent_to_internal_nodes_fracture(M : Mesh3D, frac : list[int] | int, genVtx = None, vertices_on_fracture = None):
    if genVtx is None:
        triangles_on_fracture = np.where(np.isin(M.triangles[:,-1],frac))[0]

        edges = boundary_fracture(M, frac)
        vertices_on_fracture = np.setdiff1d(np.unique(M.triangles[triangles_on_fracture,:3]),
                                            np.unique(edges[:,:2]))
        tetrahedra = np.unique(sp.find(M.verticesToTetra[vertices_on_fracture-1,:])[1])
    else: 
        # Internal nodes: those which have more than one generalized vertices 
        vtx = np.asarray([len(np.unique(genVtx.data[genVtx.indptr[i]:genVtx.indptr[i+1]])) for i in range(genVtx.shape[0])])
        internal_nodes = vertices_on_fracture[np.where(vtx>1)[0]]
        tetrahedra = np.unique(sp.find(M.verticesToTetra[internal_nodes,:])[1])

    return tetrahedra

def get_tetras_adjacent_to_internal_edges_fracture(M : Mesh3D, frac):
    triangles_on_fracture = np.where(np.isin(M.triangles[:,-1],frac))[0]
    vertices_to_vertices = M.verticesToTriangles[:,triangles_on_fracture] @ M.verticesToTriangles[:,triangles_on_fracture].T
    vertices_to_vertices -= sp.diags(vertices_to_vertices.diagonal())
    # Trouver les arêtes adjacentes à plus de deux triangles : ce sont les 
    # internal edges
    I, J, _ = sp.find(vertices_to_vertices>=2)
    internal_edges = sp.csr_matrix((np.ones_like(I),(I,J)),shape=(M.nv,M.nv))
    A = (M.verticesToTetra.T).tocsr()
    B = (internal_edges @ M.verticesToTetra).tocsc()
    tetras = np.where((A.multiply(B.T)).sum(axis=1))[0]
    return tetras

def get_tetras_adjacent_to_fracture(M : Mesh3D, frac):
    triangles_on_fracture = np.where(np.isin(M.triangles[:,-1],frac))[0]

    trisToTetra = M.verticesToTriangles[:,triangles_on_fracture].T @ M.verticesToTetra 
    _, tetrahedra, _ = sp.find(trisToTetra)
    return np.unique(tetrahedra)


def construct_graph(A : sp.csr_matrix,B : sp.csr_matrix):
    tetras = [A.indices[A.indptr[i]:A.indptr[i+1]] for i in range(A.shape[0])]
    graphs = sp.block_diag([B[tetra,:][:,tetra] for tetra in tetras])
    return graphs

def generalizedVertices(M : Mesh, frac : list[int] | int) -> tuple[sp.csr_matrix, np.ndarray]:
    A = M.verticesToTriangles
    B = M.trianglesToTriangles

    if isinstance(frac, int):
        frac = [frac]

    edges_on_fracture = np.where(np.isin(M.edges[:,-1],frac))[0]
    edges_to_tris = (M.verticesToEdges[:,edges_on_fracture]).T @ M.verticesToTriangles
    edges_to_tris = select(edges_to_tris,2)
    tris_to_tris_on_fracture = edges_to_tris.T @ edges_to_tris
    tris_to_tris_on_fracture = tris_to_tris_on_fracture - sp.diags(tris_to_tris_on_fracture.diagonal())

    B = B - tris_to_tris_on_fracture

    vertices_on_fracture = np.unique(M.edges[edges_on_fracture,:-1])-1
    A = A[vertices_on_fracture,:]

    graphs = construct_graph(A,B)
    # 2. Composantes connexes globales
    _, global_labels = connected_components(graphs, directed=False)

    label_matrix = sp.csr_matrix((global_labels+1,A.indices, A.indptr))
    return label_matrix, vertices_on_fracture

def generalizedVertices3d(M : Mesh3D, frac : list[int] | int) -> tuple[sp.csr_matrix,np.ndarray]:
    tic()
    A = M.verticesToTetra
    B = M.tetrahedronToTetrahedron

    if isinstance(frac, int):
        frac = [frac]

    triangles_on_fracture = np.where(np.isin(M.triangles[:,-1],frac))[0]
    trisToTetra = M.verticesToTriangles[:,triangles_on_fracture].T @ M.verticesToTetra 
    trisToTetra = select(trisToTetra,3)
    tetras_to_tetras_on_fracture = trisToTetra.T @ trisToTetra
    tetras_to_tetras_on_fracture -= sp.diags(tetras_to_tetras_on_fracture.diagonal())
    
    B -= tetras_to_tetras_on_fracture
    print("First part took "+toc())

    vertices_on_fracture = np.unique(M.triangles[triangles_on_fracture,:-1])-1
    A = A[vertices_on_fracture,:]

    tic()
    graphs = construct_graph(A,B)
    print("Construct graph took "+toc())

    # 2. Composantes connexes globales

    tic()
    _, global_labels = connected_components(graphs, directed=False)
    print("connected components took "+toc())

    label_matrix = sp.csr_matrix((global_labels+1,A.indices, A.indptr))
    return label_matrix, vertices_on_fracture

def remap(arr : np.array):
    rename = np.unique(arr)
    mapping = dict(zip(rename, list(range(1,len(rename)+1))))
    arr_remap = np.vectorize(mapping.get)(arr)
    return arr_remap

def _cover_tris(M, frac):# genVtx: sp.csr_matrix | None = None, vertices_on_fracture: np.ndarray | None = None):
    # Routine pour partitionner maillage des triangles adjacents à la fracture
    if isinstance(frac, int):
        frac = [frac]
    edges_on_fracture = np.where(np.isin(M.edges[:,-1],frac))[0]
    edges_to_tris = (M.verticesToEdges[:,edges_on_fracture]).T @ M.verticesToTriangles
    edges_to_tris = select(edges_to_tris,2)
    tris_to_tris_on_fracture = edges_to_tris.T @ edges_to_tris
    tris_to_tris_on_fracture = tris_to_tris_on_fracture - sp.diags(tris_to_tris_on_fracture.diagonal())
    graph = M.trianglesToTriangles - tris_to_tris_on_fracture

    # Extraire le maillage des triangles adjacents aux noeuds internes ou aux faces 
    # Et calculer ses sommets généralisés
    genVtx, vertices_on_fracture = generalizedVertices(M, frac)

    # interdire liaisons entre triangles entre différents sommets généralisés 
    genVtx_csc = genVtx.tocsc()
    m = max(genVtx.data)
    composantespartri = [genVtx_csc[:,i].data for i in range(genVtx_csc.shape[1])]
    indices = np.concatenate(composantespartri)
    D = np.ones_like(indices)
    indptr=np.concatenate(([0],np.cumsum([len(t) for t in composantespartri])))
    tris_to_composantes = sp.csr_matrix((D,indices,indptr),shape=(M.nt,m+1)).tocsc()
    toforbid = [np.unique(genVtx.data[genVtx.indptr[i]:genVtx.indptr[i+1]]) \
                for i in range(genVtx.shape[0])]
    toforbid = [list(map(int,x)) for x in toforbid if len(x)>1]
    edges_between_components = [(f,g) for forbid in toforbid for f in forbid for g in forbid if f<g]
    edges = []
    edges = [(int(u),int(v)) for (i,j) in edges_between_components for u in tris_to_composantes[:,i].indices \
             for v in tris_to_composantes[:,j].indices]
    I, J=zip(*edges) 
    edges = np.asarray((I,J)).T
    edges.sort(axis=1)
    cannot_link_edges = np.unique(edges, axis=0)

    return partition(graph, cannot_link_edges)

def _cover_tetras(M : Mesh3D, frac):
    if isinstance(frac, int):
        frac = [frac]
    triangles_on_fracture = np.where(np.isin(M.triangles[:,-1],frac))[0]
    trisToTetra = M.verticesToTriangles[:,triangles_on_fracture].T @ M.verticesToTetra 
    trisToTetra = select(trisToTetra,3)
    tetras_to_tetras_on_fracture = trisToTetra.T @ trisToTetra
    tetras_to_tetras_on_fracture -= sp.diags(tetras_to_tetras_on_fracture.diagonal())
    graph = M.tetrahedronToTetrahedron - tetras_to_tetras_on_fracture

    genVtx, vertices_on_fracture = generalizedVertices3d(M, frac)

    # interdire liasons entre tetras entre différents sommets généralisés de Mf
    genVtx_csc = genVtx.tocsc()
    m = max(genVtx.data)
    composantespartetra = [genVtx_csc.data[genVtx_csc.indptr[i]:genVtx_csc.indptr[i+1]] for i in range(M.ntet)]
    indices = np.concatenate(composantespartetra)
    D = np.ones_like(indices)
    indptr=np.concatenate(([0],np.cumsum([len(t) for t in composantespartetra])))
    tetras_to_composantes = sp.csr_matrix((D,indices,indptr),shape=(M.ntet,m+1)).tocsc()
    toforbid = [np.unique(genVtx.data[genVtx.indptr[i]:genVtx.indptr[i+1]]) \
                for i in range(genVtx.shape[0])]
    toforbid = [list(map(int,x)) for x in toforbid if len(x)>1]
    edges_between_components = [(f,g) for forbid in toforbid for f in forbid for g in forbid if f<g]
    edges = []
    edges = [(int(u),int(v)) for (i,j) in edges_between_components for u in tetras_to_composantes.indices[tetras_to_composantes.indptr[i]:tetras_to_composantes.indptr[i+1]] \
             for v in tetras_to_composantes.indices[tetras_to_composantes.indptr[j]:tetras_to_composantes.indptr[j+1]]]
    I, J=zip(*edges) 
    edges = np.asarray((I,J)).T
    edges.sort(axis=1)
    cannot_link = np.unique(edges, axis=0)

    return partition(graph, cannot_link)

def partition_fractured_mesh(
    M: Mesh, frac_labels: list[int] | int
) -> tuple[np.ndarray, np.ndarray]:

    if M.Dimension == 3:
        raise Exception("Use partition_fractured_mesh_3D for 3D meshes")

    if isinstance(frac_labels, int):
        frac_labels = [frac_labels]

    # Partition only tetra adjacent to fracture
    triangles = get_tris_adjacent_to_internal_nodes_fracture(M, frac_labels)
    label = max(M.triangles[:,-1]+1)*10
    M = M.copy()
    M.triangles[triangles,-1]=label 
    Mf, n2o_vtx, n2o_tris = trunc(M,label, return_new2old=True)

    partitioning = _cover_tris(Mf, frac_labels)
    partitioning_Th = np.zeros(M.nt,dtype=int)

    partitioning_Th[n2o_tris] = partitioning 

    n_components = max(partitioning)
    chiMatrix = np.zeros((1 + n_components, M.nt), dtype=int)
    chiMatrix[partitioning_Th, np.arange(M.nt)] = 1

    return partitioning_Th, chiMatrix


def partition_fractured_mesh_3D(M : Mesh3D, frac_labels : list[int]):
    """ Compute a fracture-splitting partitioning for a 3D mesh M"""
    if isinstance(frac_labels,int):
        frac_labels = [frac_labels]

    genVtx, vertices_on_fracture = generalizedVertices3d(M, frac_labels)

    tetras_adjacents_nodes = get_tetras_adjacent_to_internal_nodes_fracture(M, frac_labels, genVtx, vertices_on_fracture)
    tetras_adjacents_edges = get_tetras_adjacent_to_internal_edges_fracture(M, frac_labels)
    tetras_adjacents_faces = get_tetras_adjacent_to_faces_fracture(M,frac_labels)
    tetras = np.unique(np.concatenate((tetras_adjacents_nodes,tetras_adjacents_edges,tetras_adjacents_faces)))

    # Restrict M to tetra adjacent to internal nodes, faces, edges on fracture
    M = M.copy()
    label = (1+max(M.tetrahedra[:,-1]))*10
    M.tetrahedra[:,-1] = 0
    M.tetrahedra[tetras,-1] = label
    Mf, _, n2o_tetra = trunc3DMesh(M,label, return_new2old=True) 

    partitioning = _cover_tetras(Mf, frac_labels)

    partitioning_M = np.zeros(M.ntet,dtype=int)
    partitioning_M[n2o_tetra] = partitioning
    
    n_components = max(partitioning_M)

    chiMatrix = np.zeros((1 + n_components, M.ntet), dtype=int)
    chiMatrix[partitioning_M, np.arange(M.ntet)] = 1

    return partitioning_M, chiMatrix

