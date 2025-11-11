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

from .mesh import Mesh, shapeGradients, integrateP0P1Matrix, integrateP1P1Matrix, metric
from .abstract import __AbstractSol, display, SolException
from .P0 import P0Function
from .utils.timing import tic, toc


class P1Function(__AbstractSol):
    """
    A structure for P1 functions (piecewise linear on each triangle)
    defined on a 2D mesh, based on the INRIA `.sol` and `.solb` formats.
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
        - the path of a `.sol` or `.solb` file
        - the path of a ".gp" file with a list of values of the solution
            saved line by line (of size `M.nv`)
        - a list or a numpy.ndarray of function values for each of the mesh
            vertices (of size `M.nv`)
        - a lambda function `lambda x : f(x)`. The values at each vertices
            `(x[0],x[1])` will be computed accordingly.
        - a `P0Function` `phi`, in that case the conversion of `phi` to a P0
            function is performed by solving the variational problem:
            find `phiP1` a `P1Function` such that for all `v` `P1Function`,
            `int2d(M)(phiP1*v)=int2d(M)(phi*v)`.

        `debug` : a level of verbosity for debugging when operations are applied to `phi`

        EXAMPLES
        --------
        >>> phi1 = P1Function(M, "phi.sol")
        >>> phi2 = P1Function(M, lambda x : x[0])
        >>> phi3 = P1Function(M, M.vertices[:,-1]) #values of the tags of the vertices
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
                M.save(f"{runner.script_dir}/Th.mesh")
                runner.execute({"IMPORT": importfrom})
                self.__init__(M, f"{runner.script_dir}/phi.sol", debug)
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
            elif isinstance(phi, P1Function):
                self.sol = phi.sol.copy()
            elif phi is None:
                self.sol = np.zeros(self.mesh.nv)
        if self.nsol != 1 or self.sol_types.tolist() != [1] or self.n != self.mesh.nv:
            raise Exception(f"Error: {phi} is invalid P1Function solution file.")
        if self.Dimension != 2:
            raise Exception(f"Error: {phi} should be associated with a 2D mesh.")
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

        `(gradx,grady)` where `gradx` and `grady` are of size `self.mesh.nt` and
        containing the values of the gradient of self on every triangle
        """
        gradLambdaA, gradLambdaB, gradLambdaC = shapeGradients(self.mesh)
        if not hasattr(self, "_P1Function__gradientP0"):
            self.__gradientP0 = (
                gradLambdaA.T * self.sol[self.mesh.triangles[:, 0] - 1]
                + gradLambdaB.T * self.sol[self.mesh.triangles[:, 1] - 1]
                + gradLambdaC.T * self.sol[self.mesh.triangles[:, 2] - 1]
            ).T
        return self.__gradientP0

    def gradientP1(self) -> "P1Vector":
        """
        Returns the gradient of the P1 function as a `P1Vector`.
        The gradient is computed by converting the components of the
        P0 gradient into a P1 functions.
        """
        return P1Vector(self.mesh, [self.dxP1(), self.dyP1()])

    def dxP0(self) -> P0Function:
        """
        Returns the x-component of the P0 gradient.
        """
        return P0Function(self.mesh, self.gradientP0()[:, 0])

    def dyP0(self) -> P0Function:
        """
        Returns the y-component of the P0 gradient.
        """
        return P0Function(self.mesh, self.gradientP0()[:, 1])

    def dxP1(self) -> "P1Function":
        """
        Returns the x component of the P1 gradient.
        """
        return P1Function(self.mesh, self.dxP0())

    def dyP1(self) -> "P1Function":
        """
        Returns the y component of the P1 gradient.
        """
        return P1Function(self.mesh, self.dyP0())

    def eval(self, x):
        """
        Evaluate at a set of points `x` using piecewise linear interpolation.
        """
        x = np.asarray(x)
        if len(x.shape) == 1:
            x = x[None, :]
        if not hasattr(self, "_P1Function__triInterp"):
            from matplotlib.tri import Triangulation, LinearTriInterpolator

            triObj = Triangulation(self.mesh.vertices[:, 0], self.mesh.vertices[:, 1])
            # linear interpolation
            self.__triInterp = LinearTriInterpolator(triObj, self.sol)
        return self.__triInterp(x[:, 0], x[:, 1])

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

        x, y = self.mesh.vertices[:, 0], self.mesh.vertices[:, 1]
        triang = self.mesh.triangles[:, :-1] - 1
        z = self.sol

        if fig is None or ax is None:
            fig, ax = plt.subplots()
        else:
            doNotPlot = True
        if vmin is None or vmax is None:
            vmin = min(z)
            vmax = max(z)
        if vmin == vmax:
            levels = [0]
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

    # def plot(self, cmap='jet', doNotPlot=False, tickFormat='',
    #         niso=49, XLIM=None, YLIM=None,
    #         title=None, vmin=None, vmax=None, fill=True, boundary=None,boundary_linewidth=2,
    #         fig = None, ax = None,
    #         **kwargs):
    #    """Plot a P1 function with matplotlib."""
    #    import matplotlib as mp
    #    import matplotlib.pyplot as plt
    #    from mpl_toolkits.axes_grid1 import make_axes_locatable
    #    x, y = self.mesh.vertices[:, 0], self.mesh.vertices[:, 1]
    #    triang = self.mesh.triangles[:, :-1]-1

    #    z = self.sol
    #    cbar = None
    #    import ipdb
    #    ipdb.set_trace()
    #    if fill and fig is None:
    #        fig, ax = plt.subplots()
    #    if not vmin is None:
    #        levels = kwargs.get('levels', np.linspace(vmin, vmax, niso))
    #        if fill:
    #            plot = plt.tricontourf(x, y, triang, z, levels=levels,
    #                                   cmap=cmap)
    #        else:
    #            plot = plt.tricontour(x, y, triang, z,
    #                                  levels=levels)
    #    else:
    #        vmin = min(z)
    #        vmax = max(z)
    #        levels = kwargs.get('levels', np.linspace(vmin, vmax, niso))
    #        if fill:
    #            plot = ax.tricontourf(x, y, triang, z, niso, cmap=cmap, extend="both")
    #        else:
    #            fig, ax = self.mesh.plot(doNotPlot=True, colormap='dim',
    #                                     boundaryColor='b',
    #                                     boundary_linewidth=0.5, fig=fig, ax=ax)
    #            plot = ax.tricontour(x, y, triang, z, 1, levels=[
    #                                 0], linewidths=0.5, colors='indigo')
    #    if boundary:
    #        if boundary == 'all':
    #            boundary = self.mesh.Boundaries.keys()
    #        for i, bc in enumerate(boundary):
    #            edges = self.mesh.edges[np.where(self.mesh.edges[:, -1] == bc)[0]]
    #            X = self.mesh.vertices[edges[:, 0]-1][:, :-1]
    #            Y = self.mesh.vertices[edges[:, 1]-1][:, :-1]
    #            lines = [[tuple(x), tuple(y)]
    #                     for (x, y) in zip(X.tolist(), Y.tolist())]
    #            color = mp.cm.Dark2(i)
    #            lc = mp.collections.LineCollection(
    #                lines, linewidths=boundary_linewidth, colors=color,
    #                zorder=100)
    #            ax.add_collection(lc)
    #    if title:
    #        plt.title(title)
    #    if fill:
    #        divider = make_axes_locatable(ax)
    #        cax = divider.append_axes("right", size="5%", pad=0.05)
    #        ax.margins(0)
    #        cbar = fig.colorbar(plot, cax=cax)
    #        cbar.set_ticks(np.linspace(vmin, vmax, 5))
    #        if tickFormat:
    #            cbar.set_ticklabels([format(x, tickFormat)
    #                                 for x in np.linspace(vmin, vmax, 5)])
    #        cbar.ax.tick_params(labelsize=16)
    #        if not kwargs.get('colorbar',True):
    #            cbar.remove()
    #    ax.set_aspect('equal')
    #    ax.tick_params(axis='both', which='both', length=0)
    #    plt.setp(ax.get_xticklabels(), visible=False)
    #    plt.setp(ax.get_yticklabels(), visible=False)
    #    if not XLIM is None:
    #        ax.set_xlim(XLIM)
    #    if not YLIM is None:
    #        ax.set_ylim(YLIM)
    #    if not doNotPlot:
    #        plt.show()
    #    return fig, ax, cbar


