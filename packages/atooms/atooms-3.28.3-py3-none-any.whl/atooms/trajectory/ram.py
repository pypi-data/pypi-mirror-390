"""Store trajectory in memory (it can be huge)."""

import copy
from atooms.system import System, Particle, Cell
from .base import TrajectoryBase


class TrajectoryRam(TrajectoryBase):

    """
    Store trajectory in RAM

    The read_system method of this class conforms with the normal
    Trajectory behavior, i.e. a copy of the system is returned when
    requesting the same frame multiple times.
    """

    def __init__(self, data=None, filename=None, mode='w'):
        super().__init__(filename, mode)
        self._system = []
        self._overwrite = True
        if data:
            self._from_data(data)

    def _from_data(self, data):
        """
        Create a system from a dictionary `data`

        The keys of `data` must be valid `what` entries for
        `System.view()`.
        """
        # TODO: accept more general System attributes beyond particle and cell
        # We need the number of particles, we look for it in
        # `particle.position`, which must be present
        from atooms.core.utils import canonicalize
        N = None
        for key in data:
            if canonicalize([key], self.thesaurus)[0] == 'particle.position':
                pos = data[key][0]
                N = pos.shape[0]
                break
        assert N, f'could not guess particle number from {data.keys()}'

        # All items of the dict must have the same len (i.e. the number of frames)
        frames = list({len(data[key]) for key in data})
        assert len(frames) == 1
        frames = int(frames[0])
        for frame in range(frames):
            s = System()
            s.particle = [Particle() for _ in range(N)]
            s.cell = Cell()
            for what in data:
                s.view(what)[...] = data[what][frame]
            self.append(s)

    def write_system(self, system, step):
        if step in self.steps:
            ind = self.steps.index(step)
            self._system[ind].update(system)
        else:
            self._system.append(copy.deepcopy(system))
            # Ensure the system cache is cleared
            # TODO: relax this once order changes are handled in System.dump()
            self._system[-1].dump(clear=True)

    def read_system(self, frame):
        return copy.deepcopy(self._system[frame])

    def __setitem__(self, i, value):
        try:
            step = self.steps[i]
        except IndexError:
            if len(self.steps) > 0:
                step = self.steps[-1]+1
            else:
                step = 0
        self.write(value, step)


class TrajectoryRamView(TrajectoryRam):

    """
    This class deviates from the normal Trajectory behavior in that it
    returns views on the System when calling read_system(), and not
    copies. Thus modifications to the read system object will be
    propagated to the trajectory.
    """

    def read_system(self, frame):
        return self._system[frame]


class TrajectoryRamLight(TrajectoryRam):

    """
    Light-weight version
    """

    def write_system(self, system, step):
        """
        Store copies of the views of the attributes of the System
        components
        """
        # We treat differently particles from the rest
        # Store all instance variables
        data = {}
        data['particle'] = {}
        for key in system.particle[0].__dict__.keys():
            value = system.view('particle.' + key)
            # Restore C order (transpose as (N, ndim))
            # We rely on the underlying storage order to detect this
            if value.flags['F_CONTIGUOUS']:
                value = value.transpose()
            data['particle'][key] = value.copy()

        data['cell'] = {}
        if system.cell is not None:
            for key in system.cell.__dict__.keys():
                data['cell'][key] = system.view('cell.' + key).copy()

        # Insert frame
        if step in self.steps:
            ind = self.steps.index(step)
            self._system[ind] = data
        else:
            self._system.append(data)

    def read_system(self, frame):
        # TODO: optimize by storing a private System
        N = len(self._system[frame]['particle']['species'])
        s = System()
        s.particle = [Particle() for _ in range(N)]
        s.cell = Cell()

        data = self._system[frame]
        particle_attrs = data['particle'].keys()
        cell_attrs = data['cell'].keys()

        for what in particle_attrs:
            for i, p in enumerate(s.particle):
                setattr(p, what, data['particle'][what][i].copy())
        for what in cell_attrs:
            setattr(s.cell, what, data['cell'][what].copy())

        # # Set all default attributes
        # default_particle_attrs = s.particle[0].__dict__.keys()
        # # Note: setting as view can be more efficient only if we use a private system
        # # Otherwise s.view() internally iterates over all particles
        # for what in default_particle_attr:
        #     s.view(f'particle.{what}')[...] = data['particle'][what].copy()
        # for what in cell_attr:
        #     s.view(f'cell.{what}')[...] = data['cell'][what].copy()

        # # Now set custom attributes. These cannot be set as views properly right now.
        # for what in set(stored_particle_attr) - set(default_particle_attr):
        #     for i, p in enumerate(s.particle):
        #         setattr(p, what, data['particle'][what][i].copy())
        return s


# This is maintanined for backward compatibility
TrajectoryRamFull = TrajectoryRamView
