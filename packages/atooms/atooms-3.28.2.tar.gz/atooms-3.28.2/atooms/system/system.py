# This file is part of atooms
# Copyright 2010-2024, Daniele Coslovich

"""
The physical system at hand.

The system of interest in a classical atomistic simulations is
composed of interacting point particles, usually enclosed in a
simulation cell. The system may be in contact with a thermostat, a
barostat or a particle reservoir.
"""

import copy
import random
import numpy

from .topology import Topology

def _canonicalize(what):
    """
    Given a descriptor string of a System property, return it
    in canonical form. This is used to canonicalize viewed / dumped
    attributes.
    """
    # Accepts some aliases
    aliases = {
        'box': 'cell.side',
        'pos': 'particle.position',
        'pos_unf': 'particle.position_unfolded',
        'pos-unf': 'particle.position_unfolded',
        'vel': 'particle.velocity',
        'spe': 'particle.species',
        'ids': 'particle.species',
        'rad': 'particle.radius'}
    if what in aliases:
        what = aliases[what]

    # If there is no dot, we assume it is a particle property
    if '.' not in what:
        what = 'particle.' + what

    return what

class System:

    """System class."""

    def __init__(self, particle=None, cell=None, interaction=None,
                 thermostat=None, barostat=None, reservoir=None,
                 wall=None, molecule=None, N=0, d=3):
        """
        Create a ``System`` with requested objects.

        If provided, `particle` must be a list of `Particle`s and `molecule`
        must be a list of `Molecule`s.

        If `N` is provided and is an `int`, the system is filled with
        `N` particles starting from a crystalline template in a
        unit-length sided `Cell` in `d` dimensions.

        If `N` is a `dict` specifying a target composition, ex. `{'A':
        N_A, 'B': N_B, ...}`, the system is filled as above but
        setting the species as requested. The assignement is random.
        """
        if particle is None:
            particle = []
        self.particle = particle
        """A list of `Particle` instances."""
        self.interaction = interaction
        self.cell = cell
        self.thermostat = thermostat
        self.barostat = barostat
        self.reservoir = reservoir
        self.wall = wall
        self.molecule = molecule if molecule is not None else []

        # Fill particle list with molecules, if not present.
        # TODO: add switch to avoid or optimize if inefficient
        for m in self.molecule:
            for p in m.particle:
                if p not in self.particle:
                    self.particle.append(p)
        self.topology = Topology(self.molecule, self.particle)

        # Initialize system
        if N != 0:
            from .particle import _lattice
            from .cell import Cell
            assert len(particle) == 0
            if isinstance(N, int):
                N = {'A': N}
            npart = sum(N.values())
            self.particle = _lattice(npart, d)
            self.cell = Cell(numpy.ones(d))
            self.set_composition(N)

        # Internal cache for array dumps
        self._data = None
        self._cache = None

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        # Note: when making a shallow copy the _data cache
        # may need to be cleared. We might set self._data to None here.
        return result

    def update(self, other, full=False, exclude=None, only=None):
        """
        Update current system attributes in-place using the `other` System
        as source.

        The default behavior is to make deep copies only of all the
        `other` system attributes that are not None, i.e. which are
        set.

        To overwrite all attributes, even those set in `self` but not
        in `other`, use `full=True`.

        The lists `exclude` and `only` can be used to avoid updating
        some system attributes or to update only some system
        attributes, respectively.

        This method can be used by subclasses to deal with performace
        or memory dellocation issues.
        """
        for key in other.__dict__:
            if exclude is not None or only is not None:
                if (exclude is not None and key not in exclude) or \
                   (only is not None and key in only):
                    self.__dict__[key] = copy.deepcopy(other.__dict__[key])
            else:
                if full or other.__dict__[key] is not None:
                    self.__dict__[key] = copy.deepcopy(other.__dict__[key])

        # Internal data dictionary for array dumps
        self._data = None

    @property
    def number_of_dimensions(self):
        """
        Number of spatial dimensions, guessed from the length of
        `particle[0].position`.
        """
        if len(self.particle) > 0:
            return len(self.particle[0].position)
        elif self.cell is not None:
            return len(self.cell.side)
        else:
            return 0

    @property
    def distinct_species(self):
        """Sorted list of distinct chemical species in the system."""
        # TODO: use views to optimize
        from atooms.system.particle import distinct_species as _distinct_species
        return _distinct_species(self.particle)

    @property
    def density(self):
        """
        Density of the system.

        It `cell` is None, an estimate is given.
        """
        if len(self.particle) == 0:
            return 0.0

        if self.cell is None:
            # Estimate density assuming V is the product of the
            # largest distances along each dimension
            volume = 1.0
            for axis in range(len(self.particle[0].position)):
                x_0 = min([p.position[axis] for p in self.particle])
                x_1 = max([p.position[axis] for p in self.particle])
                volume *= (x_1 - x_0)
            return len(self.particle) / volume
        else:
            return len(self.particle) / self.cell.volume

    @density.setter
    def density(self, rho):
        self.set_density(rho)

    def set_density(self, rho):
        """Set the system density to `rho` by rescaling the coordinates."""
        if self.cell is None:
            raise ValueError('cannot compute density without a cell')
        factor = (self.density / rho)**(1./len(self.cell.side))
        for particle in self.particle:
            particle.position *= factor
        self.cell.side *= factor

    @property
    def packing_fraction(self):
        from math import pi
        return pi / 6 * sum([(2 * p.radius)**3 for p in self.particle]) / self.cell.volume

    @property
    def temperature(self):
        """
        Kinetic temperature.
        """
        # TODO: determine translational invariance via some additional attribute.
        if len(self.particle) > 1:
            # Number of degrees of freddom is (N-1)*ndim
            ndof = (len(self.particle)-1) * self.number_of_dimensions
            return 2.0 / ndof * self.kinetic_energy()
        elif len(self.particle) == 1:
            # Pathological case
            return 2.0 / self.number_of_dimensions * self.kinetic_energy()
        else:
            # Empty particle list
            return 0.0

    @temperature.setter
    def temperature(self, T):
        self.set_temperature(T)

    def set_temperature(self, temperature):
        """Reset velocities to a Maxwellian distribution with fixed CM."""
        from .particle import fix_total_momentum
        T = temperature
        for p in self.particle:
            p.maxwellian(T)
        fix_total_momentum(self.particle)
        # After fixing the CM the temperature is not exactly the targeted one
        # Therefore we scale the velocities so as to get to the right T
        T_old = self.temperature
        if T_old > 0.0:
            fac = (T/T_old)**0.5
            for p in self.particle:
                p.velocity *= fac

    @property
    def composition(self):
        """Chemical composition"""
        from .particle import composition
        return dict(composition(self.particle))

    @composition.setter
    def composition(self, value):
        self.set_composition(value)

    def set_composition(self, N):
        """Set the chemical composition as specified in the `N` dictionary."""
        assert sum(N.values()) == len(self.particle), 'composition {} does not match N = {}'.format(N, len(self.particle))
        # Create array of species
        species = []
        for sp in N:
            species += [sp] * N[sp]
        # Randomize the species and assign them
        random.shuffle(species)
        for sp, p in zip(species, self.particle):
            p.species = sp

    @property
    def concentration(self):
        """Chemical concentration"""
        return {k: float(v) / len(self.particle) for k, v in self.composition.items()}

    @concentration.setter
    def concentration(self, value):
        self.set_concentration(value)

    def set_concentration(self, x):
        """Set the chemical concentration as specified in the `x` dictionary."""
        assert abs(sum(x.values()) - 1) < 1e-10, f'concentrations {x} do not sum to 1'
        N = {}
        last = None
        for species in x:
            N[species] = round(len(self.particle)*x[species])
            last = species
        if sum(N.values()) != len(self.particle):
            N[last] = sum(N[_] for _ in N if _ != last)
        self.set_composition(N)

    def scale_velocities(self, factor):
        """Scale particles' velocities by `factor`."""
        for p in self.particle:
            p.velocity *= factor

    def kinetic_energy(self, per_particle=False, normed=False):
        """
        Return the total kinetic energy of the system.

        If `per_particle` or `normed` is `True`, return the kinetic
        energy per particle.
        """
        ekin = sum([p.kinetic_energy for p in self.particle])
        if per_particle or normed:
            return ekin / len(self.particle)
        return ekin

    def compute_interaction(self, what=None):
        """
        Compute interaction in the system
        """
        if self.interaction is not None:
            kwargs = {}
            # TODO: ops, doing like this there is an issue when different terms use
            # the same name for different variables!
            for variable, variable_to_dump in self.interaction.variables.items():
                # Get the optional data type
                dtype = None
                if ':' in variable_to_dump:
                    variable_to_dump, dtype = variable_to_dump.split(':')
                kwargs[variable] = self.dump(variable_to_dump,
                                             view=True, dtype=dtype,
                                             order=self.interaction.order)
            self.interaction.compute(what, **kwargs)

    def potential_energy(self, per_particle=False, normed=False, cache=False):
        """
        Return the total potential energy of the system.

        If `per_particle` or `normed` is `True`, return the potential
        energy per particle.
        """
        if self.interaction is not None:
            if not cache or self.interaction.energy is None:
                # TODO: we should compute 'energy' instead
                self.compute_interaction('forces')
            if per_particle or normed:
                return self.interaction.energy / len(self.particle)
            return self.interaction.energy
        return 0.0

    def total_energy(self, per_particle=False, normed=None, cache=False):
        """
        Return the total energy of the system.

        If `per_particle` or `normed` is `True`, return the total
        energy per particle.
        """
        if normed is not None:
            per_particle = normed
        return self.potential_energy(per_particle, cache=cache) + self.kinetic_energy(per_particle)

    def force_norm(self, per_particle=True, cache=False):
        """
        Return the norm of the force vector.

        If `per_particle` is `True`, return the force norm per particle.
        """
        if self.interaction is not None:
            if not cache or self.interaction.forces is None:
                self.compute_interaction('forces')
            if per_particle:
                return numpy.sum(self.interaction.forces**2)**0.5 / len(self.particle)
            return numpy.sum(self.interaction.forces**2)**0.5
        return 0.0

    def force_norm_square(self, per_particle=True, cache=False):
        """
        Return the squared norm of the force vector.

        If `per_particle` is `True`, return the force squared norm per particle.
        """
        if self.interaction is not None:
            if not cache or self.interaction.forces is None:
                self.compute_interaction('forces')
            if per_particle:
                return numpy.sum(self.interaction.forces**2) / len(self.particle)
            return numpy.sum(self.interaction.forces**2)
        return 0.0

    def virial(self, per_particle=True, cache=False):
        """
        Return the virial of the system.

        If `per_unit_volume` is `True`, return the virial per particle.
        """
        if self.interaction is not None:
            if not cache or self.interaction.virial is None:
                self.compute_interaction('forces')
            if per_particle:
                return self.interaction.virial / len(self.particle)
            return self.interaction.virial
        return 0.0

    @property
    def pressure(self):
        """
        Return the pressure of the system.

        It assumes that `self.interaction` has already been computed.
        """
        if self.thermostat:
            T = self.thermostat.temperature
        else:
            T = self.temperature
        return (len(self.particle) * T + self.interaction.virial / self.number_of_dimensions) / self.cell.volume

    def cm(self, what):
        """General center-of-mass attribute."""
        # It could be implemented in a more general and faster way via dumps
        # but one should pay attention to array ordering and views
        x = numpy.zeros_like(getattr(self.particle[0], what))
        mtot = 0.0
        for p in self.particle:
            x += getattr(p, what) * p.mass
            mtot += p.mass
        return x / mtot

    def center_of_mass(self, what):
        """General center-of-mass attribute."""
        x = self.view(what)
        mass = self.view('mass')
        if x.shape[0] == self.number_of_dimensions:
            x_cm = numpy.dot(x, mass)
        else:
            x_cm = numpy.dot(x.transpose(), mass)
        return x_cm / numpy.sum(mass)

    @property
    def cm_velocity(self):
        """Center-of-mass velocity."""
        return self.cm('velocity')

    @property
    def cm_position(self):
        """Center-of-mass position."""
        return self.cm('position')

    def fix_momentum(self):
        """Subtract out the the center-of-mass motion."""
        vel = self.view('velocity')
        vcm = self.center_of_mass('velocity')
        if vel.shape[0] == self.number_of_dimensions:
            vel[:, :] -= vcm[:, numpy.newaxis]
        else:
            vel[:, :] -= vcm[:, numpy.newaxis].transpose()

    def fix_center_of_mass(self, what='vel'):
        """
        Subtract out the the center-of-mass motion.

        This works with velocity by default, but can be used with any
        attribute, like positions, too.
        """
        var = self.view(what)
        var_cm = self.center_of_mass(what)
        if var.shape[0] == self.number_of_dimensions:
            var[:, :] -= var_cm[:, numpy.newaxis]
        else:
            var[:, :] -= var_cm[:, numpy.newaxis].transpose()

    def fold(self):
        """Fold positions into central cell."""
        for p in self.particle:
            p.fold(self.cell)

    def replicate(self, times, axis):
        """Replicate the system several `times` along `axis`"""
        n = times
        assert n > 1
        npart = len(self.particle)
        L = self.cell.side[axis]
        for p in self.particle:
            p.position[axis] += L/2
        for i in range(1, n):
            for j in range(npart):
                p = copy.deepcopy(self.particle[j])
                p.position[axis] = self.particle[j].position[axis] + i*L
                self.particle.append(p)
        self.cell.side[axis] *= n
        for p in self.particle:
            p.position[axis] -= L * n / 2

    def slab(self, width=1.0, n=0, axis=-1):
        """
        Return slabs orthogonal to `axis` as `System` instances. The slabs'
        thickness is either `width` or such that there are `n` slabs, if
        `n` > 0. The returned systems contain references to the objects of `self`.

        :param width: slab thickness
        :param axis: axis orthogonal to the slab
        :return: a list of `System` instances
        """
        if n > 0:
            width = self.cell.side[axis] / n
        else:
            n = 1 + int(self.cell.side[axis] / width)
        pos = self.dump('pos')[:, axis]
        idx = (pos[:] + self.cell.side[axis] / 2) / width
        idx = idx.astype('int')
        slabs = [[] for _ in range(n)]
        for i, p in zip(idx, self.particle):
            slabs[i].append(p)
        return [System(particle=slab, cell=self.cell) for slab in slabs]

    # Attempt to have a self-contained view method
    # TODO: with attributes that are read only, we should skip the cache
    def __view(self, what, order='C', dtype=None):  # pragma: no cover
        """
        Return a view of system properties specified by `what` as numpy array.

        `what` must be a string of the form `particle.<attribute>` or
        `cell.<attribute>`. Some aliases are allowed like:

        - `pos` (`particle.position`)
        - `vel` (`particle.velocity`)
        - `spe` (`particle.species`)

        If `what` is a System attribute, it is returned.

        The requested particle property is set as
        a view on the corresponding portion of an internal array. This
        allows one to modify the array efficiently and keep the
        particle properties in sync. Numpy arrays must be modified
        in-place to keep everything in sync.

        Particles' coordinates are returned as (N, ndim) arrays if
        `order` is `C` or (ndim, N) arrays if `order` is `F`.

        Examples
        --------

        These numpy arrays are element-wise identical

        .. code-block:: python

           pos = system.dump('particle.position')
           pos = system.dump('position')
           pos = system.dump('pos')

        Collect several properties in a dict

        .. code-block:: python
           data = {what: system.view(what) for what in ['position', 'velocity']}
        """
        # Note: the current design is that view() calls dump() internally
        # and setting the properties in a cache. There is some code
        # duplication, but this way accessing a copy of the data does not
        # interferes with the views. Another approach is that dump() is just view().copy().
        # This will save quite some lines of codes, but one should be careful with order.
        # If the order is different, than we should not change the
        # view but just transpose the copy.

        # It would be better that dump could operate also without an underlying view...
        # For instance, changing a Particle object would break also dump()...
        # But having a cache would be more efficient.

        # TODO: default order should be None. If the cache is not set up, it will be C by default, otherwise we should respect the view.

        assert order in ['C', 'F']
        what = _canonicalize(what)

        # If the attribute to dump is a plain System attribute, return it
        if what in self.__dict__:
            return getattr(self, what)

        # Extract the requested attribute
        assert what.count('.') == 1, f'cannot access nested attribute {what}'
        component, attribute = what.split('.')

        # Setup data cache dictionary for more complex attributes
        if self._cache is None:
            self._cache = {}
            self._cache['data'] = {}
            self._cache['order'] = {}
            self._cache['npart'] = {}

        # Make array of attributes
        assert component in ['particle', 'cell', 'molecule']
        if component == 'particle':
            # We retrieve the view from cache if the array is in the cache
            # and shape and type have not changed.
            # Note: if particles are reassigned without changing N the cache will
            # not be updated. It can be fixed by keeping a list of ids
            # although testing it would bring a overhead.
            if what not in self._cache['data'] or \
                    self._cache['data'][what].dtype != dtype or \
                    self._cache['npart'][what] != len(self.particle) or \
                    self._cache['order'][what] != order:
                # Get the requested data as an array and cache it
                # 1) Using dump internally -> code duplication elsewhere
                # data = self._dump(what, order=order, dtype=dtype)
                # 2) Explicitly here, then dump just make a copy of views
                data = numpy.array([getattr(p, attribute) for p in self.particle], dtype=dtype)
                # We transpose the array if F order is requested
                if order == 'F':
                    data = numpy.transpose(data)
                    data = numpy.asfortranarray(data)

                # TODO: swap order of keys (data <-> what)
                # Set the particle property as a view on the cached array.
                # Note: to check if particle properties and cached array are associated:
                # numpy.may_share_memory(p[0].position, pos[:, 0])
                if order == 'F':
                    for i, p in enumerate(self.particle):
                        setattr(p, attribute, data[..., i])
                if order == 'C':
                    for i, p in enumerate(self.particle):
                        setattr(p, attribute, data[i, ...])

                # Store data in cache
                self._cache['data'][what] = data
                self._cache['order'][what] = order
                self._cache['npart'][what] = len(self.particle)

        if component == 'molecule':
            # TODO: fix this if we ever use this method
            raise ValueError('cannot view molecule attributes, they are read only')
            if what not in self._cache['data']:
                data = numpy.array([getattr(m, attribute) for m in self.molecule])
                self._cache['data'][what] = data

        if component == 'cell':
            if what not in self._cache['data'] or \
               self._cache['data'][what].dtype != dtype:
                # Get the requested data as an array and cache it
                # 1) dump
                # data = self._dump(what, order=order, dtype=dtype)
                # 2) explicitly
                data = numpy.array(getattr(self.cell, attribute), dtype=dtype)
                # Set the particle property as a view on the cached array.
                setattr(self.cell, attribute, data)

                # Store data in cache
                self._cache['data'][what] = data

        return self._cache['data'][what]

    # Attempt to have dump rely on view entirely.
    def __dump(self, what, order='C', dtype=None):
        # TODO: do not modify order/dtype of the view, just cast it if it is different
        # This way the view stays safe and we dump the data efficiently
        return self._view(what, order, dtype).copy()

    # Attempt to have a self-contained dump()
    # def __dump(self, what, order='C', dtype=None):

    #     assert order in ['C', 'F']
    #     what = _canonicalize(what)

    #     # If the attribute to dump is a plain System attribute, return it
    #     if what in self.__dict__:
    #         return copy.deepcopy(getattr(self, what))

    #     # Extract the requested attribute
    #     assert what.count('.') == 1, f'cannot access nested attribute {what}'
    #     component, attribute = what.split('.')

    #     # Make array of attributes
    #     assert component in ['particle', 'cell']
    #     if component == 'particle':
    #         data = numpy.array([getattr(p, attribute) for p in self.particle], dtype=dtype)
    #         # We transpose the array if F order is requested
    #         if order == 'F':
    #             data = numpy.transpose(data)
    #             data = numpy.asfortranarray(data)

    #     if component == 'cell':
    #         data = numpy.array(getattr(self.cell, attribute), dtype=dtype)

    #     return copy.deepcopy(data)

    def dump(self, what=None, order='C', dtype=None, view=False, clear=False, flat=False):
        """
        Return a numpy array with system properties specified by `what`.

        `what` must be a string of the form `particle.<attribute>` or
        `cell.<attribute>`. Some aliases are allowed like:

        - `pos` (`particle.position`)
        - `vel` (`particle.velocity`)
        - `spe` (`particle.species`)

        If `what` is a System attribute, it is returned.

        If `view` is `True`, the requested particle property is set as
        a view on the corresponding portion of the dump array. This
        allows one to modify the dump array efficiently and keep the
        particle properties in sync. Numpy arrays must be modified
        in-place to keep everything in sync. An `AssertionError` is raised
        if a property cannot be viewed, e.g. because it is read-only.

        If `clear` is True, a new view is created on the requested
        particle property.

        If `flat` is True, the resulting array is flatted following
        `order` using numpy.flatten().

        Particles' coordinates are returned as (N, ndim) arrays if
        `order` is `C` or (ndim, N) arrays if `order` is `F`.

        Examples
        --------

        These numpy arrays are element-wise identical

        .. code-block:: python

           pos = system.dump('particle.position')
           pos = system.dump('position')
           pos = system.dump('pos')
        """
        if isinstance(what, list):
            raise ValueError('list arguments to dump() are not supported, use dict comprehension instead')

        # If the attribute to dump is a plain System attribute, return it
        if what in self.__dict__:
            if view:
                return getattr(self, what)
            else:
                return copy.deepcopy(getattr(self, what))

        # Setup data cache dictionary for more complex attributes
        if self._data is None or clear:
            self._data = {}

        # Return immediately if we only want to clear the dump
        if clear and what is None:
            return

        # Accepts some aliases
        aliases = {
            'box': 'cell.side',
            'pos': 'particle.position',
            'vel': 'particle.velocity',
            'spe': 'particle.species',
            'rad': 'particle.radius'}
        if what in aliases:
            what = aliases[what]

        # We accept unbounded particle attributes (without 'particle' prefix)
        if not what.startswith('particle') and not what.startswith('cell') and \
           not what.startswith('molecule') and not what.startswith('topology'):
            what = 'particle.' + what
        # Extract the requested attribute
        attr = what.split('.')[-1]

        # Make array of attributes
        if what.startswith('particle'):
            if what in self._data and len(self.particle) == self._data['npart']:
                # TODO: handle change of dtype
                # Get the data in cache if it is present
                # and the number of particles has not changed.
                # Note: if particles are reassigned the cache will
                # not be updated. It can be fixed by keeping a list of ids
                # although testing it would bring a overhead.
                data = self._data[what]
                # If order changes, we transpose the array. This may
                # happen if a trajectory has stored the system in ram
                # with a fortran order and postprocessing asks for a C
                # order array.  This will fail if there are n
                # particles in n dimensions but it is still better
                # than nothing. We must refactor this.
                if len(data.shape) == 2:
                    current_order = 'F' if data.shape[0] == self.number_of_dimensions else 'C'
                    if order != current_order:
                        self._data[what] = data.transpose()
                        data = self._data[what]
                # If we are asking a flat copy we must not flatten the cached array
                if not view and flat:
                    data = copy.deepcopy(data).flatten(order=order)
            else:
                # We create a new array
                data = numpy.array([getattr(p, attr) for p in self.particle], dtype=dtype)
                # We transpose the array if F order is requested
                if order == 'F':
                    data = numpy.transpose(data)
                    data = numpy.asfortranarray(data)
                # If view is True, we set the particle property as a
                # view on the dump array. Pay attention of C / F order.
                # To check if particle properties and dump are associated:
                # numpy.may_share_memory(p[0].position, pos[:, 0])
                if view:
                    if not flat:
                        if order == 'C':
                            for i, p in enumerate(self.particle):
                                setattr(p, attr, data[i, ...])
                        if order == 'F':
                            for i, p in enumerate(self.particle):
                                setattr(p, attr, data[..., i])
                    else:
                        data = data.flatten(order=order)
                        shape = getattr(self.particle[0], attr).shape
                        if len(shape) == 2:
                            ndim = self.number_of_dimensions
                            for i, p in enumerate(self.particle):
                                setattr(p, attr, data[i*ndim: (i + 1)*ndim])
                else:
                    # We flatten the array if requested
                    if flat:
                        data = data.flatten(order=order)

        elif what.startswith('molecule'):
            # TODO: check which properties are read only
            # assert not view, 'cannot view molecule attributes, they are read only'
            if what in self._data:
                data = self._data[what]
            else:
                data = numpy.array([getattr(m, attr) for m in self.molecule])
                # TODO: same as particle, refactor?
                if view:
                    if order == 'C':
                        for i, p in enumerate(self.molecule):
                            setattr(p, attr, data[i, ...])
                    if order == 'F':
                        for i, p in enumerate(self.molecule):
                            setattr(p, attr, data[..., i])
                    # We must update the topology after setting the views
                    self.topology = Topology(self.molecule, self.particle)

        elif what.startswith('topology'):
            # assert not view, 'cannot view topology attributes, they are read only'
            if what in self._data:
                data = self._data[what]
            else:
                data = numpy.array(getattr(self.topology, attr), dtype=dtype)
                # TODO: should we do this or not?
                # if view:
                #     setattr(self.topology, attr, data)

        elif what.startswith('cell'):
            if what in self._data:
                data = self._data[what]
            else:
                data = numpy.array(getattr(self.cell, attr), dtype=dtype)
                if view:
                    setattr(self.cell, attr, data)
        else:
            raise ValueError('Unknown attribute %s' % what)

        if view:
            # Store data in local dict and keep track of the number of particles
            self._data[what] = data
            self._data['npart'] = len(self.particle)
        else:
            data = copy.deepcopy(data)
        return data

    def get(self, what=None, order='C', dtype=None, view=False, clear=False, flat=False):
        """
        Alias of `System.dump()`
        """
        return self.dump(what=what, order=order, dtype=dtype, clear=clear, flat=flat, view=view)

    def view(self, what=None, order='C', dtype=None, clear=False, flat=False):
        """
        Return a view on a system property

        This is an alias of `System.dump(view=True, *args, **kwargs)`
        """
        # TODO: possibly rewrite dump() as view().copy()
        # TODO: if what is None set default internal values of order, flat, dtype (as a dict)
        return self.dump(what=what, order=order, dtype=dtype, clear=clear, flat=flat, view=True)

    def __getitem__(self, key):
        return self.view(key)

    def __setitem__(self, key, value):
        self.view(key)[:] = value

    def __str__(self):
        from .particle import composition
        txt = ''
        if self.particle:
            txt += 'system composed of N={0} particles\n'.format(len(self.particle))
            txt += 'with chemical composition C={}\n'.format(self.composition)
            txt += 'with chemical concentration x={}\n'.format(self.concentration)
        if self.cell:
            txt += 'enclosed in a {0.shape} box at number density rho={1:.6f}\n'.format(self.cell, self.density)
        if self.wall:
            txt += 'surrounded by {} walls\n'.format(len(self.wall))
        if self.thermostat:
            txt += 'in contact with a thermostat at T={0.temperature}\n'.format(self.thermostat)
        if self.barostat:
            txt += 'in contact with a barostat at P={0.pressure}\n'.format(self.barostat)
        if self.reservoir:
            txt += 'in contact with a reservoir at mu={0.chemical_potential}\n'.format(self.reservoir)
        if self.interaction:
            txt += '\n'
            txt += str(self.interaction)
        return txt

    def show(self, backend='matplotlib', **kwargs):
        from .visualize import show_ovito
        from .visualize import show_matplotlib
        from .visualize import show_3dmol

        if backend == 'matplotlib':
            _show = show_matplotlib
        elif backend == 'ovito':
            _show = show_ovito
        elif backend == '3dmol':
            _show = show_3dmol
        else:
            raise ValueError(f'unknown {backend} backend for visualization')
        try:
            return _show(self.particle, self.cell, **kwargs)
        except ModuleNotFoundError:
            import warnings
            warnings.warn(f'missing visualization backend {backend}')

    @property
    def species_layout(self):
        """
        Return species layout (A=alphabetical, C=C indexed, F=fortran indexed)
        """
        try:
            species = [int(p.species) for p in self.particle]
        except ValueError:
            # The species cannot be converted to int, thus layout is
            # alphabetical
            # TODO: add periodic table layout 'P'?
            layout = 'A'
        else:
            min_sp = numpy.min(species)
            if min_sp == 0:
                layout = 'C'
            elif min_sp == 1:
                layout = 'F'
            else:
                raise ValueError('Numeric species should start from 0 or 1')
        return layout

    @species_layout.setter
    def species_layout(self, layout):
        """
        Set species layout
        """
        # Sanity checks
        layouts = ['A', 'C', 'F']
        assert layout[0] in layouts, 'layout must be A, C or F (not {})'.format(layout)

        # Do nothing if the layout is already ok
        current_layout = self.species_layout
        if layout == current_layout:
            return

        # Convert to new layout
        import string
        if layout[0] == 'A':
            # We get the index of the species map:
            # - if current layout is F (min_sp=1), we subtract one.
            # - if current layout is C (min_sp=0), we do nothing
            species = [int(p.species) for p in self.particle]
            min_sp = numpy.min(species)
            species_map = string.ascii_uppercase
            for p in self.particle:
                p.species = species_map[int(p.species) - min_sp]
        else:
            # Output layout is numerical (C or F)
            offset = 1 if layout[0] == 'F' else 0
            # Note that distinct_species is sorted alphabetically
            species_list = self.distinct_species
            if current_layout[0] == 'A':
                for p in self.particle:
                    p.species = str(species_list.index(p.species) + offset)
            else:
                # If layout=C, current_layout is F and we subtract 2*offset-1=-1
                # If layout=F, current_layout is C and we add 2*offset-1=+1
                for p in self.particle:
                    p.species = str(int(p.species) + 2*offset - 1)