class P1Vector(__AbstractSol):
    """
    A structure for P1 vectors (components are piecewise linear on
    each triangle) on a 2D mesh, based on the INRIA `.sol` and `.solb` formats.
    """

    def __init__(
        self,
        M: Mesh,
        phi: str | list | np.ndarray | FunctionType | None = None,
        debug: int | None = None,
    ):
        """
        Load a P1 vector on a 2D mesh.

        INPUTS
        ------

        `M`    :  a 2D `Mesh` object

        `phi`  :  Either:
        - the path of a ".sol" or ".solb" file
        - the path of a ".gp" file with an array of values of the solution
            saved line by line and separated by spaces (of size `(M.nv,2)`)
        - a list or a numpy.ndarray of function values for each of the mesh
            vertices (of size `(M.nv,2)`)
        - a list of two P1 functions determining the components x and y
        - a lambda function `lambda x : [ux(x),uy(x)]`.
            The components of the vector at each vertices
            `(x[0],x[1])` is computed accordingly.

        `debug` : a level of verbosity for debugging when operations are applied to `phi`

        EXAMPLES
        --------
        >>> phi = P1Vector(M, "u.sol")
        >>> phi = P1Vector(M, lambda x : [x[0],1]) # vector field (x,1)
        """
        try:
            super().__init__(M, phi, debug)
        except SolException:
            self.n = self.mesh.nv
            self.nsol = 1
            self.sol_types = np.asarray([2])
            if isinstance(phi, list) and len(phi) == 2:
                x = P1Function(M, phi[0], self.debug)
                y = P1Function(M, phi[1], self.debug)
                self.sol = np.column_stack((x.sol, y.sol))
            elif callable(phi):
                self.sol = np.apply_along_axis(phi, 1, self.mesh.vertices)
            elif phi is None:
                self.sol = np.zeros((self.mesh.nv, 2))
            elif isinstance(phi, P1Vector):
                self.sol = phi.sol.copy()
            else:
                self.sol = np.asarray(phi)
        if self.nsol != 1 or self.sol_types.tolist() != [2]:
            raise Exception(f"Error: {phi} is invalid P1Vector solution file.")
        if self.Dimension != 2:
            raise Exception(f"Error: {phi} should be associated with a 2D mesh.")
        if self.sol.shape != (self.mesh.nv, 2):
            raise Exception(
                "Error: the provided array of values should be"
                f" of size ({self.mesh.nv},2) while it is of size {self.sol.shape}."
            )

    @property
    def x(self) -> P1Function:
        """
        The x component of a P1 vector as a P1 function.
        """
        return P1Function(self.mesh, self.sol[:, 0], self.debug)

    @property
    def y(self) -> P1Function:
        """
        The y component of a P1 vector as a P1 function.
        """
        return P1Function(self.mesh, self.sol[:, 1], self.debug)

    def plot(
        self,
        title: str | None = None,
        doNotPlot: bool = False,
        XLIM: tuple[float, float] = None,
        YLIM: tuple[float, float] = None,
        fig=None,
        ax=None,
        scaling: float = 1.5,
        color: bool = False,
        background: bool = True,
        **kwargs,
    ):
        """Quiver plot of a 2D vector field with matplotlib."""
        import matplotlib.pyplot as plt
        import matplotlib as mp

        x, y = self.mesh.vertices[:, 0], self.mesh.vertices[:, 1]
        (vx, vy) = zip(*self.sol)
        if fig is None and background:
            if background == "norm":
                norms = [np.sqrt(x**2 + y**2) for (x, y) in zip(vx, vy)]
                fig, ax, _ = P1Function(self.mesh, norms).plot(
                    doNotPlot=True, colorbar=False
                )
            elif color:
                fig, ax = self.mesh.plot(
                    doNotPlot=True,
                    colormap=[[1, 1, 1], [1, 1, 1]],
                    edgeColor="gray",
                )
            else:
                fig, ax = self.mesh.plot(
                    doNotPlot=True,
                    colormap=[[0.9, 0.9, 1], [1, 1, 0.9]],
                    edgeColor="gray",
                )
        if not background:
            ax = plt.subplot()
        norms = [np.sqrt(x**2 + y**2) for (x, y) in zip(vx, vy)]
        _, h = metric(self.mesh, True)
        localSize = (1 / np.sqrt(h[:, 0]) + 1 / np.sqrt(h[:, 1])) * 0.5

        meshSize = np.mean(localSize)  # * scaling
        rescale = np.max(norms) / meshSize
        vx = [x / rescale for x in vx]
        vy = [y / rescale for y in vy]
        norm = mp.colors.Normalize()
        norm.autoscale(norms)
        scale = kwargs.get("scale", 1)
        width = kwargs.get("width", 0.002)
        alpha = kwargs.get("alpha", 0.8)
        headwidth = kwargs.get("headwidth", 3.0)
        if color:
            if isinstance(color, str):
                plot = ax.quiver(
                    x,
                    y,
                    vx,
                    vy,
                    units="xy",
                    scale_units="xy",
                    color=color,
                    angles="xy",
                    scale=scale,
                    width=width,
                    headwidth=headwidth,
                    alpha=alpha,
                )
            else:
                plot = ax.quiver(
                    x,
                    y,
                    vx,
                    vy,
                    norms,
                    units="xy",
                    scale_units="xy",
                    cmap=mp.cm.jet,
                    angles="xy",
                    scale=scale,
                    width=width,
                    headwidth=headwidth,
                    alpha=alpha,
                )
        else:
            plot = ax.quiver(
                x,
                y,
                vx,
                vy,
                color="black",
                units="xy",
                scale_units="xy",
                angles="xy",
                scale=scale,
                width=width,
                headwidth=headwidth,
                alpha=alpha,
            )
        if color:
            ax.margins(0)
            cbar = fig.colorbar(plot)
            # cbar.set_ticks(np.linspace(vmin, vmax, 5))
            # if tickFormat:
            #    cbar.set_ticklabels([format(x, tickFormat)
            #                         for x in np.linspace(vmin, vmax, 5)])
            cbar.ax.tick_params(labelsize=16)
        if title:
            plt.title(title)
        if not XLIM is None:
            ax.set_xlim(XLIM)
        if not YLIM is None:
            ax.set_ylim(YLIM)
        if not doNotPlot:
            plt.show()
        return fig, ax


