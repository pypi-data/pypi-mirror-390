# This file is part of atooms
# Copyright 2010-2024, Daniele Coslovich

"""
Trajectory callbacks and class decorators.

- "Callbacks" are simple functions that modify the `System` instance
  returned by `read_system()`. They can be registered to `trajectory`
  instance via `add_callback()`.

- "Class decorators" can be used for more complex modifications of
  trajectory behavior. They return dynamically subclassed trajectory
  instance.
"""

import copy
import numpy
from atooms.system import System, Molecule

__all__ = ['center', 'change_species', 'sort', 'filter_species',
           'set_density', 'set_temperature', 'fix_cm', 'fold',
           'create_molecular_system', 'Sliced', 'Unfolded']


# Callbacks

def center(system):
    """
    Shift the origin of reference frame at the center of the
    simulation cell. Particles positions will thus lie between -L/2
    and L/2, where L is the cell side along each direction.

    This function does not check if that is done multiple times.
    """
    system.cell.center[:] = 0
    for p in system.particle:
        p.position -= system.cell.side / 2.0
    return system

def change_species(system, layout):
    """
    Return a modified `system` with particle species changed according
    to `layout`.

    The possible values of `layout` are:

    - 'A': alphabetic, i.e. species are strings like 'A', 'B', ...
    - 'C': C-like, i.e. species are integers starting from 0
    - 'F': F-like, i.e. species are integers starting from 1

    If the current layout already matches the requested one, the
    system is returned unchanged.
    """
    if layout not in ['A', 'C', 'F']:
        raise ValueError('species layout must be A, C, or F (not %s)' % layout)

    # Detect species layout (A=alphabetic, C=C style, F=fortran style)
    try:
        species = [int(p.species) for p in system.particle]
    except ValueError:
        # The species cannot be converted to int, thus layout is
        # alphabetical
        current_layout = 'A'
    else:
        min_sp = numpy.min(species)
        if min_sp == 0:
            current_layout = 'C'
        elif min_sp == 1:
            current_layout = 'F'
        else:
            raise ValueError('Numeric species should start from 0 or 1')

    # Do nothing if the layout is already ok
    if layout == current_layout:
        return system

    # Convert to new layout
    import string
    if layout == 'A':
        # We get the index of the species map:
        # - if current layout is F (min_sp=1), we subtract one.
        # - if current layout is C (min_sp=0), we do nothing
        species_map = string.ascii_uppercase
        for p in system.particle:
            p.species = species_map[int(p.species) - min_sp]
    else:
        # Output layout is numerical (C or F)
        from atooms.system.particle import distinct_species
        offset = 1 if layout == 'F' else 0
        # Note that distinct_species is sorted alphabetically
        species_list = distinct_species(system.particle)
        if current_layout == 'A':
            for p in system.particle:
                p.species = str(species_list.index(p.species) + offset)
        else:
            # If layout=C, current_layout is F and we subtract 2*offset-1=-1
            # If layout=F, current_layout is C and we add 2*offset-1=+1
            for p in system.particle:
                p.species = str(int(p.species) + 2*offset - 1)
    return system

def sort(system):
    """Sort particles by species id."""
    system.particle = sorted(system.particle, key=lambda a: a.species)
    return system

def filter_species(system, species):
    """Return particles of a given `species` id."""
    system.particle = [p for p in system.particle if p.species == species]
    return system

def set_density(system, rho):
    """Set density of system to `rho` by rescaling the cell."""
    rho_old = system.density
    x = (rho_old / rho)**(1./3)
    system.cell.side *= x
    for p in system.particle:
        p.position *= x
    return system

def set_temperature(system, T):
    """Set system temperature to `T` by reassigning velocities."""
    from atooms.system.particle import cm_velocity
    for p in system.particle:
        p.maxwellian(T)
    v_cm = cm_velocity(system.particle)
    for p in system.particle:
        p.velocity -= v_cm
    return system

def fix_cm(s):
    """
    Return a system whose positions are relative to the original
    system's center of mass.
    """
    # Get current position of CM from unfolded positions
    cm = s.cm_position
    for p in s.particle:
        p.position -= cm
    return s

def fold(s):
    """Center and fold positions into central cell."""
    for p in s.particle:
        p.position -= s.cell.side / 2
        p.fold(s.cell)
    return s

def create_molecular_system(particle_system):
    """
    Convert a particle system to a molecular system.

    Args:
        particle_system (System): The particle system to convert.

    Returns:
        System: The molecular system.
    """
    molecules, molecule_species, ps = {}, {}, []
    for p in particle_system.particle:
        # Store molecule id if present. It uniquely identifies
        # a molecule of a System.
        if not hasattr(p, 'molecule_id'):
            ps.append(p)
            continue
        molecule_id = p.molecule_id
        if molecule_id not in molecules:
            molecules[molecule_id] = []
        molecules[molecule_id].append(p)
        # If we find a molecular species (ex. 'H2O') we use it,
        # else it will be inferred from the species of the particles
        if hasattr(p, 'molecule_species'):
            molecule_species[molecule_id] = p.molecule_species
        else:
            molecule_species[molecule_id] = None
    if len(molecules) == 0:
        raise AttributeError("No molecules found (missing 'molecule_id' attribute). Cannot create molecular trajectory.")

    ms = [Molecule(molecules[idx], species=molecule_species[idx], bond=(),
                   cell=particle_system.cell) for idx in molecules]
    return System(particle=ps, molecule=ms, cell=particle_system.cell)


