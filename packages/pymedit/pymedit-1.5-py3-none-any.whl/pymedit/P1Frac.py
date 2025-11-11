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
from typing import Literal

from .mesh import Mesh, integrateP0P1Matrix
from .mesh import integrateP1P1Matrix
from .abstract import __AbstractSol, display, SolException
from .P0 import P0Function
from .utils.timing import tic, toc


class P1FracFunction(__AbstractSol):
    """
    A structure for P1 functions (piecewise linear on each triangle)
    defined on a fractured 2D mesh, based on the INRIA .sol and .solb formats.
    """

    def __init__(
        self,
        M: Mesh,
        phi: str | list | np.ndarray | FunctionType | P0Function | None = None,
        debug: int | None = None,
        importfrom=None,
    ):
        """
        Load a P1 function on a 2D mesh.

        INPUTS
        ------

        `M`    :  input 2D mesh

        `phi`  :  Either:
            - the path of a ".sol" or ".solb" file
            - the path of a ".gp" file with a list of values of the solution
              saved line by line (of size `M.nv`)
            - a list or a numpy.ndarray of function values for each of the mesh
              vertices (of size `M.nv`)
            - a lambda function `lambda x : f(x)`. The values at each vertices
                `(x[0],x[1])` will be computed accordingly.
            - a `P0Function` phi, in that case the conversion of phi to a P0
              function is performed by solving the variational problem
                Find `phiP1` a `P1Function` such that for all `v` `P1Function`,
                    int2d(M)(phiP1*v)=int2d(M)(phi*v).

        `debug` : a level of verbosity for debugging when operations are applied
                to `phi`
        """

        if importfrom:
            from pyfreefem import FreeFemRunner

            code = (
                """
                load "medit";
                mesh Th=readmesh("$SCRIPTDIR/Th.mesh");
                fespace Fh1b(Th,$IMPORT);
                fespace Fh1(Th,P1);
                Fh1b phi;
                {
                
                string dummy="";
                ifstream f("""
                + '"'
                + phi
                + '"'
                + """);
                f>>dummy;
                for(int i=0;i<Fh1b.ndof;i++){
                f>>phi[][i];
                }
                }
                Fh1 phiInterp=phi;
                savesol("$SCRIPTDIR/phi.sol",Th,phiInterp,order=1);
            """
            )
            if debug is None:
                debug = 0
            with FreeFemRunner(code, debug=debug) as runner:
                M.save(runner.script_dir + "/Th.mesh")
                runner.execute({"IMPORT": importfrom})
                self.__init__(M, runner.script_dir + "/phi.sol", debug)
            return
        try:
            super().__init__(M, phi, debug)
            self.sol = self.sol.flatten()
        except SolException:
            self.n = self.mesh.nv
            self.nsol = 1
            self.sol_types = np.asarray([1])

            if callable(phi):
                try:
                    self.sol = np.apply_along_axis(phi, 1, self.mesh.vertices)
                except TypeError:
                    newsol = lambda x: phi(x[0], x[1])
                    self.sol = np.apply_along_axis(newsol, 1, self.mesh.vertices)
                self.sol = self.sol.astype(float)
            elif isinstance(phi, P0Function):
                display(
                    "Converting P0 function into P1 function.", 2, self.debug, "green"
                )
                tic(20)
                B = integrateP0P1Matrix(self.mesh)
                A = integrateP1P1Matrix(self.mesh)
                RHS = B.dot(phi.sol)
                self.sol = lg.spsolve(A, RHS)
                display(
                    f"Conversion achieved in {toc(20)}s.", 3, self.debug, "orange_4a"
                )
            elif isinstance(phi, P1FracFunction):
                self.sol = phi.sol.copy()
            elif phi is None:
                self.sol = np.zeros(self.mesh.nv)
        if self.nsol != 1 or self.sol_types.tolist() != [1]:
            raise Exception(f"Error: {phi} is invalid P1Function solution file.")
        if self.Dimension != 2:
            raise Exception(f"Error: {phi} should be associated with a 2D mesh.")

        """if self.sol.shape != (self.mesh.nv,) or self.n != self.mesh.nv:
            raise Exception(
                "Error: the provided array of values should be"
                f" of size ({self.mesh.nv},) while it is of size "
                f"{self.sol.shape}."
            )"""

    def plot(
        self,
        title: str | None = None,
        fig=None,
        ax=None,
        cmap: str = "jet",
        doNotPlot: bool = False,
        tickFormat: str = "",
        niso: int = 49,
        XLIM: tuple[float, float] = None,
        YLIM: tuple[float, float] = None,
        type_plot: Literal["tricontourf", "tricontour", "tripcolor"] = "tricontourf",
        vmin: float | None = None,
        vmax: float | None = None,
        boundary: list[int] | Literal["all"] | None = None,
        boundary_linewidth: float = 2,
        **kwargs,
    ):
        import matplotlib as mp
        import matplotlib.pyplot as plt
        from mpl_toolkits.axes_grid1 import make_axes_locatable

        triang = self.local_to_global
        F = self.global_to_local
        X = np.zeros((self.ngv, 2))
        X += self.mesh.vertices[F[:, 0], :-1]
        x, y = X[:, 0], X[:, 1]
        z = self.sol

        if fig is None or ax is None:
            fig, ax = plt.subplots()
        else:
            doNotPlot = True
        if vmin is None or vmax is None:
            vmin = min(z)
            vmax = max(z)
        if vmin == vmax:
            levels = None
        else:
            levels = kwargs.get("levels", np.linspace(vmin, vmax, niso))
        if "colors" in kwargs:
            cmap = None
        if type_plot == "tricontourf":
            plot = ax.tricontourf(
                x,
                y,
                triang,
                z,
                niso,
                cmap=cmap,
                extend="both",
                colors=kwargs.get("colors", None),
                norm=kwargs.get("norm", None),
                levels=levels,
                antialiased=kwargs.get("antialiased", False),
            )
        elif type_plot == "tricontour":
            plot = ax.tricontour(
                x,
                y,
                triang,
                z,
                cmap=cmap,
                extend="both",
                levels=levels,
                linewidths=kwargs.get("linewidths", None),
                colors=kwargs.get("colors", None),
                norm=kwargs.get("norm", None),
            )
        elif type_plot == "tripcolor":
            plot = ax.tripcolor(
                x,
                y,
                triang,
                z,
                cmap=cmap,
                linewidths=kwargs.get("linewidths", None),
                norm=kwargs.get("norm", None),
                vmin=vmin,
                vmax=vmax,
            )
        if boundary:
            if boundary == "all":
                boundary = self.mesh.Boundaries.keys()
            for i, bc in enumerate(boundary):
                edges = self.mesh.edges[np.where(self.mesh.edges[:, -1] == bc)[0]]
                X = self.mesh.vertices[edges[:, 0] - 1][:, :-1]
                Y = self.mesh.vertices[edges[:, 1] - 1][:, :-1]
                lines = [[tuple(x), tuple(y)] for (x, y) in zip(X.tolist(), Y.tolist())]
                color = mp.cm.Dark2(i)
                lc = mp.collections.LineCollection(
                    lines, linewidths=boundary_linewidth, colors=color, zorder=100
                )
                ax.add_collection(lc)
        if title:
            ax.set_title(title)
        # Colorbar
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        ax.margins(0)
        cbar = None
        if levels is not None and len(levels) > 1:
            cbar = fig.colorbar(plot, cax=cax)
            cbar.set_ticks(np.linspace(vmin, vmax, 5))
            if tickFormat:
                cbar.set_ticklabels(
                    [format(x, tickFormat) for x in np.linspace(vmin, vmax, 5)]
                )
            # cbar.ax.tick_params(labelsize=16)
        if not kwargs.get("colorbar", True) and not cbar is None:
            cbar.remove()
        ax.set_aspect("equal")
        ax.tick_params(axis="both", which="both", length=0)
        plt.setp(ax.get_xticklabels(), visible=False)
        plt.setp(ax.get_yticklabels(), visible=False)
        if not XLIM is None:
            ax.set_xlim(XLIM)
        if not YLIM is None:
            ax.set_ylim(YLIM)
        if not doNotPlot:
            plt.show()
        return fig, ax, cbar