class P1Metric(__AbstractSol):
    """
    A structure for metric files to use with mesh adaptation based on
    the INRIA `.sol` and `.solb` formats.
    """

    def __init__(
        self, M: Mesh, phi=None, isotropic: bool = False, debug: int | None = None
    ):
        try:
            super().__init__(M, phi, debug)
        except SolException:
            self.n = self.mesh.nv
            self.nsol = 1
            self.sol_types = np.asarray([3], dtype=int)
            if isinstance(phi, list) and len(phi) == 3:
                m11 = P1Function(M, phi[0], self.debug)
                m12 = P1Function(M, phi[1], self.debug)
                m22 = P1Function(M, phi[2], self.debug)
                self.sol = np.column_stack((m11.sol, m12.sol, m22.sol))
            elif callable(phi):
                self.sol = np.apply_along_axis(phi, 1, self.mesh.vertices)
            elif phi is None:
                self.sol = np.zeros((self.mesh.nv, 3))
            elif isinstance(phi, __AbstractSol):
                self.sol = phi.sol.copy()
            else:
                self.sol = np.asarray(phi)
            if isotropic:
                if self.sol.shape != (self.mesh.nv,):
                    raise Exception(
                        "Error: provide only one component if you want to "
                        "define an isotropic metric field."
                    )
                self.sol = np.column_stack(
                    (self.sol, np.zeros_like(self.sol), self.sol)
                )
        if self.nsol != 1 or self.sol_types.tolist() != [3]:
            raise Exception(f"Error: {phi} is invalid P1Metric solution file.")
        if self.Dimension != 2:
            raise Exception(f"Error: {phi} should be associated with a 2D mesh.")
        if self.sol.shape != (self.mesh.nv, 3):
            raise Exception(
                "Error: the provided array of values should be"
                f" of size ({self.mesh.nv},3) while it is of size {self.sol.shape}."
            )
