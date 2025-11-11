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
import subprocess
import tempfile
import os
import time
import shutil
from types import FunctionType
from typing import Literal

from ..abstract import display, __AbstractMesh, exec2, __AbstractSol
from .timing import tic, toc
from ..mesh3D import Mesh3D
from ..mesh import Mesh
from ..P1 import P1Function, P1Vector
from ..P1_3D import P1Function3D, P1Vector3D, P0Function3D


def mshdist(
    M: Mesh | Mesh3D | str,
    output: str | None = None,
    fastMarching: bool = True,
    phi: P1Function | P1Function3D | None = None,
    dom: bool = True,
    verb: int | None = None,
    ncpu: int = 1,
    it: int | None = None,
    options: str | None = None,
    debug: int = 0,
) -> Literal[1] | P1Function | P1Function3D:
    """
    Compute the signed distance function of a mesh subdomain with `mshdist` (if available).
    See https://github.com/ISCDtoolbox/Mshdist and the examples
    pymedit/examples/iscd2d.py
    pymedit/examples/iscd3d.py

    INPUT
    -----

    `M`     : either a 2D `Mesh` object, a `Mesh3D` object or the path of a mesh file.

    `output`: (optional) a file name to save the solution.

    `debug` : a tuning level for the verbosity

    `phi`   : a level set function (for redistancing instead of computing the
              signed distance to a meshed subdomain)

    Other arguments are those of the `mshdist` command

    OUTPUT
    ------

    If `output` is not `None`, then the function returns 1 if the execution of
    `mshdist` is successful. The signed distance function can then be loaded
    from the user, e.g. with
    >>> phi=P1Function(M,output)

    If `output` is `None`, then the function returns the signed distance
    function as a `P1Function` or `P1Function3D` object.
    """
    if shutil.which("mshdist") is None:
        raise Exception(
            "Error: mshdist does not seem installed. "
            "Please install it for using mshdist command."
        )
    with tempfile.TemporaryDirectory() as tmpdir:
        if isinstance(M, str):
            meshFile = M
            outputMshdist = f"{os.path.splitext(M)[0]}.sol"
        else:
            meshFile = os.path.join(tmpdir, "Th.meshb")
            outputMshdist = f"{tmpdir}/Th.sol"
            M.debug -= 3
            M.save(meshFile)
            M.debug += 3
            debug = M.debug if debug is None else max(debug, M.debug)
        if isinstance(phi, str):
            solFile = f"{tmpdir}/Th.sol"
            exec2(f"cp {phi} {solFile}")
        elif isinstance(phi, P1Function) or isinstance(phi, P1Function3D):
            solFile = f"{tmpdir}/Th.sol"
            phi.debug -= 3
            phi.save(solFile)
            phi.debug += 3
        verbosity = debug if verb is None else verb
        cmd = f"mshdist -v {verbosity} -ncpu {ncpu} {meshFile}"
        if dom:
            cmd += " -dom"
        if it:
            cmd += f" -it {it}"
        if fastMarching:
            cmd += " -fmm"
        if options:
            cmd += f" {options}"
        exec2(cmd, level=1, debug=debug, silent=False)
        if isinstance(M, __AbstractMesh):
            if M.Dimension == 2:
                phi = P1Function(M, outputMshdist, debug - 3)
            elif M.Dimension == 3:
                phi = P1Function3D(M, outputMshdist, debug - 3)
            if output:
                phi.save(output)
            phi.debug += 3
            return phi
        if output:
            exec2(f"mv {outputMshdist} {output}", 5, debug)
    return 1


