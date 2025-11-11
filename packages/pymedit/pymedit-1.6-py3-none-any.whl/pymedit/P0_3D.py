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
from types import FunctionType
from typing import Union

import pyvista as pv
from .mesh3D import Mesh3D, meshCenters3D
from .abstract import __AbstractSol, SolException, display


class P0Function3D(__AbstractSol):
    """
    A structure for 3D P0 functions (constant on each tetrahedra)
    defined on a mesh, based on the INRIA `.sol` and `.solb` formats.
    """

    # TODO fix type annotation "P1Function3D" using 'from __future__ import annotations'
    # then replace: phi.__class__.__name__ == "P1Function3D"
    # with isinstance()

    def __init__(
        self,
        M: Mesh3D,
        phi: Union[str, list, np.ndarray, FunctionType, "P1Function3D", None] = None,
        debug: int | None = None,
    ):
        """
        Load a 3D P0 function.

        INPUTS
        ------

        `M`     : a `Mesh3D` object

        `phi`   : Either:
        - the path of a `.sol` or `.solb` file
        - the path of a `.gp` file with a list of values of the solution
          saved line by line (of size `M.ntet`)
        - a list or a `np.array` of function values for each of the mesh
            tetrahedra (of size `M.ntet`)
        - a lambda function `lambda x : f(x)`. The values of the P0 function
            is determined by the values of the function at the center `(x[0],x[1],x[2])` of each tetrahedra
        - a `P1Function3D` `phi`, in that case the value of the solution
            at the tetrahedra `i` is the mean of the values of `phi` at the vertices of the tetrahedra `i`

        `debug` : a level of verbosity for debugging when operations are applied to `phi`

        EXAMPLES
        --------
        >>> phi = P0Function3D(M, "phi.sol")
        >>> phi = P0Function3D(M, lambda x : x[0])
        >>> phi = P0Function3D(M, M.tetrahedra[:,-1]) #values of the tags of the triangles
        """
        try:
            super().__init__(M, phi, debug)
        except SolException:
            self.n = self.mesh.ntet
            self.nsol = 1
            self.sol_types = np.asarray([1])
            if callable(phi):
                self.sol = np.apply_along_axis(phi, 1, meshCenters3D(M))
            elif phi is None:
                self.sol = np.zeros(self.mesh.ntet)
            elif phi.__class__.__name__ == "P1Function3D":
                self.sol = (
                    phi[self.mesh.tetrahedra[:, 0] - 1]
                    + phi[self.mesh.tetrahedra[:, 1] - 1]
                    + phi[self.mesh.tetrahedra[:, 2] - 1]
                    + phi[self.mesh.tetrahedra[:, 3] - 1]
                ) / 4
        if self.nsol != 1 or self.sol_types.tolist() != [1] or self.n != self.mesh.ntet:
            raise Exception("Error: invalid P0Function3D solution.")
        if self.Dimension != 3:
            raise Exception(f"Error: {phi} should be associated with a 3D mesh.")
        if self.sol.shape != (self.mesh.ntet,) or self.n != self.mesh.ntet:
            raise Exception(
                "Error: the provided array of values should be"
                f" of size ({self.mesh.ntet},) while it is of size {self.sol.shape}."
            )

    def plot(self, title: str = 'sol', **kwargs):
        pvmesh, _ = self.mesh.to_pvmesh()
        pvmesh.cell_data[title] = self.sol
        plotter = pv.Plotter()

        toggle = False
        saved_normal = (1, 0, 0)
        saved_origin = np.array(pvmesh.center)
        plotter.add_mesh(pvmesh, 
                         name="P1",
                         scalars=title,**kwargs)

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
                                     scalars=title,
                                     **kwargs)

                # Widget plan avec dernière position connue
                plotter.add_plane_widget(
                    callback=clip_callback,
                    normal=saved_normal,
                    origin=saved_origin,
                    implicit=True,
                    bounds = pvmesh.bounds
                )
                toggle = True

            else:
                toggle = False
                # Nettoyer le clipping et remettre la scène originale
                plotter.clear_plane_widgets()
                plotter.remove_actor('P1_clip')

                plotter.add_mesh(pvmesh, 
                                 name="P1",
                                 scalars=title, **kwargs)
        plotter.add_key_event("F1", toggle_clipping)
        print("Interactive plot with PyVista.")
        print("Press F1 for clipping")
        plotter.show()

    def plot_medit(
        self, title: str | None = None, keys: str | None = None, silent: bool = True
    ):
        """
        Plot a 3D P0 function with `medit`.

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