# Class decorators

# Some of these decorators raise pylint errors because of the
# lack of visibility on parent methods() or attributes

# To properly implement decorators in python see
# http://stackoverflow.com/questions/3118929/implementing-the-decorator-pattern-in-python
# asnwer by Alec Thomas. if we don't subclass at runtime we won't be able to use the decorated
# mathod in other non-subclassed methods.

class Sliced:

    """Only return a slice of a trajectory."""

    # This is still necessary. slicing via __getitem__ has a large memory fingerprint
    # since we couldnt write it as a generator (maybe it is possible?)
    # TODO: adjust uslice to pick up blocks without truncating them

    def __new__(cls, component, uslice):
        import copy
        cls = type('Sliced', (Sliced, component.__class__), component.__dict__)
        return object.__new__(cls)

    def __init__(self, component, uslice):
        # pylint:disable=access-member-before-definition
        self._sliced_frames = range(len(self.steps))[uslice]
        self.steps = self.steps[uslice]
        # Reset cache (this fix was long due...)
        self._cache = None
        self._initialized_read = False
        # Ensure callbacks are not shared from this moment onwards
        import copy
        self.callbacks = copy.copy(component.callbacks)

    def read_system(self, frame):
        i = self._sliced_frames[frame]
        return super().read_system(i)


class Unfolded:

    """Decorate Trajectory to unfold particles positions on the fly."""

    def __new__(cls, component, fixed_cm=False):
        cls = type('Unfolded', (Unfolded, component.__class__), component.__dict__)
        return object.__new__(cls)

    def __init__(self, component, fixed_cm=False):
        self._component = component
        self._cache = None  # reset cache
        self._initialized_read = False
        # Ensure callbacks are not shared from this moment onwards
        import copy
        self.callbacks = copy.copy(component.callbacks)
        self.fixed_cm = fixed_cm

    def read_init(self):
        s = super().read_init()
        # Cache the initial sample and cell
        s = copy.deepcopy(self._component.read(0))
        self._old = numpy.array([p.position for p in s.particle])
        self._last_read = 0

    def read_system(self, frame):
        # Return here if first frame
        if frame == 0:
            # Deepcopy needed, see below
            s = copy.deepcopy(self._component.read(frame))
            if self.fixed_cm:
                s = fix_cm(s)
            return s

        # Compare requested frame with last read
        delta = frame - self._last_read
        if delta < 0:
            raise ValueError('cannot unfold jumping backwards (delta=%d)' % delta)
        if delta > 1:
            # Allow to skip some frames by reading them internally
            # We read delta-1 frames, then delta is 1
            for _ in range(delta-1):
                self.read_system(self._last_read+1)

        # With deepcopy we make sure that Unfolded() returns copies of
        # the system read by the component trajectory and does not
        # modify the underlying system, which is important in case the
        # latter is stored in memory (TrajectoryRam) and with caching
        s = copy.deepcopy(self._component.read(frame))
        self._last_read = frame

        # Unfold positions
        # Note that since L can be variable we get it at each step
        # TODO: I am not entirely sure this is correct with NPT.
        # The best thing in this case is to get unfolded positions
        # from the simulation.
        L = s.cell.side
        pos = numpy.array([p.position.copy() for p in s.particle])
        dif = pos - self._old
        dif = dif - numpy.rint(dif / L) * L
        self._old += dif

        # Copy unfolded positions back to the system
        # Here we cannot do
        #   s.particle[i].position = self._old[i][:]
        # because this a shallow view and the arrays share memory.
        # Fixing the CM later on will not work correctly.
        for i in range(len(pos)):
            s.particle[i].position = self._old[i].copy()

        if self.fixed_cm:
            s = fix_cm(s)

        return s


# Not necessary for the time being
# class _Molecular:
#     """
#     Create a molecular trajectory from a particle trajectory.
#     """

#     def __new__(cls, component):
#         cls = type('Molecular', (Molecular, component.__class__), component.__dict__)
#         return object.__new__(cls)

#     def __init__(self, particle_trajectory):
#         """
#         Initialize the Molecular trajectory with a particle trajectory.

#         Args:
#             particle_trajectory (TrajectoryBase): The particle trajectory to convert.
#         """
#         # pylint:disable=access-member-before-definition
#         self._particle_trajectory = particle_trajectory

#     def read_system(self, frame):
#         """
#         Read the system for a given frame and convert it to a molecular system.

#         Args:
#             frame (int): The frame index to read.

#         Returns:
#             System: The molecular system for the given frame.
#         """
#         particle_system = self._particle_trajectory.read_system(frame)
#         return create_molecular_system(particle_system)


def _Molecular(cls):

    class Molecular(cls):

        def read_system(self, frame):
            """
            Read the system for a given frame and convert it to a molecular system.

            Args:
                frame (int): The frame index to read.

            Returns:
                System: The molecular system for the given frame.
            """
            particle_system = super().read_system(frame)
            return create_molecular_system(particle_system)

        def write_system(self, system, step):
            """
            Write the system for a given frame, adding the molecule_id variable

            Args:
                system (System): the system instance to be written
                step (int): The step index being written.
            """
            if 'particle.molecule_id' not in self.variables:
                self.variables.append('particle.molecule_id')
            for i, molecule in enumerate(system.molecule):
                for p in molecule.particle:
                    p.molecule_id = i
            super().write_system(system, step)

    return Molecular