def advect(
    M: Mesh | Mesh3D | str,
    sol: P1Function | P1Function3D | str,
    vel: P1Vector | P1Vector3D | str,
    output: str | None = None,
    T: float = 1,
    verbosity: bool = False,
    debug: int = 0,
    nocfl: bool = True
) -> Literal[1] | P1Function | P1Function3D:
    """
    Advect a P1 function using the command `advect`
    See https://github.com/ISCDtoolbox/Advection and the examples
    pymedit/examples/iscd2d.py
    pymedit/examples/iscd3d.py

    INPUT
    -----

    `M`         : either a 2D `Mesh` object, a `Mesh3D` object or file path of the mesh

    `sol`       : either a `P1Function`, `P1Function3D` or file path of the
                  solution file to be advected

    `vel`       : either a `P1Vector`, `P1Vector3D` or file path of the advection
                  velocity

    `output`    : (optional) output path of the advected solution to be saved

    `T`         : final advection time

    `verbosity` : advect command verbosity

    `debug`     : tune the python shell verbosity

    `nocfl`     : use the parameter -nocfl in the advection

    OUTPUT
    ------

    If `output` is not `None`, then the function returns 1 if the execution of
    `advect` is successful. The advected function can then be loaded
    from the user, e.g. with
    >>> phi=P1Function(M,output)

    If `output` is `None`, then the function returns the advected
    function as a `P1Function` or `P1Function3D` object.
    """
    if shutil.which("advect") is None:
        raise Exception(
            "Error: advect does not seem installed. "
            "Please install it for using advect command.",
        )
    with tempfile.TemporaryDirectory() as tmpdir:
        if isinstance(sol, str):
            solFile = sol
        else:
            solFile = f"{tmpdir}/phi.chi.sol"
            sol.debug -= 3
            sol.save(solFile)
            sol.debug += 3
        if isinstance(M, str):
            meshFile = M
        else:
            meshFile = f"{tmpdir}/Th.meshb"
            M.debug -= 3
            M.save(meshFile)
            M.debug += 3
            debug = max(debug, M.debug)
        if isinstance(vel, str):
            velFile = vel
        else:
            velFile = f"{tmpdir}/velocity.solb"
            vel.debug -= 3
            vel.save(velFile)
            vel.debug += 3
        if output:
            outputAdvect = output
        else:
            outputAdvect = f"{tmpdir}/phi.o.solb"
        cmd = f"advect"+(" -nocfl" if nocfl else " ")+f" -dt {T} {meshFile} -c {solFile} -s {velFile} -o {outputAdvect}"
        if verbosity:
            cmd += " +v"
        exec2(cmd, level=1, debug=debug, silent=False)
        # Will return phi if output is none --> need to load M
        if isinstance(M, str) and output is None:
            M = __AbstractMesh(M)
        if isinstance(M, __AbstractMesh):
            if M.Dimension == 2:
                phi = P1Function(M, outputAdvect, debug=debug - 3)
            elif M.Dimension == 3:
                phi = P1Function3D(M, outputAdvect, debug=debug - 3)
            phi.debug += 3
            return phi
    return 1


def __mmgHeader(
    M: Mesh | Mesh3D | str,
    hmin: float | None = None,
    hmax: float | None = None,
    hgrad: float | None = None,
    hausd: float | None = None,
    params: str | None = None,
    output: str | None = None,
    sol: P1Function | str | None = None,
    ls: bool = False,
    verb: int = 0,
    nr: bool = True,
    extra_args: str = "",
    debug: int = 0,
    dimension: int = 2,
    tmpdir: str = "",
) -> tuple[str, str, str]:
    """Assemble mmg command arguments."""
    if isinstance(M, str):
        meshFile = M
    else:
        meshFile = f"{tmpdir}/Th.meshb"
        M.debug -= 3
        M.save(meshFile)
        M.debug += 3
    if output is None:
        outputMmg = f"{tmpdir}/Th.o.meshb"
    else:
        outputMmg = output
    options = ""
    if hausd is None and isinstance(hmin, float):
        hausd = 0.1 * hmin
    if nr:
        options += " -nr"
    if hmin:
        options += f" -hmin {hmin}"
    if hmax:
        options += f" -hmax {hmax}"
    if hgrad:
        options += f" -hgrad {hgrad}"
    if hausd:
        options += f" -hausd {hausd}"
    if ls:
        options += " -ls"
    if sol:
        if isinstance(sol, str):
            solFile = sol
        else:
            solFile = f"{tmpdir}/Th.solb"
            sol.debug -= 3
            sol.save(solFile)
            sol.debug += 3
        options += f" -sol {solFile}"
    if verb:
        options += f" -v {verb}"
    if output:
        options += f" -out {output}"
    if extra_args:
        options += f" {extra_args}"
    if params:
        paramFile = f"{os.path.splitext(meshFile)[0]}.mmg{dimension}d"
        if os.path.isfile(params):
            exec2(f"cp {params} {paramFile}", level=5, debug=debug)
        else:
            with open(paramFile, "w") as f:
                f.write(params)
    return options, meshFile, outputMmg


