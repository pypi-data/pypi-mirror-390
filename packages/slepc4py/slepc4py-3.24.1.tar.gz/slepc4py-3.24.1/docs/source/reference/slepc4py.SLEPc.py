"""
Scalable Library for Eigenvalue Problem Computations
"""
from __future__ import annotations
import sys
from typing import (
    Any,
    Union,
    Optional,
    Callable,
    Sequence,
)
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import numpy
from numpy import dtype, ndarray
from mpi4py.MPI import (
    Intracomm,
    Datatype,
    Op,
)

# -----------------------------------------------------------------------------

from petsc4py.PETSc import (
    Object,
    Comm,
    NormType,
    Random,
    Viewer,
    Vec,
    Mat,
)

# -----------------------------------------------------------------------------

class _dtype:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

IntType: dtype = _dtype('IntType')
RealType: dtype =  _dtype('RealType')
ComplexType: dtype = _dtype('ComplexType')
ScalarType: dtype = _dtype('ScalarType')

class _Int(int): pass
class _Str(str): pass
class _Float(float): pass
class _Dict(dict): pass

def _repr(obj):
    try:
        return obj._name
    except AttributeError:
        return super(obj).__repr__()

def _def(cls, name):
    if cls is int:
       cls = _Int
    if cls is str:
       cls = _Str
    if cls is float:
       cls = _Float
    if cls is dict:
       cls = _Dict

    obj = cls()
    obj._name = name
    if '__repr__' not in cls.__dict__:
        cls.__repr__ = _repr
    return obj

DECIDE: int = _def(int, 'DECIDE')  #: Constant ``DECIDE`` of type :class:`int`
DEFAULT: int = _def(int, 'DEFAULT')  #: Constant ``DEFAULT`` of type :class:`int`
DETERMINE: int = _def(int, 'DETERMINE')  #: Constant ``DETERMINE`` of type :class:`int`
CURRENT: int = _def(int, 'CURRENT')  #: Constant ``CURRENT`` of type :class:`int`
__arch__: str = _def(str, '__arch__')  #: Object ``__arch__`` of type :class:`str`

class ST(Object):
    """ST."""
    class Type:
        """ST types.
        
        - `SHELL`:   User-defined.
        - `SHIFT`:   Shift from origin.
        - `SINVERT`: Shift-and-invert.
        - `CAYLEY`:  Cayley transform.
        - `PRECOND`: Preconditioner.
        - `FILTER`:  Polynomial filter.
        
        """
        SHELL: str = _def(str, 'SHELL')  #: Object ``SHELL`` of type :class:`str`
        SHIFT: str = _def(str, 'SHIFT')  #: Object ``SHIFT`` of type :class:`str`
        SINVERT: str = _def(str, 'SINVERT')  #: Object ``SINVERT`` of type :class:`str`
        CAYLEY: str = _def(str, 'CAYLEY')  #: Object ``CAYLEY`` of type :class:`str`
        PRECOND: str = _def(str, 'PRECOND')  #: Object ``PRECOND`` of type :class:`str`
        FILTER: str = _def(str, 'FILTER')  #: Object ``FILTER`` of type :class:`str`
    class MatMode:
        """ST matrix mode.
        
        - `COPY`:    A working copy of the matrix is created.
        - `INPLACE`: The operation is computed in-place.
        - `SHELL`:   The matrix :math:`A - \sigma B` is handled as an
                     implicit matrix.
        
        """
        COPY: int = _def(int, 'COPY')  #: Constant ``COPY`` of type :class:`int`
        INPLACE: int = _def(int, 'INPLACE')  #: Constant ``INPLACE`` of type :class:`int`
        SHELL: int = _def(int, 'SHELL')  #: Constant ``SHELL`` of type :class:`int`
    class FilterType:
        """ST filter type.
        
        - ``FILTLAN``:  An adapted implementation of the Filtered Lanczos Package.
        - ``CHEBYSEV``: A polynomial filter based on a truncated Chebyshev series.
        
        """
        FILTLAN: int = _def(int, 'FILTLAN')  #: Constant ``FILTLAN`` of type :class:`int`
        CHEBYSHEV: int = _def(int, 'CHEBYSHEV')  #: Constant ``CHEBYSHEV`` of type :class:`int`
    class FilterDamping:
        """ST filter damping.
        
        - `NONE`:    No damping
        - `JACKSON`: Jackson damping
        - `LANCZOS`: Lanczos damping
        - `FEJER`:   Fejer damping
        
        """
        NONE: int = _def(int, 'NONE')  #: Constant ``NONE`` of type :class:`int`
        JACKSON: int = _def(int, 'JACKSON')  #: Constant ``JACKSON`` of type :class:`int`
        LANCZOS: int = _def(int, 'LANCZOS')  #: Constant ``LANCZOS`` of type :class:`int`
        FEJER: int = _def(int, 'FEJER')  #: Constant ``FEJER`` of type :class:`int`
    def view(self, viewer: Viewer | None = None) -> None:
        """Print the ST data structure.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:73 <slepc4py/SLEPc/ST.pyx#L73>`
    
        """
        ...
    def destroy(self) -> Self:
        """Destroy the ST object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:88 <slepc4py/SLEPc/ST.pyx#L88>`
    
        """
        ...
    def reset(self) -> None:
        """Reset the ST object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:98 <slepc4py/SLEPc/ST.pyx#L98>`
    
        """
        ...
    def create(self, comm: Comm | None = None) -> Self:
        """Create the ST object.
    
        Collective.
    
        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all processes.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:106 <slepc4py/SLEPc/ST.pyx#L106>`
    
        """
        ...
    def setType(self, st_type: Type | str) -> None:
        """Set the particular spectral transformation to be used.
    
        Logically collective.
    
        Parameters
        ----------
        st_type
            The spectral transformation to be used.
    
        Notes
        -----
        See `ST.Type` for available methods. The default is
        `ST.Type.SHIFT` with a zero shift.  Normally, it is best to
        use `setFromOptions()` and then set the ST type from the
        options database rather than by using this routine.  Using the
        options database provides the user with maximum flexibility in
        evaluating the different available methods.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:123 <slepc4py/SLEPc/ST.pyx#L123>`
    
        """
        ...
    def getType(self) -> str:
        """Get the ST type of this object.
    
        Not collective.
    
        Returns
        -------
        str
            The spectral transformation currently being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:147 <slepc4py/SLEPc/ST.pyx#L147>`
    
        """
        ...
    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all ST options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all ST option requests.
    
        Notes
        -----
        A hyphen (``-``) must NOT be given at the beginning of the
        prefix name.  The first character of all runtime options is
        AUTOMATICALLY the hyphen.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:162 <slepc4py/SLEPc/ST.pyx#L162>`
    
        """
        ...
    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all ST options in the database.
    
        Not collective.
    
        Returns
        -------
        str
            The prefix string set for this ST object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:183 <slepc4py/SLEPc/ST.pyx#L183>`
    
        """
        ...
    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all ST options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all ST option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:198 <slepc4py/SLEPc/ST.pyx#L198>`
    
        """
        ...
    def setFromOptions(self) -> None:
        """Set ST options from the options database.
    
        Collective.
    
        This routine must be called before `setUp()` if the user is to be
        allowed to set the solver type.
    
        Notes
        -----
        To see all options, run your program with the -help option.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:213 <slepc4py/SLEPc/ST.pyx#L213>`
    
        """
        ...
    def setShift(self, shift: Scalar) -> None:
        """Set the shift associated with the spectral transformation.
    
        Collective.
    
        Parameters
        ----------
        shift
            The value of the shift.
    
        Notes
        -----
        In some spectral transformations, changing the shift may have
        associated a lot of work, for example recomputing a
        factorization.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:230 <slepc4py/SLEPc/ST.pyx#L230>`
    
        """
        ...
    def getShift(self) -> Scalar:
        """Get the shift associated with the spectral transformation.
    
        Not collective.
    
        Returns
        -------
        Scalar
            The value of the shift.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:250 <slepc4py/SLEPc/ST.pyx#L250>`
    
        """
        ...
    def setTransform(self, flag: bool = True) -> None:
        """Set a flag to indicate whether the transformed matrices are computed or not.
    
        Logically collective.
    
        Parameters
        ----------
        flag
            This flag is intended for the case of polynomial
            eigenproblems solved via linearization.
            If this flag is False (default) the spectral transformation
            is applied to the linearization (handled by the eigensolver),
            otherwise it is applied to the original problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:265 <slepc4py/SLEPc/ST.pyx#L265>`
    
        """
        ...
    def getTransform(self) -> bool:
        """Get the flag indicating whether the transformed matrices are computed or not.
    
        Not collective.
    
        Returns
        -------
        bool
            This flag is intended for the case of polynomial
            eigenproblems solved via linearization.
            If this flag is False (default) the spectral transformation
            is applied to the linearization (handled by the eigensolver),
            otherwise it is applied to the original problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:283 <slepc4py/SLEPc/ST.pyx#L283>`
    
        """
        ...
    def setMatMode(self, mode: MatMode) -> None:
        """Set a flag to indicate how the matrix is being shifted.
    
        Logically collective.
    
        Set a flag to indicate how the matrix is being shifted in the
        shift-and-invert and Cayley spectral transformations.
    
        Parameters
        ----------
        mode
            The mode flag.
    
        Notes
        -----
        By default (`ST.MatMode.COPY`), a copy of matrix :math:`A` is made
        and then this copy is shifted explicitly, e.g.
        :math:`A \leftarrow (A - s B)`.
    
        With `ST.MatMode.INPLACE`, the original matrix :math:`A` is shifted at
        `setUp()` and unshifted at the end of the computations. With respect to
        the previous one, this mode avoids a copy of matrix :math:`A`. However,
        a backdraw is that the recovered matrix might be slightly different
        from the original one (due to roundoff).
    
        With `ST.MatMode.SHELL`, the solver works with an implicit shell matrix
        that represents the shifted matrix. This mode is the most efficient in
        creating the shifted matrix but it places serious limitations to the
        linear solves performed in each iteration of the eigensolver
        (typically, only iterative solvers with Jacobi preconditioning can be
        used).
    
        In the case of generalized problems, in the two first modes the matrix
        :math:`A - s B` has to be computed explicitly. The efficiency of
        this computation can be controlled with `setMatStructure()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:302 <slepc4py/SLEPc/ST.pyx#L302>`
    
        """
        ...
    def getMatMode(self) -> MatMode:
        """Get a flag that indicates how the matrix is being shifted.
    
        Not collective.
    
        Get a flag that indicates how the matrix is being shifted in
        the shift-and-invert and Cayley spectral transformations.
    
        Returns
        -------
        MatMode
            The mode flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:342 <slepc4py/SLEPc/ST.pyx#L342>`
    
        """
        ...
    def setMatrices(self, operators: list[Mat]) -> None:
        """Set the matrices associated with the eigenvalue problem.
    
        Collective.
    
        Parameters
        ----------
        operators
            The matrices associated with the eigensystem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:360 <slepc4py/SLEPc/ST.pyx#L360>`
    
        """
        ...
    def getMatrices(self) -> list[petsc4py.PETSc.Mat]:
        """Get the matrices associated with the eigenvalue problem.
    
        Collective.
    
        Returns
        -------
        list of petsc4py.PETSc.Mat
            The matrices associated with the eigensystem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:378 <slepc4py/SLEPc/ST.pyx#L378>`
    
        """
        ...
    def setMatStructure(self, structure: petsc4py.PETSc.Mat.Structure) -> None:
        """Set an internal Mat.Structure attribute.
    
        Logically collective.
    
        Set an internal Mat.Structure attribute to indicate which is the
        relation of the sparsity pattern of the two matrices :math:`A` and
        :math:`B` constituting the generalized eigenvalue problem. This
        function has no effect in the case of standard eigenproblems.
    
        Parameters
        ----------
        structure
            Either same, different, or a subset of the non-zero
            sparsity pattern.
    
        Notes
        -----
        By default, the sparsity patterns are assumed to be
        different. If the patterns are equal or a subset then it is
        recommended to set this attribute for efficiency reasons (in
        particular, for internal *AXPY()* matrix operations).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:400 <slepc4py/SLEPc/ST.pyx#L400>`
    
        """
        ...
    def getMatStructure(self) -> petsc4py.PETSc.Mat.Structure:
        """Get the internal Mat.Structure attribute.
    
        Not collective.
    
        Get the internal Mat.Structure attribute to indicate which is
        the relation of the sparsity pattern of the matrices.
    
        Returns
        -------
        petsc4py.PETSc.Mat.Structure
            The structure flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:427 <slepc4py/SLEPc/ST.pyx#L427>`
    
        """
        ...
    def setKSP(self, ksp: petsc4py.PETSc.KSP) -> None:
        """Set the ``KSP`` object associated with the spectral transformation.
    
        Collective.
    
        Parameters
        ----------
        `petsc4py.PETSc.KSP`
            The linear solver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:445 <slepc4py/SLEPc/ST.pyx#L445>`
    
        """
        ...
    def getKSP(self) -> KSP:
        """Get the ``KSP`` object associated with the spectral transformation.
    
        Collective.
    
        Returns
        -------
        `petsc4py.PETSc.KSP`
            The linear solver object.
    
        Notes
        -----
        On output, the internal value of `petsc4py.PETSc.KSP` can be ``NULL`` if the
        combination of eigenproblem type and selected transformation
        does not require to solve a linear system of equations.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:458 <slepc4py/SLEPc/ST.pyx#L458>`
    
        """
        ...
    def setPreconditionerMat(self, P: Mat | None = None) -> None:
        """Set the matrix to be used to build the preconditioner.
    
        Collective.
    
        Parameters
        ----------
        P
            The matrix that will be used in constructing the preconditioner.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:480 <slepc4py/SLEPc/ST.pyx#L480>`
    
        """
        ...
    def getPreconditionerMat(self) -> petsc4py.PETSc.Mat:
        """Get the matrix previously set by setPreconditionerMat().
    
        Not collective.
    
        Returns
        -------
        petsc4py.PETSc.Mat
            The matrix that will be used in constructing the preconditioner.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:494 <slepc4py/SLEPc/ST.pyx#L494>`
    
        """
        ...
    def setSplitPreconditioner(self, operators: list[petsc4py.PETSc.Mat], structure: petsc4py.PETSc.Mat.Structure | None = None) -> None:
        """Set the matrices to be used to build the preconditioner.
    
        Collective.
    
        Parameters
        ----------
        operators
            The matrices associated with the preconditioner.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:510 <slepc4py/SLEPc/ST.pyx#L510>`
    
        """
        ...
    def getSplitPreconditioner(self) -> tuple[list[petsc4py.PETSc.Mat], petsc4py.PETSc.Mat.Structure]:
        """Get the matrices to be used to build the preconditioner.
    
        Not collective.
    
        Returns
        -------
        list of petsc4py.PETSc.Mat
            The list of matrices associated with the preconditioner.
        petsc4py.PETSc.Mat.Structure
            The structure flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:529 <slepc4py/SLEPc/ST.pyx#L529>`
    
        """
        ...
    def setUp(self) -> None:
        """Prepare for the use of a spectral transformation.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:555 <slepc4py/SLEPc/ST.pyx#L555>`
    
        """
        ...
    def apply(self, x: Vec, y: Vec) -> None:
        """Apply the spectral transformation operator to a vector.
    
        Collective.
    
        Apply the spectral transformation operator to a vector, for instance
        :math:`(A - s B)^{-1} B` in the case of the shift-and-invert
        transformation and generalized eigenproblem.
    
        Parameters
        ----------
        x
            The input vector.
        y
            The result vector.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:563 <slepc4py/SLEPc/ST.pyx#L563>`
    
        """
        ...
    def applyTranspose(self, x: Vec, y: Vec) -> None:
        """Apply the transpose of the operator to a vector.
    
        Collective.
    
        Apply the transpose of the operator to a vector, for instance
        :math:`B^T(A - s B)^{-T}` in the case of the shift-and-invert
        transformation and generalized eigenproblem.
    
        Parameters
        ----------
        x
            The input vector.
        y
            The result vector.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:582 <slepc4py/SLEPc/ST.pyx#L582>`
    
        """
        ...
    def applyHermitianTranspose(self, x: Vec, y: Vec) -> None:
        """Apply the hermitian-transpose of the operator to a vector.
    
        Collective.
    
        Apply the hermitian-transpose of the operator to a vector, for instance
        :math:`B^H(A - s B)^{-H}` in the case of the shift-and-invert
        transformation and generalized eigenproblem.
    
        Parameters
        ----------
        x
            The input vector.
        y
            The result vector.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:601 <slepc4py/SLEPc/ST.pyx#L601>`
    
        """
        ...
    def applyMat(self, x: Mat, y: Mat) -> None:
        """Apply the spectral transformation operator to a matrix.
    
        Collective.
    
        Apply the spectral transformation operator to a matrix, for instance
        :math:`(A - s B)^{-1} B` in the case of the shift-and-invert
        transformation and generalized eigenproblem.
    
        Parameters
        ----------
        x
            The input matrix.
        y
            The result matrix.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:620 <slepc4py/SLEPc/ST.pyx#L620>`
    
        """
        ...
    def getOperator(self) -> petsc4py.PETSc.Mat:
        """Get a shell matrix that represents the operator of the spectral transformation.
    
        Collective.
    
        Returns
        -------
        petsc4py.PETSc.Mat
            Operator matrix.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:639 <slepc4py/SLEPc/ST.pyx#L639>`
    
        """
        ...
    def restoreOperator(self, op: Mat) -> None:
        """Restore the previously seized operator matrix.
    
        Logically collective.
    
        Parameters
        ----------
        op
            Operator matrix previously obtained with getOperator().
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:655 <slepc4py/SLEPc/ST.pyx#L655>`
    
        """
        ...
    def setCayleyAntishift(self, tau: Scalar) -> None:
        """Set the value of the anti-shift for the Cayley spectral transformation.
    
        Logically collective.
    
        Parameters
        ----------
        tau
            The anti-shift.
    
        Notes
        -----
        In the generalized Cayley transform, the operator can be expressed as
        :math:`OP = inv(A - \sigma B) (A + tau B)`. This function sets
        the value of :math:`tau`.  Use `setShift()` for setting
        :math:`\sigma`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:671 <slepc4py/SLEPc/ST.pyx#L671>`
    
        """
        ...
    def getCayleyAntishift(self) -> Scalar:
        """Get the value of the anti-shift for the Cayley spectral transformation.
    
        Not collective.
    
        Returns
        -------
        Scalar
            The anti-shift.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:692 <slepc4py/SLEPc/ST.pyx#L692>`
    
        """
        ...
    def setFilterType(self, filter_type: FilterType) -> None:
        """Set the method to be used to build the polynomial filter.
    
        Logically collective.
    
        Parameter
        ---------
        filter_type
            The type of filter.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:707 <slepc4py/SLEPc/ST.pyx#L707>`
    
        """
        ...
    def getFilterType(self) -> FilterType:
        """Get the method to be used to build the polynomial filter.
    
        Not collective.
    
        Returns
        -------
        FilterType
            The type of filter.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:721 <slepc4py/SLEPc/ST.pyx#L721>`
    
        """
        ...
    def setFilterInterval(self, inta: float, intb: float) -> None:
        """Set the interval containing the desired eigenvalues.
    
        Logically collective.
    
        Parameters
        ----------
        inta
            The left end of the interval.
        intb
            The right end of the interval.
    
        Notes
        -----
        The filter will be configured to emphasize eigenvalues contained
        in the given interval, and damp out eigenvalues outside it. If the
        interval is open, then the filter is low- or high-pass, otherwise
        it is mid-pass.
    
        Common usage is to set the interval in `EPS` with `EPS.setInterval()`.
    
        The interval must be contained within the numerical range of the
        matrix, see `ST.setFilterRange()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:736 <slepc4py/SLEPc/ST.pyx#L736>`
    
        """
        ...
    def getFilterInterval(self) -> tuple[float, float]:
        """Get the interval containing the desired eigenvalues.
    
        Not collective.
    
        Returns
        -------
        inta: float
            The left end of the interval.
        intb: float
            The right end of the interval.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:765 <slepc4py/SLEPc/ST.pyx#L765>`
    
        """
        ...
    def setFilterRange(self, left: float, right: float) -> None:
        """Set the numerical range (or field of values) of the matrix.
    
        Logically collective.
    
        Set the numerical range (or field of values) of the matrix, that is,
        the interval containing all eigenvalues.
    
        Parameters
        ----------
        left
            The left end of the interval.
        right
            The right end of the interval.
    
        Notes
        -----
        The filter will be most effective if the numerical range is tight,
        that is, left and right are good approximations to the leftmost and
        rightmost eigenvalues, respectively.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:783 <slepc4py/SLEPc/ST.pyx#L783>`
    
        """
        ...
    def getFilterRange(self) -> tuple[float, float]:
        """Get the interval containing all eigenvalues.
    
        Not collective.
    
        Returns
        -------
        left: float
            The left end of the interval.
        right: float
            The right end of the interval.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:809 <slepc4py/SLEPc/ST.pyx#L809>`
    
        """
        ...
    def setFilterDegree(self, deg: int) -> None:
        """Set the degree of the filter polynomial.
    
        Logically collective.
    
        Parameters
        ----------
        deg
            The polynomial degree.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:827 <slepc4py/SLEPc/ST.pyx#L827>`
    
        """
        ...
    def getFilterDegree(self) -> int:
        """Get the degree of the filter polynomial.
    
        Not collective.
    
        Returns
        -------
        int
            The polynomial degree.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:841 <slepc4py/SLEPc/ST.pyx#L841>`
    
        """
        ...
    def setFilterDamping(self, damping: FilterDamping) -> None:
        """Set the type of damping to be used in the polynomial filter.
    
        Logically collective.
    
        Parameter
        ---------
        damping
            The type of damping.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:856 <slepc4py/SLEPc/ST.pyx#L856>`
    
        """
        ...
    def getFilterDamping(self) -> FilterDamping:
        """Get the type of damping used in the polynomial filter.
    
        Not collective.
    
        Returns
        -------
        FilterDamping
            The type of damping.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:870 <slepc4py/SLEPc/ST.pyx#L870>`
    
        """
        ...
    @property
    def shift(self) -> float:
        """Value of the shift.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:887 <slepc4py/SLEPc/ST.pyx#L887>`
    
        """
        ...
    @property
    def transform(self) -> bool:
        """If the transformed matrices are computed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:894 <slepc4py/SLEPc/ST.pyx#L894>`
    
        """
        ...
    @property
    def mat_mode(self) -> STMatMode:
        """How the transformed matrices are being stored in the ST.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:901 <slepc4py/SLEPc/ST.pyx#L901>`
    
        """
        ...
    @property
    def mat_structure(self) -> MatStructure:
        """Relation of the sparsity pattern of all ST matrices.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:908 <slepc4py/SLEPc/ST.pyx#L908>`
    
        """
        ...
    @property
    def ksp(self) -> KSP:
        """KSP object associated with the spectral transformation.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/ST.pyx:915 <slepc4py/SLEPc/ST.pyx#L915>`
    
        """
        ...

class BV(Object):
    """BV."""
    class Type:
        """BV type."""
        MAT: str = _def(str, 'MAT')  #: Object ``MAT`` of type :class:`str`
        SVEC: str = _def(str, 'SVEC')  #: Object ``SVEC`` of type :class:`str`
        VECS: str = _def(str, 'VECS')  #: Object ``VECS`` of type :class:`str`
        CONTIGUOUS: str = _def(str, 'CONTIGUOUS')  #: Object ``CONTIGUOUS`` of type :class:`str`
        TENSOR: str = _def(str, 'TENSOR')  #: Object ``TENSOR`` of type :class:`str`
    class OrthogType:
        """BV orthogonalization types.
        
        - `CGS`: Classical Gram-Schmidt.
        - `MGS`: Modified Gram-Schmidt.
        
        """
        CGS: int = _def(int, 'CGS')  #: Constant ``CGS`` of type :class:`int`
        MGS: int = _def(int, 'MGS')  #: Constant ``MGS`` of type :class:`int`
    class OrthogRefineType:
        """BV orthogonalization refinement types.
        
        - `IFNEEDED`: Reorthogonalize if a criterion is satisfied.
        - `NEVER`:    Never reorthogonalize.
        - `ALWAYS`:   Always reorthogonalize.
        
        """
        IFNEEDED: int = _def(int, 'IFNEEDED')  #: Constant ``IFNEEDED`` of type :class:`int`
        NEVER: int = _def(int, 'NEVER')  #: Constant ``NEVER`` of type :class:`int`
        ALWAYS: int = _def(int, 'ALWAYS')  #: Constant ``ALWAYS`` of type :class:`int`
    class OrthogRefineType:
        """BV orthogonalization refinement types.
        
        - `IFNEEDED`: Reorthogonalize if a criterion is satisfied.
        - `NEVER`:    Never reorthogonalize.
        - `ALWAYS`:   Always reorthogonalize.
        
        """
        IFNEEDED: int = _def(int, 'IFNEEDED')  #: Constant ``IFNEEDED`` of type :class:`int`
        NEVER: int = _def(int, 'NEVER')  #: Constant ``NEVER`` of type :class:`int`
        ALWAYS: int = _def(int, 'ALWAYS')  #: Constant ``ALWAYS`` of type :class:`int`
    class OrthogBlockType:
        """BV block-orthogonalization types.
        
        - `GS`:       Gram-Schmidt.
        - `CHOL`:     Cholesky.
        - `TSQR`:     Tall-skinny QR.
        - `TSQRCHOL`: Tall-skinny QR with Cholesky.
        - `SVQB`:     SVQB.
        
        """
        GS: int = _def(int, 'GS')  #: Constant ``GS`` of type :class:`int`
        CHOL: int = _def(int, 'CHOL')  #: Constant ``CHOL`` of type :class:`int`
        TSQR: int = _def(int, 'TSQR')  #: Constant ``TSQR`` of type :class:`int`
        TSQRCHOL: int = _def(int, 'TSQRCHOL')  #: Constant ``TSQRCHOL`` of type :class:`int`
        SVQB: int = _def(int, 'SVQB')  #: Constant ``SVQB`` of type :class:`int`
    class OrthogBlockType:
        """BV block-orthogonalization types.
        
        - `GS`:       Gram-Schmidt.
        - `CHOL`:     Cholesky.
        - `TSQR`:     Tall-skinny QR.
        - `TSQRCHOL`: Tall-skinny QR with Cholesky.
        - `SVQB`:     SVQB.
        
        """
        GS: int = _def(int, 'GS')  #: Constant ``GS`` of type :class:`int`
        CHOL: int = _def(int, 'CHOL')  #: Constant ``CHOL`` of type :class:`int`
        TSQR: int = _def(int, 'TSQR')  #: Constant ``TSQR`` of type :class:`int`
        TSQRCHOL: int = _def(int, 'TSQRCHOL')  #: Constant ``TSQRCHOL`` of type :class:`int`
        SVQB: int = _def(int, 'SVQB')  #: Constant ``SVQB`` of type :class:`int`
    class MatMultType:
        """BV mat-mult types.
        
        - `VECS`: Perform a matrix-vector multiply per each column.
        - `MAT`:  Carry out a Mat-Mat product with a dense matrix.
        
        """
        VECS: int = _def(int, 'VECS')  #: Constant ``VECS`` of type :class:`int`
        MAT: int = _def(int, 'MAT')  #: Constant ``MAT`` of type :class:`int`
    def view(self, viewer: Viewer | None = None) -> None:
        """Print the BV data structure.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:150 <slepc4py/SLEPc/BV.pyx#L150>`
    
        """
        ...
    def destroy(self) -> Self:
        """Destroy the BV object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:165 <slepc4py/SLEPc/BV.pyx#L165>`
    
        """
        ...
    def create(self, comm: Comm | None = None) -> Self:
        """Create the BV object.
    
        Collective.
    
        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all
            processes.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:175 <slepc4py/SLEPc/BV.pyx#L175>`
    
        """
        ...
    def createFromMat(self, A: Mat) -> Self:
        """Create a basis vectors object from a dense Mat object.
    
        Collective.
    
        Parameters
        ----------
        A
            A dense tall-skinny matrix.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:193 <slepc4py/SLEPc/BV.pyx#L193>`
    
        """
        ...
    def createMat(self) -> petsc4py.PETSc.Mat:
        """Create a new Mat object of dense type and copy the contents of the BV.
    
        Collective.
    
        Returns
        -------
        petsc4py.PETSc.Mat
            The new matrix.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:209 <slepc4py/SLEPc/BV.pyx#L209>`
    
        """
        ...
    def duplicate(self) -> BV:
        """Duplicate the BV object with the same type and dimensions.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:224 <slepc4py/SLEPc/BV.pyx#L224>`
    
        """
        ...
    def duplicateResize(self, m: int) -> BV:
        """Create a BV object of the same type and dimensions as an existing one.
    
        Collective.
    
        Parameters
        ----------
        m
            The number of columns.
    
        Notes
        -----
        With possibly different number of columns.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:234 <slepc4py/SLEPc/BV.pyx#L234>`
    
        """
        ...
    def copy(self, result: BV | None = None) -> BV:
        """Copy a basis vector object into another one.
    
        Logically collective.
    
        Parameters
        ----------
        result
            The copy.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:255 <slepc4py/SLEPc/BV.pyx#L255>`
    
        """
        ...
    def setType(self, bv_type: Type | str) -> None:
        """Set the type for the BV object.
    
        Logically collective.
    
        Parameters
        ----------
        bv_type
            The inner product type to be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:273 <slepc4py/SLEPc/BV.pyx#L273>`
    
        """
        ...
    def getType(self) -> str:
        """Get the BV type of this object.
    
        Not collective.
    
        Returns
        -------
        str
            The inner product type currently being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:288 <slepc4py/SLEPc/BV.pyx#L288>`
    
        """
        ...
    def setSizes(self, sizes: LayoutSizeSpec, m: int) -> None:
        """Set the local and global sizes, and the number of columns.
    
        Collective.
    
        Parameters
        ----------
        sizes
            The global size ``N`` or a two-tuple ``(n, N)``
            with the local and global sizes.
        m
            The number of columns.
    
        Notes
        -----
        Either ``n`` or ``N`` (but not both) can be ``PETSc.DECIDE``
        or ``None`` to have it automatically set.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:303 <slepc4py/SLEPc/BV.pyx#L303>`
    
        """
        ...
    def setSizesFromVec(self, w: Vec, m: int) -> None:
        """Set the local and global sizes, and the number of columns.
    
        Collective.
    
        Local and global sizes are specified indirectly by passing a template
        vector.
    
        Parameters
        ----------
        w
            The template vector.
        m
            The number of columns.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:327 <slepc4py/SLEPc/BV.pyx#L327>`
    
        """
        ...
    def getSizes(self) -> tuple[LayoutSizeSpec, int]:
        """Get the local and global sizes, and the number of columns.
    
        Not collective.
    
        Returns
        -------
        (n, N): tuple of int
            The local and global sizes
        m: int
            The number of columns.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:346 <slepc4py/SLEPc/BV.pyx#L346>`
    
        """
        ...
    def setLeadingDimension(self, ld: int) -> None:
        """Set the leading dimension.
    
        Not collective.
    
        Parameters
        ----------
        ld
            The leading dimension.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:363 <slepc4py/SLEPc/BV.pyx#L363>`
    
        """
        ...
    def getLeadingDimension(self) -> int:
        """Get the leading dimension.
    
        Not collective.
    
        Returns
        -------
        int
            The leading dimension.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:377 <slepc4py/SLEPc/BV.pyx#L377>`
    
        """
        ...
    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all BV options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all BV option requests.
    
        Notes
        -----
        A hyphen (``-``) must NOT be given at the beginning of the
        prefix name.  The first character of all runtime options is
        AUTOMATICALLY the hyphen.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:392 <slepc4py/SLEPc/BV.pyx#L392>`
    
        """
        ...
    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all BV options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all BV option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:413 <slepc4py/SLEPc/BV.pyx#L413>`
    
        """
        ...
    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all BV options in the database.
    
        Not collective.
    
        Returns
        -------
        str
            The prefix string set for this BV object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:428 <slepc4py/SLEPc/BV.pyx#L428>`
    
        """
        ...
    def setFromOptions(self) -> None:
        """Set BV options from the options database.
    
        Collective.
    
        Notes
        -----
        To see all options, run your program with the ``-help``
        option.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:443 <slepc4py/SLEPc/BV.pyx#L443>`
    
        """
        ...
    def getOrthogonalization(self) -> tuple[OrthogType, OrthogRefineType, float, OrthogBlockType]:
        """Get the orthogonalization settings from the BV object.
    
        Not collective.
    
        Returns
        -------
        type: OrthogType
            The type of orthogonalization technique.
        refine: OrthogRefineType
            The type of refinement.
        eta: float
            Parameter for selective refinement (used when the
            refinement type is `BV.OrthogRefineType.IFNEEDED`).
        block: OrthogBlockType
            The type of block orthogonalization .
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:458 <slepc4py/SLEPc/BV.pyx#L458>`
    
        """
        ...
    def setOrthogonalization(self, otype: OrthogType | None = None, refine: OrthogRefineType | None = None, eta: float | None = None, block: OrthogBlockType | None = None) -> None:
        """Set the method used for the (block-)orthogonalization of vectors.
    
        Logically collective.
    
        Ortogonalization of vectors (classical or modified Gram-Schmidt
        with or without refinement), and for the block-orthogonalization
        (simultaneous orthogonalization of a set of vectors).
    
        Parameters
        ----------
        otype
            The type of orthogonalization technique.
        refine
            The type of refinement.
        eta
            Parameter for selective refinement.
        block
            The type of block orthogonalization.
    
        Notes
        -----
        The default settings work well for most problems.
    
        The parameter ``eta`` should be a real value between ``0`` and
        ``1`` (or `DETERMINE`).  The value of ``eta`` is used only when
        the refinement type is `BV.OrthogRefineType.IFNEEDED`.
    
        When using several processors, `BV.OrthogType.MGS` is likely to
        result in bad scalability.
    
        If the method set for block orthogonalization is GS, then the
        computation is done column by column with the vector orthogonalization.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:483 <slepc4py/SLEPc/BV.pyx#L483>`
    
        """
        ...
    def getMatMultMethod(self) -> MatMultType:
        """Get the method used for the `matMult()` operation.
    
        Not collective.
    
        Returns
        -------
        MatMultType
            The method for the `matMult()` operation.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:535 <slepc4py/SLEPc/BV.pyx#L535>`
    
        """
        ...
    def setMatMultMethod(self, method: MatMultType) -> None:
        """Set the method used for the `matMult()` operation.
    
        Logically collective.
    
        Parameters
        ----------
        method
            The method for the `matMult()` operation.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:550 <slepc4py/SLEPc/BV.pyx#L550>`
    
        """
        ...
    def getMatrix(self) -> tuple[petsc4py.PETSc.Mat, bool] | tuple[None, bool]:
        """Get the matrix representation of the inner product.
    
        Not collective.
    
        Returns
        -------
        mat: petsc4py.PETSc.Mat
            The matrix of the inner product
        indef: bool
            Whether the matrix is indefinite
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:566 <slepc4py/SLEPc/BV.pyx#L566>`
    
        """
        ...
    def setMatrix(self, mat: Mat, indef: bool = False) -> None:
        """Set the bilinear form to be used for inner products.
    
        Collective.
    
        Parameters
        ----------
        mat
            The matrix of the inner product.
        indef
            Whether the matrix is indefinite
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:588 <slepc4py/SLEPc/BV.pyx#L588>`
    
        """
        ...
    def applyMatrix(self, x: Vec, y: Vec) -> None:
        """Multiply a vector with the matrix associated to the bilinear form.
    
        Neighbor-wise collective.
    
        Parameters
        ----------
        x
            The input vector.
        y
            The result vector.
    
        Notes
        -----
        If the bilinear form has no associated matrix this function
        copies the vector.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:605 <slepc4py/SLEPc/BV.pyx#L605>`
    
        """
        ...
    def setActiveColumns(self, l: int, k: int) -> None:
        """Set the columns that will be involved in operations.
    
        Logically collective.
    
        Parameters
        ----------
        l
            The leading number of columns.
        k
            The active number of columns.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:625 <slepc4py/SLEPc/BV.pyx#L625>`
    
        """
        ...
    def getActiveColumns(self) -> tuple[int, int]:
        """Get the current active dimensions.
    
        Not collective.
    
        Returns
        -------
        l: int
            The leading number of columns.
        k: int
            The active number of columns.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:642 <slepc4py/SLEPc/BV.pyx#L642>`
    
        """
        ...
    def scaleColumn(self, j: int, alpha: Scalar) -> None:
        """Scale column j by alpha.
    
        Logically collective.
    
        Parameters
        ----------
        j
            column number to be scaled.
        alpha
            scaling factor.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:659 <slepc4py/SLEPc/BV.pyx#L659>`
    
        """
        ...
    def scale(self, alpha: Scalar) -> None:
        """Multiply the entries by a scalar value.
    
        Logically collective.
    
        Parameters
        ----------
        alpha
            scaling factor.
    
        Notes
        -----
        All active columns (except the leading ones) are scaled.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:676 <slepc4py/SLEPc/BV.pyx#L676>`
    
        """
        ...
    def insertVec(self, j: int, w: Vec) -> None:
        """Insert a vector into the specified column.
    
        Logically collective.
    
        Parameters
        ----------
        j
            The column to be overwritten.
        w
            The vector to be copied.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:694 <slepc4py/SLEPc/BV.pyx#L694>`
    
        """
        ...
    def insertVecs(self, s: int, W: Vec | list[Vec], orth: bool = False) -> int:
        """Insert a set of vectors into specified columns.
    
        Collective.
    
        Parameters
        ----------
        s
            The first column to be overwritten.
        W
            Set of vectors to be copied.
        orth
            Flag indicating if the vectors must be orthogonalized.
    
        Returns
        -------
        int
            Number of linearly independent vectors.
    
        Notes
        -----
        Copies the contents of vectors W into self(:,s:s+n), where n is the
        length of W. If orthogonalization flag is set then the vectors are
        copied one by one then orthogonalized against the previous one.  If any
        are linearly dependent then it is discared and the value of m is
        decreased.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:710 <slepc4py/SLEPc/BV.pyx#L710>`
    
        """
        ...
    def insertConstraints(self, C: Vec | list[Vec]) -> int:
        """Insert a set of vectors as constraints.
    
        Collective.
    
        Parameters
        ----------
        C
            Set of vectors to be inserted as constraints.
    
        Returns
        -------
        int
            Number of constraints.
    
        Notes
        -----
        The constraints are relevant only during orthogonalization. Constraint
        vectors span a subspace that is deflated in every orthogonalization
        operation, so they are intended for removing those directions from the
        orthogonal basis computed in regular BV columns.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:749 <slepc4py/SLEPc/BV.pyx#L749>`
    
        """
        ...
    def setNumConstraints(self, nc: int) -> None:
        """Set the number of constraints.
    
        Logically collective.
    
        Parameters
        ----------
        nc
            The number of constraints.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:781 <slepc4py/SLEPc/BV.pyx#L781>`
    
        """
        ...
    def getNumConstraints(self) -> int:
        """Get the number of constraints.
    
        Not collective.
    
        Returns
        -------
        int
            The number of constraints.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:795 <slepc4py/SLEPc/BV.pyx#L795>`
    
        """
        ...
    def createVec(self) -> petsc4py.PETSc.Vec:
        """Create a Vec with the type and dimensions of the columns of the BV.
    
        Collective.
    
        Returns
        -------
        petsc4py.PETSc.Vec
            New vector.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:810 <slepc4py/SLEPc/BV.pyx#L810>`
    
        """
        ...
    def setVecType(self, vec_type: petsc4py.PETSc.Vec.Type | str) -> None:
        """Set the vector type.
    
        Collective.
    
        Parameters
        ----------
        vec_type
            Vector type used when creating vectors with `createVec`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:825 <slepc4py/SLEPc/BV.pyx#L825>`
    
        """
        ...
    def getVecType(self) -> str:
        """Get the vector type used by the basis vectors object.
    
        Not collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:840 <slepc4py/SLEPc/BV.pyx#L840>`
    
        """
        ...
    def copyVec(self, j: int, v: Vec) -> None:
        """Copy one of the columns of a basis vectors object into a Vec.
    
        Logically collective.
    
        Parameters
        ----------
        j
            The column number to be copied.
        v
            A vector.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:850 <slepc4py/SLEPc/BV.pyx#L850>`
    
        """
        ...
    def copyColumn(self, j: int, i: int) -> None:
        """Copy the values from one of the columns to another one.
    
        Logically collective.
    
        Parameters
        ----------
        j
            The number of the source column.
        i
            The number of the destination column.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:866 <slepc4py/SLEPc/BV.pyx#L866>`
    
        """
        ...
    def setDefiniteTolerance(self, deftol: float) -> None:
        """Set the tolerance to be used when checking a definite inner product.
    
        Logically collective.
    
        Parameters
        ----------
        deftol
            The tolerance.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:883 <slepc4py/SLEPc/BV.pyx#L883>`
    
        """
        ...
    def getDefiniteTolerance(self) -> float:
        """Get the tolerance to be used when checking a definite inner product.
    
        Not collective.
    
        Returns
        -------
        float
            The tolerance.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:897 <slepc4py/SLEPc/BV.pyx#L897>`
    
        """
        ...
    def dotVec(self, v: Vec) -> ArrayScalar:
        """Dot products of a vector against all the column vectors of the BV.
    
        Collective.
    
        Parameters
        ----------
        v
            A vector.
    
        Returns
        -------
        ArrayScalar 
            The computed values.
    
        Notes
        -----
        This is analogue to VecMDot(), but using BV to represent a collection
        of vectors. The result is :math:`m = X^H y`, so :math:`m_i` is
        equal to :math:`x_j^H y`. Note that here :math:`X` is transposed
        as opposed to BVDot().
    
        If a non-standard inner product has been specified with BVSetMatrix(),
        then the result is :math:`m = X^H B y`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:912 <slepc4py/SLEPc/BV.pyx#L912>`
    
        """
        ...
    def dotColumn(self, j: int) -> ArrayScalar:
        """Dot products of a column against all the column vectors of a BV.
    
        Collective.
    
        Parameters
        ----------
        j
            The index of the column.
    
        Returns
        -------
        ArrayScalar
            The computed values.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:948 <slepc4py/SLEPc/BV.pyx#L948>`
    
        """
        ...
    def getColumn(self, j: int) -> petsc4py.PETSc.Vec:
        """Get a Vec object with the entries of the column of the BV object.
    
        Logically collective.
    
        Parameters
        ----------
        j
            The index of the requested column.
    
        Returns
        -------
        petsc4py.PETSc.Vec
            The vector containing the jth column.
    
        Notes
        -----
        Modifying the returned Vec will change the BV entries as well.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:975 <slepc4py/SLEPc/BV.pyx#L975>`
    
        """
        ...
    def restoreColumn(self, j: int, v: Vec) -> None:
        """Restore a column obtained with `getColumn()`.
    
        Logically collective.
    
        Parameters
        ----------
        j
            The index of the requested column.
        v
            The vector obtained with `getColumn()`.
    
        Notes
        -----
        The arguments must match the corresponding call to `getColumn()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1001 <slepc4py/SLEPc/BV.pyx#L1001>`
    
        """
        ...
    def getMat(self) -> petsc4py.PETSc.Mat:
        """Get a Mat object of dense type that shares the memory of the BV object.
    
        Collective.
    
        Returns
        -------
        petsc4py.PETSc.Mat
            The matrix.
    
        Notes
        -----
        The returned matrix contains only the active columns. If the content
        of the Mat is modified, these changes are also done in the BV object.
        The user must call `restoreMat()` when no longer needed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1022 <slepc4py/SLEPc/BV.pyx#L1022>`
    
        """
        ...
    def restoreMat(self, A: Mat) -> None:
        """Restore the Mat obtained with `getMat()`.
    
        Logically collective.
    
        Parameters
        ----------
        A
            The matrix obtained with `getMat()`.
    
        Notes
        -----
        A call to this function must match a previous call of `getMat()`.
        The effect is that the contents of the Mat are copied back to the
        BV internal data structures.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1044 <slepc4py/SLEPc/BV.pyx#L1044>`
    
        """
        ...
    def dot(self, Y: BV) -> petsc4py.PETSc.Mat:
        """Compute the 'block-dot' product of two basis vectors objects.
    
        Collective.
    
        :math:`M = Y^H X` :math:`(m_{ij} = y_i^H x_j)` or
        :math:`M = Y^H B X`
    
        Parameters
        ----------
        Y
            Left basis vectors, can be the same as self, giving
            :math:`M = X^H X`.
    
        Returns
        -------
        petsc4py.PETSc.Mat
            The resulting matrix.
    
        Notes
        -----
        This is the generalization of VecDot() for a collection of vectors,
        :math:`M = Y^H X`. The result is a matrix :math:`M` whose entry
        :math:`m_{ij}` is equal to :math:`y_i^H x_j`
        (where :math:`y_i^H` denotes the conjugate transpose of :math:`y_i`).
    
        :math:`X` and :math:`Y` can be the same object.
    
        If a non-standard inner product has been specified with setMatrix(),
        then the result is :math:`M = Y^H B X`. In this case, both
        :math:`X` and :math:`Y` must have the same associated matrix.
    
        Only rows (resp. columns) of :math:`M` starting from :math:`ly` (resp.
        :math:`lx`) are computed, where :math:`ly` (resp. :math:`lx`) is the
        number of leading columns of :math:`Y` (resp. :math:`X`).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1064 <slepc4py/SLEPc/BV.pyx#L1064>`
    
        """
        ...
    def matProject(self, A: petsc4py.PETSc.Mat | None, Y: BV) -> petsc4py.PETSc.Mat:
        """Compute the projection of a matrix onto a subspace.
    
        Collective.
    
        :math:`M = Y^H A X`
    
        Parameters
        ----------
        A
            Matrix to be projected.
        Y
            Left basis vectors, can be the same as self, giving
            :math:`M = X^H A X`.
    
        Returns
        -------
        petsc4py.PETSc.Mat
            Projection of the matrix A onto the subspace.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1109 <slepc4py/SLEPc/BV.pyx#L1109>`
    
        """
        ...
    def matMult(self, A: Mat, Y: BV | None = None) -> BV:
        """Compute the matrix-vector product for each column, :math:`Y = A V`.
    
        Neighbor-wise collective.
    
        Parameters
        ----------
        A
            The matrix.
    
        Returns
        -------
        BV
            The result.
    
        Notes
        -----
        Only active columns (excluding the leading ones) are processed.
    
        It is possible to choose whether the computation is done column by column
        or using dense matrices using the options database keys:
    
            -bv_matmult_vecs
            -bv_matmult_mat
    
        The default is bv_matmult_mat.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1139 <slepc4py/SLEPc/BV.pyx#L1139>`
    
        """
        ...
    def matMultHermitianTranspose(self, A: Mat, Y: BV | None = None) -> BV:
        """Pre-multiplication with the conjugate transpose of a matrix.
    
        Neighbor-wise collective.
    
        :math:`Y = A^H V`.
    
        Parameters
        ----------
        A
            The matrix.
    
        Returns
        -------
        BV
            The result.
    
        Notes
        -----
        Only active columns (excluding the leading ones) are processed.
    
        As opoosed to matMult(), this operation is always done by column by
        column, with a sequence of calls to MatMultHermitianTranspose().
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1188 <slepc4py/SLEPc/BV.pyx#L1188>`
    
        """
        ...
    def matMultColumn(self, A: Mat, j: int) -> None:
        """Mat-vec product for a column, storing the result in the next column.
    
        Neighbor-wise collective.
    
        :math:`v_{j+1} = A v_j`.
    
        Parameters
        ----------
        A
            The matrix.
        j
            Index of column.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1234 <slepc4py/SLEPc/BV.pyx#L1234>`
    
        """
        ...
    def matMultTransposeColumn(self, A: Mat, j: int) -> None:
        """Transpose matrix-vector product for a specified column.
    
        Neighbor-wise collective.
    
        Store the result in the next column: :math:`v_{j+1} = A^T v_j`.
    
        Parameters
        ----------
        A
            The matrix.
        j
            Index of column.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1252 <slepc4py/SLEPc/BV.pyx#L1252>`
    
        """
        ...
    def matMultHermitianTransposeColumn(self, A: Mat, j: int) -> None:
        """Conjugate-transpose matrix-vector product for a specified column.
    
        Neighbor-wise collective.
    
        Store the result in the next column: :math:`v_{j+1} = A^H v_j`.
    
        Parameters
        ----------
        A
            The matrix.
        j
            Index of column.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1270 <slepc4py/SLEPc/BV.pyx#L1270>`
    
        """
        ...
    def mult(self, alpha: Scalar, beta: Scalar, X: BV, Q: Mat) -> None:
        """Compute :math:`Y = beta Y + alpha X Q`.
    
        Logically collective.
    
        Parameters
        ----------
        alpha
            Coefficient that multiplies X.
        beta
            Coefficient that multiplies Y.
        X
            Input basis vectors.
        Q
            Input matrix, if not given the identity matrix is assumed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1288 <slepc4py/SLEPc/BV.pyx#L1288>`
    
        """
        ...
    def multInPlace(self, Q: Mat, s: int, e: int) -> None:
        """Update a set of vectors as :math:`V(:,s:e-1) = V Q(:,s:e-1)`.
    
        Logically collective.
    
        Parameters
        ----------
        Q
            A sequential dense matrix.
        s
            First column to be overwritten.
        e
            Last column to be overwritten.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1310 <slepc4py/SLEPc/BV.pyx#L1310>`
    
        """
        ...
    def multColumn(self, alpha: Scalar, beta: Scalar, j: int, q: Sequence[Scalar]) -> None:
        """Compute :math:`y = beta y + alpha X q`.
    
        Logically collective.
    
        Compute :math:`y = beta y + alpha X q`, where
        :math:`y` is the :math:`j^{th}` column.
    
        Parameters
        ----------
        alpha
            Coefficient that multiplies X.
        beta
            Coefficient that multiplies y.
        j
            The column index.
        q
            Input coefficients.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1329 <slepc4py/SLEPc/BV.pyx#L1329>`
    
        """
        ...
    def multVec(self, alpha: Scalar, beta: Scalar, y: Vec, q: Sequence[Scalar]) -> None:
        """Compute :math:`y = beta y + alpha X q`.
    
        Logically collective.
    
        Parameters
        ----------
        alpha
            Coefficient that multiplies X.
        beta
            Coefficient that multiplies y.
        y
            Input/output vector.
        q
            Input coefficients.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1360 <slepc4py/SLEPc/BV.pyx#L1360>`
    
        """
        ...
    def normColumn(self, j: int, norm_type: NormType | None = None) -> float:
        """Compute the vector norm of a selected column.
    
        Collective.
    
        Parameters
        ----------
        j
            Index of column.
        norm_type
            The norm type.
    
        Returns
        -------
        float
            The norm.
    
        Notes
        -----
        The norm of :math:`V_j` is computed (NORM_1, NORM_2, or NORM_INFINITY).
    
        If a non-standard inner product has been specified with BVSetMatrix(),
        then the returned value is :math:`\sqrt{V_j^H B V_j}`,
        where :math:`B` is the inner product matrix (argument 'type' is
        ignored).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1387 <slepc4py/SLEPc/BV.pyx#L1387>`
    
        """
        ...
    def norm(self, norm_type: NormType | None = None) -> float:
        """Compute the matrix norm of the BV.
    
        Collective.
    
        Parameters
        ----------
        norm_type
            The norm type.
    
        Returns
        -------
        float
            The norm.
    
        Notes
        -----
        All active columns (except the leading ones) are considered as a
        matrix. The allowed norms are NORM_1, NORM_FROBENIUS, and
        NORM_INFINITY.
    
        This operation fails if a non-standard inner product has been specified
        with BVSetMatrix().
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1420 <slepc4py/SLEPc/BV.pyx#L1420>`
    
        """
        ...
    def resize(self, m: int, copy: bool = True) -> None:
        """Change the number of columns.
    
        Collective.
    
        Parameters
        ----------
        m
            The new number of columns.
        copy
            A flag indicating whether current values should be kept.
    
        Notes
        -----
        Internal storage is reallocated. If copy is True, then the contents are
        copied to the leading part of the new space.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1451 <slepc4py/SLEPc/BV.pyx#L1451>`
    
        """
        ...
    def setRandom(self) -> None:
        """Set the active columns of the BV to random numbers.
    
        Logically collective.
    
        Notes
        -----
        All active columns (except the leading ones) are modified.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1473 <slepc4py/SLEPc/BV.pyx#L1473>`
    
        """
        ...
    def setRandomNormal(self) -> None:
        """Set the active columns of the BV to normal random numbers.
    
        Logically collective.
    
        Notes
        -----
        All active columns (except the leading ones) are modified.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1485 <slepc4py/SLEPc/BV.pyx#L1485>`
    
        """
        ...
    def setRandomSign(self) -> None:
        """Set the entries of a BV to values 1 or -1 with equal probability.
    
        Logically collective.
    
        Notes
        -----
        All active columns (except the leading ones) are modified.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1497 <slepc4py/SLEPc/BV.pyx#L1497>`
    
        """
        ...
    def setRandomColumn(self, j: int) -> None:
        """Set one column of the BV to random numbers.
    
        Logically collective.
    
        Parameters
        ----------
        j
            Column number to be set.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1509 <slepc4py/SLEPc/BV.pyx#L1509>`
    
        """
        ...
    def setRandomCond(self, condn: float) -> None:
        """Set the columns of a BV to random numbers.
    
        Logically collective.
    
        The generated matrix has a prescribed condition number.
    
        Parameters
        ----------
        condn
            Condition number.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1523 <slepc4py/SLEPc/BV.pyx#L1523>`
    
        """
        ...
    def setRandomContext(self, rnd: Random) -> None:
        """Set the `petsc4py.PETSc.Random` object associated with the BV.
    
        Collective.
    
        To be used in operations that need random numbers.
    
        Parameters
        ----------
        rnd
            The random number generator context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1539 <slepc4py/SLEPc/BV.pyx#L1539>`
    
        """
        ...
    def getRandomContext(self) -> Random:
        """Get the `petsc4py.PETSc.Random` object associated with the BV.
    
        Collective.
    
        Returns
        -------
        petsc4py.PETSc.Random
            The random number generator context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1554 <slepc4py/SLEPc/BV.pyx#L1554>`
    
        """
        ...
    def orthogonalizeVec(self, v: Vec) -> tuple[float, bool]:
        """Orthogonalize a vector with respect to a set of vectors.
    
        Collective.
    
        Parameters
        ----------
        v
            Vector to be orthogonalized, modified on return.
    
        Returns
        -------
        norm: float
            The norm of the resulting vector.
        lindep: bool
            Flag indicating that refinement did not improve the
            quality of orthogonalization.
    
        Notes
        -----
        This function applies an orthogonal projector to project vector
        :math:`v` onto the orthogonal complement of the span of the columns
        of the BV.
    
        This routine does not normalize the resulting vector.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1570 <slepc4py/SLEPc/BV.pyx#L1570>`
    
        """
        ...
    def orthogonalizeColumn(self, j: int) -> tuple[float, bool]:
        """Orthogonalize a column vector with respect to the previous ones.
    
        Collective.
    
        Parameters
        ----------
        j
            Index of the column to be orthogonalized.
    
        Returns
        -------
        norm: float
            The norm of the resulting vector.
        lindep: bool
            Flag indicating that refinement did not improve the
            quality of orthogonalization.
    
        Notes
        -----
        This function applies an orthogonal projector to project vector
        :math:`V_j` onto the orthogonal complement of the span of the columns
        :math:`V[0..j-1]`, where :math:`V[.]` are the vectors of the BV.
        The columns :math:`V[0..j-1]` are assumed to be mutually orthonormal.
    
        This routine does not normalize the resulting vector.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1602 <slepc4py/SLEPc/BV.pyx#L1602>`
    
        """
        ...
    def orthonormalizeColumn(self, j: int, replace: bool = False) -> tuple[float, bool]:
        """Orthonormalize a column vector with respect to the previous ones.
    
        Collective.
    
        This is equivalent to a call to `orthogonalizeColumn()` followed by a
        call to `scaleColumn()` with the reciprocal of the norm.
    
        Parameters
        ----------
        j
            Index of the column to be orthonormalized.
        replace
            Whether it is allowed to set the vector randomly.
    
        Returns
        -------
        norm: float
            The norm of the resulting vector.
        lindep: bool
            Flag indicating that refinement did not improve the
            quality of orthogonalization.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1636 <slepc4py/SLEPc/BV.pyx#L1636>`
    
        """
        ...
    def orthogonalize(self, R: Mat | None = None, **kargs: Any) -> None:
        """Orthogonalize all columns (except leading ones) (QR decomposition).
    
        Collective.
    
        Parameters
        ----------
        R
            A sequential dense matrix.
    
        Notes
        -----
        The output satisfies :math:`V_0 = V R` (where :math:`V_0` represent the
        input :math:`V`) and :math:`V' V = I`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1668 <slepc4py/SLEPc/BV.pyx#L1668>`
    
        """
        ...
    @property
    def sizes(self) -> tuple[LayoutSizeSpec, int]:
        """Basis vectors local and global sizes, and the number of columns.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1690 <slepc4py/SLEPc/BV.pyx#L1690>`
    
        """
        ...
    @property
    def size(self) -> tuple[int, int]:
        """Basis vectors global size.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1695 <slepc4py/SLEPc/BV.pyx#L1695>`
    
        """
        ...
    @property
    def local_size(self) -> int:
        """Basis vectors local size.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1700 <slepc4py/SLEPc/BV.pyx#L1700>`
    
        """
        ...
    @property
    def column_size(self) -> int:
        """Basis vectors column size.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/BV.pyx:1705 <slepc4py/SLEPc/BV.pyx#L1705>`
    
        """
        ...

class DS(Object):
    """DS."""
    class Type:
        """DS type."""
        HEP: str = _def(str, 'HEP')  #: Object ``HEP`` of type :class:`str`
        NHEP: str = _def(str, 'NHEP')  #: Object ``NHEP`` of type :class:`str`
        GHEP: str = _def(str, 'GHEP')  #: Object ``GHEP`` of type :class:`str`
        GHIEP: str = _def(str, 'GHIEP')  #: Object ``GHIEP`` of type :class:`str`
        GNHEP: str = _def(str, 'GNHEP')  #: Object ``GNHEP`` of type :class:`str`
        NHEPTS: str = _def(str, 'NHEPTS')  #: Object ``NHEPTS`` of type :class:`str`
        SVD: str = _def(str, 'SVD')  #: Object ``SVD`` of type :class:`str`
        HSVD: str = _def(str, 'HSVD')  #: Object ``HSVD`` of type :class:`str`
        GSVD: str = _def(str, 'GSVD')  #: Object ``GSVD`` of type :class:`str`
        PEP: str = _def(str, 'PEP')  #: Object ``PEP`` of type :class:`str`
        NEP: str = _def(str, 'NEP')  #: Object ``NEP`` of type :class:`str`
    class StateType:
        """DS state types.
        
        - `RAW`:          Not processed yet.
        - `INTERMEDIATE`: Reduced to Hessenberg or tridiagonal form (or equivalent).
        - `CONDENSED`:    Reduced to Schur or diagonal form (or equivalent).
        - `TRUNCATED`:    Condensed form truncated to a smaller size.
        
        """
        RAW: int = _def(int, 'RAW')  #: Constant ``RAW`` of type :class:`int`
        INTERMEDIATE: int = _def(int, 'INTERMEDIATE')  #: Constant ``INTERMEDIATE`` of type :class:`int`
        CONDENSED: int = _def(int, 'CONDENSED')  #: Constant ``CONDENSED`` of type :class:`int`
        TRUNCATED: int = _def(int, 'TRUNCATED')  #: Constant ``TRUNCATED`` of type :class:`int`
    class MatType:
        """To refer to one of the matrices stored internally in DS.
        
        - `A`:  first matrix of eigenproblem/singular value problem.
        - `B`:  second matrix of a generalized eigenproblem.
        - `C`:  third matrix of a quadratic eigenproblem.
        - `T`:  tridiagonal matrix.
        - `D`:  diagonal matrix.
        - `Q`:  orthogonal matrix of (right) Schur vectors.
        - `Z`:  orthogonal matrix of left Schur vectors.
        - `X`:  right eigenvectors.
        - `Y`:  left eigenvectors.
        - `U`:  left singular vectors.
        - `V`:  right singular vectors.
        - `W`:  workspace matrix.
        
        """
        A: int = _def(int, 'A')  #: Constant ``A`` of type :class:`int`
        B: int = _def(int, 'B')  #: Constant ``B`` of type :class:`int`
        C: int = _def(int, 'C')  #: Constant ``C`` of type :class:`int`
        T: int = _def(int, 'T')  #: Constant ``T`` of type :class:`int`
        D: int = _def(int, 'D')  #: Constant ``D`` of type :class:`int`
        Q: int = _def(int, 'Q')  #: Constant ``Q`` of type :class:`int`
        Z: int = _def(int, 'Z')  #: Constant ``Z`` of type :class:`int`
        X: int = _def(int, 'X')  #: Constant ``X`` of type :class:`int`
        Y: int = _def(int, 'Y')  #: Constant ``Y`` of type :class:`int`
        U: int = _def(int, 'U')  #: Constant ``U`` of type :class:`int`
        V: int = _def(int, 'V')  #: Constant ``V`` of type :class:`int`
        W: int = _def(int, 'W')  #: Constant ``W`` of type :class:`int`
    class ParallelType:
        """DS parallel types.
        
        - `REDUNDANT`:    Every process performs the computation redundantly.
        - `SYNCHRONIZED`: The first process sends the result to the rest.
        - `DISTRIBUTED`:  Used in some cases to distribute the computation among
                          processes.
        
        """
        REDUNDANT: int = _def(int, 'REDUNDANT')  #: Constant ``REDUNDANT`` of type :class:`int`
        SYNCHRONIZED: int = _def(int, 'SYNCHRONIZED')  #: Constant ``SYNCHRONIZED`` of type :class:`int`
        DISTRIBUTED: int = _def(int, 'DISTRIBUTED')  #: Constant ``DISTRIBUTED`` of type :class:`int`
    def view(self, viewer: Viewer | None = None) -> None:
        """Print the DS data structure.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:89 <slepc4py/SLEPc/DS.pyx#L89>`
    
        """
        ...
    def destroy(self) -> Self:
        """Destroy the DS object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:104 <slepc4py/SLEPc/DS.pyx#L104>`
    
        """
        ...
    def reset(self) -> None:
        """Reset the DS object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:114 <slepc4py/SLEPc/DS.pyx#L114>`
    
        """
        ...
    def create(self, comm: Comm | None = None) -> Self:
        """Create the DS object.
    
        Collective.
    
        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all processes.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:122 <slepc4py/SLEPc/DS.pyx#L122>`
    
        """
        ...
    def setType(self, ds_type: Type | str) -> None:
        """Set the type for the DS object.
    
        Logically collective.
    
        Parameters
        ----------
        ds_type
            The direct solver type to be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:139 <slepc4py/SLEPc/DS.pyx#L139>`
    
        """
        ...
    def getType(self) -> str:
        """Get the DS type of this object.
    
        Not collective.
    
        Returns
        -------
        str
            The direct solver type currently being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:154 <slepc4py/SLEPc/DS.pyx#L154>`
    
        """
        ...
    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all DS options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all DS option requests.
    
        Notes
        -----
        A hyphen (``-``) must NOT be given at the beginning of the
        prefix name.  The first character of all runtime options is
        AUTOMATICALLY the hyphen.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:169 <slepc4py/SLEPc/DS.pyx#L169>`
    
        """
        ...
    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all DS options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all DS option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:190 <slepc4py/SLEPc/DS.pyx#L190>`
    
        """
        ...
    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all DS options in the database.
    
        Not collective.
    
        Returns
        -------
        str
            The prefix string set for this DS object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:205 <slepc4py/SLEPc/DS.pyx#L205>`
    
        """
        ...
    def setFromOptions(self) -> None:
        """Set DS options from the options database.
    
        Collective.
    
        Notes
        -----
        To see all options, run your program with the ``-help``
        option.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:220 <slepc4py/SLEPc/DS.pyx#L220>`
    
        """
        ...
    def duplicate(self) -> DS:
        """Duplicate the DS object with the same type and dimensions.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:233 <slepc4py/SLEPc/DS.pyx#L233>`
    
        """
        ...
    def allocate(self, ld: int) -> None:
        """Allocate memory for internal storage or matrices in DS.
    
        Logically collective.
    
        Parameters
        ----------
        ld
            Leading dimension (maximum allowed dimension for the
            matrices, including the extra row if present).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:245 <slepc4py/SLEPc/DS.pyx#L245>`
    
        """
        ...
    def getLeadingDimension(self) -> int:
        """Get the leading dimension of the allocated matrices.
    
        Not collective.
    
        Returns
        -------
        int
            Leading dimension (maximum allowed dimension for the matrices).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:260 <slepc4py/SLEPc/DS.pyx#L260>`
    
        """
        ...
    def setState(self, state: StateType) -> None:
        """Set the state of the DS object.
    
        Logically collective.
    
        Parameters
        ----------
        state
            The new state.
    
        Notes
        -----
        The state indicates that the dense system is in an initial
        state (raw), in an intermediate state (such as tridiagonal,
        Hessenberg or Hessenberg-triangular), in a condensed state
        (such as diagonal, Schur or generalized Schur), or in a
        truncated state.
    
        This function is normally used to return to the raw state when
        the condensed structure is destroyed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:275 <slepc4py/SLEPc/DS.pyx#L275>`
    
        """
        ...
    def getState(self) -> StateType:
        """Get the current state.
    
        Not collective.
    
        Returns
        -------
        StateType
            The current state.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:300 <slepc4py/SLEPc/DS.pyx#L300>`
    
        """
        ...
    def setParallel(self, pmode: ParallelType) -> None:
        """Set the mode of operation in parallel runs.
    
        Logically collective.
    
        Parameters
        ----------
        pmode
            The parallel mode.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:315 <slepc4py/SLEPc/DS.pyx#L315>`
    
        """
        ...
    def getParallel(self) -> ParallelType:
        """Get the mode of operation in parallel runs.
    
        Not collective.
    
        Returns
        -------
        ParallelType
            The parallel mode.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:329 <slepc4py/SLEPc/DS.pyx#L329>`
    
        """
        ...
    def setDimensions(self, n: int | None = None, l: int | None = None, k: int | None = None) -> None:
        """Set the matrices sizes in the DS object.
    
        Logically collective.
    
        Parameters
        ----------
        n
            The new size.
        l
            Number of locked (inactive) leading columns.
        k
            Intermediate dimension (e.g., position of arrow).
    
        Notes
        -----
        The internal arrays are not reallocated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:344 <slepc4py/SLEPc/DS.pyx#L344>`
    
        """
        ...
    def getDimensions(self) -> tuple[int, int, int, int]:
        """Get the current dimensions.
    
        Not collective.
    
        Returns
        -------
        n: int
            The new size.
        l: int
            Number of locked (inactive) leading columns.
        k: int
            Intermediate dimension (e.g., position of arrow).
        t: int
            Truncated length.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:371 <slepc4py/SLEPc/DS.pyx#L371>`
    
        """
        ...
    def setBlockSize(self, bs: int) -> None:
        """Set the block size.
    
        Logically collective.
    
        Parameters
        ----------
        bs
            The block size.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:395 <slepc4py/SLEPc/DS.pyx#L395>`
    
        """
        ...
    def getBlockSize(self) -> int:
        """Get the block size.
    
        Not collective.
    
        Returns
        -------
        int
            The block size.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:409 <slepc4py/SLEPc/DS.pyx#L409>`
    
        """
        ...
    def setMethod(self, meth: int) -> None:
        """Set the method to be used to solve the problem.
    
        Logically collective.
    
        Parameters
        ----------
        meth
            An index identifying the method.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:424 <slepc4py/SLEPc/DS.pyx#L424>`
    
        """
        ...
    def getMethod(self) -> int:
        """Get the method currently used in the DS.
    
        Not collective.
    
        Returns
        -------
        int
            Identifier of the method.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:438 <slepc4py/SLEPc/DS.pyx#L438>`
    
        """
        ...
    def setCompact(self, comp: bool) -> None:
        """Set the matrices' compact storage flag.
    
        Logically collective.
    
        Parameters
        ----------
        comp
            True means compact storage.
    
        Notes
        -----
        Compact storage is used in some `DS` types such as
        `DS.Type.HEP` when the matrix is tridiagonal. This flag
        can be used to indicate whether the user provides the
        matrix entries via the compact form (the tridiagonal
        `DS.MatType.T`) or the non-compact one (`DS.MatType.A`).
    
        The default is ``False``.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:453 <slepc4py/SLEPc/DS.pyx#L453>`
    
        """
        ...
    def getCompact(self) -> bool:
        """Get the compact storage flag.
    
        Not collective.
    
        Returns
        -------
        bool
            The flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:477 <slepc4py/SLEPc/DS.pyx#L477>`
    
        """
        ...
    def setExtraRow(self, ext: bool) -> None:
        """Set a flag to indicate that the matrix has one extra row.
    
        Logically collective.
    
        Parameters
        ----------
        ext
            True if the matrix has extra row.
    
        Notes
        -----
        In Krylov methods it is useful that the matrix representing the direct
        solver has one extra row, i.e., has dimension :math:`(n+1) n`. If
        this flag is activated, all transformations applied to the right of the
        matrix also affect this additional row. In that case, :math:`(n+1)`
        must be less or equal than the leading dimension.
    
        The default is ``False``.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:492 <slepc4py/SLEPc/DS.pyx#L492>`
    
        """
        ...
    def getExtraRow(self) -> bool:
        """Get the extra row flag.
    
        Not collective.
    
        Returns
        -------
        bool
            The flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:516 <slepc4py/SLEPc/DS.pyx#L516>`
    
        """
        ...
    def setRefined(self, ref: bool) -> None:
        """Set a flag to indicate that refined vectors must be computed.
    
        Logically collective.
    
        Parameters
        ----------
        ref
            True if refined vectors must be used.
    
        Notes
        -----
        Normally the vectors returned in `DS.MatType.X` are eigenvectors of
        the projected matrix. With this flag activated, `vectors()` will return
        the right singular vector of the smallest singular value of matrix
        :math:`At - theta I`, where :math:`At` is the extended
        :math:`(n+1) times n` matrix and :math:`theta` is the Ritz value.
        This is used in the refined Ritz approximation.
    
        The default is ``False``.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:531 <slepc4py/SLEPc/DS.pyx#L531>`
    
        """
        ...
    def getRefined(self) -> bool:
        """Get the refined vectors flag.
    
        Not collective.
    
        Returns
        -------
        bool
            The flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:556 <slepc4py/SLEPc/DS.pyx#L556>`
    
        """
        ...
    def truncate(self, n: int, trim: bool = False) -> None:
        """Truncate the system represented in the DS object.
    
        Logically collective.
    
        Parameters
        ----------
        n
            The new size.
        trim
            A flag to indicate if the factorization must be trimmed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:571 <slepc4py/SLEPc/DS.pyx#L571>`
    
        """
        ...
    def updateExtraRow(self) -> None:
        """Ensure that the extra row gets up-to-date after a call to `DS.solve()`.
    
        Logically collective.
    
        Perform all necessary operations so that the extra row gets up-to-date
        after a call to `DS.solve()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:588 <slepc4py/SLEPc/DS.pyx#L588>`
    
        """
        ...
    def getMat(self, matname: MatType) -> petsc4py.PETSc.Mat:
        """Get the requested matrix as a sequential dense Mat object.
    
        Not collective.
    
        Parameters
        ----------
        matname
            The requested matrix.
    
        Returns
        -------
        petsc4py.PETSc.Mat
            The matrix.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:599 <slepc4py/SLEPc/DS.pyx#L599>`
    
        """
        ...
    def restoreMat(self, matname: MatType, mat: petsc4py.PETSc.Mat) -> None:
        """Restore the previously seized matrix.
    
        Not collective.
    
        Parameters
        ----------
        matname
            The selected matrix.
        mat
            The matrix previously obtained with `getMat()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:621 <slepc4py/SLEPc/DS.pyx#L621>`
    
        """
        ...
    def setIdentity(self, matname: MatType) -> None:
        """Set the identity on the active part of a matrix.
    
        Logically collective.
    
        Parameters
        ----------
        matname
            The requested matrix.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:638 <slepc4py/SLEPc/DS.pyx#L638>`
    
        """
        ...
    def cond(self) -> float:
        """Compute the inf-norm condition number of the first matrix.
    
        Logically collective.
    
        Returns
        -------
        float
            Condition number.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:654 <slepc4py/SLEPc/DS.pyx#L654>`
    
        """
        ...
    def solve(self) -> ArrayScalar:
        """Solve the problem.
    
        Logically collective.
    
        Returns
        -------
        ArrayScalar
            Eigenvalues or singular values.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:669 <slepc4py/SLEPc/DS.pyx#L669>`
    
        """
        ...
    def vectors(self, matname=MatType.X) -> None:
        """Compute vectors associated to the dense system such as eigenvectors.
    
        Logically collective.
    
        Parameters
        ----------
        matname: `DS.MatType` enumerate
           The matrix, used to indicate which vectors are required.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:693 <slepc4py/SLEPc/DS.pyx#L693>`
    
        """
        ...
    def setSVDDimensions(self, m: int) -> None:
        """Set the number of columns of a `DS` of type `SVD`.
    
        Logically collective.
    
        Parameters
        ----------
        m
            The number of columns.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:709 <slepc4py/SLEPc/DS.pyx#L709>`
    
        """
        ...
    def getSVDDimensions(self) -> int:
        """Get the number of columns of a `DS` of type `SVD`.
    
        Not collective.
    
        Returns
        -------
        int
            The number of columns.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:723 <slepc4py/SLEPc/DS.pyx#L723>`
    
        """
        ...
    def setHSVDDimensions(self, m: int) -> None:
        """Set the number of columns of a `DS` of type `HSVD`.
    
        Logically collective.
    
        Parameters
        ----------
        m
            The number of columns.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:738 <slepc4py/SLEPc/DS.pyx#L738>`
    
        """
        ...
    def getHSVDDimensions(self) -> int:
        """Get the number of columns of a `DS` of type `HSVD`.
    
        Not collective.
    
        Returns
        -------
        int
            The number of columns.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:752 <slepc4py/SLEPc/DS.pyx#L752>`
    
        """
        ...
    def setGSVDDimensions(self, m: int, p: int) -> None:
        """Set the number of columns and rows of a `DS` of type `GSVD`.
    
        Logically collective.
    
        Parameters
        ----------
        m
            The number of columns.
        p
            The number of rows for the second matrix.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:767 <slepc4py/SLEPc/DS.pyx#L767>`
    
        """
        ...
    def getGSVDDimensions(self) -> tuple[int, int]:
        """Get the number of columns and rows of a `DS` of type `GSVD`.
    
        Not collective.
    
        Returns
        -------
        m: int
            The number of columns.
        p: int
            The number of rows for the second matrix.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:784 <slepc4py/SLEPc/DS.pyx#L784>`
    
        """
        ...
    def setPEPDegree(self, deg: int) -> None:
        """Set the polynomial degree of a `DS` of type `PEP`.
    
        Logically collective.
    
        Parameters
        ----------
        deg
            The polynomial degree.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:802 <slepc4py/SLEPc/DS.pyx#L802>`
    
        """
        ...
    def getPEPDegree(self) -> int:
        """Get the polynomial degree of a `DS` of type `PEP`.
    
        Not collective.
    
        Returns
        -------
        int
            The polynomial degree.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:816 <slepc4py/SLEPc/DS.pyx#L816>`
    
        """
        ...
    def setPEPCoefficients(self, pbc: Sequence[float]) -> None:
        """Set the polynomial basis coefficients of a `DS` of type `PEP`.
    
        Logically collective.
    
        Parameters
        ----------
        pbc
            Coefficients.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:831 <slepc4py/SLEPc/DS.pyx#L831>`
    
        """
        ...
    def getPEPCoefficients(self) -> ArrayReal:
        """Get the polynomial basis coefficients of a `DS` of type `PEP`.
    
        Not collective.
    
        Returns
        -------
        ArrayReal
            Coefficients.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:847 <slepc4py/SLEPc/DS.pyx#L847>`
    
        """
        ...
    @property
    def state(self) -> DSStateType:
        """The state of the DS object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:871 <slepc4py/SLEPc/DS.pyx#L871>`
    
        """
        ...
    @property
    def parallel(self) -> DSParallelType:
        """The mode of operation in parallel runs.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:878 <slepc4py/SLEPc/DS.pyx#L878>`
    
        """
        ...
    @property
    def block_size(self) -> int:
        """The block size.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:885 <slepc4py/SLEPc/DS.pyx#L885>`
    
        """
        ...
    @property
    def method(self) -> int:
        """The method to be used to solve the problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:892 <slepc4py/SLEPc/DS.pyx#L892>`
    
        """
        ...
    @property
    def compact(self) -> bool:
        """Compact storage of matrices.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:899 <slepc4py/SLEPc/DS.pyx#L899>`
    
        """
        ...
    @property
    def extra_row(self) -> bool:
        """If the matrix has one extra row.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:906 <slepc4py/SLEPc/DS.pyx#L906>`
    
        """
        ...
    @property
    def refined(self) -> bool:
        """If refined vectors must be computed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/DS.pyx:913 <slepc4py/SLEPc/DS.pyx#L913>`
    
        """
        ...

class FN(Object):
    """FN."""
    class Type:
        """FN type."""
        COMBINE: str = _def(str, 'COMBINE')  #: Object ``COMBINE`` of type :class:`str`
        RATIONAL: str = _def(str, 'RATIONAL')  #: Object ``RATIONAL`` of type :class:`str`
        EXP: str = _def(str, 'EXP')  #: Object ``EXP`` of type :class:`str`
        LOG: str = _def(str, 'LOG')  #: Object ``LOG`` of type :class:`str`
        PHI: str = _def(str, 'PHI')  #: Object ``PHI`` of type :class:`str`
        SQRT: str = _def(str, 'SQRT')  #: Object ``SQRT`` of type :class:`str`
        INVSQRT: str = _def(str, 'INVSQRT')  #: Object ``INVSQRT`` of type :class:`str`
    class CombineType:
        """FN type of combination of child functions.
        
        - `ADD`:       Addition         f(x) = f1(x)+f2(x)
        - `MULTIPLY`:  Multiplication   f(x) = f1(x)*f2(x)
        - `DIVIDE`:    Division         f(x) = f1(x)/f2(x)
        - `COMPOSE`:   Composition      f(x) = f2(f1(x))
        
        """
        ADD: int = _def(int, 'ADD')  #: Constant ``ADD`` of type :class:`int`
        MULTIPLY: int = _def(int, 'MULTIPLY')  #: Constant ``MULTIPLY`` of type :class:`int`
        DIVIDE: int = _def(int, 'DIVIDE')  #: Constant ``DIVIDE`` of type :class:`int`
        COMPOSE: int = _def(int, 'COMPOSE')  #: Constant ``COMPOSE`` of type :class:`int`
    class ParallelType:
        """FN parallel types.
        
        - `REDUNDANT`:    Every process performs the computation redundantly.
        - `SYNCHRONIZED`: The first process sends the result to the rest.
        
        """
        REDUNDANT: int = _def(int, 'REDUNDANT')  #: Constant ``REDUNDANT`` of type :class:`int`
        SYNCHRONIZED: int = _def(int, 'SYNCHRONIZED')  #: Constant ``SYNCHRONIZED`` of type :class:`int`
    def view(self, viewer: Viewer | None = None) -> None:
        """Print the FN data structure.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:119 <slepc4py/SLEPc/FN.pyx#L119>`
    
        """
        ...
    def destroy(self) -> Self:
        """Destroy the FN object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:134 <slepc4py/SLEPc/FN.pyx#L134>`
    
        """
        ...
    def create(self, comm: Comm | None = None) -> Self:
        """Create the FN object.
    
        Collective.
    
        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all processes.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:144 <slepc4py/SLEPc/FN.pyx#L144>`
    
        """
        ...
    def setType(self, fn_type: Type | str) -> None:
        """Set the type for the FN object.
    
        Logically collective.
    
        Parameters
        ----------
        fn_type
            The inner product type to be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:161 <slepc4py/SLEPc/FN.pyx#L161>`
    
        """
        ...
    def getType(self) -> str:
        """Get the FN type of this object.
    
        Not collective.
    
        Returns
        -------
        str
            The inner product type currently being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:176 <slepc4py/SLEPc/FN.pyx#L176>`
    
        """
        ...
    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all FN options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all FN option requests.
    
        Notes
        -----
        A hyphen (``-``) must NOT be given at the beginning of the
        prefix name.  The first character of all runtime options is
        AUTOMATICALLY the hyphen.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:191 <slepc4py/SLEPc/FN.pyx#L191>`
    
        """
        ...
    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all FN options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all FN option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:212 <slepc4py/SLEPc/FN.pyx#L212>`
    
        """
        ...
    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all FN options in the database.
    
        Not collective.
    
        Returns
        -------
        str
            The prefix string set for this FN object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:227 <slepc4py/SLEPc/FN.pyx#L227>`
    
        """
        ...
    def setFromOptions(self) -> None:
        """Set FN options from the options database.
    
        Collective.
    
        Notes
        -----
        To see all options, run your program with the ``-help``
        option.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:242 <slepc4py/SLEPc/FN.pyx#L242>`
    
        """
        ...
    def duplicate(self, comm: Comm | None = None) -> FN:
        """Duplicate the FN object copying all parameters.
    
        Collective.
    
        Duplicate the FN object copying all parameters, possibly with a
        different communicator.
    
        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to the
            object's communicator.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:255 <slepc4py/SLEPc/FN.pyx#L255>`
    
        """
        ...
    def evaluateFunction(self, x: Scalar) -> Scalar:
        """Compute the value of the function f(x) for a given x.
    
        Not collective.
    
        Parameters
        ----------
        x
            Value where the function must be evaluated.
    
        Returns
        -------
        Scalar
            The result of f(x).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:277 <slepc4py/SLEPc/FN.pyx#L277>`
    
        """
        ...
    def evaluateDerivative(self, x: Scalar) -> Scalar:
        """Compute the value of the derivative :math:`f'(x)` for a given x.
    
        Not collective.
    
        Parameters
        ----------
        x
            Value where the derivative must be evaluated.
    
        Returns
        -------
        Scalar
            The result of :math:`f'(x)`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:298 <slepc4py/SLEPc/FN.pyx#L298>`
    
        """
        ...
    def evaluateFunctionMat(self, A: petsc4py.PETSc.Mat, B: petsc4py.PETSc.Mat | None = None) -> petsc4py.PETSc.Mat:
        """Compute the value of the function :math:`f(A)` for a given matrix A.
    
        Logically collective.
    
        Parameters
        ----------
        A
            Matrix on which the function must be evaluated.
        B
            Placeholder for the result.
    
        Returns
        -------
        petsc4py.PETSc.Mat
            The result of :math:`f(A)`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:319 <slepc4py/SLEPc/FN.pyx#L319>`
    
        """
        ...
    def evaluateFunctionMatVec(self, A: petsc4py.PETSc.Mat, v: petsc4py.PETSc.Vec | None = None) -> petsc4py.PETSc.Vec:
        """Compute the first column of the matrix f(A) for a given matrix A.
    
        Logically collective.
    
        Parameters
        ----------
        A
            Matrix on which the function must be evaluated.
    
        Returns
        -------
        petsc4py.PETSc.Vec
            The first column of the result f(A).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:341 <slepc4py/SLEPc/FN.pyx#L341>`
    
        """
        ...
    def setScale(self, alpha: Scalar | None = None, beta: Scalar | None = None) -> None:
        """Set the scaling parameters that define the matematical function.
    
        Logically collective.
    
        Parameters
        ----------
        alpha
            Inner scaling (argument), default is 1.0.
        beta
            Outer scaling (result), default is 1.0.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:361 <slepc4py/SLEPc/FN.pyx#L361>`
    
        """
        ...
    def getScale(self) -> tuple[Scalar, Scalar]:
        """Get the scaling parameters that define the matematical function.
    
        Not collective.
    
        Returns
        -------
        alpha: Scalar
            Inner scaling (argument).
        beta: Scalar
            Outer scaling (result).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:380 <slepc4py/SLEPc/FN.pyx#L380>`
    
        """
        ...
    def setMethod(self, meth: int) -> None:
        """Set the method to be used to evaluate functions of matrices.
    
        Logically collective.
    
        Parameters
        ----------
        meth
            An index identifying the method.
    
        Notes
        -----
        In some `FN` types there are more than one algorithms available
        for computing matrix functions. In that case, this function allows
        choosing the wanted method.
    
        If ``meth`` is currently set to 0 and the input argument of
        `FN.evaluateFunctionMat()` is a symmetric/Hermitian matrix, then
        the computation is done via the eigendecomposition, rather than
        with the general algorithm.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:397 <slepc4py/SLEPc/FN.pyx#L397>`
    
        """
        ...
    def getMethod(self) -> int:
        """Get the method currently used for matrix functions.
    
        Not collective.
    
        Returns
        -------
        int
            An index identifying the method.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:422 <slepc4py/SLEPc/FN.pyx#L422>`
    
        """
        ...
    def setParallel(self, pmode: ParallelType) -> None:
        """Set the mode of operation in parallel runs.
    
        Logically collective.
    
        Parameters
        ----------
        pmode
            The parallel mode.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:437 <slepc4py/SLEPc/FN.pyx#L437>`
    
        """
        ...
    def getParallel(self) -> ParallelType:
        """Get the mode of operation in parallel runs.
    
        Not collective.
    
        Returns
        -------
        ParallelType
            The parallel mode.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:451 <slepc4py/SLEPc/FN.pyx#L451>`
    
        """
        ...
    def setRationalNumerator(self, alpha: Sequence[Scalar]) -> None:
        """Set the coefficients of the numerator of the rational function.
    
        Logically collective.
    
        Parameters
        ----------
        alpha
            Coefficients.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:468 <slepc4py/SLEPc/FN.pyx#L468>`
    
        """
        ...
    def getRationalNumerator(self) -> ArrayScalar:
        """Get the coefficients of the numerator of the rational function.
    
        Not collective.
    
        Returns
        -------
        ArrayScalar
            Coefficients.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:484 <slepc4py/SLEPc/FN.pyx#L484>`
    
        """
        ...
    def setRationalDenominator(self, alpha: Sequence[Scalar]) -> None:
        """Set the coefficients of the denominator of the rational function.
    
        Logically collective.
    
        Parameters
        ----------
        alpha
            Coefficients.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:505 <slepc4py/SLEPc/FN.pyx#L505>`
    
        """
        ...
    def getRationalDenominator(self) -> ArrayScalar:
        """Get the coefficients of the denominator of the rational function.
    
        Not collective.
    
        Returns
        -------
        ArrayScalar
            Coefficients.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:521 <slepc4py/SLEPc/FN.pyx#L521>`
    
        """
        ...
    def setCombineChildren(self, comb: CombineType, f1: FN, f2: FN) -> None:
        """Set the two child functions that constitute this combined function.
    
        Logically collective.
    
        Set the two child functions that constitute this combined function,
        and the way they must be combined.
    
        Parameters
        ----------
        comb
            How to combine the functions (addition, multiplication, division,
            composition).
        f1
            First function.
        f2
            Second function.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:542 <slepc4py/SLEPc/FN.pyx#L542>`
    
        """
        ...
    def getCombineChildren(self) -> tuple[CombineType, FN, FN]:
        """Get the two child functions that constitute this combined function.
    
        Not collective.
    
        Get the two child functions that constitute this combined
        function, and the way they must be combined.
    
        Returns
        -------
        comb: CombineType
            How to combine the functions (addition, multiplication, division,
            composition).
        f1: FN
            First function.
        f2: FN
            Second function.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:564 <slepc4py/SLEPc/FN.pyx#L564>`
    
        """
        ...
    def setPhiIndex(self, k: int) -> None:
        """Set the index of the phi-function.
    
        Logically collective.
    
        Parameters
        ----------
        k
            The index.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:591 <slepc4py/SLEPc/FN.pyx#L591>`
    
        """
        ...
    def getPhiIndex(self) -> int:
        """Get the index of the phi-function.
    
        Not collective.
    
        Returns
        -------
        int
            The index.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:605 <slepc4py/SLEPc/FN.pyx#L605>`
    
        """
        ...
    @property
    def method(self) -> int:
        """The method to be used to evaluate functions of matrices.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:622 <slepc4py/SLEPc/FN.pyx#L622>`
    
        """
        ...
    @property
    def parallel(self) -> FNParallelType:
        """The mode of operation in parallel runs.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/FN.pyx:629 <slepc4py/SLEPc/FN.pyx#L629>`
    
        """
        ...

class RG(Object):
    """RG."""
    class Type:
        """RG type."""
        INTERVAL: str = _def(str, 'INTERVAL')  #: Object ``INTERVAL`` of type :class:`str`
        POLYGON: str = _def(str, 'POLYGON')  #: Object ``POLYGON`` of type :class:`str`
        ELLIPSE: str = _def(str, 'ELLIPSE')  #: Object ``ELLIPSE`` of type :class:`str`
        RING: str = _def(str, 'RING')  #: Object ``RING`` of type :class:`str`
    class QuadRule:
        """RG quadrature rule for contour integral methods.
        
        - `TRAPEZOIDAL`: Trapezoidal rule.
        - `CHEBYSHEV`:   Chebyshev points.
        
        """
        TRAPEZOIDAL: int = _def(int, 'TRAPEZOIDAL')  #: Constant ``TRAPEZOIDAL`` of type :class:`int`
        CHEBYSHEV: int = _def(int, 'CHEBYSHEV')  #: Constant ``CHEBYSHEV`` of type :class:`int`
    def view(self, viewer: Viewer | None = None) -> None:
        """Print the RG data structure.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:33 <slepc4py/SLEPc/RG.pyx#L33>`
    
        """
        ...
    def destroy(self) -> Self:
        """Destroy the RG object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:48 <slepc4py/SLEPc/RG.pyx#L48>`
    
        """
        ...
    def create(self, comm: Comm | None = None) -> Self:
        """Create the RG object.
    
        Collective.
    
        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all processes.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:58 <slepc4py/SLEPc/RG.pyx#L58>`
    
        """
        ...
    def setType(self, rg_type: Type | str) -> None:
        """Set the type for the RG object.
    
        Logically collective.
    
        Parameters
        ----------
        rg_type
            The inner product type to be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:75 <slepc4py/SLEPc/RG.pyx#L75>`
    
        """
        ...
    def getType(self) -> str:
        """Get the RG type of this object.
    
        Not collective.
    
        Returns
        -------
        str
            The inner product type currently being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:90 <slepc4py/SLEPc/RG.pyx#L90>`
    
        """
        ...
    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all RG options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all RG option requests.
    
        Notes
        -----
        A hyphen (``-``) must NOT be given at the beginning of the
        prefix name.  The first character of all runtime options is
        AUTOMATICALLY the hyphen.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:105 <slepc4py/SLEPc/RG.pyx#L105>`
    
        """
        ...
    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all RG options in the database.
    
        Not collective.
    
        Returns
        -------
        str
            The prefix string set for this RG object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:126 <slepc4py/SLEPc/RG.pyx#L126>`
    
        """
        ...
    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all RG options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all RG option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:141 <slepc4py/SLEPc/RG.pyx#L141>`
    
        """
        ...
    def setFromOptions(self) -> None:
        """Set RG options from the options database.
    
        Collective.
    
        Notes
        -----
        To see all options, run your program with the ``-help``
        option.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:156 <slepc4py/SLEPc/RG.pyx#L156>`
    
        """
        ...
    def isTrivial(self) -> bool:
        """Tell whether it is the trivial region (whole complex plane).
    
        Not collective.
    
        Returns
        -------
        bool
            True if the region is equal to the whole complex plane, e.g.,
            an interval region with all four endpoints unbounded or an
            ellipse with infinite radius.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:171 <slepc4py/SLEPc/RG.pyx#L171>`
    
        """
        ...
    def isAxisymmetric(self, vertical: bool = False) -> bool:
        """Determine if the region is symmetric wrt. the real or imaginary axis.
    
        Not collective.
    
        Determine if the region is symmetric with respect to the real or
        imaginary axis.
    
        Parameters
        ----------
        vertical
            True if symmetry must be checked against the vertical axis.
    
        Returns
        -------
        bool
            True if the region is axisymmetric.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:188 <slepc4py/SLEPc/RG.pyx#L188>`
    
        """
        ...
    def getComplement(self) -> bool:
        """Get the flag indicating whether the region is complemented or not.
    
        Not collective.
    
        Returns
        -------
        bool
            Whether the region is complemented or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:212 <slepc4py/SLEPc/RG.pyx#L212>`
    
        """
        ...
    def setComplement(self, comp: bool = True) -> None:
        """Set a flag to indicate that the region is the complement of the specified one.
    
        Logically collective.
    
        Parameters
        ----------
        comp
            Activate/deactivate the complementation of the region.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:227 <slepc4py/SLEPc/RG.pyx#L227>`
    
        """
        ...
    def setScale(self, sfactor: float = None) -> None:
        """Set the scaling factor to be used.
    
        Logically collective.
    
        Set the scaling factor to be used when checking that a
        point is inside the region and when computing the contour.
    
        Parameters
        ----------
        sfactor
            The scaling factor (default=1).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:241 <slepc4py/SLEPc/RG.pyx#L241>`
    
        """
        ...
    def getScale(self) -> float:
        """Get the scaling factor.
    
        Not collective.
    
        Returns
        -------
        float
            The scaling factor.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:259 <slepc4py/SLEPc/RG.pyx#L259>`
    
        """
        ...
    def checkInside(self, a: Sequence[complex]) -> ArrayInt:
        """Determine if a set of given points are inside the region or not.
    
        Not collective.
    
        Parameters
        ----------
        a
            The coordinates of the points.
    
        Returns
        -------
        ArrayInt
            Computed result for each point (1=inside, 0=on the contour, -1=outside).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:274 <slepc4py/SLEPc/RG.pyx#L274>`
    
        """
        ...
    def computeContour(self, n: int) -> list[complex]:
        """Compute the coordinates of several points of the contour on the region.
    
        Not collective.
    
        Compute the coordinates of several points lying on the contour
        of the region.
    
        Parameters
        ----------
        n
            The number of points to compute.
    
        Returns
        -------
        list of complex
            Computed points.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:306 <slepc4py/SLEPc/RG.pyx#L306>`
    
        """
        ...
    def computeBoundingBox(self) -> tuple[float, float, float, float]:
        """Endpoints of a rectangle in the complex plane containing the region.
    
        Not collective.
    
        Determine the endpoints of a rectangle in the complex plane that
        contains the region.
    
        Returns
        -------
        a: float
            The left endpoint of the bounding box in the real axis
        b: float
            The right endpoint of the bounding box in the real axis
        c: float
            The left endpoint of the bounding box in the imaginary axis
        d: float
            The right endpoint of the bounding box in the imaginary axis
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:337 <slepc4py/SLEPc/RG.pyx#L337>`
    
        """
        ...
    def canUseConjugates(self, realmats: bool = True) -> bool:
        """Half of integration points can be avoided (use their conjugates).
    
        Not collective.
    
        Used in contour integral methods to determine whether half of
        integration points can be avoided (use their conjugates).
    
        Parameters
        ----------
        realmats
            True if the problem matrices are real.
    
        Returns
        -------
        bool
            Whether it is possible to use conjugates.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:361 <slepc4py/SLEPc/RG.pyx#L361>`
    
        """
        ...
    def computeQuadrature(self, quad: QuadRule, n: int) -> tuple[ArrayScalar, ArrayScalar, ArrayScalar]:
        """Compute the values of the parameters used in a quadrature rule.
    
        Not collective.
    
        Compute the values of the parameters used in a quadrature rule for a
        contour integral around the boundary of the region.
    
        Parameters
        ----------
        quad
            The type of quadrature.
        n
            The number of quadrature points to compute.
    
        Returns
        -------
        z: ArrayScalar
            Quadrature points.
        zn: ArrayScalar
            Normalized quadrature points.
        w: ArrayScalar
            Quadrature weights.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:385 <slepc4py/SLEPc/RG.pyx#L385>`
    
        """
        ...
    def setEllipseParameters(self, center: Scalar, radius: float, vscale: float | None = None) -> None:
        """Set the parameters defining the ellipse region.
    
        Logically collective.
    
        Parameters
        ----------
        center
            The center.
        radius
            The radius.
        vscale
            The vertical scale.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:421 <slepc4py/SLEPc/RG.pyx#L421>`
    
        """
        ...
    def getEllipseParameters(self) -> tuple[Scalar, float, float]:
        """Get the parameters that define the ellipse region.
    
        Not collective.
    
        Returns
        -------
        center: Scalar
            The center.
        radius: float
            The radius.
        vscale: float
            The vertical scale.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:442 <slepc4py/SLEPc/RG.pyx#L442>`
    
        """
        ...
    def setIntervalEndpoints(self, a: float, b: float, c: float, d: float) -> None:
        """Set the parameters defining the interval region.
    
        Logically collective.
    
        Parameters
        ----------
        a
            The left endpoint in the real axis.
        b
            The right endpoint in the real axis.
        c
            The upper endpoint in the imaginary axis.
        d
            The lower endpoint in the imaginary axis.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:463 <slepc4py/SLEPc/RG.pyx#L463>`
    
        """
        ...
    def getIntervalEndpoints(self) -> tuple[float, float, float, float]:
        """Get the parameters that define the interval region.
    
        Not collective.
    
        Returns
        -------
        a: float
            The left endpoint in the real axis.
        b: float
            The right endpoint in the real axis.
        c: float
            The upper endpoint in the imaginary axis.
        d: float
            The lower endpoint in the imaginary axis.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:486 <slepc4py/SLEPc/RG.pyx#L486>`
    
        """
        ...
    def setPolygonVertices(self, v: Sequence[float] | Sequence[Scalar]) -> None:
        """Set the vertices that define the polygon region.
    
        Logically collective.
    
        Parameters
        ----------
        v
            The vertices.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:510 <slepc4py/SLEPc/RG.pyx#L510>`
    
        """
        ...
    def getPolygonVertices(self) -> ArrayComplex:
        """Get the parameters that define the interval region.
    
        Not collective.
    
        Returns
        -------
        ArrayComplex
            The vertices.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:534 <slepc4py/SLEPc/RG.pyx#L534>`
    
        """
        ...
    def setRingParameters(self, center: Scalar, radius: float, vscale: float, start_ang: float, end_ang: float, width: float) -> None:
        """Set the parameters defining the ring region.
    
        Logically collective.
    
        Parameters
        ----------
        center
            The center.
        radius
            The radius.
        vscale
            The vertical scale.
        start_ang
            The right-hand side angle.
        end_ang
            The left-hand side angle.
        width
            The width of the ring.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:556 <slepc4py/SLEPc/RG.pyx#L556>`
    
        """
        ...
    def getRingParameters(self) -> tuple[Scalar, float, float, float, float, float]:
        """Get the parameters that define the ring region.
    
        Not collective.
    
        Returns
        -------
        center: Scalar
            The center.
        radius: float
            The radius.
        vscale: float
            The vertical scale.
        start_ang: float
            The right-hand side angle.
        end_ang: float
            The left-hand side angle.
        width: float
            The width of the ring.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:593 <slepc4py/SLEPc/RG.pyx#L593>`
    
        """
        ...
    @property
    def complement(self) -> bool:
        """If the region is the complement of the specified one.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:625 <slepc4py/SLEPc/RG.pyx#L625>`
    
        """
        ...
    @property
    def scale(self) -> float:
        """The scaling factor to be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/RG.pyx:632 <slepc4py/SLEPc/RG.pyx#L632>`
    
        """
        ...

class EPS(Object):
    """EPS."""
    class Type:
        """EPS type.
        
        Native sparse eigensolvers.
        
        - `POWER`:        Power Iteration, Inverse Iteration, RQI.
        - `SUBSPACE`:     Subspace Iteration.
        - `ARNOLDI`:      Arnoldi.
        - `LANCZOS`:      Lanczos.
        - `KRYLOVSCHUR`:  Krylov-Schur (default).
        - `GD`:           Generalized Davidson.
        - `JD`:           Jacobi-Davidson.
        - `RQCG`:         Rayleigh Quotient Conjugate Gradient.
        - `LOBPCG`:       Locally Optimal Block Preconditioned Conjugate Gradient.
        - `CISS`:         Contour Integral Spectrum Slicing.
        - `LYAPII`:       Lyapunov inverse iteration.
        - `LAPACK`:       Wrappers to dense eigensolvers in Lapack.
        
        Wrappers to external eigensolvers
        (should be enabled during installation of SLEPc)
        
        - `ARPACK`:
        - `BLOPEX`:
        - `PRIMME`:
        - `FEAST`:
        - `SCALAPACK`:
        - `ELPA`:
        - `ELEMENTAL`:
        - `EVSL`:
        - `CHASE`:
        
        """
        POWER: str = _def(str, 'POWER')  #: Object ``POWER`` of type :class:`str`
        SUBSPACE: str = _def(str, 'SUBSPACE')  #: Object ``SUBSPACE`` of type :class:`str`
        ARNOLDI: str = _def(str, 'ARNOLDI')  #: Object ``ARNOLDI`` of type :class:`str`
        LANCZOS: str = _def(str, 'LANCZOS')  #: Object ``LANCZOS`` of type :class:`str`
        KRYLOVSCHUR: str = _def(str, 'KRYLOVSCHUR')  #: Object ``KRYLOVSCHUR`` of type :class:`str`
        GD: str = _def(str, 'GD')  #: Object ``GD`` of type :class:`str`
        JD: str = _def(str, 'JD')  #: Object ``JD`` of type :class:`str`
        RQCG: str = _def(str, 'RQCG')  #: Object ``RQCG`` of type :class:`str`
        LOBPCG: str = _def(str, 'LOBPCG')  #: Object ``LOBPCG`` of type :class:`str`
        CISS: str = _def(str, 'CISS')  #: Object ``CISS`` of type :class:`str`
        LYAPII: str = _def(str, 'LYAPII')  #: Object ``LYAPII`` of type :class:`str`
        LAPACK: str = _def(str, 'LAPACK')  #: Object ``LAPACK`` of type :class:`str`
        ARPACK: str = _def(str, 'ARPACK')  #: Object ``ARPACK`` of type :class:`str`
        BLOPEX: str = _def(str, 'BLOPEX')  #: Object ``BLOPEX`` of type :class:`str`
        PRIMME: str = _def(str, 'PRIMME')  #: Object ``PRIMME`` of type :class:`str`
        FEAST: str = _def(str, 'FEAST')  #: Object ``FEAST`` of type :class:`str`
        SCALAPACK: str = _def(str, 'SCALAPACK')  #: Object ``SCALAPACK`` of type :class:`str`
        ELPA: str = _def(str, 'ELPA')  #: Object ``ELPA`` of type :class:`str`
        ELEMENTAL: str = _def(str, 'ELEMENTAL')  #: Object ``ELEMENTAL`` of type :class:`str`
        EVSL: str = _def(str, 'EVSL')  #: Object ``EVSL`` of type :class:`str`
        CHASE: str = _def(str, 'CHASE')  #: Object ``CHASE`` of type :class:`str`
    class ProblemType:
        """EPS problem type.
        
        - `HEP`:    Hermitian eigenproblem.
        - `NHEP`:   Non-Hermitian eigenproblem.
        - `GHEP`:   Generalized Hermitian eigenproblem.
        - `GNHEP`:  Generalized Non-Hermitian eigenproblem.
        - `PGNHEP`: Generalized Non-Hermitian eigenproblem
                    with positive definite :math:`B`.
        - `GHIEP`:  Generalized Hermitian-indefinite eigenproblem.
        - `BSE`:    Structured Bethe-Salpeter eigenproblem.
        - `HAMILT`: Hamiltonian eigenproblem.
        
        """
        HEP: int = _def(int, 'HEP')  #: Constant ``HEP`` of type :class:`int`
        NHEP: int = _def(int, 'NHEP')  #: Constant ``NHEP`` of type :class:`int`
        GHEP: int = _def(int, 'GHEP')  #: Constant ``GHEP`` of type :class:`int`
        GNHEP: int = _def(int, 'GNHEP')  #: Constant ``GNHEP`` of type :class:`int`
        PGNHEP: int = _def(int, 'PGNHEP')  #: Constant ``PGNHEP`` of type :class:`int`
        GHIEP: int = _def(int, 'GHIEP')  #: Constant ``GHIEP`` of type :class:`int`
        BSE: int = _def(int, 'BSE')  #: Constant ``BSE`` of type :class:`int`
        HAMILT: int = _def(int, 'HAMILT')  #: Constant ``HAMILT`` of type :class:`int`
    class Extraction:
        """EPS extraction technique.
        
        - `RITZ`:              Standard Rayleigh-Ritz extraction.
        - `HARMONIC`:          Harmonic extraction.
        - `HARMONIC_RELATIVE`: Harmonic extraction relative to the eigenvalue.
        - `HARMONIC_RIGHT`:    Harmonic extraction for rightmost eigenvalues.
        - `HARMONIC_LARGEST`:  Harmonic extraction for largest magnitude (without
                               target).
        - `REFINED`:           Refined extraction.
        - `REFINED_HARMONIC`:  Refined harmonic extraction.
        
        """
        RITZ: int = _def(int, 'RITZ')  #: Constant ``RITZ`` of type :class:`int`
        HARMONIC: int = _def(int, 'HARMONIC')  #: Constant ``HARMONIC`` of type :class:`int`
        HARMONIC_RELATIVE: int = _def(int, 'HARMONIC_RELATIVE')  #: Constant ``HARMONIC_RELATIVE`` of type :class:`int`
        HARMONIC_RIGHT: int = _def(int, 'HARMONIC_RIGHT')  #: Constant ``HARMONIC_RIGHT`` of type :class:`int`
        HARMONIC_LARGEST: int = _def(int, 'HARMONIC_LARGEST')  #: Constant ``HARMONIC_LARGEST`` of type :class:`int`
        REFINED: int = _def(int, 'REFINED')  #: Constant ``REFINED`` of type :class:`int`
        REFINED_HARMONIC: int = _def(int, 'REFINED_HARMONIC')  #: Constant ``REFINED_HARMONIC`` of type :class:`int`
    class Balance:
        """EPS type of balancing used for non-Hermitian problems.
        
        - `NONE`:     None.
        - `ONESIDE`:  One-sided balancing.
        - `TWOSIDE`:  Two-sided balancing.
        - `USER`:     User-provided balancing matrices.
        
        """
        NONE: int = _def(int, 'NONE')  #: Constant ``NONE`` of type :class:`int`
        ONESIDE: int = _def(int, 'ONESIDE')  #: Constant ``ONESIDE`` of type :class:`int`
        TWOSIDE: int = _def(int, 'TWOSIDE')  #: Constant ``TWOSIDE`` of type :class:`int`
        USER: int = _def(int, 'USER')  #: Constant ``USER`` of type :class:`int`
    class ErrorType:
        """EPS error type to assess accuracy of computed solutions.
        
        - `ABSOLUTE`: Absolute error.
        - `RELATIVE`: Relative error.
        - `BACKWARD`: Backward error.
        
        """
        ABSOLUTE: int = _def(int, 'ABSOLUTE')  #: Constant ``ABSOLUTE`` of type :class:`int`
        RELATIVE: int = _def(int, 'RELATIVE')  #: Constant ``RELATIVE`` of type :class:`int`
        BACKWARD: int = _def(int, 'BACKWARD')  #: Constant ``BACKWARD`` of type :class:`int`
    class Which:
        """EPS desired part of spectrum.
        
        - `LARGEST_MAGNITUDE`:  Largest magnitude (default).
        - `SMALLEST_MAGNITUDE`: Smallest magnitude.
        - `LARGEST_REAL`:       Largest real parts.
        - `SMALLEST_REAL`:      Smallest real parts.
        - `LARGEST_IMAGINARY`:  Largest imaginary parts in magnitude.
        - `SMALLEST_IMAGINARY`: Smallest imaginary parts in magnitude.
        - `TARGET_MAGNITUDE`:   Closest to target (in magnitude).
        - `TARGET_REAL`:        Real part closest to target.
        - `TARGET_IMAGINARY`:   Imaginary part closest to target.
        - `ALL`:                All eigenvalues in an interval.
        - `USER`:               User defined selection.
        
        """
        LARGEST_MAGNITUDE: int = _def(int, 'LARGEST_MAGNITUDE')  #: Constant ``LARGEST_MAGNITUDE`` of type :class:`int`
        SMALLEST_MAGNITUDE: int = _def(int, 'SMALLEST_MAGNITUDE')  #: Constant ``SMALLEST_MAGNITUDE`` of type :class:`int`
        LARGEST_REAL: int = _def(int, 'LARGEST_REAL')  #: Constant ``LARGEST_REAL`` of type :class:`int`
        SMALLEST_REAL: int = _def(int, 'SMALLEST_REAL')  #: Constant ``SMALLEST_REAL`` of type :class:`int`
        LARGEST_IMAGINARY: int = _def(int, 'LARGEST_IMAGINARY')  #: Constant ``LARGEST_IMAGINARY`` of type :class:`int`
        SMALLEST_IMAGINARY: int = _def(int, 'SMALLEST_IMAGINARY')  #: Constant ``SMALLEST_IMAGINARY`` of type :class:`int`
        TARGET_MAGNITUDE: int = _def(int, 'TARGET_MAGNITUDE')  #: Constant ``TARGET_MAGNITUDE`` of type :class:`int`
        TARGET_REAL: int = _def(int, 'TARGET_REAL')  #: Constant ``TARGET_REAL`` of type :class:`int`
        TARGET_IMAGINARY: int = _def(int, 'TARGET_IMAGINARY')  #: Constant ``TARGET_IMAGINARY`` of type :class:`int`
        ALL: int = _def(int, 'ALL')  #: Constant ``ALL`` of type :class:`int`
        USER: int = _def(int, 'USER')  #: Constant ``USER`` of type :class:`int`
    class Conv:
        """EPS convergence test.
        
        - `ABS`:  Absolute convergence test.
        - `REL`:  Convergence test relative to the eigenvalue.
        - `NORM`: Convergence test relative to the matrix norms.
        - `USER`: User-defined convergence test.
        
        """
        ABS: int = _def(int, 'ABS')  #: Constant ``ABS`` of type :class:`int`
        REL: int = _def(int, 'REL')  #: Constant ``REL`` of type :class:`int`
        NORM: int = _def(int, 'NORM')  #: Constant ``NORM`` of type :class:`int`
        USER: int = _def(int, 'USER')  #: Constant ``USER`` of type :class:`int`
    class Stop:
        """EPS stopping test.
        
        - `BASIC`:     Default stopping test.
        - `USER`:      User-defined stopping test.
        - `THRESHOLD`: Threshold stopping test.
        
        """
        BASIC: int = _def(int, 'BASIC')  #: Constant ``BASIC`` of type :class:`int`
        USER: int = _def(int, 'USER')  #: Constant ``USER`` of type :class:`int`
        THRESHOLD: int = _def(int, 'THRESHOLD')  #: Constant ``THRESHOLD`` of type :class:`int`
    class ConvergedReason:
        """EPS convergence reasons.
        
        - `CONVERGED_TOL`:          All eigenpairs converged to requested tolerance.
        - `CONVERGED_USER`:         User-defined convergence criterion satisfied.
        - `DIVERGED_ITS`:           Maximum number of iterations exceeded.
        - `DIVERGED_BREAKDOWN`:     Solver failed due to breakdown.
        - `DIVERGED_SYMMETRY_LOST`: Lanczos-type method could not preserve symmetry.
        - `CONVERGED_ITERATING`:    Iteration not finished yet.
        
        """
        CONVERGED_TOL: int = _def(int, 'CONVERGED_TOL')  #: Constant ``CONVERGED_TOL`` of type :class:`int`
        CONVERGED_USER: int = _def(int, 'CONVERGED_USER')  #: Constant ``CONVERGED_USER`` of type :class:`int`
        DIVERGED_ITS: int = _def(int, 'DIVERGED_ITS')  #: Constant ``DIVERGED_ITS`` of type :class:`int`
        DIVERGED_BREAKDOWN: int = _def(int, 'DIVERGED_BREAKDOWN')  #: Constant ``DIVERGED_BREAKDOWN`` of type :class:`int`
        DIVERGED_SYMMETRY_LOST: int = _def(int, 'DIVERGED_SYMMETRY_LOST')  #: Constant ``DIVERGED_SYMMETRY_LOST`` of type :class:`int`
        CONVERGED_ITERATING: int = _def(int, 'CONVERGED_ITERATING')  #: Constant ``CONVERGED_ITERATING`` of type :class:`int`
        ITERATING: int = _def(int, 'ITERATING')  #: Constant ``ITERATING`` of type :class:`int`
    class PowerShiftType:
        """EPS Power shift type.
        
        - `CONSTANT`:  Constant shift.
        - `RAYLEIGH`:  Rayleigh quotient.
        - `WILKINSON`: Wilkinson shift.
        
        """
        CONSTANT: int = _def(int, 'CONSTANT')  #: Constant ``CONSTANT`` of type :class:`int`
        RAYLEIGH: int = _def(int, 'RAYLEIGH')  #: Constant ``RAYLEIGH`` of type :class:`int`
        WILKINSON: int = _def(int, 'WILKINSON')  #: Constant ``WILKINSON`` of type :class:`int`
    class KrylovSchurBSEType:
        """EPS Krylov-Schur method for BSE problems.
        
        - `SHAO`:         Lanczos recurrence for H square.
        - `GRUNING`:      Lanczos recurrence for H.
        - `PROJECTEDBSE`: Lanczos where the projected problem has BSE structure.
        
        """
        SHAO: int = _def(int, 'SHAO')  #: Constant ``SHAO`` of type :class:`int`
        GRUNING: int = _def(int, 'GRUNING')  #: Constant ``GRUNING`` of type :class:`int`
        PROJECTEDBSE: int = _def(int, 'PROJECTEDBSE')  #: Constant ``PROJECTEDBSE`` of type :class:`int`
    class LanczosReorthogType:
        """EPS Lanczos reorthogonalization type.
        
        - `LOCAL`:     Local reorthogonalization only.
        - `FULL`:      Full reorthogonalization.
        - `SELECTIVE`: Selective reorthogonalization.
        - `PERIODIC`:  Periodic reorthogonalization.
        - `PARTIAL`:   Partial reorthogonalization.
        - `DELAYED`:   Delayed reorthogonalization.
        
        """
        LOCAL: int = _def(int, 'LOCAL')  #: Constant ``LOCAL`` of type :class:`int`
        FULL: int = _def(int, 'FULL')  #: Constant ``FULL`` of type :class:`int`
        SELECTIVE: int = _def(int, 'SELECTIVE')  #: Constant ``SELECTIVE`` of type :class:`int`
        PERIODIC: int = _def(int, 'PERIODIC')  #: Constant ``PERIODIC`` of type :class:`int`
        PARTIAL: int = _def(int, 'PARTIAL')  #: Constant ``PARTIAL`` of type :class:`int`
        DELAYED: int = _def(int, 'DELAYED')  #: Constant ``DELAYED`` of type :class:`int`
    class CISSQuadRule:
        """EPS CISS quadrature rule.
        
        - `TRAPEZOIDAL`: Trapezoidal rule.
        - `CHEBYSHEV`:   Chebyshev points.
        
        """
        TRAPEZOIDAL: int = _def(int, 'TRAPEZOIDAL')  #: Constant ``TRAPEZOIDAL`` of type :class:`int`
        CHEBYSHEV: int = _def(int, 'CHEBYSHEV')  #: Constant ``CHEBYSHEV`` of type :class:`int`
    class CISSExtraction:
        """EPS CISS extraction technique.
        
        - `RITZ`:   Ritz extraction.
        - `HANKEL`: Extraction via Hankel eigenproblem.
        
        """
        RITZ: int = _def(int, 'RITZ')  #: Constant ``RITZ`` of type :class:`int`
        HANKEL: int = _def(int, 'HANKEL')  #: Constant ``HANKEL`` of type :class:`int`
    def view(self, viewer: Viewer | None = None) -> None:
        """Print the EPS data structure.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:290 <slepc4py/SLEPc/EPS.pyx#L290>`
    
        """
        ...
    def destroy(self) -> Self:
        """Destroy the EPS object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:305 <slepc4py/SLEPc/EPS.pyx#L305>`
    
        """
        ...
    def reset(self) -> None:
        """Reset the EPS object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:315 <slepc4py/SLEPc/EPS.pyx#L315>`
    
        """
        ...
    def create(self, comm: Comm | None = None) -> Self:
        """Create the EPS object.
    
        Collective.
    
        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all processes.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:323 <slepc4py/SLEPc/EPS.pyx#L323>`
    
        """
        ...
    def setType(self, eps_type: Type | str) -> None:
        """Set the particular solver to be used in the EPS object.
    
        Logically collective.
    
        Parameters
        ----------
        eps_type
            The solver to be used.
    
        Notes
        -----
        See `EPS.Type` for available methods. The default is
        `EPS.Type.KRYLOVSCHUR`.  Normally, it is best to use
        `setFromOptions()` and then set the EPS type from the options
        database rather than by using this routine.  Using the options
        database provides the user with maximum flexibility in
        evaluating the different available methods.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:340 <slepc4py/SLEPc/EPS.pyx#L340>`
    
        """
        ...
    def getType(self) -> str:
        """Get the EPS type of this object.
    
        Not collective.
    
        Returns
        -------
        str
            The solver currently being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:364 <slepc4py/SLEPc/EPS.pyx#L364>`
    
        """
        ...
    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all EPS options in the database.
    
        Not collective.
    
        Returns
        -------
        str
            The prefix string set for this EPS object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:379 <slepc4py/SLEPc/EPS.pyx#L379>`
    
        """
        ...
    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all EPS options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all EPS option requests.
    
        Notes
        -----
        A hyphen (-) must NOT be given at the beginning of the prefix
        name.  The first character of all runtime options is
        AUTOMATICALLY the hyphen.
    
        For example, to distinguish between the runtime options for
        two different EPS contexts, one could call::
    
            E1.setOptionsPrefix("eig1_")
            E2.setOptionsPrefix("eig2_")
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:394 <slepc4py/SLEPc/EPS.pyx#L394>`
    
        """
        ...
    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all EPS options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all EPS option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:421 <slepc4py/SLEPc/EPS.pyx#L421>`
    
        """
        ...
    def setFromOptions(self) -> None:
        """Set EPS options from the options database.
    
        Collective.
    
        This routine must be called before `setUp()` if the user is to be
        allowed to set the solver type.
    
        Notes
        -----
        To see all options, run your program with the ``-help``
        option.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:436 <slepc4py/SLEPc/EPS.pyx#L436>`
    
        """
        ...
    def getProblemType(self) -> ProblemType:
        """Get the problem type from the EPS object.
    
        Not collective.
    
        Returns
        -------
        ProblemType
            The problem type that was previously set.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:454 <slepc4py/SLEPc/EPS.pyx#L454>`
    
        """
        ...
    def setProblemType(self, problem_type: ProblemType) -> None:
        """Set the type of the eigenvalue problem.
    
        Logically collective.
    
        Parameters
        ----------
        problem_type
            The problem type to be set.
    
        Notes
        -----
        Allowed values are: Hermitian (HEP), non-Hermitian (NHEP), generalized
        Hermitian (GHEP), generalized non-Hermitian (GNHEP), and generalized
        non-Hermitian with positive semi-definite B (PGNHEP).
    
        This function must be used to instruct SLEPc to exploit symmetry. If
        no problem type is specified, by default a non-Hermitian problem is
        assumed (either standard or generalized). If the user knows that the
        problem is Hermitian (i.e. :math:`A=A^H`) or generalized Hermitian
        (i.e. :math:`A=A^H`, :math:`B=B^H`, and :math:`B` positive definite)
        then it is recommended to set the problem type so that eigensolver can
        exploit these properties.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:469 <slepc4py/SLEPc/EPS.pyx#L469>`
    
        """
        ...
    def isGeneralized(self) -> bool:
        """Tell if the EPS object corresponds to a generalized eigenproblem.
    
        Not collective.
    
        Returns
        -------
        bool
            True if two matrices were set with `setOperators()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:497 <slepc4py/SLEPc/EPS.pyx#L497>`
    
        """
        ...
    def isHermitian(self) -> bool:
        """Tell if the EPS object corresponds to a Hermitian eigenproblem.
    
        Not collective.
    
        Returns
        -------
        bool
            True if the problem type set with `setProblemType()` was Hermitian.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:512 <slepc4py/SLEPc/EPS.pyx#L512>`
    
        """
        ...
    def isPositive(self) -> bool:
        """Eigenproblem requiring a positive (semi-) definite matrix :math:`B`.
    
        Not collective.
    
        Tell if the EPS corresponds to an eigenproblem requiring a positive
        (semi-) definite matrix :math:`B`.
    
        Returns
        -------
        bool
            True if the problem type set with `setProblemType()` was positive.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:527 <slepc4py/SLEPc/EPS.pyx#L527>`
    
        """
        ...
    def isStructured(self) -> bool:
        """Tell if the EPS object corresponds to a structured eigenvalue problem.
    
        Not collective.
    
        Returns
        -------
        bool
            True if the problem type set with `setProblemType()` was structured.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:545 <slepc4py/SLEPc/EPS.pyx#L545>`
    
        """
        ...
    def getBalance(self) -> tuple[Balance, int, float]:
        """Get the balancing type used by the EPS, and the associated parameters.
    
        Not collective.
    
        Returns
        -------
        balance: Balance
            The balancing method
        iterations: int
            Number of iterations of the balancing algorithm
        cutoff: float
            Cutoff value
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:560 <slepc4py/SLEPc/EPS.pyx#L560>`
    
        """
        ...
    def setBalance(self, balance: Balance | None = None, iterations: int | None = None, cutoff: float | None = None) -> None:
        """Set the balancing technique to be used by the eigensolver.
    
        Logically collective.
    
        Set the balancing technique to be used by the eigensolver, and some
        parameters associated to it.
    
        Parameters
        ----------
        balance
            The balancing method
        iterations
            Number of iterations of the balancing algorithm
        cutoff
            Cutoff value
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:581 <slepc4py/SLEPc/EPS.pyx#L581>`
    
        """
        ...
    def getExtraction(self) -> Extraction:
        """Get the extraction type used by the EPS object.
    
        Not collective.
    
        Returns
        -------
        Extraction
            The method of extraction.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:613 <slepc4py/SLEPc/EPS.pyx#L613>`
    
        """
        ...
    def setExtraction(self, extraction: Extraction) -> None:
        """Set the extraction type used by the EPS object.
    
        Logically collective.
    
        Parameters
        ----------
        extraction
            The extraction method to be used by the solver.
    
        Notes
        -----
        Not all eigensolvers support all types of extraction. See the
        SLEPc documentation for details.
    
        By default, a standard Rayleigh-Ritz extraction is used. Other
        extractions may be useful when computing interior eigenvalues.
    
        Harmonic-type extractions are used in combination with a
        *target*. See `setTarget()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:628 <slepc4py/SLEPc/EPS.pyx#L628>`
    
        """
        ...
    def getWhichEigenpairs(self) -> Which:
        """Get which portion of the spectrum is to be sought.
    
        Not collective.
    
        Returns
        -------
        Which
            The portion of the spectrum to be sought by the solver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:653 <slepc4py/SLEPc/EPS.pyx#L653>`
    
        """
        ...
    def setWhichEigenpairs(self, which: Which) -> None:
        """Set which portion of the spectrum is to be sought.
    
        Logically collective.
    
        Parameters
        ----------
        which
            The portion of the spectrum to be sought by the solver.
    
        Notes
        -----
        Not all eigensolvers implemented in EPS account for all the
        possible values. Also, some values make sense only for certain
        types of problems. If SLEPc is compiled for real numbers
        `EPS.Which.LARGEST_IMAGINARY` and
        `EPS.Which.SMALLEST_IMAGINARY` use the absolute value of the
        imaginary part for eigenvalue selection.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:668 <slepc4py/SLEPc/EPS.pyx#L668>`
    
        """
        ...
    def getThreshold(self) -> tuple[float, bool]:
        """Get the threshold used in the threshold stopping test.
    
        Not collective.
    
        Returns
        -------
        thres: float
            The threshold.
        rel: bool
            Whether the threshold is relative or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:691 <slepc4py/SLEPc/EPS.pyx#L691>`
    
        """
        ...
    def setThreshold(self, thres: float, rel: bool = False) -> None:
        """Set the threshold used in the threshold stopping test.
    
        Logically collective.
    
        Parameters
        ----------
        thres
            The threshold.
        rel
            Whether the threshold is relative or not.
    
        Notes
        -----
        This function internally sets a special stopping test based on
        the threshold, where eigenvalues are computed in sequence
        until one of the computed eigenvalues is below/above the
        threshold (depending on whether largest or smallest eigenvalues
        are computed).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:709 <slepc4py/SLEPc/EPS.pyx#L709>`
    
        """
        ...
    def getTarget(self) -> Scalar:
        """Get the value of the target.
    
        Not collective.
    
        Returns
        -------
        Scalar
            The value of the target.
    
        Notes
        -----
        If the target was not set by the user, then zero is returned.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:734 <slepc4py/SLEPc/EPS.pyx#L734>`
    
        """
        ...
    def setTarget(self, target: Scalar) -> None:
        """Set the value of the target.
    
        Logically collective.
    
        Parameters
        ----------
        target
            The value of the target.
    
        Notes
        -----
        The target is a scalar value used to determine the portion of
        the spectrum of interest. It is used in combination with
        `setWhichEigenpairs()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:753 <slepc4py/SLEPc/EPS.pyx#L753>`
    
        """
        ...
    def getInterval(self) -> tuple[float, float]:
        """Get the computational interval for spectrum slicing.
    
        Not collective.
    
        Returns
        -------
        inta: float
            The left end of the interval.
        intb: float
            The right end of the interval.
    
        Notes
        -----
        If the interval was not set by the user, then zeros are returned.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:773 <slepc4py/SLEPc/EPS.pyx#L773>`
    
        """
        ...
    def setInterval(self, inta: float, intb: float) -> None:
        """Set the computational interval for spectrum slicing.
    
        Logically collective.
    
        Parameters
        ----------
        inta
            The left end of the interval.
        intb
            The right end of the interval.
    
        Notes
        -----
        Spectrum slicing is a technique employed for computing all
        eigenvalues of symmetric eigenproblems in a given interval.
        This function provides the interval to be considered. It must
        be used in combination with `EPS.Which.ALL`, see
        `setWhichEigenpairs()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:795 <slepc4py/SLEPc/EPS.pyx#L795>`
    
        """
        ...
    def getTolerances(self) -> tuple[float, int]:
        """Get the tolerance and max. iter. count used for convergence tests.
    
        Not collective.
    
        Get the tolerance and iteration limit used by the default EPS
        convergence tests.
    
        Returns
        -------
        tol: float
            The convergence tolerance.
        max_it: int
            The maximum number of iterations.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:822 <slepc4py/SLEPc/EPS.pyx#L822>`
    
        """
        ...
    def setTolerances(self, tol: float | None = None, max_it: int | None = None) -> None:
        """Set the tolerance and max. iter. used by the default EPS convergence tests.
    
        Logically collective.
    
        Parameters
        ----------
        tol
            The convergence tolerance.
        max_it
            The maximum number of iterations.
    
        Notes
        -----
        Use `DECIDE` for maxits to assign a reasonably good value,
        which is dependent on the solution method.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:843 <slepc4py/SLEPc/EPS.pyx#L843>`
    
        """
        ...
    def getTwoSided(self) -> bool:
        """Get the flag indicating if a two-sided variant of the algorithm is being used.
    
        Not collective.
    
        Returns
        -------
        bool
            Whether the two-sided variant is to be used or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:867 <slepc4py/SLEPc/EPS.pyx#L867>`
    
        """
        ...
    def setTwoSided(self, twosided: bool) -> None:
        """Set to use a two-sided variant that also computes left eigenvectors.
    
        Logically collective.
    
        Parameters
        ----------
        twosided
            Whether the two-sided variant is to be used or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:882 <slepc4py/SLEPc/EPS.pyx#L882>`
    
        """
        ...
    def getPurify(self) -> bool:
        """Get the flag indicating whether purification is activated or not.
    
        Not collective.
    
        Returns
        -------
        bool
            Whether purification is activated or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:896 <slepc4py/SLEPc/EPS.pyx#L896>`
    
        """
        ...
    def setPurify(self, purify: bool = True) -> None:
        """Set (toggle) eigenvector purification.
    
        Logically collective.
    
        Parameters
        ----------
        purify
            True to activate purification (default).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:911 <slepc4py/SLEPc/EPS.pyx#L911>`
    
        """
        ...
    def getConvergenceTest(self) -> Conv:
        """Get how to compute the error estimate used in the convergence test.
    
        Not collective.
    
        Returns
        -------
        Conv
            The method used to compute the error estimate
            used in the convergence test.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:925 <slepc4py/SLEPc/EPS.pyx#L925>`
    
        """
        ...
    def setConvergenceTest(self, conv: Conv) -> None:
        """Set how to compute the error estimate used in the convergence test.
    
        Logically collective.
    
        Parameters
        ----------
        conv
            The method used to compute the error estimate
            used in the convergence test.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:941 <slepc4py/SLEPc/EPS.pyx#L941>`
    
        """
        ...
    def getTrueResidual(self) -> bool:
        """Get the flag indicating if true residual must be computed explicitly.
    
        Not collective.
    
        Returns
        -------
        bool
            Whether the solver compute all residuals or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:956 <slepc4py/SLEPc/EPS.pyx#L956>`
    
        """
        ...
    def setTrueResidual(self, trueres: bool) -> None:
        """Set if the solver must compute the true residual explicitly or not.
    
        Logically collective.
    
        Parameters
        ----------
        trueres
            Whether compute the true residual or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:971 <slepc4py/SLEPc/EPS.pyx#L971>`
    
        """
        ...
    def getTrackAll(self) -> bool:
        """Get the flag indicating if all residual norms must be computed or not.
    
        Not collective.
    
        Returns
        -------
        bool
            Whether the solver compute all residuals or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:985 <slepc4py/SLEPc/EPS.pyx#L985>`
    
        """
        ...
    def setTrackAll(self, trackall: bool) -> None:
        """Set if the solver must compute the residual of all approximate eigenpairs.
    
        Logically collective.
    
        Parameters
        ----------
        trackall
            Whether compute all residuals or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1000 <slepc4py/SLEPc/EPS.pyx#L1000>`
    
        """
        ...
    def getDimensions(self) -> tuple[int, int, int]:
        """Get number of eigenvalues to compute and the dimension of the subspace.
    
        Not collective.
    
        Returns
        -------
        nev: int
            Number of eigenvalues to compute.
        ncv: int
            Maximum dimension of the subspace to be used by the solver.
        mpd: int
            Maximum dimension allowed for the projected problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1014 <slepc4py/SLEPc/EPS.pyx#L1014>`
    
        """
        ...
    def setDimensions(self, nev: int | None = None, ncv: int | None = None, mpd: int | None = None) -> None:
        """Set number of eigenvalues to compute and the dimension of the subspace.
    
        Logically collective.
    
        Parameters
        ----------
        nev
            Number of eigenvalues to compute.
        ncv
            Maximum dimension of the subspace to be used by the solver.
        mpd
            Maximum dimension allowed for the projected problem.
    
        Notes
        -----
        Use `DECIDE` for ``ncv`` and ``mpd`` to assign a reasonably good
        value, which is dependent on the solution method.
    
        The parameters ``ncv`` and ``mpd`` are intimately related, so that
        the user is advised to set one of them at most. Normal usage
        is the following:
    
        + In cases where ``nev`` is small, the user sets ``ncv``
          (a reasonable default is 2 * ``nev``).
    
        + In cases where ``nev`` is large, the user sets ``mpd``.
    
        The value of ``ncv`` should always be between ``nev`` and (``nev`` +
        ``mpd``), typically ``ncv`` = ``nev`` + ``mpd``. If ``nev`` is not too
        large, ``mpd`` = ``nev`` is a reasonable choice, otherwise a
        smaller value should be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1035 <slepc4py/SLEPc/EPS.pyx#L1035>`
    
        """
        ...
    def getST(self) -> ST:
        """Get the spectral transformation object associated to the eigensolver.
    
        Not collective.
    
        Returns
        -------
        ST
            The spectral transformation.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1082 <slepc4py/SLEPc/EPS.pyx#L1082>`
    
        """
        ...
    def setST(self, st: ST) -> None:
        """Set a spectral transformation object associated to the eigensolver.
    
        Collective.
    
        Parameters
        ----------
        st
            The spectral transformation.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1098 <slepc4py/SLEPc/EPS.pyx#L1098>`
    
        """
        ...
    def getBV(self) -> BV:
        """Get the basis vector objects associated to the eigensolver.
    
        Not collective.
    
        Returns
        -------
        BV
            The basis vectors context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1111 <slepc4py/SLEPc/EPS.pyx#L1111>`
    
        """
        ...
    def setBV(self, bv: BV) -> None:
        """Set a basis vectors object associated to the eigensolver.
    
        Collective.
    
        Parameters
        ----------
        bv
            The basis vectors context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1127 <slepc4py/SLEPc/EPS.pyx#L1127>`
    
        """
        ...
    def getDS(self) -> DS:
        """Get the direct solver associated to the eigensolver.
    
        Not collective.
    
        Returns
        -------
        DS
            The direct solver context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1140 <slepc4py/SLEPc/EPS.pyx#L1140>`
    
        """
        ...
    def setDS(self, ds: DS) -> None:
        """Set a direct solver object associated to the eigensolver.
    
        Collective.
    
        Parameters
        ----------
        ds
            The direct solver context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1156 <slepc4py/SLEPc/EPS.pyx#L1156>`
    
        """
        ...
    def getRG(self) -> RG:
        """Get the region object associated to the eigensolver.
    
        Not collective.
    
        Returns
        -------
        RG
            The region context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1169 <slepc4py/SLEPc/EPS.pyx#L1169>`
    
        """
        ...
    def setRG(self, rg: RG) -> None:
        """Set a region object associated to the eigensolver.
    
        Collective.
    
        Parameters
        ----------
        rg
            The region context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1185 <slepc4py/SLEPc/EPS.pyx#L1185>`
    
        """
        ...
    def getOperators(self) -> tuple[petsc4py.PETSc.Mat, petsc4py.PETSc.Mat] | tuple[petsc4py.PETSc.Mat, None]:
        """Get the matrices associated with the eigenvalue problem.
    
        Collective.
    
        Returns
        -------
        A: petsc4py.PETSc.Mat
            The matrix associated with the eigensystem.
        B: petsc4py.PETSc.Mat
            The second matrix in the case of generalized eigenproblems.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1198 <slepc4py/SLEPc/EPS.pyx#L1198>`
    
        """
        ...
    def setOperators(self, A: Mat, B: Mat | None = None) -> None:
        """Set the matrices associated with the eigenvalue problem.
    
        Collective.
    
        Parameters
        ----------
        A
            The matrix associated with the eigensystem.
        B
            The second matrix in the case of generalized eigenproblems;
            if not provided, a standard eigenproblem is assumed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1221 <slepc4py/SLEPc/EPS.pyx#L1221>`
    
        """
        ...
    def setDeflationSpace(self, space: Vec | list[Vec]) -> None:
        """Add vectors to the basis of the deflation space.
    
        Collective.
    
        Parameters
        ----------
        space
            Set of basis vectors to be added to the deflation space.
    
        Notes
        -----
        When a deflation space is given, the eigensolver seeks the
        eigensolution in the restriction of the problem to the
        orthogonal complement of this space. This can be used for
        instance in the case that an invariant subspace is known
        beforehand (such as the nullspace of the matrix).
    
        The vectors do not need to be mutually orthonormal, since they
        are explicitly orthonormalized internally.
    
        These vectors do not persist from one `solve()` call to the other,
        so the deflation space should be set every time.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1238 <slepc4py/SLEPc/EPS.pyx#L1238>`
    
        """
        ...
    def setInitialSpace(self, space: Vec | list[Vec]) -> None:
        """Set the initial space from which the eigensolver starts to iterate.
    
        Collective.
    
        Parameters
        ----------
        space
            The initial space
    
        Notes
        -----
        Some solvers start to iterate on a single vector (initial vector).
        In that case, the other vectors are ignored.
    
        In contrast to `setDeflationSpace()`, these vectors do not persist
        from one `solve()` call to the other, so the initial space should be
        set every time.
    
        The vectors do not need to be mutually orthonormal, since they are
        explicitly orthonormalized internally.
    
        Common usage of this function is when the user can provide a rough
        approximation of the wanted eigenspace. Then, convergence may be faster.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1272 <slepc4py/SLEPc/EPS.pyx#L1272>`
    
        """
        ...
    def setLeftInitialSpace(self, space: Vec | list[Vec]) -> None:
        """Set a left initial space from which the eigensolver starts to iterate.
    
        Collective.
    
        Parameters
        ----------
        space
            The left initial space
    
        Notes
        -----
        Left initial vectors are used to initiate the left search space
        in two-sided eigensolvers. Users should pass here an approximation
        of the left eigenspace, if available.
    
        The same comments in `setInitialSpace()` are applicable here.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1305 <slepc4py/SLEPc/EPS.pyx#L1305>`
    
        """
        ...
    def setStoppingTest(self, stopping: EPSStoppingFunction | None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Set when to stop the outer iteration of the eigensolver.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1333 <slepc4py/SLEPc/EPS.pyx#L1333>`
    
        """
        ...
    def getStoppingTest(self) -> EPSStoppingFunction:
        """Get the stopping function.
    
        Not collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1353 <slepc4py/SLEPc/EPS.pyx#L1353>`
    
        """
        ...
    def setArbitrarySelection(self, arbitrary: EPSArbitraryFunction | None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Set an arbitrary selection criterion function.
    
        Logically collective.
    
        Set a function to look for eigenvalues according to an arbitrary
        selection criterion. This criterion can be based on a computation
        involving the current eigenvector approximation.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1363 <slepc4py/SLEPc/EPS.pyx#L1363>`
    
        """
        ...
    def setEigenvalueComparison(self, comparison: EPSEigenvalueComparison | None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Set an eigenvalue comparison function.
    
        Logically collective.
    
        Specify the eigenvalue comparison function when `setWhichEigenpairs()`
        is set to `EPS.Which.USER`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1390 <slepc4py/SLEPc/EPS.pyx#L1390>`
    
        """
        ...
    def setMonitor(self, monitor: EPSMonitorFunction | None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Append a monitor function to the list of monitors.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1414 <slepc4py/SLEPc/EPS.pyx#L1414>`
    
        """
        ...
    def getMonitor(self) -> EPSMonitorFunction:
        """Get the list of monitor functions.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1435 <slepc4py/SLEPc/EPS.pyx#L1435>`
    
        """
        ...
    def cancelMonitor(self) -> None:
        """Clear all monitors for an `EPS` object.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1439 <slepc4py/SLEPc/EPS.pyx#L1439>`
    
        """
        ...
    def setUp(self) -> None:
        """Set up all the internal data structures.
    
        Collective.
    
        Set up all the internal data structures necessary for the execution
        of the eigensolver.
    
        Notes
        -----
        This function need not be called explicitly in most cases,
        since `solve()` calls it. It can be useful when one wants to
        measure the set-up time separately from the solve time.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1450 <slepc4py/SLEPc/EPS.pyx#L1450>`
    
        """
        ...
    def solve(self) -> None:
        """Solve the eigensystem.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1467 <slepc4py/SLEPc/EPS.pyx#L1467>`
    
        """
        ...
    def getIterationNumber(self) -> int:
        """Get the current iteration number.
    
        Not collective.
    
        If the call to `solve()` is complete, then it returns the number of
        iterations carried out by the solution method.
    
        Returns
        -------
        int
            Iteration number.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1475 <slepc4py/SLEPc/EPS.pyx#L1475>`
    
        """
        ...
    def getConvergedReason(self) -> ConvergedReason:
        """Get the reason why the `solve()` iteration was stopped.
    
        Not collective.
    
        Returns
        -------
        ConvergedReason
            Negative value indicates diverged, positive value converged.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1493 <slepc4py/SLEPc/EPS.pyx#L1493>`
    
        """
        ...
    def getConverged(self) -> int:
        """Get the number of converged eigenpairs.
    
        Not collective.
    
        Returns
        -------
        int
            Number of converged eigenpairs.
    
        Notes
        -----
        This function should be called after `solve()` has finished.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1508 <slepc4py/SLEPc/EPS.pyx#L1508>`
    
        """
        ...
    def getEigenvalue(self, i: int) -> Scalar:
        """Get the i-th eigenvalue as computed by `solve()`.
    
        Not collective.
    
        Parameters
        ----------
        i
            Index of the solution to be obtained.
    
        Returns
        -------
        Scalar
            The computed eigenvalue. It will be a real variable in case
            of a Hermitian or generalized Hermitian eigenproblem. Otherwise
            it will be a complex variable (possibly with zero imaginary part).
    
        Notes
        -----
        The index ``i`` should be a value between ``0`` and ``nconv-1`` (see
        `getConverged()`). Eigenpairs are indexed according to the ordering
        criterion established with `setWhichEigenpairs()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1527 <slepc4py/SLEPc/EPS.pyx#L1527>`
    
        """
        ...
    def getEigenvector(self, i: int, Vr: Vec | None = None, Vi: Vec | None = None) -> None:
        """Get the i-th eigenvector as computed by `solve()`.
    
        Collective.
    
        Parameters
        ----------
        i
            Index of the solution to be obtained.
        Vr
            Placeholder for the returned eigenvector (real part).
        Vi
            Placeholder for the returned eigenvector (imaginary part).
    
        Notes
        -----
        The index ``i`` should be a value between ``0`` and
        ``nconv-1`` (see `getConverged()`). Eigenpairs are indexed
        according to the ordering criterion established with
        `setWhichEigenpairs()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1561 <slepc4py/SLEPc/EPS.pyx#L1561>`
    
        """
        ...
    def getLeftEigenvector(self, i: int, Wr: Vec | None = None, Wi: Vec | None = None) -> None:
        """Get the i-th left eigenvector as computed by `solve()`.
    
        Collective.
    
        Parameters
        ----------
        i
            Index of the solution to be obtained.
        Wr
            Placeholder for the returned eigenvector (real part).
        Wi
            Placeholder for the returned eigenvector (imaginary part).
    
        Notes
        -----
        The index ``i`` should be a value between ``0`` and ``nconv-1`` (see
        `getConverged()`). Eigensolutions are indexed according to the
        ordering criterion established with `setWhichEigenpairs()`.
    
        Left eigenvectors are available only if the twosided flag was set
        with `setTwoSided()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1587 <slepc4py/SLEPc/EPS.pyx#L1587>`
    
        """
        ...
    def getEigenpair(self, i: int, Vr: Vec | None = None, Vi: Vec | None = None) -> Scalar:
        """Get the i-th solution of the eigenproblem as computed by `solve()`.
    
        Collective.
    
        The solution consists of both the eigenvalue and the eigenvector.
    
        Parameters
        ----------
        i
            Index of the solution to be obtained.
        Vr
            Placeholder for the returned eigenvector (real part).
        Vi
            Placeholder for the returned eigenvector (imaginary part).
    
        Returns
        -------
        e: Scalar
           The computed eigenvalue. It will be a real variable in case
           of a Hermitian or generalized Hermitian eigenproblem. Otherwise
           it will be a complex variable (possibly with zero imaginary part).
    
        Notes
        -----
        The index ``i`` should be a value between ``0`` and ``nconv-1`` (see
        `getConverged()`). Eigenpairs are indexed according to the ordering
        criterion established with `setWhichEigenpairs()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1615 <slepc4py/SLEPc/EPS.pyx#L1615>`
    
        """
        ...
    def getInvariantSubspace(self) -> list[petsc4py.PETSc.Vec]:
        """Get an orthonormal basis of the computed invariant subspace.
    
        Collective.
    
        Returns
        -------
        list of petsc4py.PETSc.Vec
            Basis of the invariant subspace.
    
        Notes
        -----
        This function should be called after `solve()` has finished.
    
        The returned vectors span an invariant subspace associated
        with the computed eigenvalues. An invariant subspace ``X`` of
        ``A` satisfies ``A x`` in ``X`` for all ``x`` in ``X`` (a
        similar definition applies for generalized eigenproblems).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1657 <slepc4py/SLEPc/EPS.pyx#L1657>`
    
        """
        ...
    def getErrorEstimate(self, i: int) -> float:
        """Get the error estimate associated to the i-th computed eigenpair.
    
        Not collective.
    
        Parameters
        ----------
        i
            Index of the solution to be considered.
    
        Returns
        -------
        float
            Error estimate.
    
        Notes
        -----
        This is the error estimate used internally by the
        eigensolver. The actual error bound can be computed with
        `computeError()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1696 <slepc4py/SLEPc/EPS.pyx#L1696>`
    
        """
        ...
    def computeError(self, i: int, etype: ErrorType | None = None) -> float:
        """Compute the error associated with the i-th computed eigenpair.
    
        Collective.
    
        Compute the error (based on the residual norm) associated with the
        i-th computed eigenpair.
    
        Parameters
        ----------
        i
            Index of the solution to be considered.
        etype
            The error type to compute.
    
        Returns
        -------
        float
            The error bound, computed in various ways from the residual norm
            :math:`\|Ax-kBx\|_2` where :math:`k` is the eigenvalue and
            :math:`x` is the eigenvector.
    
        Notes
        -----
        The index ``i`` should be a value between ``0`` and
        ``nconv-1`` (see `getConverged()`).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1722 <slepc4py/SLEPc/EPS.pyx#L1722>`
    
        """
        ...
    def errorView(self, etype: ErrorType | None = None, viewer: petsc4py.PETSc.Viewer | None = None) -> None:
        """Display the errors associated with the computed solution.
    
        Collective.
    
        Display the errors and the eigenvalues.
    
        Parameters
        ----------
        etype
            The error type to compute.
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
        Notes
        -----
        By default, this function checks the error of all eigenpairs and prints
        the eigenvalues if all of them are below the requested tolerance.
        If the viewer has format ``ASCII_INFO_DETAIL`` then a table with
        eigenvalues and corresponding errors is printed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1756 <slepc4py/SLEPc/EPS.pyx#L1756>`
    
        """
        ...
    def valuesView(self, viewer: Viewer | None = None) -> None:
        """Display the computed eigenvalues in a viewer.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1784 <slepc4py/SLEPc/EPS.pyx#L1784>`
    
        """
        ...
    def vectorsView(self, viewer: Viewer | None = None) -> None:
        """Output computed eigenvectors to a viewer.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1799 <slepc4py/SLEPc/EPS.pyx#L1799>`
    
        """
        ...
    def setPowerShiftType(self, shift: PowerShiftType) -> None:
        """Set the type of shifts used during the power iteration.
    
        Logically collective.
    
        This can be used to emulate the Rayleigh Quotient Iteration (RQI)
        method.
    
        Parameters
        ----------
        shift
            The type of shift.
    
        Notes
        -----
        This call is only relevant if the type was set to
        `EPS.Type.POWER` with `setType()`.
    
        By default, shifts are constant
        (`EPS.PowerShiftType.CONSTANT`) and the iteration is the
        simple power method (or inverse iteration if a
        shift-and-invert transformation is being used).
    
        A variable shift can be specified
        (`EPS.PowerShiftType.RAYLEIGH` or
        `EPS.PowerShiftType.WILKINSON`). In this case, the iteration
        behaves rather like a cubic converging method as RQI.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1816 <slepc4py/SLEPc/EPS.pyx#L1816>`
    
        """
        ...
    def getPowerShiftType(self) -> PowerShiftType:
        """Get the type of shifts used during the power iteration.
    
        Not collective.
    
        Returns
        -------
        PowerShiftType
            The type of shift.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1848 <slepc4py/SLEPc/EPS.pyx#L1848>`
    
        """
        ...
    def setArnoldiDelayed(self, delayed: bool) -> None:
        """Set (toggle) delayed reorthogonalization in the Arnoldi iteration.
    
        Logically collective.
    
        Parameters
        ----------
        delayed
            True if delayed reorthogonalization is to be used.
    
        Notes
        -----
        This call is only relevant if the type was set to
        `EPS.Type.ARNOLDI` with `setType()`.
    
        Delayed reorthogonalization is an aggressive optimization for
        the Arnoldi eigensolver than may provide better scalability,
        but sometimes makes the solver converge less than the default
        algorithm.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1863 <slepc4py/SLEPc/EPS.pyx#L1863>`
    
        """
        ...
    def getArnoldiDelayed(self) -> bool:
        """Get the type of reorthogonalization used during the Arnoldi iteration.
    
        Not collective.
    
        Returns
        -------
        bool
            True if delayed reorthogonalization is to be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1887 <slepc4py/SLEPc/EPS.pyx#L1887>`
    
        """
        ...
    def setLanczosReorthogType(self, reorthog: LanczosReorthogType) -> None:
        """Set the type of reorthogonalization used during the Lanczos iteration.
    
        Logically collective.
    
        Parameters
        ----------
        reorthog
            The type of reorthogonalization.
    
        Notes
        -----
        This call is only relevant if the type was set to
        `EPS.Type.LANCZOS` with `setType()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1902 <slepc4py/SLEPc/EPS.pyx#L1902>`
    
        """
        ...
    def getLanczosReorthogType(self) -> LanczosReorthogType:
        """Get the type of reorthogonalization used during the Lanczos iteration.
    
        Not collective.
    
        Returns
        -------
        LanczosReorthogType
            The type of reorthogonalization.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1921 <slepc4py/SLEPc/EPS.pyx#L1921>`
    
        """
        ...
    def setKrylovSchurBSEType(self, bse: KrylovSchurBSEType) -> None:
        """Set the Krylov-Schur variant used for BSE structured eigenproblems.
    
        Logically collective.
    
        Parameters
        ----------
        bse
            The BSE method.
    
        Notes
        -----
        This call is only relevant if the type was set to
        `EPS.Type.KRYLOVSCHUR` with `setType()` and the problem
        type to `EPS.ProblemType.BSE` with `setProblemType()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1939 <slepc4py/SLEPc/EPS.pyx#L1939>`
    
        """
        ...
    def getKrylovSchurBSEType(self) -> KrylovSchurBSEType:
        """Get the method used for BSE structured eigenproblems (Krylov-Schur).
    
        Not collective.
    
        Returns
        -------
        KrylovSchurBSEType
            The BSE method.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1959 <slepc4py/SLEPc/EPS.pyx#L1959>`
    
        """
        ...
    def setKrylovSchurRestart(self, keep: float) -> None:
        """Set the restart parameter for the Krylov-Schur method.
    
        Logically collective.
    
        It is the proportion of basis vectors that must be kept after restart.
    
        Parameters
        ----------
        keep
            The number of vectors to be kept at restart.
    
        Notes
        -----
        Allowed values are in the range [0.1,0.9]. The default is 0.5.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1974 <slepc4py/SLEPc/EPS.pyx#L1974>`
    
        """
        ...
    def getKrylovSchurRestart(self) -> float:
        """Get the restart parameter used in the Krylov-Schur method.
    
        Not collective.
    
        Returns
        -------
        float
            The number of vectors to be kept at restart.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:1994 <slepc4py/SLEPc/EPS.pyx#L1994>`
    
        """
        ...
    def setKrylovSchurLocking(self, lock: bool) -> None:
        """Set (toggle) locking/non-locking variants of the Krylov-Schur method.
    
        Logically collective.
    
        Parameters
        ----------
        lock
            True if the locking variant must be selected.
    
        Notes
        -----
        The default is to lock converged eigenpairs when the method restarts.
        This behavior can be changed so that all directions are kept in the
        working subspace even if already converged to working accuracy (the
        non-locking variant).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2009 <slepc4py/SLEPc/EPS.pyx#L2009>`
    
        """
        ...
    def getKrylovSchurLocking(self) -> bool:
        """Get the locking flag used in the Krylov-Schur method.
    
        Not collective.
    
        Returns
        -------
        bool
            The locking flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2030 <slepc4py/SLEPc/EPS.pyx#L2030>`
    
        """
        ...
    def setKrylovSchurPartitions(self, npart: int) -> None:
        """Set the number of partitions of the communicator (spectrum slicing).
    
        Logically collective.
    
        Set the number of partitions for the case of doing spectrum
        slicing for a computational interval with the communicator split
        in several sub-communicators.
    
        Parameters
        ----------
        npart
            The number of partitions.
    
        Notes
        -----
        By default, npart=1 so all processes in the communicator participate in
        the processing of the whole interval. If npart>1 then the interval is
        divided into npart subintervals, each of them being processed by a
        subset of processes.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2045 <slepc4py/SLEPc/EPS.pyx#L2045>`
    
        """
        ...
    def getKrylovSchurPartitions(self) -> int:
        """Get the number of partitions of the communicator (spectrum slicing).
    
        Not collective.
    
        Returns
        -------
        int
            The number of partitions.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2070 <slepc4py/SLEPc/EPS.pyx#L2070>`
    
        """
        ...
    def setKrylovSchurDetectZeros(self, detect: bool) -> None:
        """Set the flag that enforces zero detection in spectrum slicing.
    
        Logically collective.
    
        Set a flag to enforce the detection of zeros during the factorizations
        throughout the spectrum slicing computation.
    
        Parameters
        ----------
        detect
            True if zeros must checked for.
    
        Notes
        -----
        A zero in the factorization indicates that a shift coincides with
        an eigenvalue.
    
        This flag is turned off by default, and may be necessary in some cases,
        especially when several partitions are being used. This feature currently
        requires an external package for factorizations with support for zero
        detection, e.g. MUMPS.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2085 <slepc4py/SLEPc/EPS.pyx#L2085>`
    
        """
        ...
    def getKrylovSchurDetectZeros(self) -> bool:
        """Get the flag that enforces zero detection in spectrum slicing.
    
        Not collective.
    
        Returns
        -------
        bool
            The zero detection flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2112 <slepc4py/SLEPc/EPS.pyx#L2112>`
    
        """
        ...
    def setKrylovSchurDimensions(self, nev: int | None = None, ncv: int | None = None, mpd: int | None = None) -> None:
        """Set the dimensions used for each subsolve step (spectrum slicing).
    
        Logically collective.
    
        Set the dimensions used for each subsolve step in case of doing
        spectrum slicing for a computational interval. The meaning of the
        parameters is the same as in `setDimensions()`.
    
        Parameters
        ----------
        nev
            Number of eigenvalues to compute.
        ncv
            Maximum dimension of the subspace to be used by the solver.
        mpd
            Maximum dimension allowed for the projected problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2127 <slepc4py/SLEPc/EPS.pyx#L2127>`
    
        """
        ...
    def getKrylovSchurDimensions(self) -> tuple[int, int, int]:
        """Get the dimensions used for each subsolve step (spectrum slicing).
    
        Not collective.
    
        Get the dimensions used for each subsolve step in case of doing
        spectrum slicing for a computational interval.
    
        Returns
        -------
        nev: int
            Number of eigenvalues to compute.
        ncv: int
            Maximum dimension of the subspace to be used by the solver.
        mpd: int
            Maximum dimension allowed for the projected problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2159 <slepc4py/SLEPc/EPS.pyx#L2159>`
    
        """
        ...
    def getKrylovSchurSubcommInfo(self) -> tuple[int, int, petsc4py.PETSc.Vec]:
        """Get information related to the case of doing spectrum slicing.
    
        Collective on the subcommunicator (if v is given).
    
        Get information related to the case of doing spectrum slicing
        for a computational interval with multiple communicators.
    
        Returns
        -------
        k: int
            Number of the subinterval for the calling process.
        n: int
            Number of eigenvalues found in the k-th subinterval.
        v: petsc4py.PETSc.Vec
            A vector owned by processes in the subcommunicator with dimensions
            compatible for locally computed eigenvectors.
    
        Notes
        -----
        This function is only available for spectrum slicing runs.
    
        The returned Vec should be destroyed by the user.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2183 <slepc4py/SLEPc/EPS.pyx#L2183>`
    
        """
        ...
    def getKrylovSchurSubcommPairs(self, i: int, V: Vec) -> Scalar:
        """Get the i-th eigenpair stored in the multi-communicator of the process.
    
        Collective on the subcommunicator (if v is given).
    
        Get the i-th eigenpair stored internally in the multi-communicator
        to which the calling process belongs.
    
        Parameters
        ----------
        i
            Index of the solution to be obtained.
        V
            Placeholder for the returned eigenvector.
    
        Returns
        -------
        Scalar
            The computed eigenvalue.
    
        Notes
        -----
        The index ``i`` should be a value between ``0`` and ``n-1``,
        where ``n`` is the number of vectors in the local subinterval,
        see `getKrylovSchurSubcommInfo()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2214 <slepc4py/SLEPc/EPS.pyx#L2214>`
    
        """
        ...
    def getKrylovSchurSubcommMats(self) -> tuple[petsc4py.PETSc.Mat, petsc4py.PETSc.Mat] | tuple[petsc4py.PETSc.Mat, None]:
        """Get the eigenproblem matrices stored in the subcommunicator.
    
        Collective on the subcommunicator.
    
        Get the eigenproblem matrices stored internally in the subcommunicator
        to which the calling process belongs.
    
        Returns
        -------
        A: petsc4py.PETSc.Mat
            The matrix associated with the eigensystem.
        B: petsc4py.PETSc.Mat
            The second matrix in the case of generalized eigenproblems.
    
        Notes
        -----
        This is the analog of `getOperators()`, but returns the matrices distributed
        differently (in the subcommunicator rather than in the parent communicator).
    
        These matrices should not be modified by the user.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2246 <slepc4py/SLEPc/EPS.pyx#L2246>`
    
        """
        ...
    def updateKrylovSchurSubcommMats(self, s: Scalar = 1.0, a: Scalar = 1.0, Au: petsc4py.PETSc.Mat | None = None, t: Scalar = 1.0, b: Scalar = 1.0, Bu: petsc4py.PETSc.Mat | None = None, structure: petsc4py.PETSc.Mat.Structure | None = None, globalup: bool = False) -> None:
        """Update the eigenproblem matrices stored internally in the communicator.
    
        Collective.
    
        Update the eigenproblem matrices stored internally in the
        subcommunicator to which the calling process belongs.
    
        Parameters
        ----------
        s
            Scalar that multiplies the existing A matrix.
        a
            Scalar used in the axpy operation on A.
        Au
            The matrix used in the axpy operation on A.
        t
            Scalar that multiplies the existing B matrix.
        b
            Scalar used in the axpy operation on B.
        Bu
            The matrix used in the axpy operation on B.
        structure
            Either same, different, or a subset of the non-zero sparsity pattern.
        globalup
            Whether global matrices must be updated or not.
    
        Notes
        -----
        This function modifies the eigenproblem matrices at subcommunicator
        level, and optionally updates the global matrices in the parent
        communicator.  The updates are expressed as
        :math:`A \leftarrow s A + a Au`,
        :math:`B \leftarrow t B + b Bu`.
    
        It is possible to update one of the matrices, or both.
    
        The matrices ``Au`` and ``Bu`` must be equal in all subcommunicators.
    
        The ``structure`` flag is passed to the `petsc4py.PETSc.Mat.axpy`
        operations to perform the updates.
    
        If ``globalup`` is True, communication is carried out to reconstruct
        the updated matrices in the parent communicator.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2279 <slepc4py/SLEPc/EPS.pyx#L2279>`
    
        """
        ...
    def setKrylovSchurSubintervals(self, subint: Sequence[float]) -> None:
        """Set the subinterval boundaries.
    
        Logically collective.
    
        Set the subinterval boundaries for spectrum slicing with a
        computational interval.
    
        Parameters
        ----------
        subint
            Real values specifying subintervals
    
        Notes
        -----
        This function must be called after setKrylovSchurPartitions().
        For npart partitions, the argument subint must contain npart+1
        real values sorted in ascending order:
        subint_0, subint_1, ..., subint_npart,
        where the first and last values must coincide with the interval
        endpoints set with EPSSetInterval().
        The subintervals are then defined by two consecutive points:
        [subint_0,subint_1], [subint_1,subint_2], and so on.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2342 <slepc4py/SLEPc/EPS.pyx#L2342>`
    
        """
        ...
    def getKrylovSchurSubintervals(self) -> ArrayReal:
        """Get the points that delimit the subintervals.
    
        Not collective.
    
        Get the points that delimit the subintervals used in spectrum slicing
        with several partitions.
    
        Returns
        -------
        ArrayReal
            Real values specifying subintervals
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2379 <slepc4py/SLEPc/EPS.pyx#L2379>`
    
        """
        ...
    def getKrylovSchurInertias(self) -> tuple[ArrayReal, ArrayInt]:
        """Get the values of the shifts and their corresponding inertias.
    
        Not collective.
    
        Get the values of the shifts and their corresponding inertias in case
        of doing spectrum slicing for a computational interval.
    
        Returns
        -------
        shifts: ArrayReal
            The values of the shifts used internally in the solver.
        inertias: ArrayInt
            The values of the inertia in each shift.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2404 <slepc4py/SLEPc/EPS.pyx#L2404>`
    
        """
        ...
    def getKrylovSchurKSP(self) -> KSP:
        """Get the linear solver object associated with the internal `EPS` object.
    
        Collective.
    
        Get the linear solver object associated with the internal `EPS`
        object in case of doing spectrum slicing for a computational interval.
    
        Returns
        -------
        `petsc4py.PETSc.KSP`
            The linear solver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2434 <slepc4py/SLEPc/EPS.pyx#L2434>`
    
        """
        ...
    def setGDKrylovStart(self, krylovstart: bool = True) -> None:
        """Set (toggle) starting the search subspace with a Krylov basis.
    
        Logically collective.
    
        Parameters
        ----------
        krylovstart
            True if starting the search subspace with a Krylov basis.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2455 <slepc4py/SLEPc/EPS.pyx#L2455>`
    
        """
        ...
    def getGDKrylovStart(self) -> bool:
        """Get a flag indicating if the search subspace is started with a Krylov basis.
    
        Not collective.
    
        Returns
        -------
        bool
            True if starting the search subspace with a Krylov basis.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2469 <slepc4py/SLEPc/EPS.pyx#L2469>`
    
        """
        ...
    def setGDBlockSize(self, bs: int) -> None:
        """Set the number of vectors to be added to the searching space.
    
        Logically collective.
    
        Set the number of vectors to be added to the searching space in every
        iteration.
    
        Parameters
        ----------
        bs
            The number of vectors added to the search space in every iteration.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2484 <slepc4py/SLEPc/EPS.pyx#L2484>`
    
        """
        ...
    def getGDBlockSize(self) -> int:
        """Get the number of vectors to be added to the searching space.
    
        Not collective.
    
        Get the number of vectors to be added to the searching space in every
        iteration.
    
        Returns
        -------
        int
            The number of vectors added to the search space in every iteration.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2501 <slepc4py/SLEPc/EPS.pyx#L2501>`
    
        """
        ...
    def setGDRestart(self, minv: int = None, plusk: int = None) -> None:
        """Set the number of vectors of the search space after restart.
    
        Logically collective.
    
        Set the number of vectors of the search space after restart and
        the number of vectors saved from the previous iteration.
    
        Parameters
        ----------
        minv
            The number of vectors of the search subspace after restart.
        plusk
            The number of vectors saved from the previous iteration.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2519 <slepc4py/SLEPc/EPS.pyx#L2519>`
    
        """
        ...
    def getGDRestart(self) -> tuple[int, int]:
        """Get the number of vectors of the search space after restart.
    
        Not collective.
    
        Get the number of vectors of the search space after restart and
        the number of vectors saved from the previous iteration.
    
        Returns
        -------
        minv: int
            The number of vectors of the search subspace after restart.
        plusk: int
            The number of vectors saved from the previous iteration.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2541 <slepc4py/SLEPc/EPS.pyx#L2541>`
    
        """
        ...
    def setGDInitialSize(self, initialsize: int) -> None:
        """Set the initial size of the searching space.
    
        Logically collective.
    
        Parameters
        ----------
        initialsize
            The number of vectors of the initial searching subspace.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2562 <slepc4py/SLEPc/EPS.pyx#L2562>`
    
        """
        ...
    def getGDInitialSize(self) -> int:
        """Get the initial size of the searching space.
    
        Not collective.
    
        Returns
        -------
        int
            The number of vectors of the initial searching subspace.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2576 <slepc4py/SLEPc/EPS.pyx#L2576>`
    
        """
        ...
    def setGDBOrth(self, borth: bool) -> int:
        """Set the orthogonalization that will be used in the search subspace.
    
        Logically collective.
    
        Set the orthogonalization that will be used in the search
        subspace in case of generalized Hermitian problems.
    
        Parameters
        ----------
        borth
            Whether to B-orthogonalize the search subspace.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2591 <slepc4py/SLEPc/EPS.pyx#L2591>`
    
        """
        ...
    def getGDBOrth(self) -> bool:
        """Get the orthogonalization used in the search subspace.
    
        Not collective.
    
        Get the orthogonalization used in the search subspace in
        case of generalized Hermitian problems.
    
        Returns
        -------
        bool
            Whether to B-orthogonalize the search subspace.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2608 <slepc4py/SLEPc/EPS.pyx#L2608>`
    
        """
        ...
    def setGDDoubleExpansion(self, doubleexp: bool) -> None:
        """Set that the search subspace is expanded with double expansion.
    
        Logically collective.
    
        Set a variant where the search subspace is expanded with
        :math:`K [A x, B x]` (double expansion) instead of the
        classic :math:`K r`, where K is the preconditioner, x the
        selected approximate eigenvector and :math:`r` its associated residual
        vector.
    
        Parameters
        ----------
        doubleexp
            True if using double expansion.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2626 <slepc4py/SLEPc/EPS.pyx#L2626>`
    
        """
        ...
    def getGDDoubleExpansion(self) -> bool:
        """Get a flag indicating whether the double expansion variant is active.
    
        Not collective.
    
        Get a flag indicating whether the double expansion variant
        has been activated or not.
    
        Returns
        -------
        bool
            True if using double expansion.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2646 <slepc4py/SLEPc/EPS.pyx#L2646>`
    
        """
        ...
    def setJDKrylovStart(self, krylovstart: bool = True) -> None:
        """Set (toggle) starting the search subspace with a Krylov basis.
    
        Logically collective.
    
        Parameters
        ----------
        krylovstart
            True if starting the search subspace with a Krylov basis.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2666 <slepc4py/SLEPc/EPS.pyx#L2666>`
    
        """
        ...
    def getJDKrylovStart(self) -> bool:
        """Get a flag indicating if the search subspace is started with a Krylov basis.
    
        Not collective.
    
        Returns
        -------
        bool
            True if starting the search subspace with a Krylov basis.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2680 <slepc4py/SLEPc/EPS.pyx#L2680>`
    
        """
        ...
    def setJDBlockSize(self, bs: int) -> None:
        """Set the number of vectors to be added to the searching space.
    
        Logically collective.
    
        Set the number of vectors to be added to the searching space in every
        iteration.
    
        Parameters
        ----------
        bs
            The number of vectors added to the search space in every iteration.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2695 <slepc4py/SLEPc/EPS.pyx#L2695>`
    
        """
        ...
    def getJDBlockSize(self) -> int:
        """Get the number of vectors to be added to the searching space.
    
        Not collective.
    
        Get the number of vectors to be added to the searching space in every
        iteration.
    
        Returns
        -------
        int
            The number of vectors added to the search space in every iteration.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2712 <slepc4py/SLEPc/EPS.pyx#L2712>`
    
        """
        ...
    def setJDRestart(self, minv: int | None = None, plusk: int | None = None) -> None:
        """Set the number of vectors of the search space after restart.
    
        Logically collective.
    
        Set the number of vectors of the search space after restart and
        the number of vectors saved from the previous iteration.
    
        Parameters
        ----------
        minv
            The number of vectors of the search subspace after restart.
        plusk
            The number of vectors saved from the previous iteration.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2730 <slepc4py/SLEPc/EPS.pyx#L2730>`
    
        """
        ...
    def getJDRestart(self) -> tuple[int, int]:
        """Get the number of vectors of the search space after restart.
    
        Not collective.
    
        Get the number of vectors of the search space after restart and
        the number of vectors saved from the previous iteration.
    
        Returns
        -------
        minv: int
            The number of vectors of the search subspace after restart.
        plusk: int
            The number of vectors saved from the previous iteration.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2752 <slepc4py/SLEPc/EPS.pyx#L2752>`
    
        """
        ...
    def setJDInitialSize(self, initialsize: int) -> None:
        """Set the initial size of the searching space.
    
        Logically collective.
    
        Parameters
        ----------
        initialsize
            The number of vectors of the initial searching subspace.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2773 <slepc4py/SLEPc/EPS.pyx#L2773>`
    
        """
        ...
    def getJDInitialSize(self) -> int:
        """Get the initial size of the searching space.
    
        Not collective.
    
        Returns
        -------
        int
            The number of vectors of the initial searching subspace.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2787 <slepc4py/SLEPc/EPS.pyx#L2787>`
    
        """
        ...
    def setJDFix(self, fix: float) -> None:
        """Set the threshold for changing the target in the correction equation.
    
        Logically collective.
    
        Parameters
        ----------
        fix
            The threshold for changing the target.
    
        Notes
        -----
        The target in the correction equation is fixed at the first iterations.
        When the norm of the residual vector is lower than the fix value,
        the target is set to the corresponding eigenvalue.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2802 <slepc4py/SLEPc/EPS.pyx#L2802>`
    
        """
        ...
    def getJDFix(self) -> float:
        """Get the threshold for changing the target in the correction equation.
    
        Not collective.
    
        Returns
        -------
        float
            The threshold for changing the target.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2822 <slepc4py/SLEPc/EPS.pyx#L2822>`
    
        """
        ...
    def setJDConstCorrectionTol(self, constant: bool) -> None:
        """Deactivate the dynamic stopping criterion.
    
        Logically collective.
    
        Deactivate the dynamic stopping criterion that sets the
        `petsc4py.PETSc.KSP` relative tolerance to ``0.5**i``, where ``i`` is
        the number of `EPS` iterations from the last converged value.
    
        Parameters
        ----------
        constant
            If False, the `petsc4py.PETSc.KSP` relative tolerance is set to ``0.5**i``.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2837 <slepc4py/SLEPc/EPS.pyx#L2837>`
    
        """
        ...
    def getJDConstCorrectionTol(self) -> bool:
        """Get the flag indicating if the dynamic stopping is being used.
    
        Not collective.
    
        Get the flag indicating if the dynamic stopping is being used for
        solving the correction equation.
    
        Returns
        -------
        bool
            True if the dynamic stopping criterion is not being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2855 <slepc4py/SLEPc/EPS.pyx#L2855>`
    
        """
        ...
    def setJDBOrth(self, borth: bool) -> None:
        """Set the orthogonalization that will be used in the search subspace.
    
        Logically collective.
    
        Set the orthogonalization that will be used in the search
        subspace in case of generalized Hermitian problems.
    
        Parameters
        ----------
        borth
            Whether to B-orthogonalize the search subspace.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2873 <slepc4py/SLEPc/EPS.pyx#L2873>`
    
        """
        ...
    def getJDBOrth(self) -> bool:
        """Get the orthogonalization used in the search subspace.
    
        Not collective.
    
        Get the orthogonalization used in the search subspace in
        case of generalized Hermitian problems.
    
        Returns
        -------
        bool
            Whether to B-orthogonalize the search subspace.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2890 <slepc4py/SLEPc/EPS.pyx#L2890>`
    
        """
        ...
    def setRQCGReset(self, nrest: int) -> None:
        """Set the reset parameter of the RQCG iteration.
    
        Logically collective.
    
        Every nrest iterations the solver performs a Rayleigh-Ritz projection
        step.
    
        Parameters
        ----------
        nrest
            The number of iterations between resets.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2910 <slepc4py/SLEPc/EPS.pyx#L2910>`
    
        """
        ...
    def getRQCGReset(self) -> int:
        """Get the reset parameter used in the RQCG method.
    
        Not collective.
    
        Returns
        -------
        int
            The number of iterations between resets.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2927 <slepc4py/SLEPc/EPS.pyx#L2927>`
    
        """
        ...
    def setLOBPCGBlockSize(self, bs: int) -> None:
        """Set the block size of the LOBPCG method.
    
        Logically collective.
    
        Parameters
        ----------
        bs
            The block size.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2942 <slepc4py/SLEPc/EPS.pyx#L2942>`
    
        """
        ...
    def getLOBPCGBlockSize(self) -> int:
        """Get the block size used in the LOBPCG method.
    
        Not collective.
    
        Returns
        -------
        int
            The block size.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2956 <slepc4py/SLEPc/EPS.pyx#L2956>`
    
        """
        ...
    def setLOBPCGRestart(self, restart: float) -> None:
        """Set the restart parameter for the LOBPCG method.
    
        Logically collective.
    
        The meaning of this parameter is the proportion of vectors within the
        current block iterate that must have converged in order to force a
        restart with hard locking.
    
        Parameters
        ----------
        restart
            The percentage of the block of vectors to force a restart.
    
        Notes
        -----
        Allowed values are in the range [0.1,1.0]. The default is 0.9.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2971 <slepc4py/SLEPc/EPS.pyx#L2971>`
    
        """
        ...
    def getLOBPCGRestart(self) -> float:
        """Get the restart parameter used in the LOBPCG method.
    
        Not collective.
    
        Returns
        -------
        float
            The restart parameter.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:2993 <slepc4py/SLEPc/EPS.pyx#L2993>`
    
        """
        ...
    def setLOBPCGLocking(self, lock: bool) -> None:
        """Toggle between locking and non-locking (LOBPCG method).
    
        Logically collective.
    
        Parameters
        ----------
        lock
            True if the locking variant must be selected.
    
        Notes
        -----
        This flag refers to soft locking (converged vectors within the current
        block iterate), since hard locking is always used (when nev is larger
        than the block size).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3008 <slepc4py/SLEPc/EPS.pyx#L3008>`
    
        """
        ...
    def getLOBPCGLocking(self) -> bool:
        """Get the locking flag used in the LOBPCG method.
    
        Not collective.
    
        Returns
        -------
        bool
            The locking flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3028 <slepc4py/SLEPc/EPS.pyx#L3028>`
    
        """
        ...
    def setLyapIIRanks(self, rkc: int | None = None, rkl: int | None = None) -> None:
        """Set the ranks used in the solution of the Lyapunov equation.
    
        Logically collective.
    
        Parameters
        ----------
        rkc
            The compressed rank.
        rkl
            The Lyapunov rank.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3043 <slepc4py/SLEPc/EPS.pyx#L3043>`
    
        """
        ...
    def getLyapIIRanks(self) -> tuple[int, int]:
        """Get the rank values used for the Lyapunov step.
    
        Not collective.
    
        Returns
        -------
        rkc: int
            The compressed rank.
        rkl: int
            The Lyapunov rank.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3062 <slepc4py/SLEPc/EPS.pyx#L3062>`
    
        """
        ...
    def setCISSExtraction(self, extraction: CISSExtraction) -> None:
        """Set the extraction technique used in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        extraction
            The extraction technique.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3082 <slepc4py/SLEPc/EPS.pyx#L3082>`
    
        """
        ...
    def getCISSExtraction(self) -> CISSExtraction:
        """Get the extraction technique used in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        CISSExtraction
            The extraction technique.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3096 <slepc4py/SLEPc/EPS.pyx#L3096>`
    
        """
        ...
    def setCISSQuadRule(self, quad: CISSQuadRule) -> None:
        """Set the quadrature rule used in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        quad
            The quadrature rule.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3111 <slepc4py/SLEPc/EPS.pyx#L3111>`
    
        """
        ...
    def getCISSQuadRule(self) -> CISSQuadRule:
        """Get the quadrature rule used in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        CISSQuadRule
            The quadrature rule.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3125 <slepc4py/SLEPc/EPS.pyx#L3125>`
    
        """
        ...
    def setCISSSizes(self, ip: int | None = None, bs: int | None = None, ms: int | None = None, npart: int | None = None, bsmax: int | None = None, realmats: bool = False) -> None:
        """Set the values of various size parameters in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        ip
            Number of integration points.
        bs
            Block size.
        ms
            Moment size.
        npart
            Number of partitions when splitting the communicator.
        bsmax
            Maximum block size.
        realmats
            True if A and B are real.
    
        Notes
        -----
        The default number of partitions is 1. This means the internal
        `petsc4py.PETSc.KSP` object is shared among all processes of the
        `EPS` communicator. Otherwise, the communicator is split into npart
        communicators, so that ``npart`` `petsc4py.PETSc.KSP` solves proceed
        simultaneously.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3140 <slepc4py/SLEPc/EPS.pyx#L3140>`
    
        """
        ...
    def getCISSSizes(self) -> tuple[int, int, int, int, int, bool]:
        """Get the values of various size parameters in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        ip: int
            Number of integration points.
        bs: int
            Block size.
        ms: int
            Moment size.
        npart: int
            Number of partitions when splitting the communicator.
        bsmax: int
            Maximum block size.
        realmats: bool
            True if A and B are real.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3190 <slepc4py/SLEPc/EPS.pyx#L3190>`
    
        """
        ...
    def setCISSThreshold(self, delta: float | None = None, spur: float | None = None) -> None:
        """Set the values of various threshold parameters in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        delta
            Threshold for numerical rank.
        spur
            Spurious threshold (to discard spurious eigenpairs).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3220 <slepc4py/SLEPc/EPS.pyx#L3220>`
    
        """
        ...
    def getCISSThreshold(self) -> tuple[float, float]:
        """Get the values of various threshold parameters in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        delta: float
            Threshold for numerical rank.
        spur: float
            Spurious threshold (to discard spurious eigenpairs.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3239 <slepc4py/SLEPc/EPS.pyx#L3239>`
    
        """
        ...
    def setCISSRefinement(self, inner: int | None = None, blsize: int | None = None) -> None:
        """Set the values of various refinement parameters in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        inner
            Number of iterative refinement iterations (inner loop).
        blsize
            Number of iterative refinement iterations (blocksize loop).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3257 <slepc4py/SLEPc/EPS.pyx#L3257>`
    
        """
        ...
    def getCISSRefinement(self) -> tuple[int, int]:
        """Get the values of various refinement parameters in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        inner: int
            Number of iterative refinement iterations (inner loop).
        blsize: int
            Number of iterative refinement iterations (blocksize loop).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3276 <slepc4py/SLEPc/EPS.pyx#L3276>`
    
        """
        ...
    def setCISSUseST(self, usest: bool) -> None:
        """Set a flag indicating that the CISS solver will use the `ST` object.
    
        Logically collective.
    
        Set a flag indicating that the CISS solver will use the `ST`
        object for the linear solves.
    
        Parameters
        ----------
        usest
            Whether to use the `ST` object or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3294 <slepc4py/SLEPc/EPS.pyx#L3294>`
    
        """
        ...
    def getCISSUseST(self) -> bool:
        """Get the flag indicating the use of the `ST` object in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        bool
            Whether to use the `ST` object or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3311 <slepc4py/SLEPc/EPS.pyx#L3311>`
    
        """
        ...
    def getCISSKSPs(self) -> list[KSP]:
        """Get the array of linear solver objects associated with the CISS solver.
    
        Not collective.
    
        Returns
        -------
        list of `petsc4py.PETSc.KSP`
            The linear solver objects.
    
        Notes
        -----
        The number of `petsc4py.PETSc.KSP` solvers is equal to the number of
        integration points divided by the number of partitions. This value is
        halved in the case of real matrices with a region centered at the real
        axis.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3326 <slepc4py/SLEPc/EPS.pyx#L3326>`
    
        """
        ...
    @property
    def problem_type(self) -> EPSProblemType:
        """The type of the eigenvalue problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3350 <slepc4py/SLEPc/EPS.pyx#L3350>`
    
        """
        ...
    @property
    def extraction(self) -> EPSExtraction:
        """The type of extraction technique to be employed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3357 <slepc4py/SLEPc/EPS.pyx#L3357>`
    
        """
        ...
    @property
    def which(self) -> EPSWhich:
        """The portion of the spectrum to be sought.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3364 <slepc4py/SLEPc/EPS.pyx#L3364>`
    
        """
        ...
    @property
    def target(self) -> float:
        """The value of the target.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3371 <slepc4py/SLEPc/EPS.pyx#L3371>`
    
        """
        ...
    @property
    def tol(self) -> float:
        """The tolerance.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3378 <slepc4py/SLEPc/EPS.pyx#L3378>`
    
        """
        ...
    @property
    def max_it(self) -> int:
        """The maximum iteration count.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3385 <slepc4py/SLEPc/EPS.pyx#L3385>`
    
        """
        ...
    @property
    def two_sided(self) -> bool:
        """Two-sided that also computes left eigenvectors.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3392 <slepc4py/SLEPc/EPS.pyx#L3392>`
    
        """
        ...
    @property
    def true_residual(self) -> bool:
        """Compute the true residual explicitly.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3399 <slepc4py/SLEPc/EPS.pyx#L3399>`
    
        """
        ...
    @property
    def purify(self) -> bool:
        """Eigenvector purification.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3406 <slepc4py/SLEPc/EPS.pyx#L3406>`
    
        """
        ...
    @property
    def track_all(self) -> bool:
        """Compute the residual norm of all approximate eigenpairs.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3413 <slepc4py/SLEPc/EPS.pyx#L3413>`
    
        """
        ...
    @property
    def st(self) -> ST:
        """The spectral transformation (ST) object associated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3420 <slepc4py/SLEPc/EPS.pyx#L3420>`
    
        """
        ...
    @property
    def bv(self) -> BV:
        """The basis vectors (BV) object associated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3427 <slepc4py/SLEPc/EPS.pyx#L3427>`
    
        """
        ...
    @property
    def rg(self) -> RG:
        """The region (RG) object associated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3434 <slepc4py/SLEPc/EPS.pyx#L3434>`
    
        """
        ...
    @property
    def ds(self) -> DS:
        """The direct solver (DS) object associated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/EPS.pyx:3441 <slepc4py/SLEPc/EPS.pyx#L3441>`
    
        """
        ...

class SVD(Object):
    """SVD."""
    class Type:
        """SVD types.
        
        - `CROSS`:      Eigenproblem with the cross-product matrix.
        - `CYCLIC`:     Eigenproblem with the cyclic matrix.
        - `LAPACK`:     Wrappers to dense SVD solvers in Lapack.
        - `LANCZOS`:    Lanczos.
        - `TRLANCZOS`:  Thick-restart Lanczos.
        - `RANDOMIZED`: Iterative RSVD for low-rank matrices.
        
        Wrappers to external SVD solvers
        (should be enabled during installation of SLEPc)
        
        - `SCALAPACK`:
        - `KSVD`:
        - `ELEMENTAL`:
        - `PRIMME`:
        
        """
        CROSS: str = _def(str, 'CROSS')  #: Object ``CROSS`` of type :class:`str`
        CYCLIC: str = _def(str, 'CYCLIC')  #: Object ``CYCLIC`` of type :class:`str`
        LAPACK: str = _def(str, 'LAPACK')  #: Object ``LAPACK`` of type :class:`str`
        LANCZOS: str = _def(str, 'LANCZOS')  #: Object ``LANCZOS`` of type :class:`str`
        TRLANCZOS: str = _def(str, 'TRLANCZOS')  #: Object ``TRLANCZOS`` of type :class:`str`
        RANDOMIZED: str = _def(str, 'RANDOMIZED')  #: Object ``RANDOMIZED`` of type :class:`str`
        SCALAPACK: str = _def(str, 'SCALAPACK')  #: Object ``SCALAPACK`` of type :class:`str`
        KSVD: str = _def(str, 'KSVD')  #: Object ``KSVD`` of type :class:`str`
        ELEMENTAL: str = _def(str, 'ELEMENTAL')  #: Object ``ELEMENTAL`` of type :class:`str`
        PRIMME: str = _def(str, 'PRIMME')  #: Object ``PRIMME`` of type :class:`str`
    class ProblemType:
        """SVD problem type.
        
        - `STANDARD`:    Standard SVD.
        - `GENERALIZED`: Generalized singular value decomposition (GSVD).
        - `HYPERBOLIC` : Hyperbolic singular value decomposition (HSVD).
        
        """
        STANDARD: int = _def(int, 'STANDARD')  #: Constant ``STANDARD`` of type :class:`int`
        GENERALIZED: int = _def(int, 'GENERALIZED')  #: Constant ``GENERALIZED`` of type :class:`int`
        HYPERBOLIC: int = _def(int, 'HYPERBOLIC')  #: Constant ``HYPERBOLIC`` of type :class:`int`
    class ErrorType:
        """SVD error type to assess accuracy of computed solutions.
        
        - `ABSOLUTE`: Absolute error.
        - `RELATIVE`: Relative error.
        - `NORM`:     Error relative to the matrix norm.
        
        """
        ABSOLUTE: int = _def(int, 'ABSOLUTE')  #: Constant ``ABSOLUTE`` of type :class:`int`
        RELATIVE: int = _def(int, 'RELATIVE')  #: Constant ``RELATIVE`` of type :class:`int`
        NORM: int = _def(int, 'NORM')  #: Constant ``NORM`` of type :class:`int`
    class Which:
        """SVD desired part of spectrum.
        
        - `LARGEST`:  Largest singular values.
        - `SMALLEST`: Smallest singular values.
        
        """
        LARGEST: int = _def(int, 'LARGEST')  #: Constant ``LARGEST`` of type :class:`int`
        SMALLEST: int = _def(int, 'SMALLEST')  #: Constant ``SMALLEST`` of type :class:`int`
    class Conv:
        """SVD convergence test.
        
        - `ABS`:   Absolute convergence test.
        - `REL`:   Convergence test relative to the singular value.
        - `NORM`:  Convergence test relative to the matrix norms.
        - `MAXIT`: No convergence until maximum number of iterations has been reached.
        - `USER`:  User-defined convergence test.
        
        """
        ABS: int = _def(int, 'ABS')  #: Constant ``ABS`` of type :class:`int`
        REL: int = _def(int, 'REL')  #: Constant ``REL`` of type :class:`int`
        NORM: int = _def(int, 'NORM')  #: Constant ``NORM`` of type :class:`int`
        MAXIT: int = _def(int, 'MAXIT')  #: Constant ``MAXIT`` of type :class:`int`
        USER: int = _def(int, 'USER')  #: Constant ``USER`` of type :class:`int`
    class Stop:
        """SVD stopping test.
        
        - `BASIC`:     Default stopping test.
        - `USER`:      User-defined stopping test.
        - `THRESHOLD`: Threshold stopping test.
        
        """
        BASIC: int = _def(int, 'BASIC')  #: Constant ``BASIC`` of type :class:`int`
        USER: int = _def(int, 'USER')  #: Constant ``USER`` of type :class:`int`
        THRESHOLD: int = _def(int, 'THRESHOLD')  #: Constant ``THRESHOLD`` of type :class:`int`
    class ConvergedReason:
        """SVD convergence reasons.
        
        - `CONVERGED_TOL`:          All eigenpairs converged to requested
                                    tolerance.
        - `CONVERGED_USER`:         User-defined convergence criterion satisfied.
        - `CONVERGED_MAXIT`:        Maximum iterations completed in case MAXIT
                                    convergence criterion.
        - `DIVERGED_ITS`:           Maximum number of iterations exceeded.
        - `DIVERGED_BREAKDOWN`:     Solver failed due to breakdown.
        - `DIVERGED_SYMMETRY_LOST`: Underlying indefinite eigensolver was not able
                                    to keep symmetry.
        - `CONVERGED_ITERATING`:    Iteration not finished yet.
        
        """
        CONVERGED_TOL: int = _def(int, 'CONVERGED_TOL')  #: Constant ``CONVERGED_TOL`` of type :class:`int`
        CONVERGED_USER: int = _def(int, 'CONVERGED_USER')  #: Constant ``CONVERGED_USER`` of type :class:`int`
        CONVERGED_MAXIT: int = _def(int, 'CONVERGED_MAXIT')  #: Constant ``CONVERGED_MAXIT`` of type :class:`int`
        DIVERGED_ITS: int = _def(int, 'DIVERGED_ITS')  #: Constant ``DIVERGED_ITS`` of type :class:`int`
        DIVERGED_BREAKDOWN: int = _def(int, 'DIVERGED_BREAKDOWN')  #: Constant ``DIVERGED_BREAKDOWN`` of type :class:`int`
        DIVERGED_SYMMETRY_LOST: int = _def(int, 'DIVERGED_SYMMETRY_LOST')  #: Constant ``DIVERGED_SYMMETRY_LOST`` of type :class:`int`
        CONVERGED_ITERATING: int = _def(int, 'CONVERGED_ITERATING')  #: Constant ``CONVERGED_ITERATING`` of type :class:`int`
        ITERATING: int = _def(int, 'ITERATING')  #: Constant ``ITERATING`` of type :class:`int`
    class TRLanczosGBidiag:
        """SVD TRLanczos bidiagonalization choices for the GSVD case.
        
        - `SINGLE`: Single bidiagonalization (Qa).
        - `UPPER`:  Joint bidiagonalization, both Qa and Qb in upper bidiagonal
                    form.
        - `LOWER`:  Joint bidiagonalization, Qa lower bidiagonal, Qb upper
                    bidiagonal.
        
        """
        SINGLE: int = _def(int, 'SINGLE')  #: Constant ``SINGLE`` of type :class:`int`
        UPPER: int = _def(int, 'UPPER')  #: Constant ``UPPER`` of type :class:`int`
        LOWER: int = _def(int, 'LOWER')  #: Constant ``LOWER`` of type :class:`int`
    def view(self, viewer: Viewer | None = None) -> None:
        """Print the SVD data structure.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:153 <slepc4py/SLEPc/SVD.pyx#L153>`
    
        """
        ...
    def destroy(self) -> Self:
        """Destroy the SVD object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:168 <slepc4py/SLEPc/SVD.pyx#L168>`
    
        """
        ...
    def reset(self) -> None:
        """Reset the SVD object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:178 <slepc4py/SLEPc/SVD.pyx#L178>`
    
        """
        ...
    def create(self, comm: Comm | None = None) -> Self:
        """Create the SVD object.
    
        Collective.
    
        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all processes.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:186 <slepc4py/SLEPc/SVD.pyx#L186>`
    
        """
        ...
    def setType(self, svd_type: Type | str) -> None:
        """Set the particular solver to be used in the SVD object.
    
        Logically collective.
    
        Parameters
        ----------
        svd_type
            The solver to be used.
    
        Notes
        -----
        See `SVD.Type` for available methods. The default is CROSS.
        Normally, it is best to use `setFromOptions()` and then set
        the SVD type from the options database rather than by using
        this routine.  Using the options database provides the user
        with maximum flexibility in evaluating the different available
        methods.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:203 <slepc4py/SLEPc/SVD.pyx#L203>`
    
        """
        ...
    def getType(self) -> str:
        """Get the SVD type of this object.
    
        Not collective.
    
        Returns
        -------
        str
            The solver currently being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:227 <slepc4py/SLEPc/SVD.pyx#L227>`
    
        """
        ...
    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all SVD options in the database.
    
        Not collective.
    
        Returns
        -------
        str
            The prefix string set for this SVD object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:242 <slepc4py/SLEPc/SVD.pyx#L242>`
    
        """
        ...
    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all SVD options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all SVD option requests.
    
        Notes
        -----
        A hyphen (-) must NOT be given at the beginning of the prefix
        name.  The first character of all runtime options is
        AUTOMATICALLY the hyphen.
    
        For example, to distinguish between the runtime options for
        two different SVD contexts, one could call::
    
            S1.setOptionsPrefix("svd1_")
            S2.setOptionsPrefix("svd2_")
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:257 <slepc4py/SLEPc/SVD.pyx#L257>`
    
        """
        ...
    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all SVD options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all SVD option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:284 <slepc4py/SLEPc/SVD.pyx#L284>`
    
        """
        ...
    def setFromOptions(self) -> None:
        """Set SVD options from the options database.
    
        Collective.
    
        This routine must be called before `setUp()` if the user is to be
        allowed to set the solver type.
    
        Notes
        -----
        To see all options, run your program with the ``-help``
        option.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:299 <slepc4py/SLEPc/SVD.pyx#L299>`
    
        """
        ...
    def getProblemType(self) -> ProblemType:
        """Get the problem type from the SVD object.
    
        Not collective.
    
        Returns
        -------
        ProblemType
            The problem type that was previously set.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:315 <slepc4py/SLEPc/SVD.pyx#L315>`
    
        """
        ...
    def setProblemType(self, problem_type: ProblemType) -> None:
        """Set the type of the singular value problem.
    
        Logically collective.
    
        Parameters
        ----------
        problem_type
            The problem type to be set.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:330 <slepc4py/SLEPc/SVD.pyx#L330>`
    
        """
        ...
    def isGeneralized(self) -> bool:
        """Tell if the SVD corresponds to a generalized singular value problem.
    
        Not collective.
    
        Tell whether the SVD object corresponds to a generalized singular
        value problem.
    
        Returns
        -------
        bool
            True if two matrices were set with `setOperators()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:344 <slepc4py/SLEPc/SVD.pyx#L344>`
    
        """
        ...
    def isHyperbolic(self) -> bool:
        """Tell whether the SVD object corresponds to a hyperbolic singular value problem.
    
        Not collective.
    
        Returns
        -------
        bool
            True if the problem was specified as hyperbolic.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:362 <slepc4py/SLEPc/SVD.pyx#L362>`
    
        """
        ...
    def getImplicitTranspose(self) -> bool:
        """Get the mode used to handle the transpose of the matrix associated.
    
        Not collective.
    
        Get the mode used to handle the transpose of the matrix associated
        with the singular value problem.
    
        Returns
        -------
        bool
            How to handle the transpose (implicitly or not).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:379 <slepc4py/SLEPc/SVD.pyx#L379>`
    
        """
        ...
    def setImplicitTranspose(self, mode: bool) -> None:
        """Set how to handle the transpose of the matrix associated.
    
        Logically collective.
    
        Set how to handle the transpose of the matrix associated with the
        singular value problem.
    
        Parameters
        ----------
        impl
            How to handle the transpose (implicitly or not).
    
        Notes
        -----
        By default, the transpose of the matrix is explicitly built
        (if the matrix has defined the MatTranspose operation).
    
        If this flag is set to true, the solver does not build the
        transpose, but handles it implicitly via MatMultTranspose().
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:397 <slepc4py/SLEPc/SVD.pyx#L397>`
    
        """
        ...
    def getWhichSingularTriplets(self) -> Which:
        """Get which singular triplets are to be sought.
    
        Not collective.
    
        Returns
        -------
        Which
            The singular values to be sought (either largest or smallest).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:422 <slepc4py/SLEPc/SVD.pyx#L422>`
    
        """
        ...
    def setWhichSingularTriplets(self, which: Which) -> None:
        """Set which singular triplets are to be sought.
    
        Logically collective.
    
        Parameters
        ----------
        which
            The singular values to be sought (either largest or smallest).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:437 <slepc4py/SLEPc/SVD.pyx#L437>`
    
        """
        ...
    def getThreshold(self) -> tuple[float, bool]:
        """Get the threshold used in the threshold stopping test.
    
        Not collective.
    
        Returns
        -------
        thres: float
            The threshold.
        rel: bool
            Whether the threshold is relative or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:451 <slepc4py/SLEPc/SVD.pyx#L451>`
    
        """
        ...
    def setThreshold(self, thres: float, rel: bool = False) -> None:
        """Set the threshold used in the threshold stopping test.
    
        Logically collective.
    
        Parameters
        ----------
        thres
            The threshold.
        rel
            Whether the threshold is relative or not.
    
        Notes
        -----
        This function internally sets a special stopping test based on
        the threshold, where singular values are computed in sequence
        until one of the computed singular values is below/above the
        threshold (depending on whether largest or smallest singular
        values are computed).
    
        In the case of largest singular values, the threshold can be
        made relative with respect to the largest singular value
        (i.e., the matrix norm).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:469 <slepc4py/SLEPc/SVD.pyx#L469>`
    
        """
        ...
    def getTolerances(self) -> tuple[float, int]:
        """Get the tolerance and maximum iteration count.
    
        Not collective.
    
        Get the tolerance and maximum iteration count used by the default SVD
        convergence tests.
    
        Returns
        -------
        tol: float
            The convergence tolerance.
        max_it: int
            The maximum number of iterations
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:498 <slepc4py/SLEPc/SVD.pyx#L498>`
    
        """
        ...
    def setTolerances(self, tol: float | None = None, max_it: int | None = None) -> None:
        """Set the tolerance and maximum iteration count used.
    
        Logically collective.
    
        Set the tolerance and maximum iteration count used by the default SVD
        convergence tests.
    
        Parameters
        ----------
        tol
            The convergence tolerance.
        max_it
            The maximum number of iterations
    
        Notes
        -----
        Use `DECIDE` for `max_it` to assign a reasonably good value,
        which is dependent on the solution method.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:519 <slepc4py/SLEPc/SVD.pyx#L519>`
    
        """
        ...
    def getConvergenceTest(self) -> Conv:
        """Get the method used to compute the error estimate used in the convergence test.
    
        Not collective.
    
        Returns
        -------
        Conv
            The method used to compute the error estimate
            used in the convergence test.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:546 <slepc4py/SLEPc/SVD.pyx#L546>`
    
        """
        ...
    def setConvergenceTest(self, conv: Conv) -> None:
        """Set how to compute the error estimate used in the convergence test.
    
        Logically collective.
    
        Parameters
        ----------
        conv
            The method used to compute the error estimate
            used in the convergence test.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:562 <slepc4py/SLEPc/SVD.pyx#L562>`
    
        """
        ...
    def getTrackAll(self) -> bool:
        """Get the flag indicating if all residual norms must be computed or not.
    
        Not collective.
    
        Returns
        -------
        bool
            Whether the solver compute all residuals or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:577 <slepc4py/SLEPc/SVD.pyx#L577>`
    
        """
        ...
    def setTrackAll(self, trackall: bool) -> None:
        """Set flag to compute the residual of all singular triplets.
    
        Logically collective.
    
        Set if the solver must compute the residual of all approximate
        singular triplets or not.
    
        Parameters
        ----------
        trackall
            Whether compute all residuals or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:592 <slepc4py/SLEPc/SVD.pyx#L592>`
    
        """
        ...
    def getDimensions(self) -> tuple[int, int, int]:
        """Get the number of singular values to compute and the dimension of the subspace.
    
        Not collective.
    
        Returns
        -------
        nsv: int
            Number of singular values to compute.
        ncv: int
            Maximum dimension of the subspace to be used by the solver.
        mpd: int
            Maximum dimension allowed for the projected problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:609 <slepc4py/SLEPc/SVD.pyx#L609>`
    
        """
        ...
    def setDimensions(self, nsv: int | None = None, ncv: int | None = None, mpd: int | None = None) -> None:
        """Set the number of singular values to compute and the dimension of the subspace.
    
        Logically collective.
    
        Parameters
        ----------
        nsv
            Number of singular values to compute.
        ncv
            Maximum dimension of the subspace to be used by the solver.
        mpd
            Maximum dimension allowed for the projected problem.
    
        Notes
        -----
        Use `DECIDE` for ``ncv`` and ``mpd`` to assign a reasonably good
        value, which is dependent on the solution method.
    
        The parameters ``ncv`` and ``mpd`` are intimately related, so that
        the user is advised to set one of them at most. Normal usage
        is the following:
    
         - In cases where ``nsv`` is small, the user sets ``ncv``
           (a reasonable default is 2 * ``nsv``).
         - In cases where ``nsv`` is large, the user sets ``mpd``.
    
        The value of ``ncv`` should always be between ``nsv`` and (``nsv`` +
        ``mpd``), typically ``ncv`` = ``nsv`` + ``mpd``. If ``nsv`` is not too
        large, ``mpd`` = ``nsv`` is a reasonable choice, otherwise a
        smaller value should be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:630 <slepc4py/SLEPc/SVD.pyx#L630>`
    
        """
        ...
    def getBV(self) -> tuple[BV, BV]:
        """Get the basis vectors objects associated to the SVD object.
    
        Not collective.
    
        Returns
        -------
        V: BV
            The basis vectors context for right singular vectors.
        U: BV
            The basis vectors context for left singular vectors.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:676 <slepc4py/SLEPc/SVD.pyx#L676>`
    
        """
        ...
    def setBV(self, V: BV, U: BV | None = None) -> None:
        """Set basis vectors objects associated to the SVD solver.
    
        Collective.
    
        Parameters
        ----------
        V
            The basis vectors context for right singular vectors.
        U
            The basis vectors context for left singular vectors.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:696 <slepc4py/SLEPc/SVD.pyx#L696>`
    
        """
        ...
    def getDS(self) -> DS:
        """Get the direct solver associated to the singular value solver.
    
        Not collective.
    
        Returns
        -------
        DS
            The direct solver context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:713 <slepc4py/SLEPc/SVD.pyx#L713>`
    
        """
        ...
    def setDS(self, ds: DS) -> None:
        """Set a direct solver object associated to the singular value solver.
    
        Collective.
    
        Parameters
        ----------
        ds
            The direct solver context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:729 <slepc4py/SLEPc/SVD.pyx#L729>`
    
        """
        ...
    def getOperators(self) -> tuple[petsc4py.PETSc.Mat, petsc4py.PETSc.Mat] | tuple[petsc4py.PETSc.Mat, None]:
        """Get the matrices associated with the singular value problem.
    
        Collective.
    
        Returns
        -------
        A: petsc4py.PETSc.Mat
            The matrix associated with the singular value problem.
        B: petsc4py.PETSc.Mat
            The second matrix in the case of GSVD.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:742 <slepc4py/SLEPc/SVD.pyx#L742>`
    
        """
        ...
    def setOperators(self, A: Mat, B: Mat | None = None) -> None:
        """Set the matrices associated with the singular value problem.
    
        Collective.
    
        Parameters
        ----------
        A
            The matrix associated with the singular value problem.
        B
            The second matrix in the case of GSVD; if not provided,
            a usual SVD is assumed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:765 <slepc4py/SLEPc/SVD.pyx#L765>`
    
        """
        ...
    def getSignature(self, omega: petsc4py.PETSc.Vec | None = None) -> petsc4py.PETSc.Vec:
        """Get the signature matrix defining a hyperbolic singular value problem.
    
        Collective.
    
        Parameters
        ----------
        omega
            Optional vector to store the diagonal elements of the signature matrix.
    
        Returns
        -------
        petsc4py.PETSc.Vec
            A vector containing the diagonal elements of the signature matrix.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:782 <slepc4py/SLEPc/SVD.pyx#L782>`
    
        """
        ...
    def setSignature(self, omega: Vec | None = None) -> None:
        """Set the signature matrix defining a hyperbolic singular value problem.
    
        Collective.
    
        Parameters
        ----------
        omega
            A vector containing the diagonal elements of the signature matrix.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:807 <slepc4py/SLEPc/SVD.pyx#L807>`
    
        """
        ...
    def setInitialSpace(self, spaceright: list[Vec] | None = None, spaceleft: list[Vec] | None = None) -> None:
        """Set the initial spaces from which the SVD solver starts to iterate.
    
        Collective.
    
        Parameters
        ----------
        spaceright
            The right initial space.
        spaceleft
            The left initial space.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:823 <slepc4py/SLEPc/SVD.pyx#L823>`
    
        """
        ...
    def setStoppingTest(self, stopping: SVDStoppingFunction | None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Set a function to decide when to stop the outer iteration of the eigensolver.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:857 <slepc4py/SLEPc/SVD.pyx#L857>`
    
        """
        ...
    def getStoppingTest(self) -> SVDStoppingFunction:
        """Get the stopping function.
    
        Not collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:877 <slepc4py/SLEPc/SVD.pyx#L877>`
    
        """
        ...
    def setMonitor(self, monitor: SVDMonitorFunction | None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Append a monitor function to the list of monitors.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:887 <slepc4py/SLEPc/SVD.pyx#L887>`
    
        """
        ...
    def getMonitor(self) -> SVDMonitorFunction:
        """Get the list of monitor functions.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:908 <slepc4py/SLEPc/SVD.pyx#L908>`
    
        """
        ...
    def cancelMonitor(self) -> None:
        """Clear all monitors for an `SVD` object.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:912 <slepc4py/SLEPc/SVD.pyx#L912>`
    
        """
        ...
    def setUp(self) -> None:
        """Set up all the necessary internal data structures.
    
        Collective.
    
        Set up all the internal data structures necessary for the execution of
        the singular value solver.
    
        Notes
        -----
        This function need not be called explicitly in most cases,
        since `solve()` calls it. It can be useful when one wants to
        measure the set-up time separately from the solve time.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:923 <slepc4py/SLEPc/SVD.pyx#L923>`
    
        """
        ...
    def solve(self) -> None:
        """Solve the singular value problem.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:940 <slepc4py/SLEPc/SVD.pyx#L940>`
    
        """
        ...
    def getIterationNumber(self) -> int:
        """Get the current iteration number.
    
        Not collective.
    
        If the call to `solve()` is complete, then it returns the number of
        iterations carried out by the solution method.
    
        Returns
        -------
        int
            Iteration number.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:948 <slepc4py/SLEPc/SVD.pyx#L948>`
    
        """
        ...
    def getConvergedReason(self) -> ConvergedReason:
        """Get the reason why the `solve()` iteration was stopped.
    
        Not collective.
    
        Returns
        -------
        ConvergedReason
            Negative value indicates diverged, positive value converged.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:966 <slepc4py/SLEPc/SVD.pyx#L966>`
    
        """
        ...
    def getConverged(self) -> int:
        """Get the number of converged singular triplets.
    
        Not collective.
    
        Returns
        -------
        int
            Number of converged singular triplets.
    
        Notes
        -----
        This function should be called after `solve()` has finished.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:981 <slepc4py/SLEPc/SVD.pyx#L981>`
    
        """
        ...
    def getValue(self, i: int) -> float:
        """Get the i-th singular value as computed by `solve()`.
    
        Collective.
    
        Parameters
        ----------
        i
            Index of the solution to be obtained.
    
        Returns
        -------
        float
            The computed singular value.
    
        Notes
        -----
        The index ``i`` should be a value between ``0`` and
        ``nconv-1`` (see `getConverged()`. Singular triplets are
        indexed according to the ordering criterion established with
        `setWhichSingularTriplets()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1000 <slepc4py/SLEPc/SVD.pyx#L1000>`
    
        """
        ...
    def getVectors(self, i: int, U: Vec, V: Vec) -> None:
        """Get the i-th left and right singular vectors as computed by `solve()`.
    
        Collective.
    
        Parameters
        ----------
        i
            Index of the solution to be obtained.
        U
            Placeholder for the returned left singular vector.
        V
            Placeholder for the returned right singular vector.
    
        Notes
        -----
        The index ``i`` should be a value between ``0`` and
        ``nconv-1`` (see `getConverged()`. Singular triplets are
        indexed according to the ordering criterion established with
        `setWhichSingularTriplets()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1027 <slepc4py/SLEPc/SVD.pyx#L1027>`
    
        """
        ...
    def getSingularTriplet(self, i: int, U: Vec | None = None, V: Vec | None = None) -> float:
        """Get the i-th triplet of the singular value decomposition.
    
        Collective.
    
        Get the i-th triplet of the singular value decomposition as computed
        by `solve()`. The solution consists of the singular value and its left
        and right singular vectors.
    
        Parameters
        ----------
        i
            Index of the solution to be obtained.
        U
            Placeholder for the returned left singular vector.
        V
           Placeholder for the returned right singular vector.
    
        Returns
        -------
        float
            The computed singular value.
    
        Notes
        -----
        The index ``i`` should be a value between ``0`` and
        ``nconv-1`` (see `getConverged()`. Singular triplets are
        indexed according to the ordering criterion established with
        `setWhichSingularTriplets()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1052 <slepc4py/SLEPc/SVD.pyx#L1052>`
    
        """
        ...
    def computeError(self, i: int, etype: ErrorType | None = None) -> float:
        """Compute the error associated with the i-th singular triplet.
    
        Collective.
    
        Compute the error (based on the residual norm) associated with the
        i-th singular triplet.
    
        Parameters
        ----------
        i
            Index of the solution to be considered.
        etype
            The error type to compute.
    
        Returns
        -------
        float
            The relative error bound, computed in various ways from the
            residual norm :math:`\sqrt{n_1^2+n_2^2}` where
            :math:`n_1 = \|A v - \sigma u\|_2`,
            :math:`n_2 = \|A^T u - \sigma v\|_2`, :math:`\sigma`
            is the singular value, :math:`u` and :math:`v` are the left and
            right singular vectors.
    
        Notes
        -----
        The index ``i`` should be a value between ``0`` and
        ``nconv-1`` (see `getConverged()`).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1091 <slepc4py/SLEPc/SVD.pyx#L1091>`
    
        """
        ...
    def errorView(self, etype: ErrorType | None = None, viewer: petsc4py.PETSc.Viewer | None = None) -> None:
        """Display the errors associated with the computed solution.
    
        Collective.
    
        Display the errors and the eigenvalues.
    
        Parameters
        ----------
        etype
            The error type to compute.
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
        Notes
        -----
        By default, this function checks the error of all eigenpairs and prints
        the eigenvalues if all of them are below the requested tolerance.
        If the viewer has format ``ASCII_INFO_DETAIL`` then a table with
        eigenvalues and corresponding errors is printed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1128 <slepc4py/SLEPc/SVD.pyx#L1128>`
    
        """
        ...
    def valuesView(self, viewer: Viewer | None = None) -> None:
        """Display the computed singular values in a viewer.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1157 <slepc4py/SLEPc/SVD.pyx#L1157>`
    
        """
        ...
    def vectorsView(self, viewer: Viewer | None = None) -> None:
        """Output computed singular vectors to a viewer.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1172 <slepc4py/SLEPc/SVD.pyx#L1172>`
    
        """
        ...
    def setCrossEPS(self, eps: EPS) -> None:
        """Set an eigensolver object associated to the singular value solver.
    
        Collective.
    
        Parameters
        ----------
        eps
            The eigensolver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1189 <slepc4py/SLEPc/SVD.pyx#L1189>`
    
        """
        ...
    def getCrossEPS(self) -> EPS:
        """Get the eigensolver object associated to the singular value solver.
    
        Collective.
    
        Returns
        -------
        EPS
            The eigensolver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1202 <slepc4py/SLEPc/SVD.pyx#L1202>`
    
        """
        ...
    def setCrossExplicitMatrix(self, flag: bool = True) -> None:
        """Set if the eigensolver operator :math:`A^T A` must be computed.
    
        Logically collective.
    
        Parameters
        ----------
        flag
            True to build :math:`A^T A` explicitly.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1218 <slepc4py/SLEPc/SVD.pyx#L1218>`
    
        """
        ...
    def getCrossExplicitMatrix(self) -> bool:
        """Get the flag indicating if ``A^T*A`` is built explicitly.
    
        Not collective.
    
        Returns
        -------
        bool
            True if ``A^T*A`` is built explicitly.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1232 <slepc4py/SLEPc/SVD.pyx#L1232>`
    
        """
        ...
    def setCyclicEPS(self, eps: EPS) -> None:
        """Set an eigensolver object associated to the singular value solver.
    
        Collective.
    
        Parameters
        ----------
        eps
            The eigensolver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1247 <slepc4py/SLEPc/SVD.pyx#L1247>`
    
        """
        ...
    def getCyclicEPS(self) -> EPS:
        """Get the eigensolver object associated to the singular value solver.
    
        Collective.
    
        Returns
        -------
        EPS
            The eigensolver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1260 <slepc4py/SLEPc/SVD.pyx#L1260>`
    
        """
        ...
    def setCyclicExplicitMatrix(self, flag: bool = True) -> None:
        """Set if the eigensolver operator ``H(A)`` must be computed explicitly.
    
        Logically collective.
    
        Set if the eigensolver operator :math:`H(A) = [ 0\; A ; A^T\; 0 ]` must be
        computed explicitly.
    
        Parameters
        ----------
        flag
            True if :math:`H(A)` is built explicitly.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1276 <slepc4py/SLEPc/SVD.pyx#L1276>`
    
        """
        ...
    def getCyclicExplicitMatrix(self) -> bool:
        """Get the flag indicating if :math:`H(A)` is built explicitly.
    
        Not collective.
    
        Get the flag indicating if :math:`H(A) = [ 0\; A ; A^T\; 0 ]` is built
        explicitly.
    
        Returns
        -------
        bool
            True if :math:`H(A)` is built explicitly.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1293 <slepc4py/SLEPc/SVD.pyx#L1293>`
    
        """
        ...
    def setLanczosOneSide(self, flag: bool = True) -> None:
        """Set if the variant of the Lanczos method to be used is one-sided or two-sided.
    
        Logically collective.
    
        Parameters
        ----------
        flag
            True if the method is one-sided.
    
        Notes
        -----
        By default, a two-sided variant is selected, which is
        sometimes slightly more robust. However, the one-sided variant
        is faster because it avoids the orthogonalization associated
        to left singular vectors. It also saves the memory required
        for storing such vectors.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1311 <slepc4py/SLEPc/SVD.pyx#L1311>`
    
        """
        ...
    def getLanczosOneSide(self) -> bool:
        """Get if the variant of the Lanczos method to be used is one-sided or two-sided.
    
        Not collective.
    
        Returns
        -------
        bool
            True if the method is one-sided.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1333 <slepc4py/SLEPc/SVD.pyx#L1333>`
    
        """
        ...
    def setTRLanczosOneSide(self, flag: bool = True) -> None:
        """Set if the variant of the method to be used is one-sided or two-sided.
    
        Logically collective.
    
        Set if the variant of the thick-restart Lanczos method to be used is
        one-sided or two-sided.
    
        Parameters
        ----------
        flag
            True if the method is one-sided.
    
        Notes
        -----
        By default, a two-sided variant is selected, which is
        sometimes slightly more robust. However, the one-sided variant
        is faster because it avoids the orthogonalization associated
        to left singular vectors.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1348 <slepc4py/SLEPc/SVD.pyx#L1348>`
    
        """
        ...
    def getTRLanczosOneSide(self) -> bool:
        """Get if the variant of the method to be used is one-sided or two-sided.
    
        Not collective.
    
        Get if the variant of the thick-restart Lanczos method to be used is
        one-sided or two-sided.
    
        Returns
        -------
        bool
            True if the method is one-sided.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1372 <slepc4py/SLEPc/SVD.pyx#L1372>`
    
        """
        ...
    def setTRLanczosGBidiag(self, bidiag: TRLanczosGBidiag) -> None:
        """Set the bidiagonalization choice to use in the GSVD TRLanczos solver.
    
        Logically collective.
    
        Parameters
        ----------
        bidiag
            The bidiagonalization choice.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1390 <slepc4py/SLEPc/SVD.pyx#L1390>`
    
        """
        ...
    def getTRLanczosGBidiag(self) -> TRLanczosGBidiag:
        """Get bidiagonalization choice used in the GSVD TRLanczos solver.
    
        Not collective.
    
        Returns
        -------
        TRLanczosGBidiag
            The bidiagonalization choice.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1404 <slepc4py/SLEPc/SVD.pyx#L1404>`
    
        """
        ...
    def setTRLanczosRestart(self, keep: float) -> None:
        """Set the restart parameter for the thick-restart Lanczos method.
    
        Logically collective.
    
        Set the restart parameter for the thick-restart Lanczos method, in
        particular the proportion of basis vectors that must be kept
        after restart.
    
        Parameters
        ----------
        keep
            The number of vectors to be kept at restart.
    
        Notes
        -----
        Allowed values are in the range [0.1,0.9]. The default is 0.5.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1419 <slepc4py/SLEPc/SVD.pyx#L1419>`
    
        """
        ...
    def getTRLanczosRestart(self) -> float:
        """Get the restart parameter used in the thick-restart Lanczos method.
    
        Not collective.
    
        Returns
        -------
        float
            The number of vectors to be kept at restart.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1441 <slepc4py/SLEPc/SVD.pyx#L1441>`
    
        """
        ...
    def setTRLanczosLocking(self, lock: bool) -> None:
        """Toggle between locking and non-locking variants of the method.
    
        Logically collective.
    
        Toggle between locking and non-locking variants of the thick-restart
        Lanczos method.
    
        Parameters
        ----------
        lock
            True if the locking variant must be selected.
    
        Notes
        -----
        The default is to lock converged singular triplets when the method restarts.
        This behavior can be changed so that all directions are kept in the
        working subspace even if already converged to working accuracy (the
        non-locking variant).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1456 <slepc4py/SLEPc/SVD.pyx#L1456>`
    
        """
        ...
    def getTRLanczosLocking(self) -> bool:
        """Get the locking flag used in the thick-restart Lanczos method.
    
        Not collective.
    
        Returns
        -------
        bool
            The locking flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1480 <slepc4py/SLEPc/SVD.pyx#L1480>`
    
        """
        ...
    def setTRLanczosKSP(self, ksp: petsc4py.PETSc.KSP) -> None:
        """Set a linear solver object associated to the SVD solver.
    
        Collective.
    
        Parameters
        ----------
        ``ksp``
            The linear solver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1495 <slepc4py/SLEPc/SVD.pyx#L1495>`
    
        """
        ...
    def getTRLanczosKSP(self) -> KSP:
        """Get the linear solver object associated with the SVD solver.
    
        Collective.
    
        Returns
        -------
        `petsc4py.PETSc.KSP`
            The linear solver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1508 <slepc4py/SLEPc/SVD.pyx#L1508>`
    
        """
        ...
    def setTRLanczosExplicitMatrix(self, flag: bool = True) -> None:
        """Set if the matrix :math:`Z=[A;B]` must be built explicitly.
    
        Logically collective.
    
        Parameters
        ----------
        flag
            True if :math:`Z=[A;B]` is built explicitly.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1524 <slepc4py/SLEPc/SVD.pyx#L1524>`
    
        """
        ...
    def getTRLanczosExplicitMatrix(self) -> bool:
        """Get the flag indicating if :math:`Z=[A;B]` is built explicitly.
    
        Not collective.
    
        Returns
        -------
        bool
            True if :math:`Z=[A;B]` is built explicitly.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1538 <slepc4py/SLEPc/SVD.pyx#L1538>`
    
        """
        ...
    @property
    def problem_type(self) -> SVDProblemType:
        """The type of the eigenvalue problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1557 <slepc4py/SLEPc/SVD.pyx#L1557>`
    
        """
        ...
    @property
    def transpose_mode(self) -> bool:
        """How to handle the transpose of the matrix.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1564 <slepc4py/SLEPc/SVD.pyx#L1564>`
    
        """
        ...
    @property
    def which(self) -> SVDWhich:
        """The portion of the spectrum to be sought.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1571 <slepc4py/SLEPc/SVD.pyx#L1571>`
    
        """
        ...
    @property
    def tol(self) -> float:
        """The tolerance.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1578 <slepc4py/SLEPc/SVD.pyx#L1578>`
    
        """
        ...
    @property
    def max_it(self) -> int:
        """The maximum iteration count.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1585 <slepc4py/SLEPc/SVD.pyx#L1585>`
    
        """
        ...
    @property
    def track_all(self) -> bool:
        """Compute the residual norm of all approximate eigenpairs.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1592 <slepc4py/SLEPc/SVD.pyx#L1592>`
    
        """
        ...
    @property
    def ds(self) -> DS:
        """The direct solver (DS) object associated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/SVD.pyx:1599 <slepc4py/SLEPc/SVD.pyx#L1599>`
    
        """
        ...

class PEP(Object):
    """PEP."""
    class Type:
        """PEP type.
        
        Polynomial eigensolvers.
        
        - `LINEAR`:   Linearization via EPS.
        - `QARNOLDI`: Q-Arnoldi for quadratic problems.
        - `TOAR`:     Two-level orthogonal Arnoldi.
        - `STOAR`:    Symmetric TOAR.
        - `JD`:       Polynomial Jacobi-Davidson.
        - `CISS`:     Contour integral spectrum slice.
        
        """
        LINEAR: str = _def(str, 'LINEAR')  #: Object ``LINEAR`` of type :class:`str`
        QARNOLDI: str = _def(str, 'QARNOLDI')  #: Object ``QARNOLDI`` of type :class:`str`
        TOAR: str = _def(str, 'TOAR')  #: Object ``TOAR`` of type :class:`str`
        STOAR: str = _def(str, 'STOAR')  #: Object ``STOAR`` of type :class:`str`
        JD: str = _def(str, 'JD')  #: Object ``JD`` of type :class:`str`
        CISS: str = _def(str, 'CISS')  #: Object ``CISS`` of type :class:`str`
    class ProblemType:
        """PEP problem type.
        
        - `GENERAL`:    No structure.
        - `HERMITIAN`:  Hermitian structure.
        - `HYPERBOLIC`: QEP with Hermitian matrices, :math:`M>0`,
                        :math:`(x^TCx)^2 > 4(x^TMx)(x^TKx)`.
        - `GYROSCOPIC`: QEP with :math:`M`, :math:`K`  Hermitian,
                        :math:`M>0`, :math:`C` skew-Hermitian.
        
        """
        GENERAL: int = _def(int, 'GENERAL')  #: Constant ``GENERAL`` of type :class:`int`
        HERMITIAN: int = _def(int, 'HERMITIAN')  #: Constant ``HERMITIAN`` of type :class:`int`
        HYPERBOLIC: int = _def(int, 'HYPERBOLIC')  #: Constant ``HYPERBOLIC`` of type :class:`int`
        GYROSCOPIC: int = _def(int, 'GYROSCOPIC')  #: Constant ``GYROSCOPIC`` of type :class:`int`
    class Which:
        """PEP desired part of spectrum.
        
        - `LARGEST_MAGNITUDE`:  Largest magnitude (default).
        - `SMALLEST_MAGNITUDE`: Smallest magnitude.
        - `LARGEST_REAL`:       Largest real parts.
        - `SMALLEST_REAL`:      Smallest real parts.
        - `LARGEST_IMAGINARY`:  Largest imaginary parts in magnitude.
        - `SMALLEST_IMAGINARY`: Smallest imaginary parts in magnitude.
        - `TARGET_MAGNITUDE`:   Closest to target (in magnitude).
        - `TARGET_REAL`:        Real part closest to target.
        - `TARGET_IMAGINARY`:   Imaginary part closest to target.
        - `ALL`:                All eigenvalues in an interval.
        - `USER`:               User-defined criterion.
        
        """
        LARGEST_MAGNITUDE: int = _def(int, 'LARGEST_MAGNITUDE')  #: Constant ``LARGEST_MAGNITUDE`` of type :class:`int`
        SMALLEST_MAGNITUDE: int = _def(int, 'SMALLEST_MAGNITUDE')  #: Constant ``SMALLEST_MAGNITUDE`` of type :class:`int`
        LARGEST_REAL: int = _def(int, 'LARGEST_REAL')  #: Constant ``LARGEST_REAL`` of type :class:`int`
        SMALLEST_REAL: int = _def(int, 'SMALLEST_REAL')  #: Constant ``SMALLEST_REAL`` of type :class:`int`
        LARGEST_IMAGINARY: int = _def(int, 'LARGEST_IMAGINARY')  #: Constant ``LARGEST_IMAGINARY`` of type :class:`int`
        SMALLEST_IMAGINARY: int = _def(int, 'SMALLEST_IMAGINARY')  #: Constant ``SMALLEST_IMAGINARY`` of type :class:`int`
        TARGET_MAGNITUDE: int = _def(int, 'TARGET_MAGNITUDE')  #: Constant ``TARGET_MAGNITUDE`` of type :class:`int`
        TARGET_REAL: int = _def(int, 'TARGET_REAL')  #: Constant ``TARGET_REAL`` of type :class:`int`
        TARGET_IMAGINARY: int = _def(int, 'TARGET_IMAGINARY')  #: Constant ``TARGET_IMAGINARY`` of type :class:`int`
        ALL: int = _def(int, 'ALL')  #: Constant ``ALL`` of type :class:`int`
        USER: int = _def(int, 'USER')  #: Constant ``USER`` of type :class:`int`
    class Basis:
        """PEP basis type for the representation of the polynomial.
        
        - `MONOMIAL`:   Monomials (default).
        - `CHEBYSHEV1`: Chebyshev polynomials of the 1st kind.
        - `CHEBYSHEV2`: Chebyshev polynomials of the 2nd kind.
        - `LEGENDRE`:   Legendre polynomials.
        - `LAGUERRE`:   Laguerre polynomials.
        - `HERMITE`:    Hermite polynomials.
        
        """
        MONOMIAL: int = _def(int, 'MONOMIAL')  #: Constant ``MONOMIAL`` of type :class:`int`
        CHEBYSHEV1: int = _def(int, 'CHEBYSHEV1')  #: Constant ``CHEBYSHEV1`` of type :class:`int`
        CHEBYSHEV2: int = _def(int, 'CHEBYSHEV2')  #: Constant ``CHEBYSHEV2`` of type :class:`int`
        LEGENDRE: int = _def(int, 'LEGENDRE')  #: Constant ``LEGENDRE`` of type :class:`int`
        LAGUERRE: int = _def(int, 'LAGUERRE')  #: Constant ``LAGUERRE`` of type :class:`int`
        HERMITE: int = _def(int, 'HERMITE')  #: Constant ``HERMITE`` of type :class:`int`
    class Scale:
        """PEP scaling strategy.
        
        - `NONE`:     No scaling.
        - `SCALAR`:   Parameter scaling.
        - `DIAGONAL`: Diagonal scaling.
        - `BOTH`:     Both parameter and diagonal scaling.
        
        """
        NONE: int = _def(int, 'NONE')  #: Constant ``NONE`` of type :class:`int`
        SCALAR: int = _def(int, 'SCALAR')  #: Constant ``SCALAR`` of type :class:`int`
        DIAGONAL: int = _def(int, 'DIAGONAL')  #: Constant ``DIAGONAL`` of type :class:`int`
        BOTH: int = _def(int, 'BOTH')  #: Constant ``BOTH`` of type :class:`int`
    class Refine:
        """PEP refinement strategy.
        
        - `NONE`:     No refinement.
        - `SIMPLE`:   Refine eigenpairs one by one.
        - `MULTIPLE`: Refine all eigenpairs simultaneously (invariant pair).
        
        """
        NONE: int = _def(int, 'NONE')  #: Constant ``NONE`` of type :class:`int`
        SIMPLE: int = _def(int, 'SIMPLE')  #: Constant ``SIMPLE`` of type :class:`int`
        MULTIPLE: int = _def(int, 'MULTIPLE')  #: Constant ``MULTIPLE`` of type :class:`int`
    class RefineScheme:
        """PEP scheme for solving linear systems during iterative refinement.
        
        - `SCHUR`:    Schur complement.
        - `MBE`:      Mixed block elimination.
        - `EXPLICIT`: Build the explicit matrix.
        
        """
        SCHUR: int = _def(int, 'SCHUR')  #: Constant ``SCHUR`` of type :class:`int`
        MBE: int = _def(int, 'MBE')  #: Constant ``MBE`` of type :class:`int`
        EXPLICIT: int = _def(int, 'EXPLICIT')  #: Constant ``EXPLICIT`` of type :class:`int`
    class Extract:
        """PEP extraction strategy used.
        
        PEP extraction strategy used to obtain eigenvectors of the PEP from the
        eigenvectors of the linearization.
        
        - `NONE`:       Use the first block.
        - `NORM`:       Use the first or last block depending on norm of H.
        - `RESIDUAL`:   Use the block with smallest residual.
        - `STRUCTURED`: Combine all blocks in a certain way.
        
        """
        NONE: int = _def(int, 'NONE')  #: Constant ``NONE`` of type :class:`int`
        NORM: int = _def(int, 'NORM')  #: Constant ``NORM`` of type :class:`int`
        RESIDUAL: int = _def(int, 'RESIDUAL')  #: Constant ``RESIDUAL`` of type :class:`int`
        STRUCTURED: int = _def(int, 'STRUCTURED')  #: Constant ``STRUCTURED`` of type :class:`int`
    class ErrorType:
        """PEP error type to assess accuracy of computed solutions.
        
        - `ABSOLUTE`: Absolute error.
        - `RELATIVE`: Relative error.
        - `BACKWARD`: Backward error.
        
        """
        ABSOLUTE: int = _def(int, 'ABSOLUTE')  #: Constant ``ABSOLUTE`` of type :class:`int`
        RELATIVE: int = _def(int, 'RELATIVE')  #: Constant ``RELATIVE`` of type :class:`int`
        BACKWARD: int = _def(int, 'BACKWARD')  #: Constant ``BACKWARD`` of type :class:`int`
    class Conv:
        """PEP convergence test.
        
        - `ABS`:  Absolute convergence test.
        - `REL`:  Convergence test relative to the eigenvalue.
        - `NORM`: Convergence test relative to the matrix norms.
        - `USER`: User-defined convergence test.
        
        """
        ABS: int = _def(int, 'ABS')  #: Constant ``ABS`` of type :class:`int`
        REL: int = _def(int, 'REL')  #: Constant ``REL`` of type :class:`int`
        NORM: int = _def(int, 'NORM')  #: Constant ``NORM`` of type :class:`int`
        USER: int = _def(int, 'USER')  #: Constant ``USER`` of type :class:`int`
    class Stop:
        """PEP stopping test.
        
        - `BASIC`: Default stopping test.
        - `USER`:  User-defined stopping test.
        
        """
        BASIC: int = _def(int, 'BASIC')  #: Constant ``BASIC`` of type :class:`int`
        USER: int = _def(int, 'USER')  #: Constant ``USER`` of type :class:`int`
    class ConvergedReason:
        """PEP convergence reasons.
        
        - `CONVERGED_TOL`:          All eigenpairs converged to requested tolerance.
        - `CONVERGED_USER`:         User-defined convergence criterion satisfied.
        - `DIVERGED_ITS`:           Maximum number of iterations exceeded.
        - `DIVERGED_BREAKDOWN`:     Solver failed due to breakdown.
        - `DIVERGED_SYMMETRY_LOST`: Lanczos-type method could not preserve symmetry.
        - `CONVERGED_ITERATING`:    Iteration not finished yet.
        
        """
        CONVERGED_TOL: int = _def(int, 'CONVERGED_TOL')  #: Constant ``CONVERGED_TOL`` of type :class:`int`
        CONVERGED_USER: int = _def(int, 'CONVERGED_USER')  #: Constant ``CONVERGED_USER`` of type :class:`int`
        DIVERGED_ITS: int = _def(int, 'DIVERGED_ITS')  #: Constant ``DIVERGED_ITS`` of type :class:`int`
        DIVERGED_BREAKDOWN: int = _def(int, 'DIVERGED_BREAKDOWN')  #: Constant ``DIVERGED_BREAKDOWN`` of type :class:`int`
        DIVERGED_SYMMETRY_LOST: int = _def(int, 'DIVERGED_SYMMETRY_LOST')  #: Constant ``DIVERGED_SYMMETRY_LOST`` of type :class:`int`
        CONVERGED_ITERATING: int = _def(int, 'CONVERGED_ITERATING')  #: Constant ``CONVERGED_ITERATING`` of type :class:`int`
        ITERATING: int = _def(int, 'ITERATING')  #: Constant ``ITERATING`` of type :class:`int`
    class JDProjection:
        """PEP type of projection to be used in the Jacobi-Davidson solver.
        
        - `HARMONIC`:   Harmonic projection.
        - `ORTHOGONAL`: Orthogonal projection.
        
        """
        HARMONIC: int = _def(int, 'HARMONIC')  #: Constant ``HARMONIC`` of type :class:`int`
        ORTHOGONAL: int = _def(int, 'ORTHOGONAL')  #: Constant ``ORTHOGONAL`` of type :class:`int`
    class CISSExtraction:
        """PEP CISS extraction technique.
        
        - `RITZ`:   Ritz extraction.
        - `HANKEL`: Extraction via Hankel eigenproblem.
        - `CAA`:    Communication-avoiding Arnoldi.
        
        """
        RITZ: int = _def(int, 'RITZ')  #: Constant ``RITZ`` of type :class:`int`
        HANKEL: int = _def(int, 'HANKEL')  #: Constant ``HANKEL`` of type :class:`int`
        CAA: int = _def(int, 'CAA')  #: Constant ``CAA`` of type :class:`int`
    def view(self, viewer: Viewer | None = None) -> None:
        """Print the PEP data structure.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:243 <slepc4py/SLEPc/PEP.pyx#L243>`
    
        """
        ...
    def destroy(self) -> Self:
        """Destroy the PEP object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:258 <slepc4py/SLEPc/PEP.pyx#L258>`
    
        """
        ...
    def reset(self) -> None:
        """Reset the PEP object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:268 <slepc4py/SLEPc/PEP.pyx#L268>`
    
        """
        ...
    def create(self, comm: Comm | None = None) -> Self:
        """Create the PEP object.
    
        Collective.
    
        Parameters
        ----------
        comm
            MPI communicator. If not provided, it defaults to all processes.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:276 <slepc4py/SLEPc/PEP.pyx#L276>`
    
        """
        ...
    def setType(self, pep_type: Type | str) -> None:
        """Set the particular solver to be used in the PEP object.
    
        Logically collective.
    
        Parameters
        ----------
        pep_type
            The solver to be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:293 <slepc4py/SLEPc/PEP.pyx#L293>`
    
        """
        ...
    def getType(self) -> str:
        """Get the PEP type of this object.
    
        Not collective.
    
        Returns
        -------
        str
            The solver currently being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:308 <slepc4py/SLEPc/PEP.pyx#L308>`
    
        """
        ...
    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all PEP options in the database.
    
        Not collective.
    
        Returns
        -------
        str
            The prefix string set for this PEP object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:323 <slepc4py/SLEPc/PEP.pyx#L323>`
    
        """
        ...
    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all PEP options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all PEP option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:338 <slepc4py/SLEPc/PEP.pyx#L338>`
    
        """
        ...
    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all PEP options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all PEP option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:353 <slepc4py/SLEPc/PEP.pyx#L353>`
    
        """
        ...
    def setFromOptions(self) -> None:
        """Set PEP options from the options database.
    
        Collective.
    
        This routine must be called before `setUp()` if the user is to be
        allowed to set the solver type.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:368 <slepc4py/SLEPc/PEP.pyx#L368>`
    
        """
        ...
    def getBasis(self) -> Basis:
        """Get the type of polynomial basis used.
    
        Not collective.
    
        Get the type of polynomial basis used to describe the polynomial
        eigenvalue problem.
    
        Returns
        -------
        Basis
            The basis that was previously set.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:379 <slepc4py/SLEPc/PEP.pyx#L379>`
    
        """
        ...
    def setBasis(self, basis: Basis) -> None:
        """Set the type of polynomial basis used.
    
        Logically collective.
    
        Set the type of polynomial basis used to describe the polynomial
        eigenvalue problem.
    
        Parameters
        ----------
        basis
            The basis to be set.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:397 <slepc4py/SLEPc/PEP.pyx#L397>`
    
        """
        ...
    def getProblemType(self) -> ProblemType:
        """Get the problem type from the PEP object.
    
        Not collective.
    
        Returns
        -------
        ProblemType
            The problem type that was previously set.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:414 <slepc4py/SLEPc/PEP.pyx#L414>`
    
        """
        ...
    def setProblemType(self, problem_type: ProblemType) -> None:
        """Set the type of the eigenvalue problem.
    
        Logically collective.
    
        Parameters
        ----------
        problem_type
            The problem type to be set.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:429 <slepc4py/SLEPc/PEP.pyx#L429>`
    
        """
        ...
    def getWhichEigenpairs(self) -> Which:
        """Get which portion of the spectrum is to be sought.
    
        Not collective.
    
        Returns
        -------
        Which
            The portion of the spectrum to be sought by the solver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:443 <slepc4py/SLEPc/PEP.pyx#L443>`
    
        """
        ...
    def setWhichEigenpairs(self, which: Which) -> None:
        """Set which portion of the spectrum is to be sought.
    
        Logically collective.
    
        Parameters
        ----------
        which
            The portion of the spectrum to be sought by the solver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:458 <slepc4py/SLEPc/PEP.pyx#L458>`
    
        """
        ...
    def getTarget(self) -> Scalar:
        """Get the value of the target.
    
        Not collective.
    
        Returns
        -------
        Scalar
            The value of the target.
    
        Notes
        -----
        If the target was not set by the user, then zero is returned.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:472 <slepc4py/SLEPc/PEP.pyx#L472>`
    
        """
        ...
    def setTarget(self, target: Scalar) -> None:
        """Set the value of the target.
    
        Logically collective.
    
        Parameters
        ----------
        target
            The value of the target.
    
        Notes
        -----
        The target is a scalar value used to determine the portion of
        the spectrum of interest. It is used in combination with
        `setWhichEigenpairs()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:491 <slepc4py/SLEPc/PEP.pyx#L491>`
    
        """
        ...
    def getTolerances(self) -> tuple[float, int]:
        """Get the tolerance and maximum iteration count.
    
        Not collective.
    
        Get the tolerance and maximum iteration count used by the default PEP
        convergence tests.
    
        Returns
        -------
        tol: float
            The convergence tolerance.
        max_it: int
            The maximum number of iterations
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:511 <slepc4py/SLEPc/PEP.pyx#L511>`
    
        """
        ...
    def setTolerances(self, tol: float | None = None, max_it: int | None = None) -> None:
        """Set the tolerance and maximum iteration count.
    
        Logically collective.
    
        Set the tolerance and maximum iteration count used by the default PEP
        convergence tests.
    
        Parameters
        ----------
        tol
            The convergence tolerance.
        max_it
            The maximum number of iterations
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:532 <slepc4py/SLEPc/PEP.pyx#L532>`
    
        """
        ...
    def getInterval(self) -> tuple[float, float]:
        """Get the computational interval for spectrum slicing.
    
        Not collective.
    
        Returns
        -------
        inta: float
            The left end of the interval.
        intb: float
            The right end of the interval.
    
        Notes
        -----
        If the interval was not set by the user, then zeros are returned.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:554 <slepc4py/SLEPc/PEP.pyx#L554>`
    
        """
        ...
    def setInterval(self, inta: float, intb: float) -> None:
        """Set the computational interval for spectrum slicing.
    
        Logically collective.
    
        Parameters
        ----------
        inta
            The left end of the interval.
        intb
            The right end of the interval.
    
        Notes
        -----
        Spectrum slicing is a technique employed for computing all
        eigenvalues of symmetric quadratic eigenproblems in a given interval.
        This function provides the interval to be considered. It must
        be used in combination with `PEP.Which.ALL`, see
        `setWhichEigenpairs()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:576 <slepc4py/SLEPc/PEP.pyx#L576>`
    
        """
        ...
    def getConvergenceTest(self) -> Conv:
        """Get the method used to compute the error estimate used in the convergence test.
    
        Not collective.
    
        Returns
        -------
        Conv
            The method used to compute the error estimate
            used in the convergence test.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:601 <slepc4py/SLEPc/PEP.pyx#L601>`
    
        """
        ...
    def setConvergenceTest(self, conv: Conv) -> None:
        """Set how to compute the error estimate used in the convergence test.
    
        Logically collective.
    
        Parameters
        ----------
        conv
            The method used to compute the error estimate
            used in the convergence test.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:617 <slepc4py/SLEPc/PEP.pyx#L617>`
    
        """
        ...
    def getRefine(self) -> tuple[Refine, int, float, int, RefineScheme]:
        """Get the refinement strategy used by the PEP object.
    
        Not collective.
    
        Get the refinement strategy used by the PEP object, and the associated
        parameters.
    
        Returns
        -------
        ref: Refine
            The refinement type.
        npart: int
            The number of partitions of the communicator.
        tol: float
            The convergence tolerance.
        its: int
            The maximum number of refinement iterations.
        scheme: RefineScheme
            Scheme for solving linear systems
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:632 <slepc4py/SLEPc/PEP.pyx#L632>`
    
        """
        ...
    def setRefine(self, ref: Refine, npart: int | None = None, tol: float | None = None, its: int | None = None, scheme: RefineScheme | None = None) -> None:
        """Set the refinement strategy used by the PEP object.
    
        Logically collective.
    
        Set the refinement strategy used by the PEP object, and the associated
        parameters.
    
        Parameters
        ----------
        ref
            The refinement type.
        npart
            The number of partitions of the communicator.
        tol
            The convergence tolerance.
        its
            The maximum number of refinement iterations.
        scheme
            Scheme for linear system solves
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:662 <slepc4py/SLEPc/PEP.pyx#L662>`
    
        """
        ...
    def getRefineKSP(self) -> KSP:
        """Get the ``KSP`` object used by the eigensolver in the refinement phase.
    
        Collective.
    
        Returns
        -------
        `petsc4py.PETSc.KSP`
            The linear solver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:702 <slepc4py/SLEPc/PEP.pyx#L702>`
    
        """
        ...
    def setExtract(self, extract: Extract) -> None:
        """Set the extraction strategy to be used.
    
        Logically collective.
    
        Parameters
        ----------
        extract
            The extraction strategy.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:718 <slepc4py/SLEPc/PEP.pyx#L718>`
    
        """
        ...
    def getExtract(self) -> Extract:
        """Get the extraction technique used by the `PEP` object.
    
        Not collective.
    
        Returns
        -------
        Extract
            The extraction strategy.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:732 <slepc4py/SLEPc/PEP.pyx#L732>`
    
        """
        ...
    def getTrackAll(self) -> bool:
        """Get the flag indicating whether all residual norms must be computed.
    
        Not collective.
    
        Returns
        -------
        bool
            Whether the solver compute all residuals or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:747 <slepc4py/SLEPc/PEP.pyx#L747>`
    
        """
        ...
    def setTrackAll(self, trackall: bool) -> None:
        """Set flag to compute the residual of all approximate eigenpairs.
    
        Logically collective.
    
        Set if the solver must compute the residual of all approximate
        eigenpairs or not.
    
        Parameters
        ----------
        trackall
            Whether compute all residuals or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:762 <slepc4py/SLEPc/PEP.pyx#L762>`
    
        """
        ...
    def getDimensions(self) -> tuple[int, int, int]:
        """Get the number of eigenvalues to compute and the dimension of the subspace.
    
        Not collective.
    
        Returns
        -------
        nev: int
            Number of eigenvalues to compute.
        ncv: int
            Maximum dimension of the subspace to be used by the solver.
        mpd: int
            Maximum dimension allowed for the projected problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:779 <slepc4py/SLEPc/PEP.pyx#L779>`
    
        """
        ...
    def setDimensions(self, nev: int | None = None, ncv: int | None = None, mpd: int | None = None) -> None:
        """Set the number of eigenvalues to compute and the dimension of the subspace.
    
        Logically collective.
    
        Parameters
        ----------
        nev
            Number of eigenvalues to compute.
        ncv
            Maximum dimension of the subspace to be used by the solver.
        mpd
            Maximum dimension allowed for the projected problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:800 <slepc4py/SLEPc/PEP.pyx#L800>`
    
        """
        ...
    def getST(self) -> ST:
        """Get the `ST` object associated to the eigensolver object.
    
        Not collective.
    
        Get the spectral transformation object associated to the eigensolver
        object.
    
        Returns
        -------
        ST
            The spectral transformation.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:828 <slepc4py/SLEPc/PEP.pyx#L828>`
    
        """
        ...
    def setST(self, st: ST) -> None:
        """Set a spectral transformation object associated to the eigensolver.
    
        Collective.
    
        Parameters
        ----------
        st
            The spectral transformation.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:847 <slepc4py/SLEPc/PEP.pyx#L847>`
    
        """
        ...
    def getScale(self, Dl: petsc4py.PETSc.Vec | None = None, Dr: petsc4py.PETSc.Vec | None = None) -> tuple[Scale, float, int, float]:
        """Get the strategy used for scaling the polynomial eigenproblem.
    
        Not collective.
    
        Parameters
        ----------
        Dl
            Placeholder for the returned left diagonal matrix.
        Dr
            Placeholder for the returned right diagonal matrix.
    
        Returns
        -------
        scale: Scale
            The scaling strategy.
        alpha: float
            The scaling factor.
        its: int
            The number of iteration of diagonal scaling.
        lbda: float
            Approximation of the wanted eigenvalues (modulus).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:860 <slepc4py/SLEPc/PEP.pyx#L860>`
    
        """
        ...
    def setScale(self, scale: Scale, alpha: float | None = None, Dl: petsc4py.PETSc.Vec | None = None, Dr: petsc4py.PETSc.Vec | None = None, its: int | None = None, lbda: float | None = None) -> None:
        """Set the scaling strategy to be used.
    
        Collective.
    
        Set the scaling strategy to be used for scaling the polynomial problem
        before attempting to solve.
    
        Parameters
        ----------
        scale
            The scaling strategy.
        alpha
            The scaling factor.
        Dl
            The left diagonal matrix.
        Dr
            The right diagonal matrix.
        its
            The number of iteration of diagonal scaling.
        lbda
            Approximation of the wanted eigenvalues (modulus).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:909 <slepc4py/SLEPc/PEP.pyx#L909>`
    
        """
        ...
    def getBV(self) -> BV:
        """Get the basis vectors object associated to the eigensolver.
    
        Not collective.
    
        Returns
        -------
        BV
            The basis vectors context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:954 <slepc4py/SLEPc/PEP.pyx#L954>`
    
        """
        ...
    def setBV(self, bv: BV) -> None:
        """Set a basis vectors object associated to the eigensolver.
    
        Collective.
    
        Parameters
        ----------
        bv
            The basis vectors context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:970 <slepc4py/SLEPc/PEP.pyx#L970>`
    
        """
        ...
    def getRG(self) -> RG:
        """Get the region object associated to the eigensolver.
    
        Not collective.
    
        Returns
        -------
        RG
            The region context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:983 <slepc4py/SLEPc/PEP.pyx#L983>`
    
        """
        ...
    def setRG(self, rg: RG) -> None:
        """Set a region object associated to the eigensolver.
    
        Collective.
    
        Parameters
        ----------
        rg
            The region context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:999 <slepc4py/SLEPc/PEP.pyx#L999>`
    
        """
        ...
    def getDS(self) -> DS:
        """Get the direct solver associated to the eigensolver.
    
        Not collective.
    
        Returns
        -------
        DS
            The direct solver context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1012 <slepc4py/SLEPc/PEP.pyx#L1012>`
    
        """
        ...
    def setDS(self, ds: DS) -> None:
        """Set a direct solver object associated to the eigensolver.
    
        Collective.
    
        Parameters
        ----------
        ds
            The direct solver context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1028 <slepc4py/SLEPc/PEP.pyx#L1028>`
    
        """
        ...
    def getOperators(self) -> list[petsc4py.PETSc.Mat]:
        """Get the matrices associated with the eigenvalue problem.
    
        Collective.
    
        Returns
        -------
        list of petsc4py.PETSc.Mat
            The matrices associated with the eigensystem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1041 <slepc4py/SLEPc/PEP.pyx#L1041>`
    
        """
        ...
    def setOperators(self, operators: list[Mat]) -> None:
        """Set the matrices associated with the eigenvalue problem.
    
        Collective.
    
        Parameters
        ----------
        operators
            The matrices associated with the eigensystem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1063 <slepc4py/SLEPc/PEP.pyx#L1063>`
    
        """
        ...
    def setInitialSpace(self, space: Vec | list[Vec]) -> None:
        """Set the initial space from which the eigensolver starts to iterate.
    
        Collective.
    
        Parameters
        ----------
        space
            The initial space
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1083 <slepc4py/SLEPc/PEP.pyx#L1083>`
    
        """
        ...
    def setStoppingTest(self, stopping: PEPStoppingFunction | None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Set a function to decide when to stop the outer iteration of the eigensolver.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1103 <slepc4py/SLEPc/PEP.pyx#L1103>`
    
        """
        ...
    def getStoppingTest(self) -> PEPStoppingFunction:
        """Get the stopping function.
    
        Not collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1123 <slepc4py/SLEPc/PEP.pyx#L1123>`
    
        """
        ...
    def setMonitor(self, monitor: PEPMonitorFunction | None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Append a monitor function to the list of monitors.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1133 <slepc4py/SLEPc/PEP.pyx#L1133>`
    
        """
        ...
    def getMonitor(self) -> PEPMonitorFunction:
        """Get the list of monitor functions.
    
        Not collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1154 <slepc4py/SLEPc/PEP.pyx#L1154>`
    
        """
        ...
    def cancelMonitor(self) -> None:
        """Clear all monitors for a `PEP` object.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1162 <slepc4py/SLEPc/PEP.pyx#L1162>`
    
        """
        ...
    def setUp(self) -> None:
        """Set up all the necessary internal data structures.
    
        Collective.
    
        Set up all the internal data structures necessary for the execution of
        the eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1173 <slepc4py/SLEPc/PEP.pyx#L1173>`
    
        """
        ...
    def solve(self) -> None:
        """Solve the eigensystem.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1184 <slepc4py/SLEPc/PEP.pyx#L1184>`
    
        """
        ...
    def getIterationNumber(self) -> int:
        """Get the current iteration number.
    
        Not collective.
    
        If the call to `solve()` is complete, then it returns the number of
        iterations carried out by the solution method.
    
        Returns
        -------
        int
            Iteration number.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1192 <slepc4py/SLEPc/PEP.pyx#L1192>`
    
        """
        ...
    def getConvergedReason(self) -> ConvergedReason:
        """Get the reason why the `solve()` iteration was stopped.
    
        Not collective.
    
        Returns
        -------
        ConvergedReason
            Negative value indicates diverged, positive value
            converged.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1210 <slepc4py/SLEPc/PEP.pyx#L1210>`
    
        """
        ...
    def getConverged(self) -> int:
        """Get the number of converged eigenpairs.
    
        Not collective.
    
        Returns
        -------
        int
            Number of converged eigenpairs.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1226 <slepc4py/SLEPc/PEP.pyx#L1226>`
    
        """
        ...
    def getEigenpair(self, i: int, Vr: Vec | None = None, Vi: Vec | None = None) -> complex:
        """Get the i-th solution of the eigenproblem as computed by `solve()`.
    
        Collective.
    
        The solution consists of both the eigenvalue and the eigenvector.
    
        Parameters
        ----------
        i
            Index of the solution to be obtained.
        Vr
            Placeholder for the returned eigenvector (real part).
        Vi
            Placeholder for the returned eigenvector (imaginary part).
    
        Returns
        -------
        complex
            The computed eigenvalue.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1241 <slepc4py/SLEPc/PEP.pyx#L1241>`
    
        """
        ...
    def getErrorEstimate(self, i: int) -> float:
        """Get the error estimate associated to the i-th computed eigenpair.
    
        Not collective.
    
        Parameters
        ----------
        i
            Index of the solution to be considered.
    
        Returns
        -------
        float
            Error estimate.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1270 <slepc4py/SLEPc/PEP.pyx#L1270>`
    
        """
        ...
    def computeError(self, i: int, etype: ErrorType | None = None) -> float:
        """Compute the error associated with the i-th computed eigenpair.
    
        Collective.
    
        Compute the error (based on the residual norm) associated with the i-th
        computed eigenpair.
    
        Parameters
        ----------
        i
            Index of the solution to be considered.
        etype
            The error type to compute.
    
        Returns
        -------
        float
            The error bound, computed in various ways from the residual norm
            :math:`||P(l)x||_2` where :math:`l` is the eigenvalue and :math:`x`
            is the eigenvector.
    
        Notes
        -----
        The index ``i`` should be a value between ``0`` and
        ``nconv-1`` (see `getConverged()`).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1290 <slepc4py/SLEPc/PEP.pyx#L1290>`
    
        """
        ...
    def errorView(self, etype: ErrorType | None = None, viewer: petsc4py.PETSc.Viewer | None = None) -> None:
        """Display the errors associated with the computed solution.
    
        Collective.
    
        Display the errors and the eigenvalues.
    
        Parameters
        ----------
        etype
            The error type to compute.
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
        Notes
        -----
        By default, this function checks the error of all eigenpairs and prints
        the eigenvalues if all of them are below the requested tolerance.
        If the viewer has format ``ASCII_INFO_DETAIL`` then a table with
        eigenvalues and corresponding errors is printed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1324 <slepc4py/SLEPc/PEP.pyx#L1324>`
    
        """
        ...
    def valuesView(self, viewer: Viewer | None = None) -> None:
        """Display the computed eigenvalues in a viewer.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1353 <slepc4py/SLEPc/PEP.pyx#L1353>`
    
        """
        ...
    def vectorsView(self, viewer: Viewer | None = None) -> None:
        """Output computed eigenvectors to a viewer.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1368 <slepc4py/SLEPc/PEP.pyx#L1368>`
    
        """
        ...
    def setLinearEPS(self, eps: EPS) -> None:
        """Set an eigensolver object associated to the polynomial eigenvalue solver.
    
        Collective.
    
        Parameters
        ----------
        eps
            The linear eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1385 <slepc4py/SLEPc/PEP.pyx#L1385>`
    
        """
        ...
    def getLinearEPS(self) -> EPS:
        """Get the eigensolver object associated to the polynomial eigenvalue solver.
    
        Collective.
    
        Returns
        -------
        EPS
            The linear eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1398 <slepc4py/SLEPc/PEP.pyx#L1398>`
    
        """
        ...
    def setLinearLinearization(self, alpha: float = 1.0, beta: float = 0.0) -> None:
        """Set the coefficients that define the linearization of a quadratic eigenproblem.
    
        Logically collective.
    
        Set the coefficients that define the linearization of a quadratic
        eigenproblem.
    
        Parameters
        ----------
        alpha
            First parameter of the linearization.
        beta
            Second parameter of the linearization.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1414 <slepc4py/SLEPc/PEP.pyx#L1414>`
    
        """
        ...
    def getLinearLinearization(self) -> tuple[float, float]:
        """Get the coeffs. defining the linearization of a quadratic eigenproblem.
    
        Not collective.
    
        Return the coefficients that define the linearization of a quadratic
        eigenproblem.
    
        Returns
        -------
        alpha: float
            First parameter of the linearization.
        beta: float
            Second parameter of the linearization.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1434 <slepc4py/SLEPc/PEP.pyx#L1434>`
    
        """
        ...
    def setLinearExplicitMatrix(self, flag: bool) -> None:
        """Set flag to explicitly build the matrices A and B.
    
        Logically collective.
    
        Toggle if the matrices A and B for the linearization of the problem
        must be built explicitly.
    
        Parameters
        ----------
        flag
            Boolean flag indicating if the matrices are built explicitly.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1455 <slepc4py/SLEPc/PEP.pyx#L1455>`
    
        """
        ...
    def getLinearExplicitMatrix(self) -> bool:
        """Get if the matrices A and B for the linearization are built explicitly.
    
        Not collective.
    
        Get the flag indicating if the matrices A and B for the linearization
        are built explicitly.
    
        Returns
        -------
        bool
            Boolean flag indicating if the matrices are built explicitly.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1472 <slepc4py/SLEPc/PEP.pyx#L1472>`
    
        """
        ...
    def setQArnoldiRestart(self, keep: float) -> None:
        """Set the restart parameter for the Q-Arnoldi method.
    
        Logically collective.
    
        Set the restart parameter for the Q-Arnoldi method, in
        particular the proportion of basis vectors that must be kept
        after restart.
    
        Parameters
        ----------
        keep
            The number of vectors to be kept at restart.
    
        Notes
        -----
        Allowed values are in the range [0.1,0.9]. The default is 0.5.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1492 <slepc4py/SLEPc/PEP.pyx#L1492>`
    
        """
        ...
    def getQArnoldiRestart(self) -> float:
        """Get the restart parameter used in the Q-Arnoldi method.
    
        Not collective.
    
        Returns
        -------
        float
            The number of vectors to be kept at restart.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1514 <slepc4py/SLEPc/PEP.pyx#L1514>`
    
        """
        ...
    def setQArnoldiLocking(self, lock: bool) -> None:
        """Toggle between locking and non-locking variants of the Q-Arnoldi method.
    
        Logically collective.
    
        Parameters
        ----------
        lock
            True if the locking variant must be selected.
    
        Notes
        -----
        The default is to lock converged eigenpairs when the method restarts.
        This behavior can be changed so that all directions are kept in the
        working subspace even if already converged to working accuracy (the
        non-locking variant).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1529 <slepc4py/SLEPc/PEP.pyx#L1529>`
    
        """
        ...
    def getQArnoldiLocking(self) -> bool:
        """Get the locking flag used in the Q-Arnoldi method.
    
        Not collective.
    
        Returns
        -------
        bool
            The locking flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1550 <slepc4py/SLEPc/PEP.pyx#L1550>`
    
        """
        ...
    def setTOARRestart(self, keep: float) -> None:
        """Set the restart parameter for the TOAR method.
    
        Logically collective.
    
        Set the restart parameter for the TOAR method, in
        particular the proportion of basis vectors that must be kept
        after restart.
    
        Parameters
        ----------
        keep
            The number of vectors to be kept at restart.
    
        Notes
        -----
        Allowed values are in the range [0.1,0.9]. The default is 0.5.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1567 <slepc4py/SLEPc/PEP.pyx#L1567>`
    
        """
        ...
    def getTOARRestart(self) -> float:
        """Get the restart parameter used in the TOAR method.
    
        Not collective.
    
        Returns
        -------
        float
            The number of vectors to be kept at restart.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1589 <slepc4py/SLEPc/PEP.pyx#L1589>`
    
        """
        ...
    def setTOARLocking(self, lock: bool) -> None:
        """Toggle between locking and non-locking variants of the TOAR method.
    
        Logically collective.
    
        Parameters
        ----------
        lock
            True if the locking variant must be selected.
    
        Notes
        -----
        The default is to lock converged eigenpairs when the method restarts.
        This behavior can be changed so that all directions are kept in the
        working subspace even if already converged to working accuracy (the
        non-locking variant).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1604 <slepc4py/SLEPc/PEP.pyx#L1604>`
    
        """
        ...
    def getTOARLocking(self) -> bool:
        """Get the locking flag used in the TOAR method.
    
        Not collective.
    
        Returns
        -------
        bool
            The locking flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1625 <slepc4py/SLEPc/PEP.pyx#L1625>`
    
        """
        ...
    def setSTOARLinearization(self, alpha: float = 1.0, beta: float = 0.0) -> None:
        """Set the coefficients that define the linearization of a quadratic eigenproblem.
    
        Logically collective.
    
        Parameters
        ----------
        alpha
            First parameter of the linearization.
        beta
            Second parameter of the linearization.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1642 <slepc4py/SLEPc/PEP.pyx#L1642>`
    
        """
        ...
    def getSTOARLinearization(self) -> tuple[float, float]:
        """Get the coefficients that define the linearization of a quadratic eigenproblem.
    
        Not collective.
    
        Returns
        -------
        alpha: float
            First parameter of the linearization.
        beta: float
            Second parameter of the linearization.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1659 <slepc4py/SLEPc/PEP.pyx#L1659>`
    
        """
        ...
    def setSTOARLocking(self, lock: bool) -> None:
        """Toggle between locking and non-locking variants of the STOAR method.
    
        Logically collective.
    
        Parameters
        ----------
        lock
            True if the locking variant must be selected.
    
        Notes
        -----
        The default is to lock converged eigenpairs when the method restarts.
        This behavior can be changed so that all directions are kept in the
        working subspace even if already converged to working accuracy (the
        non-locking variant).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1677 <slepc4py/SLEPc/PEP.pyx#L1677>`
    
        """
        ...
    def getSTOARLocking(self) -> bool:
        """Get the locking flag used in the STOAR method.
    
        Not collective.
    
        Returns
        -------
        bool
            The locking flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1698 <slepc4py/SLEPc/PEP.pyx#L1698>`
    
        """
        ...
    def setSTOARDetectZeros(self, detect: bool) -> None:
        """Set flag to enforce detection of zeros during the factorizations.
    
        Logically collective.
    
        Set a flag to enforce detection of zeros during the factorizations
        throughout the spectrum slicing computation.
    
        Parameters
        ----------
        detect
            True if zeros must checked for.
    
        Notes
        -----
        A zero in the factorization indicates that a shift coincides with
        an eigenvalue.
    
        This flag is turned off by default, and may be necessary in some cases.
        This feature currently requires an external package for factorizations
        with support for zero detection, e.g. MUMPS.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1713 <slepc4py/SLEPc/PEP.pyx#L1713>`
    
        """
        ...
    def getSTOARDetectZeros(self) -> bool:
        """Get the flag that enforces zero detection in spectrum slicing.
    
        Not collective.
    
        Returns
        -------
        bool
            The zero detection flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1739 <slepc4py/SLEPc/PEP.pyx#L1739>`
    
        """
        ...
    def setSTOARDimensions(self, nev: int | None = None, ncv: int | None = None, mpd: int | None = None) -> None:
        """Set the dimensions used for each subsolve step.
    
        Logically collective.
    
        Set the dimensions used for each subsolve step in case of doing
        spectrum slicing for a computational interval. The meaning of the
        parameters is the same as in `setDimensions()`.
    
        Parameters
        ----------
        nev
            Number of eigenvalues to compute.
        ncv
            Maximum dimension of the subspace to be used by the solver.
        mpd
            Maximum dimension allowed for the projected problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1754 <slepc4py/SLEPc/PEP.pyx#L1754>`
    
        """
        ...
    def getSTOARDimensions(self) -> tuple[int, int, int]:
        """Get the dimensions used for each subsolve step.
    
        Not collective.
    
        Get the dimensions used for each subsolve step in case of doing
        spectrum slicing for a computational interval.
    
        Returns
        -------
        nev: int
            Number of eigenvalues to compute.
        ncv: int
            Maximum dimension of the subspace to be used by the solver.
        mpd: int
            Maximum dimension allowed for the projected problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1786 <slepc4py/SLEPc/PEP.pyx#L1786>`
    
        """
        ...
    def getSTOARInertias(self) -> tuple[ArrayReal, ArrayInt]:
        """Get the values of the shifts and their corresponding inertias.
    
        Not collective.
    
        Get the values of the shifts and their corresponding inertias
        in case of doing spectrum slicing for a computational interval.
    
        Returns
        -------
        shifts: ArrayReal
            The values of the shifts used internally in the solver.
        inertias: ArrayInt
            The values of the inertia in each shift.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1810 <slepc4py/SLEPc/PEP.pyx#L1810>`
    
        """
        ...
    def setSTOARCheckEigenvalueType(self, flag: bool) -> None:
        """Set flag to check if all eigenvalues have the same definite type.
    
        Logically collective.
    
        Set a flag to check that all the eigenvalues obtained throughout the
        spectrum slicing computation have the same definite type.
    
        Parameters
        ----------
        flag
            Whether the eigenvalue type is checked or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1840 <slepc4py/SLEPc/PEP.pyx#L1840>`
    
        """
        ...
    def getSTOARCheckEigenvalueType(self) -> bool:
        """Get the flag for the eigenvalue type check in spectrum slicing.
    
        Not collective.
    
        Returns
        -------
        bool
            Whether the eigenvalue type is checked or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1857 <slepc4py/SLEPc/PEP.pyx#L1857>`
    
        """
        ...
    def setJDRestart(self, keep: float) -> None:
        """Set the restart parameter for the Jacobi-Davidson method.
    
        Logically collective.
    
        Set the restart parameter for the Jacobi-Davidson method, in
        particular the proportion of basis vectors that must be kept
        after restart.
    
        Parameters
        ----------
        keep
            The number of vectors to be kept at restart.
    
        Notes
        -----
        Allowed values are in the range [0.1,0.9]. The default is 0.5.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1874 <slepc4py/SLEPc/PEP.pyx#L1874>`
    
        """
        ...
    def getJDRestart(self) -> float:
        """Get the restart parameter used in the Jacobi-Davidson method.
    
        Not collective.
    
        Returns
        -------
        float
            The number of vectors to be kept at restart.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1896 <slepc4py/SLEPc/PEP.pyx#L1896>`
    
        """
        ...
    def setJDFix(self, fix: float) -> None:
        """Set the threshold for changing the target in the correction equation.
    
        Logically collective.
    
        Parameters
        ----------
        fix
            Threshold for changing the target.
    
        Notes
        -----
        The target in the correction equation is fixed at the first iterations.
        When the norm of the residual vector is lower than the fix value,
        the target is set to the corresponding eigenvalue.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1911 <slepc4py/SLEPc/PEP.pyx#L1911>`
    
        """
        ...
    def getJDFix(self) -> float:
        """Get threshold for changing the target in the correction equation.
    
        Not collective.
    
        Returns
        -------
        float
            The threshold for changing the target.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1931 <slepc4py/SLEPc/PEP.pyx#L1931>`
    
        """
        ...
    def setJDReusePreconditioner(self, flag: bool) -> None:
        """Set a flag indicating whether the preconditioner must be reused or not.
    
        Logically collective.
    
        Parameters
        ----------
        flag
            The reuse flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1946 <slepc4py/SLEPc/PEP.pyx#L1946>`
    
        """
        ...
    def getJDReusePreconditioner(self) -> bool:
        """Get the flag for reusing the preconditioner.
    
        Not collective.
    
        Returns
        -------
        bool
            The reuse flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1960 <slepc4py/SLEPc/PEP.pyx#L1960>`
    
        """
        ...
    def setJDMinimalityIndex(self, flag: int) -> None:
        """Set the maximum allowed value for the minimality index.
    
        Logically collective.
    
        Parameters
        ----------
        flag
            The maximum minimality index.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1975 <slepc4py/SLEPc/PEP.pyx#L1975>`
    
        """
        ...
    def getJDMinimalityIndex(self) -> int:
        """Get the maximum allowed value of the minimality index.
    
        Not collective.
    
        Returns
        -------
        int
            The maximum minimality index.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:1989 <slepc4py/SLEPc/PEP.pyx#L1989>`
    
        """
        ...
    def setJDProjection(self, proj: JDProjection) -> None:
        """Set the type of projection to be used in the Jacobi-Davidson solver.
    
        Logically collective.
    
        Parameters
        ----------
        proj
            The type of projection.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2004 <slepc4py/SLEPc/PEP.pyx#L2004>`
    
        """
        ...
    def getJDProjection(self) -> JDProjection:
        """Get the type of projection to be used in the Jacobi-Davidson solver.
    
        Not collective.
    
        Returns
        -------
        JDProjection
            The type of projection.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2018 <slepc4py/SLEPc/PEP.pyx#L2018>`
    
        """
        ...
    def setCISSExtraction(self, extraction: CISSExtraction) -> None:
        """Set the extraction technique used in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        extraction
            The extraction technique.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2035 <slepc4py/SLEPc/PEP.pyx#L2035>`
    
        """
        ...
    def getCISSExtraction(self) -> CISSExtraction:
        """Get the extraction technique used in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        CISSExtraction
            The extraction technique.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2049 <slepc4py/SLEPc/PEP.pyx#L2049>`
    
        """
        ...
    def setCISSSizes(self, ip: int | None = None, bs: int | None = None, ms: int | None = None, npart: int | None = None, bsmax: int | None = None, realmats: bool = False) -> None:
        """Set the values of various size parameters in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        ip
            Number of integration points.
        bs
            Block size.
        ms
            Moment size.
        npart
            Number of partitions when splitting the communicator.
        bsmax
            Maximum block size.
        realmats
            True if A and B are real.
    
        Notes
        -----
        The default number of partitions is 1. This means the internal
        `petsc4py.PETSc.KSP` object is shared among all processes of the `PEP`
        communicator. Otherwise, the communicator is split into npart
        communicators, so that ``npart`` `petsc4py.PETSc.KSP` solves proceed
        simultaneously.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2064 <slepc4py/SLEPc/PEP.pyx#L2064>`
    
        """
        ...
    def getCISSSizes(self) -> tuple[int, int, int, int, int, bool]:
        """Get the values of various size parameters in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        ip: int
            Number of integration points.
        bs: int
            Block size.
        ms: int
            Moment size.
        npart: int
            Number of partitions when splitting the communicator.
        bsmax: int
            Maximum block size.
        realmats: bool
            True if A and B are real.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2114 <slepc4py/SLEPc/PEP.pyx#L2114>`
    
        """
        ...
    def setCISSThreshold(self, delta: float | None = None, spur: float | None = None) -> None:
        """Set the values of various threshold parameters in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        delta
            Threshold for numerical rank.
        spur
            Spurious threshold (to discard spurious eigenpairs).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2144 <slepc4py/SLEPc/PEP.pyx#L2144>`
    
        """
        ...
    def getCISSThreshold(self) -> tuple[float, float]:
        """Get the values of various threshold parameters in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        delta: float
            Threshold for numerical rank.
        spur: float
            Spurious threshold (to discard spurious eigenpairs.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2163 <slepc4py/SLEPc/PEP.pyx#L2163>`
    
        """
        ...
    def setCISSRefinement(self, inner: int | None = None, blsize: int | None = None) -> None:
        """Set the values of various refinement parameters in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        inner
            Number of iterative refinement iterations (inner loop).
        blsize
            Number of iterative refinement iterations (blocksize loop).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2181 <slepc4py/SLEPc/PEP.pyx#L2181>`
    
        """
        ...
    def getCISSRefinement(self) -> tuple[int, int]:
        """Get the values of various refinement parameters in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        inner: int
            Number of iterative refinement iterations (inner loop).
        blsize: int
            Number of iterative refinement iterations (blocksize loop).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2200 <slepc4py/SLEPc/PEP.pyx#L2200>`
    
        """
        ...
    def getCISSKSPs(self) -> list[KSP]:
        """Get the array of linear solver objects associated with the CISS solver.
    
        Collective.
    
        Returns
        -------
        list of `petsc4py.PETSc.KSP`
            The linear solver objects.
    
        Notes
        -----
        The number of `petsc4py.PETSc.KSP` solvers is equal to the number of
        integration points divided by the number of partitions. This value is
        halved in the case of real matrices with a region centered at the real
        axis.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2218 <slepc4py/SLEPc/PEP.pyx#L2218>`
    
        """
        ...
    @property
    def problem_type(self) -> PEPProblemType:
        """The type of the eigenvalue problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2243 <slepc4py/SLEPc/PEP.pyx#L2243>`
    
        """
        ...
    @property
    def which(self) -> PEPWhich:
        """The portion of the spectrum to be sought.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2250 <slepc4py/SLEPc/PEP.pyx#L2250>`
    
        """
        ...
    @property
    def target(self) -> float:
        """The value of the target.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2257 <slepc4py/SLEPc/PEP.pyx#L2257>`
    
        """
        ...
    @property
    def extract(self) -> PEPExtract:
        """The type of extraction technique to be employed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2264 <slepc4py/SLEPc/PEP.pyx#L2264>`
    
        """
        ...
    @property
    def tol(self) -> float:
        """The tolerance.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2271 <slepc4py/SLEPc/PEP.pyx#L2271>`
    
        """
        ...
    @property
    def max_it(self) -> int:
        """The maximum iteration count.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2278 <slepc4py/SLEPc/PEP.pyx#L2278>`
    
        """
        ...
    @property
    def track_all(self) -> bool:
        """Compute the residual norm of all approximate eigenpairs.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2285 <slepc4py/SLEPc/PEP.pyx#L2285>`
    
        """
        ...
    @property
    def st(self) -> ST:
        """The spectral transformation (ST) object associated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2292 <slepc4py/SLEPc/PEP.pyx#L2292>`
    
        """
        ...
    @property
    def bv(self) -> BV:
        """The basis vectors (BV) object associated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2299 <slepc4py/SLEPc/PEP.pyx#L2299>`
    
        """
        ...
    @property
    def rg(self) -> RG:
        """The region (RG) object associated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2306 <slepc4py/SLEPc/PEP.pyx#L2306>`
    
        """
        ...
    @property
    def ds(self) -> DS:
        """The direct solver (DS) object associated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/PEP.pyx:2313 <slepc4py/SLEPc/PEP.pyx#L2313>`
    
        """
        ...

class NEP(Object):
    """NEP."""
    class Type:
        """NEP type.
        
        Nonlinear eigensolvers.
        
        - `RII`:      Residual inverse iteration.
        - `SLP`:      Successive linear problems.
        - `NARNOLDI`: Nonlinear Arnoldi.
        - `CISS`:     Contour integral spectrum slice.
        - `INTERPOL`: Polynomial interpolation.
        - `NLEIGS`:   Fully rational Krylov method for nonlinear eigenproblems.
        
        """
        RII: str = _def(str, 'RII')  #: Object ``RII`` of type :class:`str`
        SLP: str = _def(str, 'SLP')  #: Object ``SLP`` of type :class:`str`
        NARNOLDI: str = _def(str, 'NARNOLDI')  #: Object ``NARNOLDI`` of type :class:`str`
        CISS: str = _def(str, 'CISS')  #: Object ``CISS`` of type :class:`str`
        INTERPOL: str = _def(str, 'INTERPOL')  #: Object ``INTERPOL`` of type :class:`str`
        NLEIGS: str = _def(str, 'NLEIGS')  #: Object ``NLEIGS`` of type :class:`str`
    class ProblemType:
        """NEP problem type.
        
        - `GENERAL`:  General nonlinear eigenproblem.
        - `RATIONAL`: NEP defined in split form with all :math:`f_i` rational.
        
        """
        GENERAL: int = _def(int, 'GENERAL')  #: Constant ``GENERAL`` of type :class:`int`
        RATIONAL: int = _def(int, 'RATIONAL')  #: Constant ``RATIONAL`` of type :class:`int`
    class ErrorType:
        """NEP error type to assess accuracy of computed solutions.
        
        - `ABSOLUTE`: Absolute error.
        - `RELATIVE`: Relative error.
        - `BACKWARD`: Backward error.
        
        """
        ABSOLUTE: int = _def(int, 'ABSOLUTE')  #: Constant ``ABSOLUTE`` of type :class:`int`
        RELATIVE: int = _def(int, 'RELATIVE')  #: Constant ``RELATIVE`` of type :class:`int`
        BACKWARD: int = _def(int, 'BACKWARD')  #: Constant ``BACKWARD`` of type :class:`int`
    class Which:
        """NEP desired part of spectrum.
        
        - `LARGEST_MAGNITUDE`:  Largest magnitude (default).
        - `SMALLEST_MAGNITUDE`: Smallest magnitude.
        - `LARGEST_REAL`:       Largest real parts.
        - `SMALLEST_REAL`:      Smallest real parts.
        - `LARGEST_IMAGINARY`:  Largest imaginary parts in magnitude.
        - `SMALLEST_IMAGINARY`: Smallest imaginary parts in magnitude.
        - `TARGET_MAGNITUDE`:   Closest to target (in magnitude).
        - `TARGET_REAL`:        Real part closest to target.
        - `TARGET_IMAGINARY`:   Imaginary part closest to target.
        - `ALL`:                All eigenvalues in a region.
        - `USER`:               User defined selection.
        
        """
        LARGEST_MAGNITUDE: int = _def(int, 'LARGEST_MAGNITUDE')  #: Constant ``LARGEST_MAGNITUDE`` of type :class:`int`
        SMALLEST_MAGNITUDE: int = _def(int, 'SMALLEST_MAGNITUDE')  #: Constant ``SMALLEST_MAGNITUDE`` of type :class:`int`
        LARGEST_REAL: int = _def(int, 'LARGEST_REAL')  #: Constant ``LARGEST_REAL`` of type :class:`int`
        SMALLEST_REAL: int = _def(int, 'SMALLEST_REAL')  #: Constant ``SMALLEST_REAL`` of type :class:`int`
        LARGEST_IMAGINARY: int = _def(int, 'LARGEST_IMAGINARY')  #: Constant ``LARGEST_IMAGINARY`` of type :class:`int`
        SMALLEST_IMAGINARY: int = _def(int, 'SMALLEST_IMAGINARY')  #: Constant ``SMALLEST_IMAGINARY`` of type :class:`int`
        TARGET_MAGNITUDE: int = _def(int, 'TARGET_MAGNITUDE')  #: Constant ``TARGET_MAGNITUDE`` of type :class:`int`
        TARGET_REAL: int = _def(int, 'TARGET_REAL')  #: Constant ``TARGET_REAL`` of type :class:`int`
        TARGET_IMAGINARY: int = _def(int, 'TARGET_IMAGINARY')  #: Constant ``TARGET_IMAGINARY`` of type :class:`int`
        ALL: int = _def(int, 'ALL')  #: Constant ``ALL`` of type :class:`int`
        USER: int = _def(int, 'USER')  #: Constant ``USER`` of type :class:`int`
    class ConvergedReason:
        """NEP convergence reasons.
        
        - `CONVERGED_TOL`:               All eigenpairs converged to requested
                                         tolerance.
        - `CONVERGED_USER`:              User-defined convergence criterion
                                         satisfied.
        - `DIVERGED_ITS`:                Maximum number of iterations exceeded.
        - `DIVERGED_BREAKDOWN`:          Solver failed due to breakdown.
        - `DIVERGED_LINEAR_SOLVE`:       Inner linear solve failed.
        - `DIVERGED_SUBSPACE_EXHAUSTED`: Run out of space for the basis in an
                                         unrestarted solver.
        - `CONVERGED_ITERATING`:         Iteration not finished yet.
        
        """
        CONVERGED_TOL: int = _def(int, 'CONVERGED_TOL')  #: Constant ``CONVERGED_TOL`` of type :class:`int`
        CONVERGED_USER: int = _def(int, 'CONVERGED_USER')  #: Constant ``CONVERGED_USER`` of type :class:`int`
        DIVERGED_ITS: int = _def(int, 'DIVERGED_ITS')  #: Constant ``DIVERGED_ITS`` of type :class:`int`
        DIVERGED_BREAKDOWN: int = _def(int, 'DIVERGED_BREAKDOWN')  #: Constant ``DIVERGED_BREAKDOWN`` of type :class:`int`
        DIVERGED_LINEAR_SOLVE: int = _def(int, 'DIVERGED_LINEAR_SOLVE')  #: Constant ``DIVERGED_LINEAR_SOLVE`` of type :class:`int`
        DIVERGED_SUBSPACE_EXHAUSTED: int = _def(int, 'DIVERGED_SUBSPACE_EXHAUSTED')  #: Constant ``DIVERGED_SUBSPACE_EXHAUSTED`` of type :class:`int`
        CONVERGED_ITERATING: int = _def(int, 'CONVERGED_ITERATING')  #: Constant ``CONVERGED_ITERATING`` of type :class:`int`
        ITERATING: int = _def(int, 'ITERATING')  #: Constant ``ITERATING`` of type :class:`int`
    class Refine:
        """NEP refinement strategy.
        
        - `NONE`:     No refinement.
        - `SIMPLE`:   Refine eigenpairs one by one.
        - `MULTIPLE`: Refine all eigenpairs simultaneously (invariant pair).
        
        """
        NONE: int = _def(int, 'NONE')  #: Constant ``NONE`` of type :class:`int`
        SIMPLE: int = _def(int, 'SIMPLE')  #: Constant ``SIMPLE`` of type :class:`int`
        MULTIPLE: int = _def(int, 'MULTIPLE')  #: Constant ``MULTIPLE`` of type :class:`int`
    class RefineScheme:
        """NEP scheme for solving linear systems during iterative refinement.
        
        - `SCHUR`:    Schur complement.
        - `MBE`:      Mixed block elimination.
        - `EXPLICIT`: Build the explicit matrix.
        
        """
        SCHUR: int = _def(int, 'SCHUR')  #: Constant ``SCHUR`` of type :class:`int`
        MBE: int = _def(int, 'MBE')  #: Constant ``MBE`` of type :class:`int`
        EXPLICIT: int = _def(int, 'EXPLICIT')  #: Constant ``EXPLICIT`` of type :class:`int`
    class Conv:
        """NEP convergence test.
        
        - `ABS`:  Absolute convergence test.
        - `REL`:  Convergence test relative to the eigenvalue.
        - `NORM`: Convergence test relative to the matrix norms.
        - `USER`: User-defined convergence test.
        
        """
        ABS: int = _def(int, 'ABS')  #: Constant ``ABS`` of type :class:`int`
        REL: int = _def(int, 'REL')  #: Constant ``REL`` of type :class:`int`
        NORM: int = _def(int, 'NORM')  #: Constant ``NORM`` of type :class:`int`
        USER: int = _def(int, 'USER')  #: Constant ``USER`` of type :class:`int`
    class Stop:
        """NEP stopping test.
        
        - `BASIC`: Default stopping test.
        - `USER`:  User-defined stopping test.
        
        """
        BASIC: int = _def(int, 'BASIC')  #: Constant ``BASIC`` of type :class:`int`
        USER: int = _def(int, 'USER')  #: Constant ``USER`` of type :class:`int`
    class CISSExtraction:
        """NEP CISS extraction technique.
        
        - `RITZ`:   Ritz extraction.
        - `HANKEL`: Extraction via Hankel eigenproblem.
        - `CAA`:    Communication-avoiding Arnoldi.
        
        """
        RITZ: int = _def(int, 'RITZ')  #: Constant ``RITZ`` of type :class:`int`
        HANKEL: int = _def(int, 'HANKEL')  #: Constant ``HANKEL`` of type :class:`int`
        CAA: int = _def(int, 'CAA')  #: Constant ``CAA`` of type :class:`int`
    def view(self, viewer: Viewer | None = None) -> None:
        """Print the NEP data structure.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:179 <slepc4py/SLEPc/NEP.pyx#L179>`
    
        """
        ...
    def destroy(self) -> Self:
        """Destroy the NEP object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:194 <slepc4py/SLEPc/NEP.pyx#L194>`
    
        """
        ...
    def reset(self) -> None:
        """Reset the NEP object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:204 <slepc4py/SLEPc/NEP.pyx#L204>`
    
        """
        ...
    def create(self, comm: Comm | None = None) -> Self:
        """Create the NEP object.
    
        Collective.
    
        Parameters
        ----------
        comm
            MPI communicator. If not provided, it defaults to all processes.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:212 <slepc4py/SLEPc/NEP.pyx#L212>`
    
        """
        ...
    def setType(self, nep_type: Type | str) -> None:
        """Set the particular solver to be used in the NEP object.
    
        Logically collective.
    
        Parameters
        ----------
        nep_type
            The solver to be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:229 <slepc4py/SLEPc/NEP.pyx#L229>`
    
        """
        ...
    def getType(self) -> str:
        """Get the NEP type of this object.
    
        Not collective.
    
        Returns
        -------
        str
            The solver currently being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:244 <slepc4py/SLEPc/NEP.pyx#L244>`
    
        """
        ...
    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all NEP options in the database.
    
        Not collective.
    
        Returns
        -------
        str
            The prefix string set for this NEP object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:259 <slepc4py/SLEPc/NEP.pyx#L259>`
    
        """
        ...
    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all NEP options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all NEP option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:274 <slepc4py/SLEPc/NEP.pyx#L274>`
    
        """
        ...
    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all NEP options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all NEP option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:289 <slepc4py/SLEPc/NEP.pyx#L289>`
    
        """
        ...
    def setFromOptions(self) -> None:
        """Set NEP options from the options database.
    
        Collective.
    
        This routine must be called before `setUp()` if the user is to be
        allowed to set the solver type.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:304 <slepc4py/SLEPc/NEP.pyx#L304>`
    
        """
        ...
    def getProblemType(self) -> ProblemType:
        """Get the problem type from the `NEP` object.
    
        Not collective.
    
        Returns
        -------
        ProblemType
            The problem type that was previously set.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:315 <slepc4py/SLEPc/NEP.pyx#L315>`
    
        """
        ...
    def setProblemType(self, problem_type: ProblemType) -> None:
        """Set the type of the eigenvalue problem.
    
        Logically collective.
    
        Parameters
        ----------
        problem_type
            The problem type to be set.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:330 <slepc4py/SLEPc/NEP.pyx#L330>`
    
        """
        ...
    def getWhichEigenpairs(self) -> Which:
        """Get which portion of the spectrum is to be sought.
    
        Not collective.
    
        Returns
        -------
        Which
            The portion of the spectrum to be sought by the solver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:344 <slepc4py/SLEPc/NEP.pyx#L344>`
    
        """
        ...
    def setWhichEigenpairs(self, which: Which) -> None:
        """Set which portion of the spectrum is to be sought.
    
        Logically collective.
    
        Parameters
        ----------
        which
            The portion of the spectrum to be sought by the solver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:359 <slepc4py/SLEPc/NEP.pyx#L359>`
    
        """
        ...
    def getTarget(self) -> Scalar:
        """Get the value of the target.
    
        Not collective.
    
        Returns
        -------
        Scalar
            The value of the target.
    
        Notes
        -----
        If the target was not set by the user, then zero is returned.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:373 <slepc4py/SLEPc/NEP.pyx#L373>`
    
        """
        ...
    def setTarget(self, target: Scalar) -> None:
        """Set the value of the target.
    
        Logically collective.
    
        Parameters
        ----------
        target
            The value of the target.
    
        Notes
        -----
        The target is a scalar value used to determine the portion of
        the spectrum of interest. It is used in combination with
        `setWhichEigenpairs()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:392 <slepc4py/SLEPc/NEP.pyx#L392>`
    
        """
        ...
    def getTolerances(self) -> tuple[float, int]:
        """Get the tolerance and maximum iteration count.
    
        Not collective.
    
        Get the tolerance and maximum iteration count used by the default
        NEP convergence tests.
    
        Returns
        -------
        tol: float
            The convergence tolerance.
        maxit: int
            The maximum number of iterations.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:412 <slepc4py/SLEPc/NEP.pyx#L412>`
    
        """
        ...
    def setTolerances(self, tol: float | None = None, maxit: int | None = None) -> None:
        """Set the tolerance and max. iteration count used in convergence tests.
    
        Logically collective.
    
        Parameters
        ----------
        tol
            The convergence tolerance.
        maxit
            The maximum number of iterations.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:433 <slepc4py/SLEPc/NEP.pyx#L433>`
    
        """
        ...
    def getConvergenceTest(self) -> Conv:
        """Get the method used to compute the error estimate used in the convergence test.
    
        Not collective.
    
        Returns
        -------
        Conv
            The method used to compute the error estimate
            used in the convergence test.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:452 <slepc4py/SLEPc/NEP.pyx#L452>`
    
        """
        ...
    def setConvergenceTest(self, conv: Conv) -> None:
        """Set how to compute the error estimate used in the convergence test.
    
        Logically collective.
    
        Parameters
        ----------
        conv
            The method used to compute the error estimate
            used in the convergence test.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:468 <slepc4py/SLEPc/NEP.pyx#L468>`
    
        """
        ...
    def getRefine(self) -> tuple[Refine, int, float, int, RefineScheme]:
        """Get the refinement strategy used by the NEP object.
    
        Not collective.
    
        Get the refinement strategy used by the NEP object and the associated
        parameters.
    
        Returns
        -------
        ref: Refine
            The refinement type.
        npart: int
            The number of partitions of the communicator.
        tol: float
            The convergence tolerance.
        its: int
            The maximum number of refinement iterations.
        scheme: RefineScheme
            Scheme for solving linear systems
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:483 <slepc4py/SLEPc/NEP.pyx#L483>`
    
        """
        ...
    def setRefine(self, ref: Refine, npart: int | None = None, tol: float | None = None, its: int | None = None, scheme: RefineScheme | None = None) -> None:
        """Set the refinement strategy used by the NEP object.
    
        Logically collective.
    
        Set the refinement strategy used by the NEP object and the associated
        parameters.
    
        Parameters
        ----------
        ref
            The refinement type.
        npart
            The number of partitions of the communicator.
        tol
            The convergence tolerance.
        its
            The maximum number of refinement iterations.
        scheme
            Scheme for linear system solves
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:513 <slepc4py/SLEPc/NEP.pyx#L513>`
    
        """
        ...
    def getRefineKSP(self) -> KSP:
        """Get the ``KSP`` object used by the eigensolver in the refinement phase.
    
        Collective.
    
        Returns
        -------
        `petsc4py.PETSc.KSP`
            The linear solver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:553 <slepc4py/SLEPc/NEP.pyx#L553>`
    
        """
        ...
    def getTrackAll(self) -> bool:
        """Get the flag indicating whether all residual norms must be computed.
    
        Not collective.
    
        Returns
        -------
        bool
            Whether the solver compute all residuals or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:569 <slepc4py/SLEPc/NEP.pyx#L569>`
    
        """
        ...
    def setTrackAll(self, trackall: bool) -> None:
        """Set if the solver must compute the residual of all approximate eigenpairs.
    
        Logically collective.
    
        Parameters
        ----------
        trackall
            Whether compute all residuals or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:584 <slepc4py/SLEPc/NEP.pyx#L584>`
    
        """
        ...
    def getDimensions(self) -> tuple[int, int, int]:
        """Get the number of eigenvalues to compute.
    
        Not collective.
    
        Get the number of eigenvalues to compute, and the dimension of the
        subspace.
    
        Returns
        -------
        nev: int
            Number of eigenvalues to compute.
        ncv: int
            Maximum dimension of the subspace to be used by the solver.
        mpd: int
            Maximum dimension allowed for the projected problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:598 <slepc4py/SLEPc/NEP.pyx#L598>`
    
        """
        ...
    def setDimensions(self, nev: int | None = None, ncv: int | None = None, mpd: int | None = None) -> None:
        """Set the number of eigenvalues to compute.
    
        Logically collective.
    
        Set the number of eigenvalues to compute and the dimension of the
        subspace.
    
        Parameters
        ----------
        nev
            Number of eigenvalues to compute.
        ncv
            Maximum dimension of the subspace to be used by the solver.
        mpd
            Maximum dimension allowed for the projected problem.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:622 <slepc4py/SLEPc/NEP.pyx#L622>`
    
        """
        ...
    def getBV(self) -> BV:
        """Get the basis vectors object associated to the eigensolver.
    
        Not collective.
    
        Returns
        -------
        BV
            The basis vectors context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:653 <slepc4py/SLEPc/NEP.pyx#L653>`
    
        """
        ...
    def setBV(self, bv: BV) -> None:
        """Set the basis vectors object associated to the eigensolver.
    
        Collective.
    
        Parameters
        ----------
        bv
            The basis vectors context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:669 <slepc4py/SLEPc/NEP.pyx#L669>`
    
        """
        ...
    def getRG(self) -> RG:
        """Get the region object associated to the eigensolver.
    
        Not collective.
    
        Returns
        -------
        RG
            The region context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:682 <slepc4py/SLEPc/NEP.pyx#L682>`
    
        """
        ...
    def setRG(self, rg: RG) -> None:
        """Set a region object associated to the eigensolver.
    
        Collective.
    
        Parameters
        ----------
        rg
            The region context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:698 <slepc4py/SLEPc/NEP.pyx#L698>`
    
        """
        ...
    def getDS(self) -> DS:
        """Get the direct solver associated to the eigensolver.
    
        Not collective.
    
        Returns
        -------
        DS
            The direct solver context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:711 <slepc4py/SLEPc/NEP.pyx#L711>`
    
        """
        ...
    def setDS(self, ds: DS) -> None:
        """Set a direct solver object associated to the eigensolver.
    
        Collective.
    
        Parameters
        ----------
        ds
            The direct solver context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:727 <slepc4py/SLEPc/NEP.pyx#L727>`
    
        """
        ...
    def setInitialSpace(self, space: Vec or list[Vec]) -> None:
        """Set the initial space from which the eigensolver starts to iterate.
    
        Collective.
    
        Parameters
        ----------
        space
            The initial space
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:742 <slepc4py/SLEPc/NEP.pyx#L742>`
    
        """
        ...
    def setStoppingTest(self, stopping: NEPStoppingFunction | None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Set a function to decide when to stop the outer iteration of the eigensolver.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:762 <slepc4py/SLEPc/NEP.pyx#L762>`
    
        """
        ...
    def getStoppingTest(self) -> NEPStoppingFunction:
        """Get the stopping function.
    
        Not collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:782 <slepc4py/SLEPc/NEP.pyx#L782>`
    
        """
        ...
    def setMonitor(self, monitor: NEPMonitorFunction | None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Append a monitor function to the list of monitors.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:792 <slepc4py/SLEPc/NEP.pyx#L792>`
    
        """
        ...
    def getMonitor(self) -> NEPMonitorFunction:
        """Get the list of monitor functions.
    
        Not collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:813 <slepc4py/SLEPc/NEP.pyx#L813>`
    
        """
        ...
    def cancelMonitor(self) -> None:
        """Clear all monitors for a `NEP` object.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:821 <slepc4py/SLEPc/NEP.pyx#L821>`
    
        """
        ...
    def setUp(self) -> None:
        """Set up all the necessary internal data structures.
    
        Collective.
    
        Set up all the internal data structures necessary for the execution of
        the eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:832 <slepc4py/SLEPc/NEP.pyx#L832>`
    
        """
        ...
    def solve(self) -> None:
        """Solve the eigensystem.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:843 <slepc4py/SLEPc/NEP.pyx#L843>`
    
        """
        ...
    def getIterationNumber(self) -> int:
        """Get the current iteration number.
    
        Not collective.
    
        If the call to `solve()` is complete, then it returns the number of
        iterations carried out by the solution method.
    
        Returns
        -------
        int
            Iteration number.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:851 <slepc4py/SLEPc/NEP.pyx#L851>`
    
        """
        ...
    def getConvergedReason(self) -> ConvergedReason:
        """Get the reason why the `solve()` iteration was stopped.
    
        Not collective.
    
        Returns
        -------
        ConvergedReason
            Negative value indicates diverged, positive value
            converged.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:869 <slepc4py/SLEPc/NEP.pyx#L869>`
    
        """
        ...
    def getConverged(self) -> int:
        """Get the number of converged eigenpairs.
    
        Not collective.
    
        Returns
        -------
        int
            Number of converged eigenpairs.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:885 <slepc4py/SLEPc/NEP.pyx#L885>`
    
        """
        ...
    def getEigenpair(self, i: int, Vr: Vec | None = None, Vi: Vec | None = None) -> None:
        """Get the i-th solution of the eigenproblem as computed by `solve()`.
    
        Collective.
    
        The solution consists of both the eigenvalue and the eigenvector.
    
        Parameters
        ----------
        i
            Index of the solution to be obtained.
        Vr
            Placeholder for the returned eigenvector (real part).
        Vi
            Placeholder for the returned eigenvector (imaginary part).
    
        Returns
        -------
        complex
            The computed eigenvalue.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:900 <slepc4py/SLEPc/NEP.pyx#L900>`
    
        """
        ...
    def getLeftEigenvector(self, i: int, Wr: Vec, Wi: Vec | None = None) -> None:
        """Get the i-th left eigenvector as computed by `solve()`.
    
        Collective.
    
        Parameters
        ----------
        i
            Index of the solution to be obtained.
        Wr
            Placeholder for the returned eigenvector (real part).
        Wi
            Placeholder for the returned eigenvector (imaginary part).
    
        Notes
        -----
        The index ``i`` should be a value between ``0`` and
        ``nconv-1`` (see `getConverged()`). Eigensolutions are indexed
        according to the ordering criterion established with
        `setWhichEigenpairs()`.
    
        Left eigenvectors are available only if the twosided flag was set
        with `setTwoSided()`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:929 <slepc4py/SLEPc/NEP.pyx#L929>`
    
        """
        ...
    def getErrorEstimate(self, i: int) -> float:
        """Get the error estimate associated to the i-th computed eigenpair.
    
        Not collective.
    
        Parameters
        ----------
        i
            Index of the solution to be considered.
    
        Returns
        -------
        float
            Error estimate.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:958 <slepc4py/SLEPc/NEP.pyx#L958>`
    
        """
        ...
    def computeError(self, i: int, etype: ErrorType | None = None) -> float:
        """Compute the error  associated with the i-th computed eigenpair.
    
        Collective.
    
        Compute the error (based on the residual norm) associated with the
        i-th computed eigenpair.
    
        Parameters
        ----------
        i
            Index of the solution to be considered.
        etype
            The error type to compute.
    
        Returns
        -------
        float
            The error bound, computed in various ways from the residual norm
            :math:`\|T(\lambda)x\|_2` where :math:`\lambda` is the eigenvalue
            and :math:`x` is the eigenvector.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:978 <slepc4py/SLEPc/NEP.pyx#L978>`
    
        """
        ...
    def errorView(self, etype: ErrorType | None = None, viewer: petsc4py.PETSc.Viewer | None = None) -> None:
        """Display the errors associated with the computed solution.
    
        Collective.
    
        Display the eigenvalues and the errors associated with the computed solution
    
        Parameters
        ----------
        etype
            The error type to compute.
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
        Notes
        -----
        By default, this function checks the error of all eigenpairs and prints
        the eigenvalues if all of them are below the requested tolerance.
        If the viewer has format ``ASCII_INFO_DETAIL`` then a table with
        eigenvalues and corresponding errors is printed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1007 <slepc4py/SLEPc/NEP.pyx#L1007>`
    
        """
        ...
    def valuesView(self, viewer: Viewer | None = None) -> None:
        """Display the computed eigenvalues in a viewer.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1036 <slepc4py/SLEPc/NEP.pyx#L1036>`
    
        """
        ...
    def vectorsView(self, viewer: Viewer | None = None) -> None:
        """Output computed eigenvectors to a viewer.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1051 <slepc4py/SLEPc/NEP.pyx#L1051>`
    
        """
        ...
    def setFunction(self, function: NEPFunction, F: petsc4py.PETSc.Mat | None = None, P: petsc4py.PETSc.Mat | None = None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Set the function to compute the nonlinear Function :math:`T(\lambda)`.
    
        Collective.
    
        Set the function to compute the nonlinear Function :math:`T(\lambda)`
        as well as the location to store the matrix.
    
        Parameters
        ----------
        function
            Function evaluation routine
        F
            Function matrix
        P
            preconditioner matrix (usually the same as F)
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1068 <slepc4py/SLEPc/NEP.pyx#L1068>`
    
        """
        ...
    def getFunction(self) -> tuple[petsc4py.PETSc.Mat, petsc4py.PETSc.Mat, NEPFunction]:
        """Get the function to compute the nonlinear Function :math:`T(\lambda)`.
    
        Collective.
    
        Get the function to compute the nonlinear Function :math:`T(\lambda)`
        and the matrix.
    
        Parameters
        ----------
        F
            Function matrix
        P
            preconditioner matrix (usually the same as the F)
        function
            Function evaluation routine
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1104 <slepc4py/SLEPc/NEP.pyx#L1104>`
    
        """
        ...
    def setJacobian(self, jacobian: NEPJacobian, J: petsc4py.PETSc.Mat | None = None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Set the function to compute the Jacobian :math:`T'(\lambda)`.
    
        Collective.
    
        Set the function to compute the Jacobian :math:`T'(\lambda)` as well as
        the location to store the matrix.
    
        Parameters
        ----------
        jacobian
            Jacobian evaluation routine
        J
            Jacobian matrix
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1130 <slepc4py/SLEPc/NEP.pyx#L1130>`
    
        """
        ...
    def getJacobian(self) -> tuple[petsc4py.PETSc.Mat, NEPJacobian]:
        """Get the function to compute the Jacobian :math:`T'(\lambda)` and J.
    
        Collective.
    
        Get the function to compute the Jacobian :math:`T'(\lambda)` and the
        matrix.
    
        Parameters
        ----------
        J
            Jacobian matrix
        jacobian
            Jacobian evaluation routine
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1162 <slepc4py/SLEPc/NEP.pyx#L1162>`
    
        """
        ...
    def setSplitOperator(self, A: petsc4py.PETSc.Mat | list[petsc4py.PETSc.Mat], f: FN | list[FN], structure: petsc4py.PETSc.Mat.Structure | None = None) -> None:
        """Set the operator of the nonlinear eigenvalue problem in split form.
    
        Collective.
    
        Parameters
        ----------
        A
            Coefficient matrices of the split form.
        f
            Scalar functions of the split form.
        structure
            Structure flag for matrices.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1184 <slepc4py/SLEPc/NEP.pyx#L1184>`
    
        """
        ...
    def getSplitOperator(self) -> tuple[list[petsc4py.PETSc.Mat], list[FN], petsc4py.PETSc.Mat.Structure]:
        """Get the operator of the nonlinear eigenvalue problem in split form.
    
        Collective.
    
        Returns
        -------
        A: list of petsc4py.PETSc.Mat
            Coefficient matrices of the split form.
        f: list of FN
            Scalar functions of the split form.
        structure: petsc4py.PETSc.Mat.Structure
            Structure flag for matrices.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1218 <slepc4py/SLEPc/NEP.pyx#L1218>`
    
        """
        ...
    def setSplitPreconditioner(self, P: petsc4py.PETSc.Mat | list[petsc4py.PETSc.Mat], structure: petsc4py.PETSc.Mat.Structure | None = None) -> None:
        """Set the operator in split form.
    
        Collective.
    
        Set the operator in split form from which to build the preconditioner
        to be used when solving the nonlinear eigenvalue problem in split form.
    
        Parameters
        ----------
        P
            Coefficient matrices of the split preconditioner.
        structure
            Structure flag for matrices.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1250 <slepc4py/SLEPc/NEP.pyx#L1250>`
    
        """
        ...
    def getSplitPreconditioner(self) -> tuple[list[petsc4py.PETSc.Mat], petsc4py.PETSc.Mat.Structure]:
        """Get the operator of the split preconditioner.
    
        Not collective.
    
        Returns
        -------
        P: list of petsc4py.PETSc.Mat
            Coefficient matrices of the split preconditioner.
        structure: petsc4py.PETSc.Mat.Structure
            Structure flag for matrices.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1279 <slepc4py/SLEPc/NEP.pyx#L1279>`
    
        """
        ...
    def getTwoSided(self) -> bool:
        """Get the flag indicating if a two-sided variant is being used.
    
        Not collective.
    
        Get the flag indicating whether a two-sided variant of the algorithm
        is being used or not.
    
        Returns
        -------
        bool
            Whether the two-sided variant is to be used or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1304 <slepc4py/SLEPc/NEP.pyx#L1304>`
    
        """
        ...
    def setTwoSided(self, twosided: bool) -> None:
        """Set the solver to use a two-sided variant.
    
        Logically collective.
    
        Set the solver to use a two-sided variant so that left eigenvectors
        are also computed.
    
        Parameters
        ----------
        twosided
            Whether the two-sided variant is to be used or not.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1322 <slepc4py/SLEPc/NEP.pyx#L1322>`
    
        """
        ...
    def applyResolvent(self, omega: Scalar, v: Vec, r: Vec, rg: RG | None = None) -> None:
        """Apply the resolvent :math:`T^{-1}(z)` to a given vector.
    
        Collective.
    
        Parameters
        ----------
        omega
            Value where the resolvent must be evaluated.
        v
            Input vector.
        r
            Placeholder for the result vector.
        rg
            Region.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1339 <slepc4py/SLEPc/NEP.pyx#L1339>`
    
        """
        ...
    def setRIILagPreconditioner(self, lag: int) -> None:
        """Set when the preconditioner is rebuilt in the nonlinear solve.
    
        Logically collective.
    
        Parameters
        ----------
        lag
            0 indicates NEVER rebuild, 1 means rebuild every time the Jacobian is
            computed within the nonlinear iteration, 2 means every second time
            the Jacobian is built, etc.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1368 <slepc4py/SLEPc/NEP.pyx#L1368>`
    
        """
        ...
    def getRIILagPreconditioner(self) -> int:
        """Get how often the preconditioner is rebuilt.
    
        Not collective.
    
        Returns
        -------
        int
            The lag parameter.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1384 <slepc4py/SLEPc/NEP.pyx#L1384>`
    
        """
        ...
    def setRIIConstCorrectionTol(self, cct: bool) -> None:
        """Set a flag to keep the tolerance used in the linear solver constant.
    
        Logically collective.
    
        Parameters
        ----------
        cct
             If True, the `petsc4py.PETSc.KSP` relative tolerance is constant.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1399 <slepc4py/SLEPc/NEP.pyx#L1399>`
    
        """
        ...
    def getRIIConstCorrectionTol(self) -> bool:
        """Get the constant tolerance flag.
    
        Not collective.
    
        Returns
        -------
        bool
            If True, the `petsc4py.PETSc.KSP` relative tolerance is constant.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1413 <slepc4py/SLEPc/NEP.pyx#L1413>`
    
        """
        ...
    def setRIIMaximumIterations(self, its: int) -> None:
        """Set the max. number of inner iterations to be used in the RII solver.
    
        Logically collective.
    
        These are the Newton iterations related to the computation of the
        nonlinear Rayleigh functional.
    
        Parameters
        ----------
        its
             Maximum inner iterations.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1428 <slepc4py/SLEPc/NEP.pyx#L1428>`
    
        """
        ...
    def getRIIMaximumIterations(self) -> int:
        """Get the maximum number of inner iterations of RII.
    
        Not collective.
    
        Returns
        -------
        int
            Maximum inner iterations.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1445 <slepc4py/SLEPc/NEP.pyx#L1445>`
    
        """
        ...
    def setRIIHermitian(self, herm: bool) -> None:
        """Set a flag to use the Hermitian version of the solver.
    
        Logically collective.
    
        Set a flag to indicate if the Hermitian version of the scalar
        nonlinear equation must be used by the solver.
    
        Parameters
        ----------
        herm
            If True, the Hermitian version is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1460 <slepc4py/SLEPc/NEP.pyx#L1460>`
    
        """
        ...
    def getRIIHermitian(self) -> bool:
        """Get if the Hermitian version must be used by the solver.
    
        Not collective.
    
        Get the flag about using the Hermitian version of the scalar nonlinear
        equation.
    
        Returns
        -------
        bool
            If True, the Hermitian version is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1477 <slepc4py/SLEPc/NEP.pyx#L1477>`
    
        """
        ...
    def setRIIDeflationThreshold(self, deftol: float) -> None:
        """Set the threshold used to switch between deflated and non-deflated.
    
        Logically collective.
    
        Set the threshold value used to switch between deflated and
        non-deflated iteration.
    
        Parameters
        ----------
        deftol
            The threshold value.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1495 <slepc4py/SLEPc/NEP.pyx#L1495>`
    
        """
        ...
    def getRIIDeflationThreshold(self) -> float:
        """Get the threshold value that controls deflation.
    
        Not collective.
    
        Returns
        -------
        float
            The threshold value.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1512 <slepc4py/SLEPc/NEP.pyx#L1512>`
    
        """
        ...
    def setRIIKSP(self, ksp: petsc4py.PETSc.KSP) -> None:
        """Set a linear solver object associated to the nonlinear eigensolver.
    
        Collective.
    
        Parameters
        ----------
        ``ksp``
            The linear solver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1527 <slepc4py/SLEPc/NEP.pyx#L1527>`
    
        """
        ...
    def getRIIKSP(self) -> KSP:
        """Get the linear solver object associated with the nonlinear eigensolver.
    
        Collective.
    
        Returns
        -------
        `petsc4py.PETSc.KSP`
            The linear solver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1540 <slepc4py/SLEPc/NEP.pyx#L1540>`
    
        """
        ...
    def setSLPDeflationThreshold(self, deftol: float) -> None:
        """Set the threshold used to switch between deflated and non-deflated.
    
        Logically collective.
    
        Parameters
        ----------
        deftol
            The threshold value.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1558 <slepc4py/SLEPc/NEP.pyx#L1558>`
    
        """
        ...
    def getSLPDeflationThreshold(self) -> float:
        """Get the threshold value that controls deflation.
    
        Not collective.
    
        Returns
        -------
        float
            The threshold value.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1572 <slepc4py/SLEPc/NEP.pyx#L1572>`
    
        """
        ...
    def setSLPEPS(self, eps: EPS) -> None:
        """Set a linear eigensolver object associated to the nonlinear eigensolver.
    
        Collective.
    
        Parameters
        ----------
        eps
            The linear eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1587 <slepc4py/SLEPc/NEP.pyx#L1587>`
    
        """
        ...
    def getSLPEPS(self) -> EPS:
        """Get the linear eigensolver object associated with the nonlinear eigensolver.
    
        Collective.
    
        Returns
        -------
        EPS
            The linear eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1600 <slepc4py/SLEPc/NEP.pyx#L1600>`
    
        """
        ...
    def setSLPEPSLeft(self, eps: EPS) -> None:
        """Set a linear eigensolver object associated to the nonlinear eigensolver.
    
        Collective.
    
        Used to compute left eigenvectors in the two-sided variant of SLP.
    
        Parameters
        ----------
        eps
            The linear eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1616 <slepc4py/SLEPc/NEP.pyx#L1616>`
    
        """
        ...
    def getSLPEPSLeft(self) -> EPS:
        """Get the left eigensolver.
    
        Collective.
    
        Returns
        -------
        EPS
            The linear eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1631 <slepc4py/SLEPc/NEP.pyx#L1631>`
    
        """
        ...
    def setSLPKSP(self, ksp: petsc4py.PETSc.KSP) -> None:
        """Set a linear solver object associated to the nonlinear eigensolver.
    
        Collective.
    
        Parameters
        ----------
        ``ksp``
            The linear solver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1647 <slepc4py/SLEPc/NEP.pyx#L1647>`
    
        """
        ...
    def getSLPKSP(self) -> KSP:
        """Get the linear solver object associated with the nonlinear eigensolver.
    
        Collective.
    
        Returns
        -------
        `petsc4py.PETSc.KSP`
            The linear solver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1660 <slepc4py/SLEPc/NEP.pyx#L1660>`
    
        """
        ...
    def setNArnoldiKSP(self, ksp: petsc4py.PETSc.KSP) -> None:
        """Set a linear solver object associated to the nonlinear eigensolver.
    
        Collective.
    
        Parameters
        ----------
        ``ksp``
            The linear solver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1678 <slepc4py/SLEPc/NEP.pyx#L1678>`
    
        """
        ...
    def getNArnoldiKSP(self) -> KSP:
        """Get the linear solver object associated with the nonlinear eigensolver.
    
        Collective.
    
        Returns
        -------
        `petsc4py.PETSc.KSP`
            The linear solver object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1691 <slepc4py/SLEPc/NEP.pyx#L1691>`
    
        """
        ...
    def setNArnoldiLagPreconditioner(self, lag: int) -> None:
        """Set when the preconditioner is rebuilt in the nonlinear solve.
    
        Logically collective.
    
        Parameters
        ----------
        lag
            0 indicates NEVER rebuild, 1 means rebuild every time the Jacobian is
            computed within the nonlinear iteration, 2 means every second time
            the Jacobian is built, etc.
    
        Notes
        -----
        The default is 1. The preconditioner is ALWAYS built in the first
        iteration of a nonlinear solve.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1707 <slepc4py/SLEPc/NEP.pyx#L1707>`
    
        """
        ...
    def getNArnoldiLagPreconditioner(self) -> int:
        """Get how often the preconditioner is rebuilt.
    
        Not collective.
    
        Returns
        -------
        int
            The lag parameter.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1728 <slepc4py/SLEPc/NEP.pyx#L1728>`
    
        """
        ...
    def setInterpolPEP(self, pep: PEP) -> None:
        """Set a polynomial eigensolver object associated to the nonlinear eigensolver.
    
        Collective.
    
        Parameters
        ----------
        pep
            The polynomial eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1745 <slepc4py/SLEPc/NEP.pyx#L1745>`
    
        """
        ...
    def getInterpolPEP(self) -> PEP:
        """Get the associated polynomial eigensolver object.
    
        Collective.
    
        Get the polynomial eigensolver object associated with the nonlinear
        eigensolver.
    
        Returns
        -------
        PEP
            The polynomial eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1758 <slepc4py/SLEPc/NEP.pyx#L1758>`
    
        """
        ...
    def setInterpolInterpolation(self, tol: float | None = None, deg: int | None = None) -> None:
        """Set the tolerance and maximum degree for the interpolation polynomial.
    
        Collective.
    
        Set the tolerance and maximum degree when building the interpolation
        polynomial.
    
        Parameters
        ----------
        tol
            The tolerance to stop computing polynomial coefficients.
        deg
            The maximum degree of interpolation.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1777 <slepc4py/SLEPc/NEP.pyx#L1777>`
    
        """
        ...
    def getInterpolInterpolation(self) -> tuple[float, int]:
        """Get the tolerance and maximum degree for the interpolation polynomial.
    
        Not collective.
    
        Returns
        -------
        tol: float
            The tolerance to stop computing polynomial coefficients.
        deg: int
            The maximum degree of interpolation.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1799 <slepc4py/SLEPc/NEP.pyx#L1799>`
    
        """
        ...
    def setNLEIGSRestart(self, keep: float) -> None:
        """Set the restart parameter for the NLEIGS method.
    
        Logically collective.
    
        The proportion of basis vectors that must be kept after restart.
    
        Parameters
        ----------
        keep
            The number of vectors to be kept at restart.
    
        Notes
        -----
        Allowed values are in the range [0.1,0.9]. The default is 0.5.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1819 <slepc4py/SLEPc/NEP.pyx#L1819>`
    
        """
        ...
    def getNLEIGSRestart(self) -> float:
        """Get the restart parameter used in the NLEIGS method.
    
        Not collective.
    
        Returns
        -------
        float
            The number of vectors to be kept at restart.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1839 <slepc4py/SLEPc/NEP.pyx#L1839>`
    
        """
        ...
    def setNLEIGSLocking(self, lock: bool) -> None:
        """Toggle between locking and non-locking variants of the NLEIGS method.
    
        Logically collective.
    
        Parameters
        ----------
        lock
            True if the locking variant must be selected.
    
        Notes
        -----
        The default is to lock converged eigenpairs when the method restarts.
        This behavior can be changed so that all directions are kept in the
        working subspace even if already converged to working accuracy (the
        non-locking variant).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1854 <slepc4py/SLEPc/NEP.pyx#L1854>`
    
        """
        ...
    def getNLEIGSLocking(self) -> bool:
        """Get the locking flag used in the NLEIGS method.
    
        Not collective.
    
        Returns
        -------
        bool
            The locking flag.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1875 <slepc4py/SLEPc/NEP.pyx#L1875>`
    
        """
        ...
    def setNLEIGSInterpolation(self, tol: float | None = None, deg: int | None = None) -> None:
        """Set the tolerance and maximum degree for the interpolation polynomial.
    
        Collective.
    
        Set the tolerance and maximum degree when building the interpolation
        via divided differences.
    
        Parameters
        ----------
        tol
            The tolerance to stop computing divided differences.
        deg
            The maximum degree of interpolation.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1890 <slepc4py/SLEPc/NEP.pyx#L1890>`
    
        """
        ...
    def getNLEIGSInterpolation(self) -> tuple[float, int]:
        """Get the tolerance and maximum degree for the interpolation polynomial.
    
        Not collective.
    
        Get the tolerance and maximum degree when building the interpolation
        via divided differences.
    
        Returns
        -------
        tol: float
            The tolerance to stop computing divided differences.
        deg: int
            The maximum degree of interpolation.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1912 <slepc4py/SLEPc/NEP.pyx#L1912>`
    
        """
        ...
    def setNLEIGSFullBasis(self, fullbasis: bool = True) -> None:
        """Set TOAR-basis (default) or full-basis variants of the NLEIGS method.
    
        Logically collective.
    
        Toggle between TOAR-basis (default) and full-basis variants of the
        NLEIGS method.
    
        Parameters
        ----------
        fullbasis
            True if the full-basis variant must be selected.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1933 <slepc4py/SLEPc/NEP.pyx#L1933>`
    
        """
        ...
    def getNLEIGSFullBasis(self) -> bool:
        """Get the flag that indicates if NLEIGS is using the full-basis variant.
    
        Not collective.
    
        Returns
        -------
        bool
            True if the full-basis variant must be selected.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1950 <slepc4py/SLEPc/NEP.pyx#L1950>`
    
        """
        ...
    def setNLEIGSEPS(self, eps: EPS) -> None:
        """Set a linear eigensolver object associated to the nonlinear eigensolver.
    
        Collective.
    
        Parameters
        ----------
        eps
            The linear eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1965 <slepc4py/SLEPc/NEP.pyx#L1965>`
    
        """
        ...
    def getNLEIGSEPS(self) -> EPS:
        """Get the linear eigensolver object associated with the nonlinear eigensolver.
    
        Collective.
    
        Returns
        -------
        EPS
            The linear eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1978 <slepc4py/SLEPc/NEP.pyx#L1978>`
    
        """
        ...
    def setNLEIGSRKShifts(self, shifts: Sequence[Scalar]) -> None:
        """Set a list of shifts to be used in the Rational Krylov method.
    
        Collective.
    
        Parameters
        ----------
        shifts
            Values specifying the shifts.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:1994 <slepc4py/SLEPc/NEP.pyx#L1994>`
    
        """
        ...
    def getNLEIGSRKShifts(self) -> ArrayScalar:
        """Get the list of shifts used in the Rational Krylov method.
    
        Not collective.
    
        Returns
        -------
        ArrayScalar
            The shift values.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2010 <slepc4py/SLEPc/NEP.pyx#L2010>`
    
        """
        ...
    def getNLEIGSKSPs(self) -> list[KSP]:
        """Get the list of linear solver objects associated with the NLEIGS solver.
    
        Collective.
    
        Returns
        -------
        list of `petsc4py.PETSc.KSP`
            The linear solver objects.
    
        Notes
        -----
        The number of `petsc4py.PETSc.KSP` solvers is equal to the number of
        shifts provided by the user, or 1 if the user did not provide shifts.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2031 <slepc4py/SLEPc/NEP.pyx#L2031>`
    
        """
        ...
    def setCISSExtraction(self, extraction: CISSExtraction) -> None:
        """Set the extraction technique used in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        extraction
            The extraction technique.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2054 <slepc4py/SLEPc/NEP.pyx#L2054>`
    
        """
        ...
    def getCISSExtraction(self) -> CISSExtraction:
        """Get the extraction technique used in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        CISSExtraction
            The extraction technique.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2068 <slepc4py/SLEPc/NEP.pyx#L2068>`
    
        """
        ...
    def setCISSSizes(self, ip: int | None = None, bs: int | None = None, ms: int | None = None, npart: int | None = None, bsmax: int | None = None, realmats: bool = False) -> None:
        """Set the values of various size parameters in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        ip
            Number of integration points.
        bs
            Block size.
        ms
            Moment size.
        npart
            Number of partitions when splitting the communicator.
        bsmax
            Maximum block size.
        realmats
            True if A and B are real.
    
        Notes
        -----
        The default number of partitions is 1. This means the internal
        `petsc4py.PETSc.KSP` object is shared among all processes of the `NEP`
        communicator. Otherwise, the communicator is split into npart
        communicators, so that ``npart`` `petsc4py.PETSc.KSP` solves proceed
        simultaneously.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2083 <slepc4py/SLEPc/NEP.pyx#L2083>`
    
        """
        ...
    def getCISSSizes(self) -> tuple[int, int, int, int, int, bool]:
        """Get the values of various size parameters in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        ip: int
            Number of integration points.
        bs: int
            Block size.
        ms: int
            Moment size.
        npart: int
            Number of partitions when splitting the communicator.
        bsmax: int
            Maximum block size.
        realmats: bool
            True if A and B are real.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2133 <slepc4py/SLEPc/NEP.pyx#L2133>`
    
        """
        ...
    def setCISSThreshold(self, delta: float | None = None, spur: float | None = None) -> None:
        """Set the values of various threshold parameters in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        delta
            Threshold for numerical rank.
        spur
            Spurious threshold (to discard spurious eigenpairs).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2163 <slepc4py/SLEPc/NEP.pyx#L2163>`
    
        """
        ...
    def getCISSThreshold(self) -> tuple[float, float]:
        """Get the values of various threshold parameters in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        delta: float
            Threshold for numerical rank.
        spur: float
            Spurious threshold (to discard spurious eigenpairs.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2182 <slepc4py/SLEPc/NEP.pyx#L2182>`
    
        """
        ...
    def setCISSRefinement(self, inner: int | None = None, blsize: int | None = None) -> None:
        """Set the values of various refinement parameters in the CISS solver.
    
        Logically collective.
    
        Parameters
        ----------
        inner
            Number of iterative refinement iterations (inner loop).
        blsize
            Number of iterative refinement iterations (blocksize loop).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2200 <slepc4py/SLEPc/NEP.pyx#L2200>`
    
        """
        ...
    def getCISSRefinement(self) -> tuple[int, int]:
        """Get the values of various refinement parameters in the CISS solver.
    
        Not collective.
    
        Returns
        -------
        inner: int
            Number of iterative refinement iterations (inner loop).
        blsize: int
            Number of iterative refinement iterations (blocksize loop).
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2219 <slepc4py/SLEPc/NEP.pyx#L2219>`
    
        """
        ...
    def getCISSKSPs(self) -> list[KSP]:
        """Get the list of linear solver objects associated with the CISS solver.
    
        Collective.
    
        Returns
        -------
        list of `petsc4py.PETSc.KSP`
            The linear solver objects.
    
        Notes
        -----
        The number of `petsc4py.PETSc.KSP` solvers is equal to the number of
        integration points divided by the number of partitions. This value is
        halved in the case of real matrices with a region centered at the real
        axis.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2237 <slepc4py/SLEPc/NEP.pyx#L2237>`
    
        """
        ...
    @property
    def problem_type(self) -> NEPProblemType:
        """The problem type from the NEP object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2260 <slepc4py/SLEPc/NEP.pyx#L2260>`
    
        """
        ...
    @property
    def which(self) -> NEPWhich:
        """The portion of the spectrum to be sought.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2267 <slepc4py/SLEPc/NEP.pyx#L2267>`
    
        """
        ...
    @property
    def target(self) -> float:
        """The value of the target.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2274 <slepc4py/SLEPc/NEP.pyx#L2274>`
    
        """
        ...
    @property
    def tol(self) -> float:
        """The tolerance used by the NEP convergence tests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2281 <slepc4py/SLEPc/NEP.pyx#L2281>`
    
        """
        ...
    @property
    def max_it(self) -> int:
        """The maximum iteration count used by the NEP convergence tests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2288 <slepc4py/SLEPc/NEP.pyx#L2288>`
    
        """
        ...
    @property
    def track_all(self) -> bool:
        """Compute the residual of all approximate eigenpairs.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2295 <slepc4py/SLEPc/NEP.pyx#L2295>`
    
        """
        ...
    @property
    def bv(self) -> BV:
        """The basis vectors (BV) object associated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2302 <slepc4py/SLEPc/NEP.pyx#L2302>`
    
        """
        ...
    @property
    def rg(self) -> RG:
        """The region (RG) object associated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2309 <slepc4py/SLEPc/NEP.pyx#L2309>`
    
        """
        ...
    @property
    def ds(self) -> DS:
        """The direct solver (DS) object associated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/NEP.pyx:2316 <slepc4py/SLEPc/NEP.pyx#L2316>`
    
        """
        ...

class MFN(Object):
    """MFN."""
    class Type:
        """MFN type.
        
        Action of a matrix function on a vector.
        
        - `KRYLOV`:  Restarted Krylov solver.
        - `EXPOKIT`: Implementation of the method in Expokit.
        
        """
        KRYLOV: str = _def(str, 'KRYLOV')  #: Object ``KRYLOV`` of type :class:`str`
        EXPOKIT: str = _def(str, 'EXPOKIT')  #: Object ``EXPOKIT`` of type :class:`str`
    class ConvergedReason:
        """MFN convergence reasons.
        
        - 'MFN_CONVERGED_TOL': All eigenpairs converged to requested tolerance.
        - 'MFN_CONVERGED_ITS': Solver completed the requested number of steps.
        - 'MFN_DIVERGED_ITS': Maximum number of iterations exceeded.
        - 'MFN_DIVERGED_BREAKDOWN': Generic breakdown in method.
        
        """
        CONVERGED_TOL: int = _def(int, 'CONVERGED_TOL')  #: Constant ``CONVERGED_TOL`` of type :class:`int`
        CONVERGED_ITS: int = _def(int, 'CONVERGED_ITS')  #: Constant ``CONVERGED_ITS`` of type :class:`int`
        DIVERGED_ITS: int = _def(int, 'DIVERGED_ITS')  #: Constant ``DIVERGED_ITS`` of type :class:`int`
        DIVERGED_BREAKDOWN: int = _def(int, 'DIVERGED_BREAKDOWN')  #: Constant ``DIVERGED_BREAKDOWN`` of type :class:`int`
        CONVERGED_ITERATING: int = _def(int, 'CONVERGED_ITERATING')  #: Constant ``CONVERGED_ITERATING`` of type :class:`int`
        ITERATING: int = _def(int, 'ITERATING')  #: Constant ``ITERATING`` of type :class:`int`
    def view(self, viewer: Viewer | None = None) -> None:
        """Print the MFN data structure.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:44 <slepc4py/SLEPc/MFN.pyx#L44>`
    
        """
        ...
    def destroy(self) -> Self:
        """Destroy the MFN object.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:59 <slepc4py/SLEPc/MFN.pyx#L59>`
    
        """
        ...
    def reset(self) -> None:
        """Reset the MFN object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:69 <slepc4py/SLEPc/MFN.pyx#L69>`
    
        """
        ...
    def create(self, comm: Comm | None = None) -> Self:
        """Create the MFN object.
    
        Collective.
    
        Parameters
        ----------
        comm
            MPI communicator. If not provided, it defaults to all processes.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:77 <slepc4py/SLEPc/MFN.pyx#L77>`
    
        """
        ...
    def setType(self, mfn_type: Type | str) -> None:
        """Set the particular solver to be used in the MFN object.
    
        Logically collective.
    
        Parameters
        ----------
        mfn_type
            The solver to be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:94 <slepc4py/SLEPc/MFN.pyx#L94>`
    
        """
        ...
    def getType(self) -> str:
        """Get the MFN type of this object.
    
        Not collective.
    
        Returns
        -------
        str
            The solver currently being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:109 <slepc4py/SLEPc/MFN.pyx#L109>`
    
        """
        ...
    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all MFN options in the database.
    
        Not collective.
    
        Returns
        -------
        str
            The prefix string set for this MFN object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:124 <slepc4py/SLEPc/MFN.pyx#L124>`
    
        """
        ...
    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all MFN options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all MFN option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:139 <slepc4py/SLEPc/MFN.pyx#L139>`
    
        """
        ...
    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all MFN options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all MFN option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:154 <slepc4py/SLEPc/MFN.pyx#L154>`
    
        """
        ...
    def setFromOptions(self) -> None:
        """Set MFN options from the options database.
    
        Collective.
    
        Set MFN options from the options database. This routine must
        be called before `setUp()` if the user is to be allowed to set
        the solver type.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:169 <slepc4py/SLEPc/MFN.pyx#L169>`
    
        """
        ...
    def getTolerances(self) -> tuple[float, int]:
        """Get the tolerance and maximum iteration count.
    
        Not collective.
    
        Get the tolerance and maximum iteration count used by the
        default MFN convergence tests.
    
        Returns
        -------
        tol: float
            The convergence tolerance.
        max_it: int
            The maximum number of iterations
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:181 <slepc4py/SLEPc/MFN.pyx#L181>`
    
        """
        ...
    def setTolerances(self, tol: float | None = None, max_it: int | None = None) -> None:
        """Set the tolerance and maximum iteration count.
    
        Logically collective.
    
        Set the tolerance and maximum iteration count used by the
        default MFN convergence tests.
    
        Parameters
        ----------
        tol
            The convergence tolerance.
        max_it
            The maximum number of iterations
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:202 <slepc4py/SLEPc/MFN.pyx#L202>`
    
        """
        ...
    def getDimensions(self) -> int:
        """Get the dimension of the subspace used by the solver.
    
        Not collective.
    
        Returns
        -------
        int
            Maximum dimension of the subspace to be used by the solver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:224 <slepc4py/SLEPc/MFN.pyx#L224>`
    
        """
        ...
    def setDimensions(self, ncv: int) -> None:
        """Set the dimension of the subspace to be used by the solver.
    
        Logically collective.
    
        Parameters
        ----------
        ncv
            Maximum dimension of the subspace to be used by the solver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:239 <slepc4py/SLEPc/MFN.pyx#L239>`
    
        """
        ...
    def getFN(self) -> FN:
        """Get the math function object associated to the MFN object.
    
        Not collective.
    
        Returns
        -------
        FN
            The math function context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:253 <slepc4py/SLEPc/MFN.pyx#L253>`
    
        """
        ...
    def setFN(self, fn: FN) -> None:
        """Set a math function object associated to the MFN object.
    
        Collective.
    
        Parameters
        ----------
        fn
            The math function context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:269 <slepc4py/SLEPc/MFN.pyx#L269>`
    
        """
        ...
    def getBV(self) -> BV:
        """Get the basis vector object associated to the MFN object.
    
        Not collective.
    
        Returns
        -------
        BV
            The basis vectors context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:282 <slepc4py/SLEPc/MFN.pyx#L282>`
    
        """
        ...
    def setBV(self, bv: BV) -> None:
        """Set a basis vector object associated to the MFN object.
    
        Collective.
    
        Parameters
        ----------
        bv
            The basis vectors context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:298 <slepc4py/SLEPc/MFN.pyx#L298>`
    
        """
        ...
    def getOperator(self) -> petsc4py.PETSc.Mat:
        """Get the matrix associated with the MFN object.
    
        Collective.
    
        Returns
        -------
        petsc4py.PETSc.Mat
            The matrix for which the matrix function is to be computed.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:311 <slepc4py/SLEPc/MFN.pyx#L311>`
    
        """
        ...
    def setOperator(self, A: Mat) -> None:
        """Set the matrix associated with the MFN object.
    
        Collective.
    
        Parameters
        ----------
        A
            The problem matrix.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:327 <slepc4py/SLEPc/MFN.pyx#L327>`
    
        """
        ...
    def setMonitor(self, monitor: MFNMonitorFunction | None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Append a monitor function to the list of monitors.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:342 <slepc4py/SLEPc/MFN.pyx#L342>`
    
        """
        ...
    def getMonitor(self) -> MFNMonitorFunction:
        """Get the list of monitor functions.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:363 <slepc4py/SLEPc/MFN.pyx#L363>`
    
        """
        ...
    def cancelMonitor(self) -> None:
        """Clear all monitors for an `MFN` object.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:367 <slepc4py/SLEPc/MFN.pyx#L367>`
    
        """
        ...
    def setUp(self) -> None:
        """Set up all the necessary internal data structures.
    
        Collective.
    
        Set up all the internal data structures necessary for the execution
        of the eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:378 <slepc4py/SLEPc/MFN.pyx#L378>`
    
        """
        ...
    def solve(self, b: Vec, x: Vec) -> None:
        """Solve the matrix function problem.
    
        Collective.
    
        Given a vector :math:`b`, the vector :math:`x = f(A) b` is
        returned.
    
        Parameters
        ----------
        b
            The right hand side vector.
        x
            The solution.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:389 <slepc4py/SLEPc/MFN.pyx#L389>`
    
        """
        ...
    def solveTranspose(self, b: Vec, x: Vec) -> None:
        """Solve the transpose matrix function problem.
    
        Collective.
    
        Given a vector :math:`b`, the vector :math:`x = f(A^T) b` is
        returned.
    
        Parameters
        ----------
        b
            The right hand side vector.
        x
            The solution.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:407 <slepc4py/SLEPc/MFN.pyx#L407>`
    
        """
        ...
    def getIterationNumber(self) -> int:
        """Get the current iteration number.
    
        Not collective.
    
        Get the current iteration number. If the call to `solve()` is
        complete, then it returns the number of iterations carried out
        by the solution method.
    
        Returns
        -------
        int
            Iteration number.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:425 <slepc4py/SLEPc/MFN.pyx#L425>`
    
        """
        ...
    def getConvergedReason(self) -> ConvergedReason:
        """Get the reason why the `solve()` iteration was stopped.
    
        Not collective.
    
        Returns
        -------
        ConvergedReason
            Negative value indicates diverged, positive value converged.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:444 <slepc4py/SLEPc/MFN.pyx#L444>`
    
        """
        ...
    def setErrorIfNotConverged(self, flg: bool = True) -> None:
        """Set `solve()` to generate an error if the solver does not converge.
    
        Logically collective.
    
        Parameters
        ----------
        flg
            True indicates you want the error generated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:459 <slepc4py/SLEPc/MFN.pyx#L459>`
    
        """
        ...
    def getErrorIfNotConverged(self) -> bool:
        """Get if `solve()` generates an error if the solver does not converge.
    
        Not collective.
    
        Get a flag indicating whether `solve()` will generate an error if the
        solver does not converge.
    
        Returns
        -------
        bool
            True indicates you want the error generated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:473 <slepc4py/SLEPc/MFN.pyx#L473>`
    
        """
        ...
    @property
    def tol(self) -> float:
        """The tolerance count used by the MFN convergence tests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:493 <slepc4py/SLEPc/MFN.pyx#L493>`
    
        """
        ...
    @property
    def max_it(self) -> int:
        """The maximum iteration count used by the MFN convergence tests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:500 <slepc4py/SLEPc/MFN.pyx#L500>`
    
        """
        ...
    @property
    def fn(self) -> FN:
        """The math function (FN) object associated to the MFN object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:507 <slepc4py/SLEPc/MFN.pyx#L507>`
    
        """
        ...
    @property
    def bv(self) -> BV:
        """The basis vectors (BV) object associated to the MFN object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/MFN.pyx:514 <slepc4py/SLEPc/MFN.pyx#L514>`
    
        """
        ...

class LME(Object):
    """LME."""
    class Type:
        """LME type.
        
        - `KRYLOV`:  Restarted Krylov solver.
        
        """
        KRYLOV: str = _def(str, 'KRYLOV')  #: Object ``KRYLOV`` of type :class:`str`
    class ProblemType:
        """LME problem type.
        
        - `LYAPUNOV`:      Continuous-time Lyapunov.
        - `SYLVESTER`:     Continuous-time Sylvester.
        - `GEN_LYAPUNOV`:  Generalized Lyapunov.
        - `GEN_SYLVESTER`: Generalized Sylvester.
        - `DT_LYAPUNOV`:   Discrete-time Lyapunov.
        - `STEIN`:         Stein.
        
        """
        LYAPUNOV: int = _def(int, 'LYAPUNOV')  #: Constant ``LYAPUNOV`` of type :class:`int`
        SYLVESTER: int = _def(int, 'SYLVESTER')  #: Constant ``SYLVESTER`` of type :class:`int`
        GEN_LYAPUNOV: int = _def(int, 'GEN_LYAPUNOV')  #: Constant ``GEN_LYAPUNOV`` of type :class:`int`
        GEN_SYLVESTER: int = _def(int, 'GEN_SYLVESTER')  #: Constant ``GEN_SYLVESTER`` of type :class:`int`
        DT_LYAPUNOV: int = _def(int, 'DT_LYAPUNOV')  #: Constant ``DT_LYAPUNOV`` of type :class:`int`
        STEIN: int = _def(int, 'STEIN')  #: Constant ``STEIN`` of type :class:`int`
    class ConvergedReason:
        """LME convergence reasons.
        
        - `CONVERGED_TOL`:       All eigenpairs converged to requested tolerance.
        - `DIVERGED_ITS`:        Maximum number of iterations exceeded.
        - `DIVERGED_BREAKDOWN`:  Solver failed due to breakdown.
        - `CONVERGED_ITERATING`: Iteration not finished yet.
        
        """
        CONVERGED_TOL: int = _def(int, 'CONVERGED_TOL')  #: Constant ``CONVERGED_TOL`` of type :class:`int`
        DIVERGED_ITS: int = _def(int, 'DIVERGED_ITS')  #: Constant ``DIVERGED_ITS`` of type :class:`int`
        DIVERGED_BREAKDOWN: int = _def(int, 'DIVERGED_BREAKDOWN')  #: Constant ``DIVERGED_BREAKDOWN`` of type :class:`int`
        CONVERGED_ITERATING: int = _def(int, 'CONVERGED_ITERATING')  #: Constant ``CONVERGED_ITERATING`` of type :class:`int`
        ITERATING: int = _def(int, 'ITERATING')  #: Constant ``ITERATING`` of type :class:`int`
    def view(self, viewer: Viewer | None = None) -> None:
        """Print the LME data structure.
    
        Collective.
    
        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:58 <slepc4py/SLEPc/LME.pyx#L58>`
    
        """
        ...
    def destroy(self) -> Self:
        """Destroy the LME object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:73 <slepc4py/SLEPc/LME.pyx#L73>`
    
        """
        ...
    def reset(self) -> None:
        """Reset the LME object.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:83 <slepc4py/SLEPc/LME.pyx#L83>`
    
        """
        ...
    def create(self, comm: Comm | None = None) -> Self:
        """Create the LME object.
    
        Collective.
    
        Parameters
        ----------
        comm
            MPI communicator. If not provided, it defaults to all processes.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:91 <slepc4py/SLEPc/LME.pyx#L91>`
    
        """
        ...
    def setType(self, lme_type: Type | str) -> None:
        """Set the particular solver to be used in the LME object.
    
        Logically collective.
    
        Parameters
        ----------
        lme_type
            The solver to be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:108 <slepc4py/SLEPc/LME.pyx#L108>`
    
        """
        ...
    def getType(self) -> str:
        """Get the LME type of this object.
    
        Not collective.
    
        Returns
        -------
        str
            The solver currently being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:123 <slepc4py/SLEPc/LME.pyx#L123>`
    
        """
        ...
    def setProblemType(self, lme_problem_type: ProblemType | str) -> None:
        """Set the LME problem type of this object.
    
        Logically collective.
    
        Parameters
        ----------
        lme_problem_type
            The problem type to be used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:138 <slepc4py/SLEPc/LME.pyx#L138>`
    
        """
        ...
    def getProblemType(self) -> ProblemType:
        """Get the LME problem type of this object.
    
        Not collective.
    
        Returns
        -------
        ProblemType
            The problem type currently being used.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:152 <slepc4py/SLEPc/LME.pyx#L152>`
    
        """
        ...
    def setCoefficients(self, A: Mat, B: Mat | None = None, D: Mat | None = None, E: Mat | None = None) -> None:
        """Set the coefficient matrices.
    
        Collective.
    
        Set the coefficient matrices that define the linear matrix equation
        to be solved.
    
        Parameters
        ----------
        A
            First coefficient matrix
        B
            Second coefficient matrix, optional
        D
            Third coefficient matrix, optional
        E
            Fourth coefficient matrix, optional
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:167 <slepc4py/SLEPc/LME.pyx#L167>`
    
        """
        ...
    def getCoefficients(self) -> tuple[Mat, Mat | None, Mat | None, Mat | None]:
        """Get the coefficient matrices of the matrix equation.
    
        Collective.
    
        Returns
        -------
        ``A``
            First coefficient matrix
        ``B``
            Second coefficient matrix, if available
        ``D``
            Third coefficient matrix, if available
        ``E``
            Fourth coefficient matrix, if available
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:193 <slepc4py/SLEPc/LME.pyx#L193>`
    
        """
        ...
    def setRHS(self, C: Mat) -> None:
        """Set the right-hand side of the matrix equation.
    
        Collective.
    
        Set the right-hand side of the matrix equation, as a low-rank
        matrix.
    
        Parameters
        ----------
        C
            The right-hand side matrix
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:223 <slepc4py/SLEPc/LME.pyx#L223>`
    
        """
        ...
    def getRHS(self) -> Mat:
        """Get the right-hand side of the matrix equation.
    
        Collective.
    
        Returns
        -------
        C
            The low-rank matrix
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:239 <slepc4py/SLEPc/LME.pyx#L239>`
    
        """
        ...
    def setSolution(self, X: Mat) -> None:
        """Set the placeholder for the solution of the matrix equation.
    
        Collective.
    
        Set the placeholder for the solution of the matrix
        equation, as a low-rank matrix.
    
        Parameters
        ----------
        X
            The solution matrix
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:255 <slepc4py/SLEPc/LME.pyx#L255>`
    
        """
        ...
    def getSolution(self) -> Mat:
        """Get the solution of the matrix equation.
    
        Collective.
    
        Returns
        -------
        X
            The low-rank matrix
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:271 <slepc4py/SLEPc/LME.pyx#L271>`
    
        """
        ...
    def getErrorEstimate(self) -> float:
        """Get the error estimate obtained during solve.
    
        Not collective.
    
        Returns
        -------
        float
            The error estimate
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:287 <slepc4py/SLEPc/LME.pyx#L287>`
    
        """
        ...
    def computeError(self) -> float:
        """Compute the error associated with the last equation solved.
    
        Collective.
    
        Computes the error (based on the residual norm) associated with the
        last equation solved.
    
        Returns
        -------
        float
            The error
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:302 <slepc4py/SLEPc/LME.pyx#L302>`
    
        """
        ...
    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all LME options in the database.
    
        Not collective.
    
        Returns
        -------
        str
            The prefix string set for this LME object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:320 <slepc4py/SLEPc/LME.pyx#L320>`
    
        """
        ...
    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all LME options in the database.
    
        Logically collective.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all LME option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:335 <slepc4py/SLEPc/LME.pyx#L335>`
    
        """
        ...
    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching in the database.
    
        Logically collective.
    
        Append to the prefix used for searching for all LME options in the
        database.
    
        Parameters
        ----------
        prefix
            The prefix string to prepend to all LME option requests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:350 <slepc4py/SLEPc/LME.pyx#L350>`
    
        """
        ...
    def setFromOptions(self) -> None:
        """Set LME options from the options database.
    
        Collective.
    
        Sets LME options from the options database. This routine must
        be called before `setUp()` if the user is to be allowed to set
        the solver type.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:368 <slepc4py/SLEPc/LME.pyx#L368>`
    
        """
        ...
    def getTolerances(self) -> tuple[float, int]:
        """Get the tolerance and maximum iteration count.
    
        Not collective.
    
        Get the tolerance and maximum iteration count used by the
        default LME convergence tests.
    
        Returns
        -------
        tol: float
            The convergence tolerance.
        max_it: int
            The maximum number of iterations
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:380 <slepc4py/SLEPc/LME.pyx#L380>`
    
        """
        ...
    def setTolerances(self, tol: float | None = None, max_it: int | None = None) -> None:
        """Set the tolerance and maximum iteration count.
    
        Logically collective.
    
        Set the tolerance and maximum iteration count used by the
        default LME convergence tests.
    
        Parameters
        ----------
        tol
            The convergence tolerance.
        max_it
            The maximum number of iterations
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:401 <slepc4py/SLEPc/LME.pyx#L401>`
    
        """
        ...
    def getDimensions(self) -> int:
        """Get the dimension of the subspace used by the solver.
    
        Not collective.
    
        Returns
        -------
        int
            Maximum dimension of the subspace to be used by the solver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:423 <slepc4py/SLEPc/LME.pyx#L423>`
    
        """
        ...
    def setDimensions(self, ncv: int) -> None:
        """Set the dimension of the subspace to be used by the solver.
    
        Logically collective.
    
        Parameters
        ----------
        ncv
            Maximum dimension of the subspace to be used by the solver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:438 <slepc4py/SLEPc/LME.pyx#L438>`
    
        """
        ...
    def getBV(self) -> BV:
        """Get the basis vector object associated to the LME object.
    
        Not collective.
    
        Returns
        -------
        BV
            The basis vectors context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:452 <slepc4py/SLEPc/LME.pyx#L452>`
    
        """
        ...
    def setBV(self, bv: BV) -> None:
        """Set a basis vector object to the LME object.
    
        Collective.
    
        Parameters
        ----------
        bv
            The basis vectors context.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:468 <slepc4py/SLEPc/LME.pyx#L468>`
    
        """
        ...
    def setMonitor(self, monitor: LMEMonitorFunction | None, args: tuple[Any, ...] | None = None, kargs: dict[str, Any] | None = None) -> None:
        """Append a monitor function to the list of monitors.
    
        Logically collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:481 <slepc4py/SLEPc/LME.pyx#L481>`
    
        """
        ...
    def getMonitor(self) -> LMEMonitorFunction:
        """Get the list of monitor functions.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:502 <slepc4py/SLEPc/LME.pyx#L502>`
    
        """
        ...
    def cancelMonitor(self) -> None:
        """Clear all monitors for an `LME` object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:508 <slepc4py/SLEPc/LME.pyx#L508>`
    
        """
        ...
    def setUp(self) -> None:
        """Set up all the internal necessary data structures.
    
        Collective.
    
        Set up all the internal data structures necessary for the
        execution of the eigensolver.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:515 <slepc4py/SLEPc/LME.pyx#L515>`
    
        """
        ...
    def solve(self) -> None:
        """Solve the linear matrix equation.
    
        Collective.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:526 <slepc4py/SLEPc/LME.pyx#L526>`
    
        """
        ...
    def getIterationNumber(self) -> int:
        """Get the current iteration number.
    
        Not collective.
    
        If the call to `solve()` is complete, then it returns the number of
        iterations carried out by the solution method.
    
        Returns
        -------
        int
            Iteration number.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:534 <slepc4py/SLEPc/LME.pyx#L534>`
    
        """
        ...
    def getConvergedReason(self) -> ConvergedReason:
        """Get the reason why the `solve()` iteration was stopped.
    
        Not collective.
    
        Returns
        -------
        ConvergedReason
            Negative value indicates diverged, positive value converged.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:552 <slepc4py/SLEPc/LME.pyx#L552>`
    
        """
        ...
    def setErrorIfNotConverged(self, flg: bool = True) -> None:
        """Set `solve()` to generate an error if the solver has not converged.
    
        Logically collective.
    
        Parameters
        ----------
        flg
            True indicates you want the error generated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:567 <slepc4py/SLEPc/LME.pyx#L567>`
    
        """
        ...
    def getErrorIfNotConverged(self) -> bool:
        """Get if `solve()` generates an error if the solver does not converge.
    
        Not collective.
    
        Get a flag indicating whether `solve()` will generate an error if the
        solver does not converge.
    
        Returns
        -------
        bool
            True indicates you want the error generated.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:581 <slepc4py/SLEPc/LME.pyx#L581>`
    
        """
        ...
    @property
    def tol(self) -> float:
        """The tolerance value used by the LME convergence tests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:601 <slepc4py/SLEPc/LME.pyx#L601>`
    
        """
        ...
    @property
    def max_it(self) -> int:
        """The maximum iteration count used by the LME convergence tests.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:608 <slepc4py/SLEPc/LME.pyx#L608>`
    
        """
        ...
    @property
    def fn(self) -> FN:
        """The math function (FN) object associated to the LME object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:615 <slepc4py/SLEPc/LME.pyx#L615>`
    
        """
        ...
    @property
    def bv(self) -> BV:
        """The basis vectors (BV) object associated to the LME object.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/LME.pyx:622 <slepc4py/SLEPc/LME.pyx#L622>`
    
        """
        ...

class Sys:
    """Sys."""
    @classmethod
    def getVersion(cls, devel: bool = False, date: bool = False, author: bool = False) -> tuple[int, int, int]:
        """Return SLEPc version information.
    
        Not collective.
    
        Parameters
        ----------
        devel
            Additionally, return whether using an in-development version.
        date
            Additionally, return date information.
        author
            Additionally, return author information.
    
        Returns
        -------
        major: int
            Major version number.
        minor: int
            Minor version number.
        micro: int
            Micro (or patch) version number.
    
        See Also
        --------
        slepc.SlepcGetVersion, slepc.SlepcGetVersionNumber
    
    
    
        :sources:`Source code at slepc4py/SLEPc/Sys.pyx:6 <slepc4py/SLEPc/Sys.pyx#L6>`
    
        """
        ...
    @classmethod
    def getVersionInfo(cls) -> dict[str, bool | int | str]:
        """Return SLEPc version information.
    
        Not collective.
    
        Returns
        -------
        info: dict
            Dictionary with version information.
    
        See Also
        --------
        slepc.SlepcGetVersion, slepc.SlepcGetVersionNumber
    
    
    
        :sources:`Source code at slepc4py/SLEPc/Sys.pyx:62 <slepc4py/SLEPc/Sys.pyx#L62>`
    
        """
        ...
    @classmethod
    def isInitialized(cls) -> bool:
        """Return whether SLEPc has been initialized.
    
        Not collective.
    
        See Also
        --------
        isFinalized
    
    
    
        :sources:`Source code at slepc4py/SLEPc/Sys.pyx:88 <slepc4py/SLEPc/Sys.pyx#L88>`
    
        """
        ...
    @classmethod
    def isFinalized(cls) -> bool:
        """Return whether SLEPc has been finalized.
    
        Not collective.
    
        See Also
        --------
        isInitialized
    
    
    
        :sources:`Source code at slepc4py/SLEPc/Sys.pyx:101 <slepc4py/SLEPc/Sys.pyx#L101>`
    
        """
        ...
    @classmethod
    def hasExternalPackage(cls, package: str) -> bool:
        """Return whether SLEPc has support for external package.
    
        Not collective.
    
        Parameters
        ----------
        package
            The external package name.
    
        See Also
        --------
        slepc.SlepcHasExternalPackage
    
    
    
        :sources:`Source code at slepc4py/SLEPc/Sys.pyx:116 <slepc4py/SLEPc/Sys.pyx#L116>`
    
        """
        ...

class Util:
    """Util."""
    @classmethod
    def createMatBSE(cls, R: petsc4py.PETSc.Mat, C: petsc4py.PETSc.Mat) -> petsc4py.PETSc.Mat:
        """Create a matrix that can be used to define a BSE type problem.
    
        Collective.
    
        Create a matrix that can be used to define a structured eigenvalue
        problem of type BSE (Bethe-Salpeter Equation).
    
        Parameters
        ----------
        R
            The matrix for the diagonal block (resonant).
        C
            The matrix for the off-diagonal block (coupling).
    
        Returns
        -------
        petsc4py.PETSc.Mat
            The matrix with the block form :math:`H = [ R\; C; {-C}^H\; {-R}^T ]`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/Util.pyx:6 <slepc4py/SLEPc/Util.pyx#L6>`
    
        """
        ...
    @classmethod
    def createMatHamiltonian(cls, A: petsc4py.PETSc.Mat, B: petsc4py.PETSc.Mat, C: petsc4py.PETSc.Mat) -> petsc4py.PETSc.Mat:
        """Create matrix to be used for a structured Hamiltonian eigenproblem.
    
        Collective.
    
        Parameters
        ----------
        A
            The matrix for (0,0) block.
        B
            The matrix for (0,1) block, must be real symmetric or Hermitian.
        C
            The matrix for (1,0) block, must be real symmetric or Hermitian.
    
        Returns
        -------
        petsc4py.PETSc.Mat
            The matrix with the block form :math:`H = [ A B; C -A^* ]`.
    
    
    
        :sources:`Source code at slepc4py/SLEPc/Util.pyx:32 <slepc4py/SLEPc/Util.pyx#L32>`
    
        """
        ...

class STFilterType:
    """ST filter type.
    
    - ``FILTLAN``:  An adapted implementation of the Filtered Lanczos Package.
    - ``CHEBYSEV``: A polynomial filter based on a truncated Chebyshev series.
    
    """
    FILTLAN: int = _def(int, 'FILTLAN')  #: Constant ``FILTLAN`` of type :class:`int`
    CHEBYSHEV: int = _def(int, 'CHEBYSHEV')  #: Constant ``CHEBYSHEV`` of type :class:`int`

class STFilterDamping:
    """ST filter damping.
    
    - `NONE`:    No damping
    - `JACKSON`: Jackson damping
    - `LANCZOS`: Lanczos damping
    - `FEJER`:   Fejer damping
    
    """
    NONE: int = _def(int, 'NONE')  #: Constant ``NONE`` of type :class:`int`
    JACKSON: int = _def(int, 'JACKSON')  #: Constant ``JACKSON`` of type :class:`int`
    LANCZOS: int = _def(int, 'LANCZOS')  #: Constant ``LANCZOS`` of type :class:`int`
    FEJER: int = _def(int, 'FEJER')  #: Constant ``FEJER`` of type :class:`int`

class BVSVDMethod:
    """BV methods for computing the SVD.
    
    - `REFINE`: Based on the SVD of the cross product matrix :math:`S^H S`,
                with refinement.
    - `QR`:     Based on the SVD of the triangular factor of qr(S).
    - `QR_CAA`: Variant of QR intended for use in communication-avoiding
                Arnoldi.
    
    """
    REFINE: int = _def(int, 'REFINE')  #: Constant ``REFINE`` of type :class:`int`
    QR: int = _def(int, 'QR')  #: Constant ``QR`` of type :class:`int`
    QR_CAA: int = _def(int, 'QR_CAA')  #: Constant ``QR_CAA`` of type :class:`int`

class EPSKrylovSchurBSEType:
    """EPS Krylov-Schur method for BSE problems.
    
    - `SHAO`:         Lanczos recurrence for H square.
    - `GRUNING`:      Lanczos recurrence for H.
    - `PROJECTEDBSE`: Lanczos where the projected problem has BSE structure.
    
    """
    SHAO: int = _def(int, 'SHAO')  #: Constant ``SHAO`` of type :class:`int`
    GRUNING: int = _def(int, 'GRUNING')  #: Constant ``GRUNING`` of type :class:`int`
    PROJECTEDBSE: int = _def(int, 'PROJECTEDBSE')  #: Constant ``PROJECTEDBSE`` of type :class:`int`

class _p_mem:
    """"""

def _initialize(args=None):
    """



    :sources:`Source code at slepc4py/SLEPc/SLEPc.pyx:261 <slepc4py/SLEPc/SLEPc.pyx#L261>`

    """
    ...
def _finalize():
    """



    :sources:`Source code at slepc4py/SLEPc/SLEPc.pyx:265 <slepc4py/SLEPc/SLEPc.pyx#L265>`

    """
    ...


from .typing import *
