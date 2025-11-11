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
import numpy as np
import scipy.sparse.linalg as lg
from types import FunctionType

from .mesh3D import (
    Mesh3D,
    shapeGradients3D,
    integrateP0P1Matrix3D,
    integrateP1P1Matrix3D,
)
from .P0_3D import P0Function3D
from .P1 import P1Function
from .abstract import __AbstractSol, display, SolException
from .utils.timing import tic, toc
import pyvista as pv


class P1Function3D(__AbstractSol):
    """
    A structure for 3D P1 functions (piecewise linear on each tetrahedra)
    defined on a 3D mesh, based on the INRIA `.sol` and `.solb`  formats.
    """

    def __init__(self, M: Mesh3D, phi=None, debug=None):
        """
        Load a P1 function on a 3D mesh.

        INPUTS
        ------

        `M`     :  input 3D mesh

        `phi`   :  Either:
        - the path of a `.sol` or `.solb` file
        - the path of a `.gp` file with a list of values of the solution
            saved line by line (of size `M.nv`)
        - a list or a `np.array` of function values for each of the mesh
            vertices (of size `M.nv`)
        - a lambda function `lambda x : f(x)`. The values at each vertices
            `(x[0],x[1],x[2])` will be computed accordingly.
        - a `P0Function3D` `phi`, in that case the conversion of `phi` to a P0
            function is performed by solving the variational problem:
            find `phiP1` a `P1Function3D` such that for all `v` `P1Function3D`,
            `int3d(M)(phiP1*v)=int2d(M)(phi*v)`.

        `debug` : a level of verbosity for debugging when operations are applied to `phi`

        EXAMPLES
        --------
        >>> phi = P1Function3D(M, "phi.sol")
        >>> phi = P1Function3D(M, lambda x : x[0])
        >>> phi = P1Function3D(M, M.vertices[:,-1]) #values of the tags of the vertices
        """
        try:
            super().__init__(M, phi, debug)
        except SolException:
            self.n = self.mesh.nv
            self.nsol = 1
            self.sol_types = np.asarray([1])
            if callable(phi):
                try:
                    self.sol = np.apply_along_axis(phi, 1, self.mesh.vertices)
                except TypeError:
                    newsol = lambda x: phi(x[0], x[1], x[2])
                    self.sol = np.apply_along_axis(newsol, 1, self.mesh.vertices)
            elif phi is None:
                self.values = np.zeros(self.mesh.nv)
            elif isinstance(phi, P1Function3D):
                self.sol = phi.sol.copy()
            elif isinstance(phi, P0Function3D):
                display(
                    "Converting P0 function into P1 function.", 2, self.debug, "green"
                )
                tic(20)
                B = integrateP0P1Matrix3D(self.mesh)
                A = integrateP1P1Matrix3D(self.mesh)
                RHS = B.dot(phi.sol)
                self.sol = lg.cg(A, RHS, atol=1e-16)[0]
                display(
                    f"Conversion achieved in {toc(20)}s.", 3, self.debug, "orange_4a"
                )
        self.sol = self.sol.flatten()
        if self.nsol != 1 or self.sol_types.tolist() != [1] or self.n != self.mesh.nv:
            raise Exception(f"Error: {phi} is invalid P1Function3D solution file.")
        if self.Dimension != 3:
            raise Exception(f"Error: {phi} should be associated with a 3-D mesh.")
        if self.sol.shape != (self.mesh.nv,) or self.n != self.mesh.nv:
            raise Exception(
                "Error: the provided array of values should be"
                f" of size ({self.mesh.nv},) while it is of size {self.sol.shape}."
            )

    def gradientP0(self) -> np.ndarray:
        """
        Returns the components of the P0 gradient of the P1 function.

        OUTPUT
        ------

        `(gradx,grady,gradz)` where `gradx` and `grady` and `gradz` are of size
        `self.mesh.ntet` and containing the values of the gradient of self on every tetrahedra.
        """
        if not hasattr(self, "_P1Function3D__gradientP0"):
            M = self.mesh
            shapeGradients = shapeGradients3D(self.mesh)
            self.__gradientP0 = (
                shapeGradients[0].T * self.sol[M.tetrahedra[:, 0] - 1]
                + shapeGradients[1].T * self.sol[M.tetrahedra[:, 1] - 1]
                + shapeGradients[2].T * self.sol[M.tetrahedra[:, 2] - 1]
                + shapeGradients[3].T * self.sol[M.tetrahedra[:, 3] - 1]
            ).T
        return self.__gradientP0

    def dxP0(self) -> P0Function3D:
        """
        Returns the x component of the P0 gradient.
        """
        return P0Function3D(self.mesh, self.gradientP0()[:, 0])

    def dyP0(self) -> P0Function3D:
        """
        Returns the y component of the P0 gradient.
        """
        return P0Function3D(self.mesh, self.gradientP0()[:, 1])

    def dzP0(self) -> P0Function3D:
        """
        Returns the z component of the P0 gradient.
        """
        return P0Function3D(self.mesh, self.gradientP0()[:, 2])

    def dxP1(self) -> "P1Function3D":
        """
        Returns the x component of the P1 gradient.
        """
        return P1Function3D(self.mesh, self.dxP0())

    def dyP1(self) -> "P1Function3D":
        """
        Returns the y component of the P1 gradient.
        """
        return P1Function3D(self.mesh, self.dyP0())

    def dzP1(self) -> "P1Function3D":
        """
        Returns the z component of the P1 gradient.
        """
        return P1Function3D(self.mesh, self.dzP0())

    def gradientP1(self) -> "P1Vector3D":
        """
        Returns the gradient of the P1 function as a `P1Vector3D`.
        The gradient is computed by converting the components of the
        P0 gradient into a P1 functions"""
        return P1Vector3D(self.mesh, [self.dxP1(), self.dyP1(), self.dzP1()])

    def plot(self, title: str = 'sol', ls: bool = False, vmin: float = -np.inf, vmax: float = np.inf, **kwargs):
        pvmesh, _ = self.mesh.to_pvmesh()
        pvmesh.point_data[title] = self.sol
        plotter = pv.Plotter()

        toggle = False
        saved_normal = (1, 0, 0)
        saved_origin = np.array(pvmesh.center)
        
        pvmesh = pvmesh.clip_scalar(value=vmin, invert=False).clip_scalar(value=vmax, invert=True)
        plotter.add_mesh(pvmesh, 
                         name="P1", **kwargs)

        def toggle_clipping():
            nonlocal toggle, saved_normal, saved_origin

            if not toggle:
                # Retire les acteurs originaux
                plotter.remove_actor('P1')

                # Callback appliqué aux deux maillages
                def clip_callback(normal, origin):
                    nonlocal saved_normal, saved_origin
                    saved_normal = normal
                    saved_origin = origin

                    clipped_mesh = pvmesh.clip(normal=normal, origin=origin)

                    plotter.remove_actor('P1_clip')

                    plotter.add_mesh(clipped_mesh,  
                                     name='P1_clip',
                                     **kwargs)

                # Widget plan avec dernière position connue
                plotter.add_plane_widget(
                    callback=clip_callback,
                    normal=saved_normal,
                    origin=saved_origin,
                    implicit=True,
                    bounds=pvmesh.bounds
                )
                toggle = True

            else:
                toggle = False
                # Nettoyer le clipping et remettre la scène originale
                plotter.clear_plane_widgets()
                plotter.remove_actor('P1_clip')

                plotter.add_mesh(pvmesh, 
                                 name="P1", **kwargs)
        plotter.add_key_event("F1", toggle_clipping)
        print("Interactive plot with PyVista.")
        print("Press F1 for clipping")
        plotter.show()

    def plot_medit(
        self, title: str | None = None, keys: str | None = None, silent: bool = True, block = True
    ):
        """
        Plot a 3D P1 function with `medit`.

        INPUT
        -----

        `title` : a message to be printed in the console before plotting

        `keys`  : a set of key strokes to be sent to the medit graphical
                window

        `silent`: (default `True`) If `silent`, then standard output of medit is
                hidden in the python execution shell

        `block` : block execution until window is closed
        """
        from .utils.external import medit

        if title:
            display(title, level=0, debug=self.debug, color="green")
        medit(self.mesh, self, keys=keys, silent=silent, block=block)