def mmg2d(
    M: Mesh | str,
    hmin: float | None = None,
    hmax: float | None = None,
    hgrad: float | None = None,
    hausd: float | None = None,
    output: str | None = None,
    sol: str | P1Function | None = None,
    ls: bool = False,
    verb: int = 0,
    nr: bool = True,
    params: str | None = None,
    extra_args: str = "",
    debug: int = 0,
) -> Mesh:
    """
    Remesh a 2D mesh using the command `mmg2d_O3`.
    See https://www.mmgtools.org/ and the example
    pymedit/examples/iscd2d.py

    INPUT
    -----

    `M`       : either a 2D `Mesh` object or the file path of the mesh

    `hmin`, `hmax`, `hgrad`, `hausd` : remeshing parameters

    `output`  : (optional) output path of the remeshed mesh to be saved

    `sol`     : either a metric file if `ls=False` (level set mode disabled)
                a level set `P1Function` or solution file  if `ls=True`(level set mode)

    `ls`     : if set to `True`, then remesh according to the zero isovalue of
               the level set function sol

    `verb`   : tune Mmg verbosity

    `nr`     : if `True`, call mmg2d_O3 with option "-nr" (no ridge detection)

    `params` : a file path or the content of the file setting local
              remeshing parameters.
              See https://www.mmgtools.org/local-parameters-for-boundaries

    `extra_args`: extra arguments to pass to the mmg2d_O3 command

    `debug`   : tune the python shell verbosity

    OUTPUT
    ------

    If `output` is not `None`, then the function returns 1 if the execution of
    mmg2d_O3 is successful. The output mesh can then be loaded
    from the user, e.g. with
    >>> M=Mesh(output)


    If `output` is `None`, then the function returns the remeshed 2D mesh as
    a `Mesh` object.
    """

    if shutil.which("mmg2d_O3") is None:
        raise Exception(
            "Error: mmg2d_O3 does not seem installed. "
            "Please install it for using mmg2d command.",
        )

    if isinstance(M, Mesh):
        debug = max(debug, M.debug)
    with tempfile.TemporaryDirectory() as tmpdir:
        options, meshFile, outputMmg = __mmgHeader(
            M,
            hmin,
            hmax,
            hgrad,
            hausd,
            params,
            output,
            sol,
            ls,
            verb,
            nr,
            extra_args,
            debug,
            2,
            tmpdir,
        )
        cmd = f"mmg2d_O3{options} {meshFile}"
        exec2(cmd, level=1, debug=debug, silent=False)

        # Load and returns the new mesh
        Mnew = Mesh(outputMmg, debug=debug - 3)
        Mnew.debug += 3
        return Mnew


def mmg2d_lsopen(
    M: Mesh | str,
    phi: P1Function,
    psi: P1Function,
    hmin: float | None = None,
    hmax: float | None = None,
    hgrad: float | None = None,
    hausd: float | None = None,
    output: str | None = None,
    verb: int = 0,
    nr: bool = True,
    params: str | None = None,
    extra_args: str = "",
    debug: int = 0,
) -> Literal[1] | Mesh:
    """
    TODO once -lsopen is official
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        phi_sol = f"{tmpdir}/phi.sol"
        phi.save(phi_sol)
        psi_sol = f"{tmpdir}/psi.sol"
        psi.save(psi_sol)

        newM = mmg2d(
            M,
            hmin,
            hmax,
            hgrad,
            hausd,
            output,
            verb=verb,
            nr=nr,
            params=params,
            extra_args=f"-lsopen -phi {phi_sol} -psi {psi_sol} {extra_args}",
            debug=debug,
        )
        if isinstance(M,Mesh): 
            return newM
        else:
            return 1

def mmg3d_lsopen(
    M: Mesh | str,
    phi: P1Function,
    psi: P1Function,
    hmin: float | None = None,
    hmax: float | None = None,
    hgrad: float | None = None,
    hausd: float | None = None,
    output: str | None = None,
    verb: int = 0,
    nr: bool = True,
    params: str | None = None,
    extra_args: str = "",
    debug: int = 0,
) -> Literal[1] | Mesh:
    """
    TODO once -lsopen is official
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        phi_sol = f"{tmpdir}/phi.sol"
        phi.save(phi_sol)
        psi_sol = f"{tmpdir}/psi.sol"
        psi.save(psi_sol)

        newM = mmg3d(
            M,
            hmin,
            hmax,
            hgrad,
            hausd,
            output,
            verb=verb,
            nr=nr,
            params=params,
            extra_args=f"-lsopen -phi {phi_sol} -psi {psi_sol} {extra_args}",
            debug=debug,
        )
        if output is None:
            return newM
    return 1

