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
import os
import tempfile
import subprocess
import threading
import queue
import shutil
import numpy as np
import scipy.sparse as sp
import colored as col
from struct import unpack, pack, calcsize
from typing import Self

from .utils.timing import tic, toc


def colored(text: str, color: str | int | None = None, attr: str | int | None = None):
    """Color texts for displays."""
    if color:
        text = col.stylize(text, col.fg(color))
    if attr:
        text = col.stylize(text, col.attr(attr))
    return text


def display(
    message: str,
    level: int = 0,
    debug: int = 0,
    color: str | int | None = None,
    attr: str | int | None = None,
    end: str = "\n",
    flag=None,
):
    """
    Display function with tunable level of verbosity.

    INPUTS
    ------

    `message`   : text to be printed

    `level`     : level of importance of the message; will be actually
                  printed if `debug >= level`

    `debug`     : current verbosity level

    `color`, `attr` : formattings with the `colored` package

    `end`       : if set to '', will remove the final line carriage return

    `flag`      : an extra indicator equal to None, 'stdout' or 'stderr',
                  the last two indicating that the text passed to display comes
                  from the standard output or error of a shell command.
                  Useful if display is overrided.
    """
    if color or attr:
        message = colored(message, color, attr)
    if debug >= level:
        print(message, end=end, flush=True)


def enqueue_stream(stream, queue, typ):
    """Thread for asynchronous reading of standard output and errors."""
    for line in iter(stream.readline, b""):
        queue.put(str(typ) + line.decode("utf-8", errors="replace"))
    stream.close()


def enqueue_process(process, queue):
    """Thread for asynchronous reading of standard output and errors."""
    process.wait()
    queue.put("x")


