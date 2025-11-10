"""Linked cells to compute neighbors."""

from collections import defaultdict
import numpy


class LinkedCells:

    def __init__(self, rcut, newton=False):
        self.rcut = rcut
        self.neighbors = []
        self.newton = newton
        self._is_adjusted = False

    def _adjust(self, box, periodic=None):
        self.box = box
        self.hbox = box / 2
        self.n_cell = (box / self.rcut).astype(int)
        self.box_cell = self.box / self.n_cell
        # if periodic is None:
        periodic = numpy.array([True] * len(box))
        self._map(self.newton, periodic)

    def _map(self, newton, periodic):
        def _pbc(t, N):
            """Apply PBCs to cell only along periodic directions"""
            for i in range(len(t)):
                if not periodic[i]:
                    continue
                if t[i] >= N[i]:
                    t[i] -= N[i]
                elif t[i] < 0:
                    t[i] += N[i]
            return t

        def _outside(t, N):
            """Check whether subcell is outside cell"""
            for i in range(len(t)):
                if t[i] >= N[i] or t[i] < 0:
                    return True
            return False

        def _map_3d_newton(n_cell):
            neigh_cell = {}
            for ix in range(n_cell[0]):
                for iy in range(n_cell[1]):
                    for iz in range(n_cell[2]):
                        # This is a map of neighbouring cells obeying III law
                        neigh_cell[(ix, iy, iz)] = \
                            [(ix+1, iy, iz), (ix+1, iy+1, iz), (ix, iy+1, iz),
                             (ix-1, iy+1, iz), (ix+1, iy, iz-1), (ix+1, iy+1, iz-1),
                             (ix, iy+1, iz-1), (ix-1, iy+1, iz-1), (ix+1, iy, iz+1),
                             (ix+1, iy+1, iz+1), (ix, iy+1, iz+1), (ix-1, iy+1, iz+1),
                             (ix, iy, iz+1)]
            return neigh_cell

        def _map_2d_newton(n_cell):
            neigh_cell = {}
            for ix in range(n_cell[0]):
                for iy in range(n_cell[1]):
                    # This is a map of neighbouring cells obeying III law
                    neigh_cell[(ix, iy)] = \
                        [(ix+1, iy), (ix+1, iy+1), (ix, iy+1), (ix-1, iy+1)]
            return neigh_cell

        def _map_3d_nonewton(n_cell):
            neigh_cell = {}
            for ix in range(n_cell[0]):
                for iy in range(n_cell[1]):
                    for iz in range(n_cell[2]):
                        neigh_cell[(ix, iy, iz)] = []
                        for deltax in [-1, 0, 1]:
                            for deltay in [-1, 0, 1]:
                                for deltaz in [-1, 0, 1]:
                                    if deltax == deltay == deltaz == 0:
                                        continue
                                    neigh_cell[(ix, iy, iz)].append((ix+deltax, iy+deltay, iz+deltaz))
            return neigh_cell

        def _map_2d_nonewton(n_cell):
            neigh_cell = {}
            for ix in range(n_cell[0]):
                for iy in range(n_cell[1]):
                    neigh_cell[(ix, iy)] = []
                    for deltax in [-1, 0, 1]:
                        for deltay in [-1, 0, 1]:
                            if deltax == deltay == 0:
                                continue
                            neigh_cell[(ix, iy)].append((ix+deltax, iy+deltay))
            return neigh_cell

        if len(self.n_cell) == 3:
            if newton:
                self._neigh_cell = _map_3d_newton(self.n_cell)
            else:
                self._neigh_cell = _map_3d_nonewton(self.n_cell)
        elif len(self.n_cell) == 2:
            if newton:
                self._neigh_cell = _map_2d_newton(self.n_cell)
            else:
                self._neigh_cell = _map_2d_nonewton(self.n_cell)
        else:
            raise ValueError('linked cells not supported for dimensions not in {2,3}')

        # Apply PBC
        for key in self._neigh_cell:
            for idx in range(len(self._neigh_cell[key])):
                folded = _pbc(list(self._neigh_cell[key][idx]), self.n_cell)
                self._neigh_cell[key][idx] = tuple(folded)

        # Remove subcells that are out of bounds
        # (this is only applied to non periodic directions)
        new_neigh_cell = {}
        for key in self._neigh_cell:
            new_neigh_cell[key] = []
            for subcell in self._neigh_cell[key]:
                if not _outside(subcell, self.n_cell):
                    new_neigh_cell[key].append(subcell)
        self._neigh_cell = new_neigh_cell

    def _index(self, pos):
        # TODO: add dimension to hbox
        x = ((pos.transpose() + self.hbox) / self.box_cell)
        return x.astype(numpy.int32)

    def compute(self, box, pos, ids, newton=True):
        if not self._is_adjusted:
            self._adjust(box, periodic=None)
            self._is_adjusted = True

        self.neighbors = []
        self.number_neighbors = []
        index = self._index(pos)
        particle_in_cell = defaultdict(list)
        for ipart, icell in enumerate(index):
            particle_in_cell[tuple(icell)].append(ipart)

        for ipart in range(pos.shape[1]):
            icell = tuple(index[ipart])
            # Initialize an empty list
            neighbors = []
            # Start with particles in the cell of particle ipart
            if self.newton:
                neighbors += [_ for _ in particle_in_cell[icell] if _ > ipart]
            else:
                neighbors += [_ for _ in particle_in_cell[icell] if _ != ipart]
            # Loop over neighbors cells and add neighbors
            for jcell in self._neigh_cell[icell]:
                neighbors += particle_in_cell[jcell]
            self.neighbors.append(neighbors)
            self.number_neighbors.append(len(neighbors))

        npart = len(self.neighbors)
        number_neighbors = numpy.array(self.number_neighbors)
        # neighbors_array = numpy.ndarray((npart, max(number_neighbors)), dtype=numpy.int32)
        neighbors_array = numpy.ndarray((max(number_neighbors), npart), dtype=numpy.int32)
        for ipart in range(len(self.neighbors)):
            neighbors_array[0:len(self.neighbors[ipart]), ipart] = self.neighbors[ipart]
        self.neighbors = neighbors_array
        self.number_neighbors = number_neighbors