def parmmg(
    M: Mesh3D | str,
    hmin: float | None = None,
    hmax: float | None = None,
    hgrad: float | None = None,
    hausd: float | None = None,
    output: str | None = None,
    sol: str | P1Function3D | None = None,
    verb: int = 0,
    params: str | None = None,
    ncpu: int = 1,
    mpicmd: str = "mpirun",
    extra_args: str = "",
    debug: int = 0,
):
    """
    Remesh a 3D mesh using the command `parmmg_O3` with default options

    INPUT
    -----

    `M`         : either a `Mesh3D` object or the file path of the mesh

    `hmin`, `hmax`, `hgrad`, `hausd` : remeshing parameters

    `output`    : (optional) output path of the remeshed mesh to be saved

    `sol`       : a metric file

    `verb`      : tune parmmg verbosity

    `params`    : a file path or the content of the file setting local
                  remeshing parameters.
                  See https://www.mmgtools.org/local-parameters-for-boundaries

    `extra_args`: extra arguments to pass to the `parmmg_O3` command

    `debug`     : tune the python shell verbosity

    OUTPUT
    ------

    If `output` is not `None`, then the function returns 1 if the execution of
    `mmg3d_O3` is successful. The output mesh can then be loaded
    from the user, e.g. with
    >>> M=Mesh3D(output)

    If `output` is `None`, then the function returns the remeshed 3D mesh as
    a Mesh3D object.
    """
    if shutil.which("parmmg_O3") is None:
        raise Exception(
            "Error: parmmg_O3 does not seem installed. "
            "Please install it for using parmmg_O3 command.",
        )
    if isinstance(M, Mesh3D):
        debug = max(M.debug, debug)
    with tempfile.TemporaryDirectory() as tmpdir:
        options, meshFile, outputMmg = __mmgHeader(
            M,
            hmin,
            hmax,
            hgrad,
            hausd,
            params,
            output,
            sol,
            False,
            verb,
            False,
            extra_args=extra_args,
            debug=debug,
            dimension=3,
            tmpdir=tmpdir,
        )
        cmd = f"{mpicmd} -np {ncpu} parmmg_O3 {meshFile} {options}"
        returncode, _, _, stdout = exec2(
            cmd, level=1, debug=debug, silent=False, strict=False
        )
        if returncode != 0:
            display(
                f"Warning, parmmg exited with return code {returncode}.",
                color="red",
                level=0,
                debug=debug,
                flag="warning",
            )
            raise Exception()

        if output is None:
            # Load and returns the new mesh
            Mnew = Mesh3D(outputMmg, debug=debug - 3)
            Mnew.debug += 3
            return Mnew
    return 1


def mmg3d(
    M: Mesh3D | str,
    hmin: float | None = None,
    hmax: float | None = None,
    hgrad: float | None = None,
    hausd: float | None = None,
    output: str | None = None,
    sol: str | P1Function3D | None = None,  # TODO other?
    ls: bool = False,
    verb: int = 0,
    nr: bool = True,
    params: str | None = None,
    extra_args: str = "",
    debug: int = 0,
):
    """
    Remesh a 3D mesh using the command `mmg3d_O3`
    See https://www.mmgtools.org/ and the example
    pymedit/examples/iscd3d.py

    INPUT
    -----

    `M`         : either a `Mesh3D` object or the file path of the mesh

    `hmin`, `hmax`, `hgrad`, `hausd` : remeshing parameters

    `output`    : (optional) output path of the remeshed mesh to be saved

    sol         : either a metric file if `ls=False` (level set mode disabled)
                  a level set P1Function or solution file  if `ls=True` (level set mode)

    `ls`        : if set to `True`, then remesh according to the zero isovalue of
                  the level set function sol

    `verb`      : tune Mmg verbosity

    `nr`        : if `True`, call mmg3d_O3 with option "-nr" (no ridge detection)

    `params`    : a file path or the content of the file setting local
                  remeshing parameters.
                  See https://www.mmgtools.org/local-parameters-for-boundaries

    `extra_args`: extra arguments to pass to the mmg3d_O3 command

    `debug`     : tune the python shell verbosity

    OUTPUT
    ------

    If `output` is not `None`, then the function returns 1 if the execution of
    `mmg3d_O3` is successful. The output mesh can then be loaded
    from the user, e.g. with
    >>> M=Mesh3D(output)

    If `output` is `None`, then the function returns the remeshed 3D mesh as
    a `Mesh3D` object.
    """
    if shutil.which("mmg3d_O3") is None:
        raise Exception(
            "Error: mmg3d_O3 does not seem installed. "
            "Please install it for using mmg3d command.",
        )
    if isinstance(M, Mesh3D):
        debug = max(M.debug, debug)
    with tempfile.TemporaryDirectory() as tmpdir:
        options, meshFile, outputMmg = __mmgHeader(
            M,
            hmin,
            hmax,
            hgrad,
            hausd,
            params,
            output,
            sol,
            ls,
            verb,
            nr,
            extra_args=extra_args,
            debug=debug,
            dimension=3,
            tmpdir=tmpdir,
        )
        cmd = f"mmg3d_O3{options} {meshFile}"
        returncode, _, _, stdout = exec2(
            cmd, level=1, debug=debug, silent=False, strict=False
        )
        if returncode != 0:
            display(
                f"Warning, mmg exited with return code {returncode}.",
                color="red",
                level=0,
                debug=debug,
                flag="warning",
            )
        if "Check" in stdout:
            display(
                "Warning, mmg encountered quality problem.",
                color="red",
                level=0,
                debug=debug,
                flag="warning",
            )
        if "Topological" in stdout:
            display(
                "Warning, mmg encountered topological problem.",
                color="red",
                level=0,
                debug=debug,
                flag="warning",
            )
        if "rarely pass" in stdout:
            display(
                "Warning, mmg encountered 'we should rarely pass here' problem.",
                color="red",
                level=0,
                debug=debug,
                flag="warning",
            )

        if output is None:
            # Load and returns the new mesh
            Mnew = Mesh3D(outputMmg, debug=debug - 3)
            Mnew.debug += 3
            return Mnew
    return 1


