import numpy
import f2py_jit
from .helpers import _merge_source


class NeighborList:

    """Neighbor list class"""
    
    def __init__(self, rcut, neighbors='neighbor_list.f90',
                 helpers='helpers.f90', inline=True, full=False,
                 max_neighbors=-1, method='fixed_cutoff', debug=False):
        self.rcut = numpy.array(rcut)
        self.neighbors = None
        self.distances = None
        self.number_neighbors = None
        self.full = full
        self.max_neighbors = max_neighbors
        self.method = method
        self._module_path = None

        # Cut off check
        if method == "sann":
            self.rcut = numpy.max(self.rcut)

        # Gather f90 sources into a single one
        source = _merge_source(helpers, neighbors)

        # Inline subroutine
        if inline:
            from f2py_jit.finline import inline_source
            source = inline_source(source, ignore='compute')  # avoid reinlining forces!

        # Build the module with f2py and store module uid
        # (better not store the module itself, else we cannot deepcopy)

        extra_args = '--opt="-O3 -ffast-math"'
        if debug:
            extra_args = '--opt="-fbounds-check"'
        self._uid = f2py_jit.build_module(source, extra_args=extra_args)

        # TODO: add parallel and debug flags?
        # This was in atooms-models
        # args, opt_args = '', '-O3 -ffree-form -ffree-line-length-none'
        # if debug:
        #     opt_args += ' -pg -fbounds-check'
        # if parallel:
        #     opt_args += ' -fopenmp'
        #     args += ' -lgomp'
        # extra_args = '--opt="{}" {}'.format(opt_args, args)

    def _setup(self, npart, nneigh):
        """Allocate or reallocate arrays for neighbor list"""
        if self.neighbors is None or self.neighbors.shape[1] != npart or self.neighbors.shape[0] < nneigh:
            self.neighbors = numpy.ndarray(shape=(nneigh, npart), order='F', dtype=numpy.int32)
            self.distances = numpy.ndarray(shape=(nneigh, npart), order='F', dtype=float)
        if self.number_neighbors is None or len(self.number_neighbors) != npart:
            self.number_neighbors = numpy.ndarray(npart, order='F', dtype=numpy.int32)

    def neighbors_as_list(self):
        return [self.neighbors[:self.number_neighbors[i], i] for i in range(len(self.number_neighbors))]

    def distances_as_list(self):
        return [self.distances[:self.number_neighbors[i], i] for i in range(len(self.number_neighbors))]

    def sort_by_distance(self):
        for i, nn in enumerate(self.number_neighbors):
            self.distances[:nn, i], self.neighbors[:nn, i] = zip(*sorted(zip(self.distances[:nn, i], self.neighbors[:nn, i])))

    def compute(self, box, pos, ids):
        # Setup
        f90 = f2py_jit.import_module(self._uid)

        # Setup arrays
        # Estimate max number of neighbors based on average density
        # We take the largest cut off distance
        npart = pos.shape[1]
        rho = npart / box.prod()
        if self.max_neighbors > 0:
            nneigh = self.max_neighbors
        else:
            nneigh = int(4.0 / 3.0 * 3.1415 * rho * numpy.max(self.rcut)**3 * 1.50)
        self._setup(npart, nneigh)

        # Compute neighbors list
        #
        # If the f90 code returns an error, the arrays are reallocated
        # based on the largest number of neighbors returned by the f90
        # routine
        func = None
        if self.method == 'fixed_cutoff' and self.full:
            func = f90.neighbor_list.compute_full
        if self.method == 'fixed_cutoff' and not self.full:
            func = f90.neighbor_list.compute
        if self.method == 'sann':
            func = f90.neighbor_list.compute_sann
        assert func, f'cannot choose method {self.method}'
        error = func(box, pos, ids, self.rcut, self.neighbors, self.number_neighbors, self.distances)
        if error:
            self._setup(npart, max(self.number_neighbors))
            error = func(box, pos, ids, self.rcut, self.neighbors, self.number_neighbors, self.distances)
            assert not error, "something wrong with neighbor_list"