def exec2(
    cmd: str,
    level: int = 1,
    debug: int = 0,
    silent: bool = True,
    strict: bool = True,
):
    """
    Interface with `subprocess.Popen`.
    Execute a shell command with asynchronous reading of
    standard output and errors.

    INPUT
    -----

    `cmd`   : the command to be executed

    `level` : command will be displayed if `debug >= level`

    `debug` : level of verbosity

    `silent`: if set to `True`, the standard output will not be displayed in
              the python shell whatever the value of debug. If set to `False`,
              it is displayed if `debug >= level+2`

    `strict`: if `True`, raise an exception if the process does not exit with status 0

    OUTPUT
    ------

    `returncode` : the return code of the process. An exception is raised if it is not zero

    `stdout`     : the standard output of the process as a text variable

    `stderr`     : the standard error of the process as a text variable

    `mix`        : the full output of the process merging both `stdout` and `stderr`

    """
    display(
        colored(cmd, color="magenta"), level=level, debug=debug, end="", flag="shell"
    )
    # Put a line break to separate from the stdout
    if not silent:
        display("", level=level + 2, debug=debug)
    tic(121)
    if shutil.which("stdbuf") is not None:
        cmdfinal = f"stdbuf -oL {cmd}"
    else:
        cmdfinal = cmd
    proc = subprocess.Popen(
        cmdfinal, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    q = queue.Queue()
    to = threading.Thread(target=enqueue_stream, args=(proc.stdout, q, 1))
    te = threading.Thread(target=enqueue_stream, args=(proc.stderr, q, 2))
    tp = threading.Thread(target=enqueue_process, args=(proc, q))
    te.start()
    to.start()
    tp.start()

    stdout = ""
    stderr = ""
    mix = ""
    while True:
        try:
            line = q.get()
            if line[0] == "x":
                break
            if line[0] == "1":
                line = line[1:]
                stdout += line
                mix += line
                if not silent:
                    display(line, level=level + 2, debug=debug, end="", flag="stdout")
            if line[0] == "2":
                line = line[1:]
                stderr += line
                mix += line
                if not silent:
                    display(line, level=level + 2, debug=debug, end="", flag="stderr")
        except queue.Empty:
            pass
    tp.join()
    te.join()
    to.join()
    if not silent:
        display("\nFinished in", level + 2, debug, end="")
    display(f" ({toc(121)})", level=level, debug=debug, color=None, flag="time")
    if proc.returncode != 0 and strict:
        raise ExecException(
            f'Error : the process "{colored(cmd, "red")}" failed with return code {proc.returncode}.'
        )
    return proc.returncode, stdout, stderr, mix


# For binary processing
def readInt(f) -> int:
    return unpack("i", f.read(4))[0]


# For text file processing
def nextLine(f):
    while True:
        line = f.readline().strip()
        if line:
            break
    return line


# INRIA keywords
__GmfKwdCod__ = [
    "GmfReserved1",
    "GmfVersionFormatted",
    "GmfReserved2",
    "GmfDimension",
    "GmfVertices",
    "GmfEdges",
    "GmfTriangles",
    "GmfQuadrilaterals",
    "GmfTetrahedra",
    "GmfPentahedra",
    "GmfHexahedra",
    "GmfReserved3",
    "GmfReserved4",
    "GmfCorners",
    "GmfRidges",
    "GmfRequiredVertices",
    "GmfRequiredEdges",
    "GmfRequiredTriangles",
    "GmfRequiredQuadrilaterals",
    "GmfTangentAtEdgeVertices",
    "GmfNormalAtVertices",
    "GmfNormalAtTriangleVertices",
    "GmfNormalAtQuadrilateralVertices",
    "GmfAngleOfCornerBound",
    "GmfReserved5",
    "GmfReserved6",
    "GmfReserved7",
    "GmfReserved8",
    "GmfReserved9",
    "GmfReserved10",
    "GmfReserved11",
    "GmfReserved12",
    "GmfReserved13",
    "GmfReserved14",
    "GmfReserved15",
    "GmfReserved16",
    "GmfReserved17",
    "GmfReserved18",
    "GmfReserved19",
    "GmfReserved20",
    "GmfReserved21",
    "GmfReserved22",
    "GmfReserved23",
    "GmfReserved24",
    "GmfReserved25",
    "GmfReserved26",
    "GmfReserved27",
    "GmfReserved28",
    "GmfReserved29",
    "GmfReserved30",
    "GmfBoundingBox",
    "GmfReserved31",
    "GmfReserved32",
    "GmfReserved33",
    "GmfEnd",
    "GmfReserved34",
    "GmfReserved35",
    "GmfReserved36",
    "GmfReserved37",
    "GmfTangents",
    "GmfNormals",
    "GmfTangentAtVertices",
    "GmfSolAtVertices",
    "GmfSolAtEdges",
    "GmfSolAtTriangles",
    "GmfSolAtQuadrilaterals",
    "GmfSolAtTetrahedra",
    "GmfSolAtPentahedra",
    "GmfSolAtHexahedra",
    "GmfDSolAtVertices",
    "GmfISolAtVertices",
    "GmfISolAtEdges",
    "GmfISolAtTriangles",
    "GmfISolAtQuadrilaterals",
    "GmfISolAtTetrahedra",
    "GmfISolAtPentahedra",
    "GmfISolAtHexahedra",
    "GmfIterations",
    "GmfTime",
    "GmfReserved38",
]

__indicesGmf__ = dict([(value, i) for i, value in enumerate(__GmfKwdCod__)])


class SolException(Exception):
    pass


class ExecException(Exception):
    pass


class __AbstractMesh:
    """
    An abstract mesh object based on the INRIA mesh file format.
    """

    def __init__(self, meshFile: str | None = None, debug: int = 0):
        """
        Initialize a mesh object with a mesh file in the INRIA format.
        This class should not be instanciated, use `Mesh` or `Mesh3D` instead.
        """

        self.MeshVersionFormatted = 2
        self.Dimension = 0

        self.debug = debug
        if meshFile is None:
            display("Creating empty mesh", 3, self.debug)
            self.meshFile = None
            return
        else:
            self.meshFile = os.path.expanduser(meshFile)
            display(f"Loading {self.meshFile}", 2, self.debug)
        if self.meshFile.endswith(".meshb"):
            display(f"Open {self.meshFile} in binary mode.", 3, self.debug, "magenta")
            self.__loadMeshb(self.meshFile)
        elif self.meshFile.endswith(".mesh"):
            display(f"Open {self.meshFile}", 3, self.debug)
            self.__loadMesh(self.meshFile)
        else:
            raise Exception(f"Error, unsupported extension for {self.meshFile}.")


    def relabel_boundaries(self, label_mapping: dict[int, int]):
        """
        Relabel the boundaries using the `label_mapping`.
        """
        for old_label, new_label in label_mapping.items():
            if self.Dimension == 2:
                idxs = np.where(self.edges[:,-1]==old_label)[0]
                self.edges[idxs, -1] = new_label
            else:
                idxs = np.where(self.triangles[:,-1]==old_label)[0]
                self.triangles[idxs, -1] = new_label

    def vertex(self, i: int) -> np.ndarray:
        """
        Returns coordinates of vertex number `i`.
        Warning, vertex numerotation starts from 1.
        """
        return self.vertices[i - 1, :-1]

    def triangle(self, i: int) -> np.ndarray:
        """
        Returns vertex indices of triangle number `i`.
        Triangle numerotation starts from 1.
        """
        return self.triangles[i - 1]

    def edge(self, i: int) -> np.ndarray:
        """
        Returns vertex indices of boundary edge number `i`.
        Edge numerotation starts from 0 but careful, the numerotation for
        required edges and ridges starts from 1.
        """
        return self.edges[i]

    def copy(self) -> Self:
        """Returns a copy of the current mesh."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.debug -= 3
            self.save(f"{tmpdir}/Th.meshb")
            M = type(self)(f"{tmpdir}/Th.meshb", self.debug)
            self.debug += 3
            M.debug += 3
        return M

    @property
    def triangleNums(self) -> dict[frozenset[int], int]:
        """
        A dictionary of triangles to their index.
        Allow to retrieve the triangle number from
        three vertices indices as follows:

        >>> ntri = self.trianglesNum[frozenset({pt1,pt2,pt3})]

        where `pt1`, `pt2`, `pt3` are three vertices numbers.
        """
        if not hasattr(self, "_AbstractMesh__trinums"):
            tic()
            triangles = [frozenset(row[:-1]) for row in self.triangles]
            self.__trinums = {triangle: idx for idx, triangle in enumerate(triangles)}
            display(
                f"Computing vertex numbers to triangles numerotation in {toc()}.",
                2,
                self.debug,
            )
        return self.__trinums

    @property
    def verticesToTriangles(self) -> sp.csr_matrix:
        """
        Sparse matrix `M` of size `(nv, nt)` satisfying that `M[i,j]=1`
        if and only if triangle number `j` contains the vertex `i`.
        """
        if not hasattr(self, "_AbstractMesh__verticesToTriangles"):
            tic()
            I = self.triangles[:, :3].flatten() - 1
            J = np.repeat(np.arange(self.nt), 3)
            data = np.ones(3 * self.nt, dtype=int)
            self.__verticesToTriangles = sp.csr_matrix(
                (data, (I, J)), shape=(self.nv, self.nt)
            )
            display(f"Computed vertices to triangles in {toc()}.", 2, self.debug)
        return self.__verticesToTriangles

    @property
    def trianglesToTriangles(self) -> sp.csr_matrix:
        """
        Sparse matrix `M` of size `(nt, nt)`
        such that `M[i,j]=1` if triangles `i` and `j` are connected by an edge.
        >>> #obtain the lists of all adjacent triangles
        >>> I, J = self.trianglesToTriangles.nonzero()
        """
        if not hasattr(self, "_AbstractMesh__trianglesToTriangles"):
            verticesToTriangles = self.verticesToTriangles
            tic()
            connectivity = verticesToTriangles.T.dot(verticesToTriangles)
            connectivity_j, connectivity_i, _ = sp.find(connectivity == 2)
            self.__trianglesToTriangles = sp.csr_matrix(
                (np.ones(len(connectivity_j)), (connectivity_i, connectivity_j))
            )
            display(
                f"Computed connectivity matrices for triangles in {toc()}.",
                2,
                self.debug,
            )
        return self.__trianglesToTriangles

    @property 
    def Boundaries(self) -> dict:
        if self.Dimension == 2:
            attr = "edges"
        else:
            attr = "triangles"
        boundaries = getattr(self, attr)
        keys = set(boundaries[:, -1])
        Boundaries = dict()
        for key in keys:
            Boundaries[key] = np.where(boundaries[:, -1] == key)[0]
        return Boundaries

    def vertexToTriangle(self, i: int) -> np.ndarray:
        """
        Returns an array containing the triangles connected to the vertex number `i`.
        """
        return self.verticesToTriangles[i - 1].indices + 1

    def elemToTri(self, elem: np.ndarray) -> list[int]:
        """
        Returns a list of the set of triangles connected to element `elem`.

        INPUT
        -----
        `elem` : a list of vertex indices (numerotation starting from 1)
        - of size 1 if it is a vertex
        - of size 2 if it is an edge
        """
        return list(set.intersection(*[set(self.vertexToTriangle(pt)) for pt in elem]))

    @property
    def verticesToEdges(self) -> sp.csr_matrix:
        """
        Sparse matrix `M` of size `(nv, ne)`,
        such that `M[i,j]=1` if and only if edge number `j` contains the vertex `i`.
        """
        if not hasattr(self, "_AbstractMesh__verticesToEdges"):
            tic()
            I = self.edges[:, :-1].flatten(order="F") - 1
            nums = np.arange(self.ne)
            J = np.concatenate([nums, nums])
            self.__verticesToEdges = sp.csr_matrix(
                (np.ones(2 * self.ne), (I, J)), shape=(self.nv, self.ne)
            )
            display(f"Computed vertices to edges in {toc()}.", 2, self.debug)
        return self.__verticesToEdges

    def vertexToEdge(self, i: int) -> np.ndarray:
        """
        Returns an array containing the boundary edges connected to the vertex number `i`.
        """
        return self.verticesToEdges[i - 1].indices

    def __loadMesh(self, meshFile: str):
        """
        Reload the mesh with meshFile (ascii format).

        INPUT
        -----
        `meshFile` : the path of the `.mesh` file (ascii format)
        """
        tic()
        f = open(meshFile, "r")
        version = nextLine(f)
        if not version.startswith("MeshVersionFormatted"):
            raise Exception(f"Error in reading the mesh file {meshFile}")
        self.MeshVersionFormatted = int(version[-1])
        display(
            f"MeshVersionFormatted {self.MeshVersionFormatted}",
            3,
            self.debug,
            color="orange_4a",
        )
        dimension = nextLine(f)
        if not dimension.startswith("Dimension"):
            raise Exception(
                f"Error in reading the mesh file {meshFile}. Field Dimension expected."
            )
        try:
            self.Dimension = int(dimension[-1])
        except:
            self.Dimension = int(f.readline())
        display(f"Dimension {self.Dimension}", 3, self.debug, "orange_4a")
        if not self.Dimension in [2, 3]:
            raise Exception(
                f"Error in reading the file {meshFile}. The dimension is not correct."
            )

        def readField(f, title, dtype=int):
            n = int(nextLine(f))
            display(f"{n} {title}.", 3, self.debug, "orange_4a")
            fields = np.asarray(
                [next(f).strip().split() for i in range(n)], dtype=dtype
            )
            return (n, fields)

        while True:
            field = nextLine(f)
            if field == "Vertices":
                _, self.vertices = readField(f, field, dtype=float)

            elif field == "Triangles":
                _, self.triangles = readField(f, field)

            elif field == "Tetrahedra":
                _, self.tetrahedra = readField(f, field)

            elif field == "Corners":
                _, self.corners = readField(f, field)

            elif field == "RequiredVertices":
                _, self.requiredVertices = readField(f, field)

            elif field == "Edges":
                _, self.edges = readField(f, field)

            elif field == "Ridges":
                _, self.ridges = readField(f, field)

            elif field == "RequiredEdges":
                _, self.requiredEdges = readField(f, field)

            elif field == "RequiredTriangles":
                _, self.requiredTriangles = readField(f, field)

            elif field == "Normals":
                _, self.normals = readField(f, field, dtype=float)

            elif field == "NormalAtVertices":
                _, self.normalAtVertices = readField(f, field)

            elif field == "Tangents":
                _, self.tangents = readField(f, field, dtype=float)

            elif field == "TangentAtVertices":
                _, self.tangentAtVertices = readField(f, field)

            elif field == "Identifier":
                self.identifier = nextLine(f)

            elif field == "Geometry":
                self.Geometry = nextLine(f)

            # FreeFEM keywords
            elif field == "SubDomainFromMesh":
                readField(f, field)
            elif field == "SubDomainFromGeom":
                readField(f, field)
            elif field == "VertexOnGeometricVertex":
                readField(f, field)
            elif field == "VertexOnGeometricEdge":
                readField(f, field)
            elif field == "EdgeOnGeometricEdge":
                readField(f, field)
            elif field == "End" or field == "END":
                display("End of mesh.", 3, self.debug, "orange_4a")
                break
            else:
                raise Exception(
                    f"Error while reading the mesh {meshFile}. The field {field} is not supported."
                )

        f.close()
        display(f"Read {meshFile} in {toc()}.", 2, self.debug)

    def __loadMeshb(self, meshFile: str):
        """
        Reload the mesh with meshFile (binary format).

        INPUT
        -----
        `meshFile` : the path of the .meshb file (binary format)
        """
        tic()
        f = open(meshFile, "rb")
        code = readInt(f)
        if not code:
            raise Exception(f"Error in reading the binary file {meshFile}")
        self.MeshVersionFormatted = readInt(f)
        display(
            f"MeshVersionFormatted {self.MeshVersionFormatted}",
            3,
            self.debug,
            "orange_4a",
        )
        if not self.MeshVersionFormatted in [1, 2]:
            raise Exception("Wrong MeshVersionFormatted. Should be 1 or 2.")
        if __GmfKwdCod__[readInt(f)] != "GmfDimension":
            raise Exception(
                f"Error in reading the binary file {meshFile}. GmfDimension expected."
            )
        nextPos = readInt(f)
        display(f"Next field position: {nextPos}.", 4, self.debug, color="green")
        self.Dimension = readInt(f)
        display(f"Dimension {self.Dimension}", 3, self.debug, "orange_4a")
        if not self.Dimension in [2, 3]:
            raise Exception(
                f"Error in reading the binary file {meshFile}. The dimension should be 2 or 3."
            )

        def readField(f, nfields, title):
            nextPos = readInt(f)
            display(f"Next field position: {nextPos}.", 4, self.debug, color="green")
            n = readInt(f)
            display(f"{n} {title}.", 3, self.debug, "orange_4a")
            code = "i" * nfields * n
            nbytes = 4 * nfields * n
            field = np.asarray(unpack(code, f.read(nbytes)))
            return (n, field.reshape((n, nfields)))

        while True:
            try:
                KwdCod = readInt(f)
            except:
                display(
                    "Warning: end of file without the END keyword.",
                    1,
                    self.debug,
                    "magenta",
                )
                break
            display(f"Reading {__GmfKwdCod__[KwdCod]}", 4, self.debug, "cyan")

            if __GmfKwdCod__[KwdCod] == "GmfVertices":
                nextPos = readInt(f)
                display(
                    f"Next field position: {nextPos}.", 4, self.debug, color="green"
                )
                nv = readInt(f)
                display(f"{nv} Vertices.", 3, self.debug, color="orange_4a")
                if self.MeshVersionFormatted == 1:
                    # Float precision
                    code = "=" + ("f" * self.Dimension + "i") * nv
                    nbytes = calcsize(code)
                elif self.MeshVersionFormatted == 2:
                    # Double precision
                    code = "=" + ("d" * self.Dimension + "i") * nv
                    nbytes = calcsize(code)
                self.vertices = np.asarray(unpack(code, f.read(nbytes)))
                self.vertices = self.vertices.reshape((nv, self.Dimension + 1))

            elif __GmfKwdCod__[KwdCod] == "GmfTriangles":
                _, self.triangles = readField(f, 4, __GmfKwdCod__[KwdCod][3:])

            elif __GmfKwdCod__[KwdCod] == "GmfTetrahedra":
                _, self.tetrahedra = readField(f, 5, __GmfKwdCod__[KwdCod][3:])

            elif __GmfKwdCod__[KwdCod] == "GmfCorners":
                _, self.corners = readField(f, 1, __GmfKwdCod__[KwdCod][3:])

            elif __GmfKwdCod__[KwdCod] == "GmfRequiredVertices":
                _, self.requiredVertices = readField(
                    f, 1, __GmfKwdCod__[KwdCod][3:]
                )

            elif __GmfKwdCod__[KwdCod] == "GmfEdges":
                _, self.edges = readField(f, 3, __GmfKwdCod__[KwdCod][3:])

            elif __GmfKwdCod__[KwdCod] == "GmfRidges":
                _, self.ridges = readField(f, 1, __GmfKwdCod__[KwdCod][3:])

            elif __GmfKwdCod__[KwdCod] == "GmfRequiredEdges":
                _, self.requiredEdges = readField(
                    f, 1, __GmfKwdCod__[KwdCod][3:]
                )

            elif __GmfKwdCod__[KwdCod] == "GmfRequiredTriangles":
                _, self.requiredTriangles = readField(
                    f, 1, __GmfKwdCod__[KwdCod][3:]
                )

            elif __GmfKwdCod__[KwdCod] == "GmfNormals":
                nextPos = readInt(f)
                display(
                    f"Next field position: {nextPos}.", 4, self.debug, color="green"
                )
                nvn = readInt(f)
                display(f"{nvn} Normals.", 3, self.debug, "orange_4a")
                if self.MeshVersionFormatted == 1:
                    code = "f" * (3 * nvn)
                    nbytes = calcsize(code)
                else:
                    code = "d" * (3 * nvn)
                    nbytes = calcsize(code)
                self.normals = np.asarray(unpack(code, f.read(nbytes)))
                self.normals = self.normals.reshape((nvn, 3))

            elif __GmfKwdCod__[KwdCod] == "GmfNormalAtVertices":
                _, self.normalAtVertices = readField(
                    f, 2, __GmfKwdCod__[KwdCod][3:]
                )

            elif __GmfKwdCod__[KwdCod] == "GmfTangents":
                nextPos = readInt(f)
                display(
                    f"Next field position: {nextPos}.", 4, self.debug, color="green"
                )
                ntg = readInt(f)
                display(f"{self.ntg} Tangents.", 3, self.debug, "orange_4a")
                if self.MeshVersionFormatted == 1:
                    code = "f" * (3 * ntg)
                    nbytes = 4 * 3 * ntg
                else:
                    code = "d" * (3 * ntg)
                    nbytes = 8 * 3 * ntg
                self.tangents = np.asarray(unpack(code, f.read(nbytes)))
                self.tangents = self.tangents.reshape((ntg, 3))

            elif __GmfKwdCod__[KwdCod] == "GmfTangentAtVertices":
                _, self.tangentAtVertices = readField(
                    f, 2, __GmfKwdCod__[KwdCod][3:]
                )

            elif __GmfKwdCod__[KwdCod] == "GmfEnd":
                display("End of mesh.", 3, self.debug, "green")
                break

            else:
                raise (f"Error, field {__GmfKwdCod__[KwdCod]} not supported.")
        f.close()
        display(f"Read {meshFile} in {toc()}.", 2, self.debug)

    def printInfos(self):
        """Print the infos of the loaded mesh."""
        display(f"Mesh {self.meshFile}", 0, self.debug)
        display(f"MeshVersionFormatted {self.MeshVersionFormatted}", 0, self.debug)
        display(f"Dimension {self.Dimension}", 0, self.debug)
        display(f"{self.nv} Vertices.", 0, self.debug)
        display(f"{self.nt} Triangles.", 0, self.debug)
        display(f"{self.ntet} Tetrahedra.", 0, self.debug)
        display(f"{self.nc} Corners.", 0, self.debug)
        display(f"{self.nr} RequiredVertices.", 0, self.debug)
        display(f"{self.ne} Edges.", 0, self.debug)
        display(f"{self.nri} Ridges.", 0, self.debug)
        display(f"{self.nre} RequiredEdges.", 0, self.debug)
        display(f"{self.nrt} RequiredTriangles.", 0, self.debug)
        display(f"{self.nvn} Normals.", 0, self.debug)
        display(f"{self.iv} NormalAtVertices.", 0, self.debug)
        display(f"{self.ntg} Tangents.", 0, self.debug)
        display(f"{self.tv} TangentAtVertices.", 0, self.debug)

    @property
    def nv(self) -> int:
        return len(getattr(self, "vertices", []))

    @property
    def nt(self) -> int:
        return len(getattr(self, "triangles", []))

    @property
    def ntet(self) -> int:
        return len(getattr(self, "tetrahedra", []))

    @property
    def nc(self) -> int:
        return len(getattr(self, "corners", []))

    @property
    def nr(self) -> int:
        return len(getattr(self, "requiredVertices", []))

    @property
    def ne(self) -> int:
        return len(getattr(self, "edges", []))

    @property
    def nri(self) -> int:
        return len(getattr(self, "ridges", []))

    @property
    def nre(self) -> int:
        return len(getattr(self, "requiredEdges", []))

    @property
    def nrt(self) -> int:
        return len(getattr(self, "requiredTriangles", []))

    @property
    def nvn(self) -> int:
        return len(getattr(self, "normals", []))

    @property
    def iv(self) -> int:
        return len(getattr(self, "normalAtVertices", []))

    @property
    def ntg(self) -> int:
        return len(getattr(self, "tangents", []))

    @property
    def tv(self) -> int:
        return len(getattr(self, "tangentAtVertices", []))

    def save(self, meshFile: str | None = None):
        """
        Save the mesh in the INRIA mesh file format.
        Supported extensions: `.mesh` and `.meshb` (binary).
        """
        if meshFile is None:
            meshFile = self.meshFile
        if isinstance(meshFile,str):
            if meshFile.endswith(".mesh"):
                self._savemesh(meshFile)
            elif meshFile.endswith(".meshb"):
                self._savemeshb(meshFile)
        else:
            raise Exception(f"Error: extension of {meshFile} not supported.")

        display(f"Saved {meshFile}", 3, self.debug)
        self.meshFile = meshFile

    def _savemesh(self, meshFile: str):
        """Save mesh in the INRIA mesh file format."""
        tic()
        f = open(meshFile, "w")
        self.MeshVersionFormatted = 2  # In python always use double
        f.write(f"MeshVersionFormatted {self.MeshVersionFormatted}\n")
        f.write("\n\n")
        f.write(f"Dimension {self.Dimension}\n\n\n")

        def writeField(f, title: str, n: int, field: str):
            field = getattr(self, field, [])
            tic(1)
            if n:
                f.write(f"{title}\n")
                f.write(f"{n}\n")
                if title == "Vertices":
                    f.write(
                        "\n".join(
                            [
                                " ".join(map(str, elem[:-1])) + " " + str(int(elem[-1]))
                                for elem in field.tolist()
                            ]
                        )
                    )
                else:
                    for elem in field.tolist():
                        f.write(" ".join(map(str, elem)) + "\n")
                f.write("\n\n")
            display(f"Write {title} in {toc(1)}", 6, self.debug, "cyan")

        writeField(f, "Vertices", self.nv, "vertices")
        writeField(f, "Triangles", self.nt, "triangles")
        writeField(f, "Tetrahedra", self.ntet, "tetrahedra")
        writeField(f, "Edges", self.ne, "edges")
        writeField(f, "Corners", self.nc, "corners")
        writeField(f, "RequiredVertices", self.nr, "requiredVertices")
        writeField(f, "Ridges", self.nri, "ridges")
        writeField(f, "RequiredEdges", self.nre, "requiredEdges")
        writeField(f, "RequiredTriangles", self.nrt, "requiredTriangles")
        writeField(f, "Normals", self.nvn, "normals")
        writeField(f, "NormalAtVertices", self.iv, "normalAtVertices")
        writeField(f, "Tangents", self.ntg, "tangents")
        writeField(f, "TangentAtVertices", self.tv, "tangentAtVertices")

        f.write("END\n")
        f.close()
        display(f"Wrote {meshFile} in {toc()}.", 4, self.debug)

    def _savemeshb(self, meshFile: str):
        """Save a mesh in the INRIA binary file format."""
        tic()
        f = open(meshFile, "wb")
        f.write(pack("i", 1))  # Write code
        f.write(pack("i", 2))  # Write MeshVersionFormatted 2

        f.write(pack("i", __indicesGmf__["GmfDimension"]))
        f.write(pack("i", 20))  # NextPos
        if not self.Dimension in [2, 3]:
            raise Exception("Error, the mesh dimension is not 2 or 3")
        f.write(pack("i", self.Dimension))

        display(f"Write {self.nv} Vertices.", 6, self.debug)
        f.write(pack("i", __indicesGmf__["GmfVertices"]))
        code = "=" + ("d" * self.Dimension + "i") * self.nv
        nextPos = f.tell() + calcsize("ii") + calcsize(code)
        display(f"Next position: {nextPos}", 7, self.debug, "green")
        f.write(pack("i", nextPos))
        f.write(pack("i", self.nv))
        data = self.vertices.flatten()
        data = [
            int(x) if (i + 1) % (self.Dimension + 1) == 0 else x
            for i, x in enumerate(data)
        ]
        f.write(pack(code, *data))

        def writeField(f, title: str, n: int, field: str):
            if n:
                display(f"Write {n} " + title + ".", 6, self.debug)
                f.write(pack("i", __indicesGmf__["Gmf" + title]))
                code = "i" * getattr(self, field).shape[1] * n

                nextPos = f.tell() + calcsize(code) + calcsize("ii")
                display(f"Next position: {nextPos}", 7, self.debug, "green")
                f.write(pack("i", nextPos))  # NulPos
                f.write(pack("i", n))
                data = getattr(self, field).flatten().tolist()
                f.write(pack(code, *data))

        writeField(f, "Corners", self.nc, "corners")
        writeField(f, "RequiredVertices", self.nr, "requiredVertices")
        writeField(f, "Tetrahedra", self.ntet, "tetrahedra")
        if self.nvn:
            display(f"Write {self.nvn} Normals.", 6, self.debug)
            f.write(pack("i", __indicesGmf__["GmfNormals"]))
            code = ("d" * self.Dimension) * self.nvn
            nextPos = f.tell() + calcsize(code) + calcsize("ii")
            display(f"Next position: {nextPos}", 7, self.debug, "green")
            f.write(pack("i", nextPos))
            f.write(pack("i", self.nvn))
            data = self.normals.flatten().tolist()
            f.write(pack(code, *data))
        writeField(f, "NormalAtVertices", self.iv, "normalAtVertices")
        if self.ntg:
            display(f"Write {self.ntg} Tangents.", 6, self.debug)
            f.write(pack("i", __indicesGmf__["GmfTangents"]))
            code = ("d" * self.Dimension) * self.ntg
            nextPos = f.tell() + calcsize(code) + calcsize("ii")
            display(f"Next position: {nextPos}", 7, self.debug, "green")
            f.write(pack("i", nextPos))
            f.write(pack("i", self.ntg))
            data = self.tangents.flatten().tolist()
            f.write(pack(code, *data))
        writeField(f, "TangentAtVertices", self.tv, "tangentAtVertices")

        writeField(f, "Triangles", self.nt, "triangles")
        writeField(f, "Edges", self.ne, "edges")
        writeField(f, "Ridges", self.nri, "ridges")
        writeField(f, "RequiredEdges", self.nre, "requiredEdges")
        writeField(f, "RequiredTriangles", self.nrt, "requiredTriangles")

        f.write(pack("i", __indicesGmf__["GmfEnd"]))
        nextPos = f.tell() + calcsize("i")
        # Final size
        f.write(pack("i", nextPos))
        f.close()

        display("Wrote " + meshFile + " in " + toc() + ".", 4, self.debug)


class __AbstractSol:
    """
    An abstract solution object based on the INRIA solution file format.
    """

    def __init__(self, M: "__AbstractMesh", solFile: str | None | np.ndarray | list[float], debug: int | None = None):
        """
        Initialize a solution object with a mesh file in the INRIA format.
        This class should not be instanciated, prefer to use
        `P1Function`, `P0Function`, and so on instead.
        """
        self.MeshVersionFormatted = 2

        self.nsol = 0
        self.sol_types = np.array([])
        self.sol = np.array([])
        self.mesh = M
        self.Dimension = self.mesh.Dimension

        if debug is None:
            debug = M.debug

        self.debug = debug

        if solFile is None:
            display("Creating empty solution", 4, self.debug)
            self.solFile = None
            return
        elif isinstance(solFile, str):
            self.solFile = os.path.expanduser(solFile)
            display(f"Loading {self.solFile}", 2, self.debug)
            if self.solFile.endswith(".solb"):
                display(
                    f"Open {self.solFile} in binary mode.", 3, self.debug, "magenta"
                )
                self._loadSolb(self.solFile)
            elif self.solFile.endswith(".sol"):
                display(f"Open {self.solFile}.", 3, self.debug, "magenta")
                self._loadSol(self.solFile)
            elif isinstance(solFile, str) and solFile.endswith(".gp"):
                f = open(solFile, "r")
                self.n = int(nextLine(f))
                self.sol = np.asarray(
                    [float(x) for line in f for x in line.strip().split()], dtype=float
                )
                f.close()
                self.nsol = 1
                self.sol_types = np.asarray([1] * self.sol.reshape(self.n, -1).shape[1])
            else:
                raise Exception(f"Error, unsupported extension for {self.solFile}")
        elif isinstance(solFile, np.ndarray) or (
            isinstance(solFile, list) and isinstance(solFile[0], float)
        ):
            self.sol = np.asarray(solFile, dtype=float)
            self.nsol = 1
            self.n = self.sol.shape[0]
            self.sol_types = np.asarray([1] * self.sol.reshape(self.n, -1).shape[1])
        else:
            raise SolException("Error: wrong solution provided.")

    def copy(self) -> "__AbstractSol":
        """Returns a copy of the solution object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.debug -= 3
            self.save(f"{tmpdir}/phi.solb")
            self.debug += 3
            phi = type(self)(self.mesh, f"{tmpdir}/phi.solb", self.debug - 3)
            phi.debug += 3
        return phi

    def _loadSol(self, solFile: str):
        """
        Load a solution with the INRIA ascii solution format.

        INPUT
        -----
        `solFile` : the path of the `.sol` file (ascii format)
        """
        tic()
        f = open(solFile, "r")
        version = nextLine(f)
        if not version.startswith("MeshVersionFormatted"):
            raise Exception(f"Error in reading the solution file {solFile}")
        self.MeshVersionFormatted = int(version[-1])
        display(
            f"MeshVersionFormatted {self.MeshVersionFormatted}",
            6,
            self.debug,
            color="orange_4a",
        )
        dimension = nextLine(f)
        if not dimension.startswith("Dimension"):
            raise Exception(
                f"Error in reading the mesh file {solFile}." "Field Dimension expected."
            )
        try:
            self.Dimension = int(dimension[-1])
        except:
            self.Dimension = int(f.readline())
        display(f"Dimension {self.Dimension}", 6, self.debug, "orange_4a")
        if not self.Dimension in [2, 3]:
            raise Exception(
                f"Error in reading the file {solFile}. The dimension is not correct."
            )
        if self.Dimension != self.mesh.Dimension:
            raise Exception(
                f"Error in reading the solution file {solFile}. "
                f"The dimension is not the same of the mesh {self.mesh.meshFile}."
            )
        meaning = {1: "scalar", 2: "vectorial", 3: "symmetric tensor"}

        def checkField(n, var, title):
            self.n = int(nextLine(f))
            if self.n != n:
                raise Exception(
                    f"Error while reading {solFile}: the "
                    f"number of {title} of the file self.n={self.n} "
                    f"does not match the one of the mesh {var} = {n}."
                )

        field = nextLine(f)
        display(f"Reading {field}", 6, self.debug, "cyan")
        if field == "SolAtVertices":
            checkField(self.mesh.nv, "M.nv", "vertices")
        elif field == "SolAtTriangles":
            checkField(self.mesh.nt, "M.nt", "triangles")
        elif field == "SolAtTetrahedra":
            checkField(self.mesh.ntet, "M.ntet", "tetrahedra")
        else:
            raise Exception(f"Error, field {field} not supported.")
        types_sol = nextLine(f).split()
        self.nsol = int(types_sol[0])
        display(f"Found {self.nsol} solutions.", 6, self.debug, "magenta")
        self.sol_types = np.array(list(map(int, types_sol[1:])))
        display(
            "\n".join(
                [
                    f"Solution {i} : type {typ} ({meaning[typ]})."
                    for (i, typ) in enumerate(self.sol_types.tolist())
                ]
            ),
            6,
            self.debug,
            "orange_4a",
        )
        self.sol = np.asarray([nextLine(f).split() for i in range(self.n)], dtype=float)
        if nextLine(f) not in ["End", "END"]:
            raise Exception(f"Invalid solution file {solFile}")
        display(f"Loaded solution file in {toc()}.", 3, self.debug, "green")

    def _loadSolb(self, solFile: str):
        """
        Load a solution with the INRIA binary solution format.

        INPUT
        -----
        solFile : the path of the `.solb` file (binary format)
        """
        tic()
        f = open(solFile, "rb")
        code = readInt(f)
        if not code:
            raise Exception(f"Error in reading the binary file {solFile}")
        self.MeshVersionFormatted = readInt(f)
        display(
            f"MeshVersionFormatted {self.MeshVersionFormatted}",
            6,
            self.debug,
            "orange_4a",
        )
        if __GmfKwdCod__[readInt(f)] != "GmfDimension":
            raise Exception(
                f"Error in reading the binary file {solFile}. GmfDimension expected."
            )
        nextPos = readInt(f)
        display(f"Next field position: {nextPos}.", 7, self.debug, color="green")
        self.Dimension = readInt(f)
        display(f"Dimension {self.Dimension}", 6, self.debug, "orange_4a")
        if not self.Dimension in [2, 3]:
            raise Exception(
                f"Error in reading the binary file {solFile}. The dimension should be 2 or 3."
            )
        if self.Dimension != self.mesh.Dimension:
            raise Exception(
                f"Error in reading the binary file {solFile}."
                f" The dimension is not the same of the mesh {self.mesh.meshFile}."
            )

        meaning = {1: "scalar", 2: "vectorial", 3: "symmetric tensor"}
        sizes = {1: 1, 2: self.Dimension, 3: self.Dimension * (self.Dimension + 1) / 2}

        def checkField(n, var, title):
            nextPos = readInt(f)
            display(f"Next field position: {nextPos}.", 7, self.debug, color="green")
            self.n = readInt(f)
            if self.n != n:
                raise Exception(
                    f"Error while reading {solFile}:"
                    f" the number of {title} of the file self.n={self.n}"
                    f" does not match the one of the mesh {var} = {n}."
                )

        KwdCod = readInt(f)
        display(f"Reading {__GmfKwdCod__[KwdCod]}", 6, self.debug, "cyan")
        if __GmfKwdCod__[KwdCod] == "GmfSolAtVertices":
            checkField(self.mesh.nv, "M.nv", "vertices")
        elif __GmfKwdCod__[KwdCod] == "GmfSolAtTriangles":
            checkField(self.mesh.nt, "M.nt", "triangles")
        elif __GmfKwdCod__[KwdCod] == "GmfSolAtTetrahedra":
            checkField(self.mesh.ntet, "M.ntet", "tetrahedra")
        else:
            raise Exception(f"Error, field {__GmfKwdCod__[KwdCod]} not supported.")

        self.nsol = readInt(f)
        display(f"Found {self.nsol} solutions.", 3, self.debug, "magenta")
        code = "i" * self.nsol
        nbytes = 4 * self.nsol
        self.sol_types = np.asarray(unpack(code, f.read(nbytes)))
        display(
            "\n".join(
                [
                    f"Solution {i} : type {typ} ({meaning[typ]})."
                    for (i, typ) in enumerate(self.sol_types.tolist())
                ]
            ),
            2,
            self.debug,
            "orange_4a",
        )
        totalcomponents = sum([sizes[typ] for typ in self.sol_types.tolist()])

        if self.MeshVersionFormatted == 1:
            code = "f" * totalcomponents * self.n
        else:
            code = "d" * totalcomponents * self.n
        nbytes = calcsize(code)
        self.sol = np.asarray(unpack(code, f.read(nbytes)))
        self.sol = self.sol.reshape((self.n, totalcomponents))
        KwdCod = readInt(f)
        if __GmfKwdCod__[KwdCod] != "GmfEnd":
            raise Exception("Error, wrong solution file.")
        else:
            display("End of file.", 6, self.debug, "green")
        f.close()
        display(f"Loaded solution file in {toc()}.", 2, self.debug, "green")

    def _checkValid(self) -> str:
        sizes = {1: 1, 2: self.Dimension, 3: self.Dimension * (self.Dimension + 1) / 2}
        types = {
            self.mesh.nv: "SolAtVertices",
            self.mesh.nt: "SolAtTriangles",
            self.mesh.ntet: "SolAtTetrahedra",
        }
        if not self.n in types:
            raise Exception(f"The number of components self.n={self.n} is invalid.")
        if self.nsol != len(self.sol_types):
            raise Exception(
                f"Invalid number {self.nsol} of solution types. {self.sol_types}"
            )
        totalcomponents = sum([sizes[typ] for typ in self.sol_types.tolist()])
        if (totalcomponents == 1 and self.n != self.sol.shape[0]) or (
            totalcomponents > 1 and self.sol.shape != (self.n, totalcomponents)
        ):
            raise Exception(
                f"The shape of self.sol={self.sol.shape} should be {(self.n,totalcomponents)}."
            )
        if not self.Dimension in [2, 3]:
            raise Exception("Error: the dimension should be 2 or 3.")
        if self.Dimension != self.mesh.Dimension:
            raise Exception(
                "Error: the solution is not of the same dimension as the mesh."
            )
        return types[self.n]

    def save(self, solFile: str | None = None):
        """
        Save the mesh in the INRIA solution file format.
        Supported extensions: `.sol` (ascii) and `.solb` (binary).
        """
        if solFile is None:
            solFile = self.solFile
        if isinstance(solFile, str):
            if solFile.endswith(".sol"):
                self._savesol(solFile)
            elif solFile.endswith(".solb"):
                self._savesolb(solFile)
            else:
                raise Exception("Error: extension of " + solFile + " not supported.")
        else:
            raise Exception("Solution file should be a string")

        self.solFile = solFile

    def _savesol(self, solFile: str):
        """Save in the INRIA `.sol` file format."""
        tic()
        typ = self._checkValid()
        f = open(solFile, "w")
        f.write("MeshVersionFormatted 2\n\n")
        f.write(f"Dimension {self.Dimension}\n\n")
        f.write(f"{typ}\n")
        f.write(f"{self.n}\n")
        f.write(f"{self.nsol} " + " ".join(map(str, self.sol_types.tolist())) + "\n\n")
        sizes = {
            1: 1,
            2: self.Dimension,
            3: int(self.Dimension * (self.Dimension + 1) / 2),
        }
        totalcomponents = sum([sizes[typ] for typ in self.sol_types.tolist()])
        sol = self.sol.reshape((self.n, totalcomponents))
        for val in sol.tolist():
            f.write(" ".join(map(str, val)) + "\n")
        f.write("\n\nEnd")
        f.close()
        display(f"Saved {solFile} in {toc()}.", 3, self.debug, "green")

    def _savesolb(self, solFile: str):
        """Save in the INRIA `.solb` binary file format."""
        tic()
        typ = self._checkValid()

        f = open(solFile, "wb")
        f.write(pack("i", 1))  # Write code
        f.write(pack("i", 2))  # Write MeshVersionFormatted 2

        f.write(pack("i", __indicesGmf__["GmfDimension"]))
        f.write(pack("i", 20))  # NextPos
        f.write(pack("i", self.Dimension))
        f.write(pack("i", __indicesGmf__["Gmf" + typ]))
        display(f"Write {self.n} {typ}", 6, self.debug, "magenta")

        code1 = "i" * self.nsol
        totalcomponents = 1 if len(self.sol.shape) == 1 else self.sol.shape[1]
        code2 = "d" * totalcomponents * self.n
        nextPos = f.tell() + calcsize("iii") + calcsize(code1) + calcsize(code2)
        display(f"Next position: {nextPos}", 6, self.debug, "orange_4a")
        f.write(pack("i", nextPos))
        f.write(pack("i", self.n))
        f.write(pack("i", self.nsol))
        display(f"Solution types: {self.sol_types}", 6, self.debug, "orange_4a")
        f.write(pack(code1, *self.sol_types))
        f.write(pack(code2, *self.sol.flatten().tolist()))
        f.write(pack("i", __indicesGmf__["GmfEnd"]))
        f.close()
        display(f"Saved {solFile} in {toc()}.", 3, self.debug, "green")

    def __add__(self, v) -> "__AbstractSol":
        res = self.copy()
        if isinstance(v, (np.ndarray, float, int)):
            res.sol += v
        code = """
if isinstance(v, __AbstractSol):
    res.sol += v.sol
        """
        exec(code)
        return res

    def __radd__(self, v) -> "__AbstractSol":
        return self.__add__(v)

    def __neg__(self) -> "__AbstractSol":
        res = self.copy()
        res.sol = -res.sol
        return res

    def __pow__(self, v) -> "__AbstractSol":
        res = self.copy()
        res.sol = self.sol**v
        return res

    def __sub__(self, v) -> "__AbstractSol":
        return self.__add__(v.__neg__())

    def __mul__(self, v) -> "__AbstractSol":
        res = self.copy()
        code = """
if isinstance(v, (np.ndarray, float, int)):
    res.sol *= v
elif isinstance(v, __AbstractSol):
    res.sol *= v.sol"""
        exec(code)
        return res

    def __rmul__(self, v) -> "__AbstractSol":
        return self.__mul__(v)

    def __truediv__(self, v) -> "__AbstractSol":
        res = self.copy()
        code = """
if isinstance(v, (np.ndarray, float, int)):
    res.sol /= v
elif isinstance(v, __AbstractSol):
    res.sol /= v.sol"""
        exec(code)
        return res

    def __rdiv__(self, v) -> "__AbstractSol":
        return self.__truediv__(v)

    def __getitem__(self, i) -> np.ndarray:
        return self.sol[i]


def old2new(new2old):
    """
    Returns an operator mapping new numerotation to old numerotation.
    Useful when suppressing mesh elements and changing numerotation.
    """
    old = new2old
    new = range(1, len(old) + 1)
    old2new = dict(zip(old, new))
    changeNum = np.vectorize(old2new.__getitem__)
    return changeNum