def generate2DMesh(
    M: Mesh,
    phis: list[FunctionType],
    labels: list,
    hmin: float | None = None,
    hmax: float | None = None,
    hgrad: float | None = None,
    hausd: float | None = None,
    params: str | None = None,
    detectCorners: bool = False,
) -> Mesh:
    """
    Generate a 2D mesh with prescribed boundary tags
    given an input raw mesh `M` and a set of level set functions determining
    the locations of these boundaries.

    Requires `mmg2d_O3`

    See the example
    pymedit/examples/generate2DMesh.py

    INPUT
    -----

    `M`     : a 2D `Mesh` object such as a meshed bounding box (without boundary labels)

    `phis`  : a list of lambda functions `[phi1,phi2,...]` such that
              points `x` satisfying `phi[i](x) <= 0` on the boundary of `M` should be
              labelled by `labels[i]`
              These functions should partition the boundary of `M` into disjoint
              subdomains, i.e. for any `x`, `phii(x)<=0` ===> `phij(x)>0` for any `j!=i`

    `labels`: a list of integer labels for each subdomain described by the level set
              functions of `phis`

    `params`: a set of local parameters for the output mesh (remeshed with `mmg3d`)

    `detectCorners`: if set to `True`, then the corners of the bounding box will
                     be detected with mmg2d and automatically added.


    OUTPUT
    ------

    `newM`  : a `Mesh` object with boundary triangles labelled according
              to each level set functions of `phis` and with respective and to
              the list argument `labels`

    """
    tic(12)
    debug = M.debug

    def phi(x):
        return min([p(x) for p in phis])

    if detectCorners:
        M = mmg2d(M, nr=False, extra_args="-noswap -noinsert -nomove -nosurf")
    phiP1 = P1Function(M, phi)
    newM = mmg2d(
        M,
        sol=phiP1,
        ls=True,
        nr=True,
        params=params,
        extra_args="-noswap -noinsert -nomove -nosurf",
    )
    newM.debug = debug
    for nedge, edge in enumerate(newM.edges.tolist()):
        (p0, p1) = tuple(edge[:-1])
        adjacents = newM.elemToTri(edge[:-1])
        if (
            len(adjacents) == 1
            and newM.triangles[adjacents[0]][-1] == 3
            and edge[-1] != 10
        ):
            for i, phii in enumerate(phis):
                if max(phii(newM.vertex(p0)), phii(newM.vertex(p1))) <= 1e-7:
                    # print(f"Rename label of triangle {nedge}
                    # {edge[-1]} ==> {labels[i]}")
                    newM.edges[nedge, -1] = int(labels[i])
                    break
    # Now improve the quality
    finalM = mmg2d(newM, hmin, hmax, hgrad, hausd, nr=True, params=params)
    display(f"Generated 2D mesh in {toc(12)}s.", 1, debug, "green")
    return finalM


