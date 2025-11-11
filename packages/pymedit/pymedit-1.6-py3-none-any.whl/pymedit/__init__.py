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
# For further information, see <http://www.gnu.org/licenses/>
from .mesh import (
    Mesh,
    square,
    shapeGradients,
    connectedComponents,
    trunc,
    chainBc,
    metric,
    meshCenters,
    integrateP0P1Matrix,
    integrateP1P1Matrix,
)
from .P1 import P1Function, P1Vector, P1Metric
from .P0 import P0Function
from .mesh3D import (
    Mesh3D,
    cube,
    trunc3DMesh,
    shapeGradients3D,
    connectedComponents3D,
    getInfosTetra,
    integrateP0P1Matrix3D,
    integrateP1P1Matrix3D,
    meshCenters3D,
    compute_non_manifold_edges
)
from .P1_3D import P1Function3D, P1Vector3D
from .P0_3D import P0Function3D
from .utils.external import (
    mshdist,
    advect,
    mmg2d,
    mmg3d,
    generate3DMesh,
    saveToVtk,
    medit,
    generate2DMesh,
    parmmg,
)
from .utils.partition import (
    partition_fractured_mesh, 
    partition_fractured_mesh_3D
)
from .abstract import display, old2new