class P1Vector3D(__AbstractSol):
    """
    A structure for 3D P1 vector fields (piecewise linear on each tetrahedra)
    defined on a 3D mesh, based on the INRIA `.sol` and `.solb` formats.
    """

    def __init__(
        self,
        M: Mesh3D,
        phi: str | list | np.ndarray | list[P1Function] | FunctionType = None,
        debug=None,
    ):
        """
        Load a P1 vector field on a 3D mesh.

        INPUTS
        ------

        `M`     : a `Mesh3D` object

        phi     :  Either:
        - the path of a `.sol` or `.solb` file
        - the path of a `.gp` file with an array of values of the solution
            saved line by line and separated by spaces (of size `(M.nv,3)`)
        - a list or a `np.array` of function values for each of the mesh
            vertices (of size `(M.nv,3)`)
        - a list of three P1 functions determining the components x, y and z
        - a lambda function `lambda x : [ux(x),uy(x),uz(x)]`.
            The components of the vector at each vertices
            `(x[0],x[1],x[2])` is computed accordingly.

        debug : a level of verbosity for debugging when operations are applied to `phi`

        EXAMPLES
        --------
        >>> phi = P1Vector3D(M, "u.sol")
        >>> # vector field (x,1,0)
        >>> phi = P1Vector3D(M, lambda x : [x[0],1,0])
        """

        try:
            super().__init__(M, phi, debug)
        except SolException:
            self.n = self.mesh.nv
            self.nsol = 1
            self.sol_types = np.asarray([2])
            if isinstance(phi, list) and len(phi) == 3:
                x = P1Function3D(M, phi[0], self.debug)
                y = P1Function3D(M, phi[1], self.debug)
                z = P1Function3D(M, phi[2], self.debug)
                self.sol = np.column_stack((x.sol, y.sol, z.sol))
            elif callable(phi):
                self.sol = np.apply_along_axis(phi, 1, self.mesh.vertices)
            elif phi is None:
                self.sol = np.zeros((self.mesh.nv, 3))
            elif isinstance(phi, P1Vector3D):
                self.sol = phi.sol.copy()
            else:
                self.sol = np.asarray(phi)
        if self.nsol != 1 or self.sol_types.tolist() != [2]:
            raise Exception(f"Error: {phi} is invalid P1Vector solution file.")
        if self.Dimension != 3:
            raise Exception(f"Error: {phi} should be associated with a 2D mesh.")
        if self.sol.shape != (self.mesh.nv, 3):
            raise Exception(
                "Error: the provided array of values should be"
                f" of size ({self.mesh.nv},3) while it is of size {self.sol.shape}."
            )

    @property
    def x(self) -> "P1Function3D":
        """
        The x component of a P1 vector as a P1 function.
        """
        return P1Function3D(self.mesh, self.sol[:, 0], self.debug)

    @property
    def y(self) -> "P1Function3D":
        """
        The y component of a P1 vector as a P1 function.
        """
        return P1Function3D(self.mesh, self.sol[:, 1], self.debug)

    @property
    def z(self) -> "P1Function3D":
        """
        The z component of a P1 vector as a P1 function.
        """
        return P1Function3D(self.mesh, self.sol[:, 2], self.debug)

    def plot(
        self, title: str | None = None, keys: str | None = None, silent: bool = True
    ):
        """
        Plot a 3D P1 vector with `medit` (it seems it is not fully supported).

        INPUT
        -----

        `title` : a message to be printed in the console before plotting

        `keys`  : a set of key strokes to be sent to the `medit` graphical window

        `silent`: (default `True`) If `silent`, then standard output of `medit` is
                hidden in the python execution shell
        """
        from .utils.external import medit

        if title:
            display(title, level=0, debug=self.debug, color="green")
        medit(self.mesh, self, keys=keys, silent=silent)