# def generate3DMeshLSSURF(M: Mesh3D, phis: list, labels: list, hmin=None, hmax=None,
#                   hausd=None, hgrad=None, params=None,
#                   detectCorners=False, debug=None):
#    """
#    Generate a 3D mesh with prescribed boundary tags
#    given an input raw mesh M and a set of level set functions determining
#    the locations of these boundaries.
#
#    Requires mmg3d_O3
#
#    See the example
#    pymedit/examples/generate3DMesh.py
#
#    INPUT
#    -----
#
#    M     :    3D mesh such as a meshed bounding box (without boundary labels)
#
#    phis  :    a list of lambda functions [phi1,phi2,...] such that
#                points x satisfying phi[i](x) <= 0 on the boundary of M should be
#                labelled by labels[i]
#                These functions should partition the boundary of M into disjoint
#                subdomains, i.e.
#                for any x, phii(x)<=0 ===> phij(x)>0 for any j!=i
#
#    labels :  a list of integer labels for each subdomain described by the level set
#              functions of phis
#
#    params :  a set of local parameters for the output mesh (remeshed with mmg3d)
#
#    detectCorners : if set to True, then the corners of the bounding box will
#                     be detected with mmg3d and automatically added.
#
#
#    OUTPUT
#    ------
#
#    newM    :   a Mesh3D object with boundary triangles labelled according
#                to each level set functions of phis and with respective and to
#                the list argument `labels`
#
#    """
#    tic(12)
#    if debug is None:
#        debug = M.debug
#
#    def phi(x): return min([p(x) for p in phis])
#    if detectCorners:
#        mmg3d(M, nr=False, extra_args="-noswap -noinsert -nomove -nosurf", output="M2.meshb",
#              debug=debug)
#    if isinstance(M,str):
#        M = Mesh3D(M)
#    phiP1 = P1Function3D(M, phi)
#    phiP1.save("phi.sol")
#    mmg3d("M2.meshb", sol="phi.sol", nr=True,
#                 params=params, hmin=hmin, hmax = hmax, hausd=hausd, extra_args="-lssurf",
#                 output="newM.meshb",
#          debug=debug)
#    newM = Mesh3D("newM.meshb")
#    newM.debug = debug
#    for (ntri, tri) in enumerate(newM.triangles.tolist()):
#        (p0, p1, p2) = tuple(tri[:-1])
#        adjacents = newM.elemToTetra(tri[:-1])
#        if len(adjacents) == 1 and newM.tetrahedra[adjacents[0]][-1] == 3 \
#                and tri[-1] != 10:
#            for (i, phii) in enumerate(phis):
#                if max(phii(newM.vertex(p0)), phii(newM.vertex(p1)),
#                       phii(newM.vertex(p2))) <= 1e-7:
#                    # print(f"Rename label of triangle {ntri}
#                    # {tri[-1]} ==> {labels[i]}")
#                    newM.triangles[ntri, -1] = int(labels[i])
#                    break
#    # Now improve the quality
#    #finalM = mmg3d(newM, hmin, hmax, hgrad, hausd, nr=True, params=params)
#    display("Generated 3D mesh in "+toc(12)+".", 1, debug, "green")
#    return finalM


def generate3DMesh(
    M: Mesh3D,
    phis: list[FunctionType],
    labels: list[int],
    hmin: float | None = None,
    hmax: float | None = None,
    hgrad: float | None = None,
    hausd: float | None = None,
    params=None,
    detectCorners: bool = False,
    debug: int | None = None,
):
    """
    Generate a 3D mesh with prescribed boundary tags
    given an input raw mesh `M` and a set of level set functions determining
    the locations of these boundaries.

    Requires `mmg3d_O3`

    See the example
    pymedit/examples/generate3DMesh.py

    INPUT
    -----

    `M`     : a `Mesh3D` object such as a meshed bounding box (without boundary labels)

    `phis`  : a list of lambda functions `[phi1,phi2,...]` such that
              points `x` satisfying `phi[i](x) <= 0` on the boundary of `M` should be
              labelled by `labels[i]`
              These functions should partition the boundary of `M` into disjoint
              subdomains, i.e. for any `x`, `phii(x)<=0 ===> phij(x)>0` for any `j!=i`

    `labels`:  a list of integer labels for each subdomain described by the level set
              functions of phis

    `params`:  a set of local parameters for the output mesh (remeshed with `mmg3d`)

    `detectCorners` : if set to `True`, then the corners of the bounding box will
                     be detected with `mmg3d` and automatically added.


    OUTPUT
    ------

    `newM`  : a `Mesh3D` object with boundary triangles labelled according
              to each level set functions of `phis` and with respective and to
              the list argument `labels`

    """
    tic(12)
    if debug is None:
        debug = M.debug

    def phi(x):
        return min([p(x) for p in phis])

    if detectCorners:
        M = mmg3d(
            M, nr=False, extra_args="-noswap -noinsert -nomove -nosurf", debug=debug
        )
    phiP1 = P1Function3D(M, phi)
    newM = mmg3d(
        M,
        sol=phiP1,
        ls=True,
        nr=True,
        params=params,
        extra_args="-noswap -noinsert -nomove -nosurf",
        debug=debug,
    )
    newM.debug = debug
    for ntri, tri in enumerate(newM.triangles.tolist()):
        (p0, p1, p2) = tuple(tri[:-1])
        adjacents = newM.elemToTetra(tri[:-1])
        if (
            len(adjacents) == 1
            and newM.tetrahedra[adjacents[0]][-1] == 3
            and tri[-1] != 10
        ):
            for i, phii in enumerate(phis):
                if (
                    max(
                        phii(newM.vertex(p0)),
                        phii(newM.vertex(p1)),
                        phii(newM.vertex(p2)),
                    )
                    <= 1e-7
                ):
                    # print(f"Rename label of triangle {ntri}
                    # {tri[-1]} ==> {labels[i]}")
                    newM.triangles[ntri, -1] = int(labels[i])
                    break
    # Now improve the quality
    finalM = mmg3d(newM, hmin, hmax, hgrad, hausd, nr=True, params=params)
    display(f"Generated 3D mesh in {toc(12)}.", 1, debug, "green")
    return finalM


def saveToVtk(
    M: Mesh3D | str,
    sols: list[P1Function3D | P1Vector3D | P0Function3D | str],
    labels: list[str],
    orders: list[int],
    output: str,
    debug: int = 0,
):
    """
    Save a 3D mesh and solutions in the `vtu` file format.
    Requires pyfreefem and a running instance of FreeFEM.

    See freefem.org/ and
    https://gitlab.com/florian.feppon/pyfreefem

    INPUT
    -----

    `M`     : either a `Mesh3D` object or the path of a 3D mesh file

    `sols`  : a list of either `P1Function3D`, `P1Vector3D`, `P0Function3D` or
              file paths of solution files

    `labels`: a list of names associated to each solution in `sols`

    `orders`: a list of integers associated to each solution in `sols` such that:
                - `orders[i] = 1` if the solution `sols[i]` should be saved at the
                              vertices of the mesh (i.e. it is a P1 function or P1 vector)
                - `orders[i] = 0` if the solution `sols[i]` should be saved on the
                              tetrahedra of the mesh (i.e. it is a P0 function)

    `output`: a `.vtu` output file

    `debug` : an integer tuning the verbosity of the python shell
    """
    try:
        from pyfreefem.freefemrunner import FreeFemRunner
    except:
        raise Exception(
            "saveToVtk requires pyfreefem. Please install it with 'pip install pyfreefem'"
        )

    tic(128)
    with tempfile.TemporaryDirectory() as tmpdir:
        if isinstance(M, Mesh3D):
            debug = max(debug, M.debug)
            M.debug -= 3
            M.save(f"{tmpdir}/Th.meshb")
            M.debug += 3
            if hasattr(M, "edges"):
                Mcopy = M.copy()
                del Mcopy.edges
                Mcopy.save(f"{tmpdir}/Th_ffb.meshb")
                M = Mcopy.meshFile
            else:
                M = M.meshFile
        if not sols is None:
            if isinstance(sols, __AbstractSol):
                sols = [sols]
            assert isinstance(M, str)
            nsols = len(sols)
            for i, sol in enumerate(sols):
                if isinstance(sol, __AbstractSol):
                    sol.debug -= 3
                    sol.save(f"{tmpdir}/phi{i}.sol")
                    sol.debug += 3
                    sols[i] = sol.solFile
                if isinstance(sol, list):
                    # Sol is a vector
                    assert len(sol) == 3
                    for j, component in enumerate(sol):
                        if isinstance(component, (P0Function3D, P1Function3D)):
                            component.debug -= 3
                            component.save(f"{tmpdir}/phi{i}_{j}.sol")
                            component.debug += 3
                            sol[j] = component.solFile
                if isinstance(sol, P1Vector3D):
                    sol.debug -= 3
                    sol.x.save(f"{tmpdir}/phi{i}_0.sol")
                    sol.y.save(f"{tmpdir}/phi{i}_1.sol")
                    sol.z.save(f"{tmpdir}/phi{i}_2.sol")
                    sol.debug += 3
                    sols[i] = [f"{tmpdir}/phi{i}_{j}.sol" for j in [0, 1, 2]]
            assert len(labels) == nsols
            assert len(orders) == nsols
        code = """
        load "medit"
        load "iovtk"

        mesh3 Th = readmesh3("$MESH");

        func real[int] readSolFile(string fileName){
                ifstream f(fileName);
                string dummy="";
                while(dummy(0:2)!="Sol"){
                        f>>dummy;
                }
                int n;
                f >> n;
            real[int]  phi(n);
                f >> dummy;
                f >> dummy;
                for(int i=0;i<n;i++){
                        f>>phi[i];
                }
            return phi;
        }
        fespace Fh0(Th,P0);
        fespace Fh1(Th,P1);
        """
        if sols:
            code += (
                "\nint[int] order = ["
                + ",".join([str(int(i)) for i in orders])
                + "];\n"
            )
            code += f'string dataname="' + " ".join(labels) + '";'
            solutions = []
            orders = list(map(int, orders))
            components_labels = {0: "x", 1: "y", 2: "z"}
            for i, solFile in enumerate(sols):
                if isinstance(solFile, list):
                    components = []
                    for j, component in enumerate(solFile):
                        components.append(f"phi{i}{components_labels[j]}")
                        code += f"""
                            Fh{orders[i]} {components[-1]};
                            {components[-1]}[] = readSolFile("{component}");"""
                    solutions.append("[" + ",".join(components) + "]")
                else:
                    code += f"""
                    Fh{orders[i]} phi{i};
                    phi{i}[] = readSolFile("{solFile}");"""
                    solutions.append(f"phi{i}")
        code += f"""
        savevtk("{output}", Th """
        if sols:
            code += ","
            code += ",".join(solutions)
            code += ",dataname=dataname, order=order"
        code += ");"

        FreeFemRunner(code, run_file="exportToVtk.edp", debug=debug - 3).execute(
            {"MESH": M}
        )
    display(f"Saved data to {output} in {toc(128)}s.", 1, debug, "green")


def medit(
    mesh: Mesh3D | str,
    sol: P1Function3D | str | None = None,
    keys: str | None = None,
    silent: bool = True,
    debug: int = 0,
    block: bool = True
):
    """
    Plot a 3D mesh and/or a 3D P1 function with medit.

    INPUT
    -----

    `mesh`  : either a `Mesh3D` object or the file path of the mesh

    `sol`   : either a `P1Function3D` object or the file path of the solution

    `keys`  : a set of key strokes to be sent to the medit graphical window

    `silent`: (default `True`) If `True`, then standard output of medit is
            hidden in the python execution shell

    `debug` : an integer tuning the verbosity of the shell

    `block` : block the execution until the window is closed
    """
    cmd = "medit"
    if shutil.which("medit") is None:
        if shutil.which("ffmedit") is None:
            raise Exception(
                "Error: medit does not seem installed. "
                "Please install it for 3D plotting.",
            )
        else:
            cmd = "ffmedit"
    with tempfile.TemporaryDirectory() as tmpdir:
        if isinstance(mesh, (Mesh3D, Mesh)):
            mesh.debug -= 3
            meshFile = f"{tmpdir}/Th.meshb"
            mesh.save(meshFile)
            mesh.debug += 3
            debug = max(debug, mesh.debug)
        else:
            meshFile = mesh
        if isinstance(sol, __AbstractSol):
            sol.debug -= 3
            sol.mesh.debug -= 3
            sol.save(f"{tmpdir}/Th.solb")
            sol.mesh.debug += 3
            sol.debug += 3
        cmd = f"{cmd} {meshFile}"
        display(cmd, level=1, debug=debug, color="magenta")
        if silent:
            proc = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        else:
            proc = subprocess.Popen(cmd, shell=True)
        time.sleep(0.15)
        if keys is not None:
            for key in keys:
                xdotool = f'xdotool search --name "Medit -" windowactivate \
                    --sync %1 key {key} windowactivate $(xdotool getactivewindow)'
                try:
                    p = subprocess.Popen(xdotool, shell="True")
                except:
                    display(
                        "Warning, xdotool not supported on this system", 0, 0, "red"
                    )
                p.wait()
        if block:
            proc.wait()
