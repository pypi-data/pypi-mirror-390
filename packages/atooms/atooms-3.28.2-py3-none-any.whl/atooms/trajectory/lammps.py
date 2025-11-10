# This file is part of atooms
# Copyright 2010-2024, Daniele Coslovich

"""LAMMPS trajectory format."""

import sys
import numpy

from atooms.system import System, Particle, Cell
from atooms.system.particle import distinct_species
from atooms.system.interaction import Interaction
from .base import TrajectoryBase
from .folder import TrajectoryFolder


# Redefine range for python
if sys.version_info[0] == 2:
    range = xrange  # noqa: F821 pylint: disable=undefined-variable

# Formatting callbacks

def _parse_type(data, idx, system):
    system.particle[idx].species = data

def _parse_x(data, idx, system):
    system.particle[idx].position[0] = float(data)

def _parse_y(data, idx, system):
    system.particle[idx].position[1] = float(data)

def _parse_z(data, idx, system):
    system.particle[idx].position[2] = float(data)

def _parse_xs(data, idx, system):
    system.particle[idx].position[0] = (float(data) - 0.5) * system.cell.side[0]

def _parse_ys(data, idx, system):
    system.particle[idx].position[1] = (float(data) - 0.5) * system.cell.side[1]

def _parse_zs(data, idx, system):
    system.particle[idx].position[2] = (float(data) - 0.5) * system.cell.side[2]

def _parse_vx(data, idx, system):
    system.particle[idx].velocity[0] = float(data)

def _parse_vy(data, idx, system):
    system.particle[idx].velocity[1] = float(data)

def _parse_vz(data, idx, system):
    system.particle[idx].velocity[2] = float(data)

def _parse_fx(data, idx, system):
    system.interaction.forces[idx, 0] = float(data)

def _parse_fy(data, idx, system):
    system.interaction.forces[idx, 1] = float(data)

def _parse_fz(data, idx, system):
    system.interaction.forces[idx, 2] = float(data)

def _parse_ix(data, idx, system):
    system.particle[idx]._ix = int(data)

def _parse_iy(data, idx, system):
    system.particle[idx]._iy = int(data)

def _parse_iz(data, idx, system):
    system.particle[idx]._iz = int(data)

def _parse_mass(data, idx, system):
    system.particle[idx].mass = float(data)

def _parse_charge(data, idx, system):
    system.particle[idx].charge = float(data)

def _parse_energy(data, idx, system):
    system.particle[idx].energy = float(data)

def _parse_molecule_id(data, idx, system):
    system.particle[idx].molecule_id = int(data)


class TrajectoryLAMMPS(TrajectoryBase):

    """
    LAMMPS format (https://docs.lammps.org/dump.html)

    In write mode, an additional .inp file is used as startup file.
    """

    suffix = 'atom'
    _cbk = {'x': _parse_x, 'y': _parse_y, 'z': _parse_z,
            'xu': _parse_x, 'yu': _parse_y, 'zu': _parse_z,
            'xs': _parse_xs, 'ys': _parse_ys, 'zs': _parse_zs,
            'xsu': _parse_xs, 'ysu': _parse_ys, 'zsu': _parse_zs,
            'vx': _parse_vx, 'vy': _parse_vy, 'vz': _parse_vz,
            'fx': _parse_fx, 'fy': _parse_fy, 'fz': _parse_fz,
            'ix': _parse_ix, 'iy': _parse_iy, 'iz': _parse_iz,
            'c_pe': _parse_energy, 'q': _parse_charge,
            'type': _parse_type, 'mass': _parse_mass, 'mol': _parse_molecule_id}

    def __init__(self, filename, mode='r', single_frame=False,
                 first_particle=-1, last_particle=-1, ignore_id=False):
        super().__init__(filename, mode)
        self.precision = 14  # default to double precision
        self.single_frame = single_frame
        self.first_particle = first_particle
        self.last_particle = last_particle
        self.ignore_id = ignore_id
        self._file = open(self.filename, self.mode)
        if mode == 'r':
            self._setup_index()

    def _setup_index(self):
        """Sample indexing via tell / seek"""
        from collections import defaultdict
        self._file.seek(0)
        self._index_db = defaultdict(list)
        while True:
            data = self._file.readline()
            # We break if file is over or we found an empty line
            if not data:
                break
            if data.startswith('ITEM:'):
                for block in ['TIMESTEP', 'NUMBER OF ATOMS',
                              'BOX BOUNDS', 'ATOMS']:
                    if data[6:].startswith(block):
                        # entry contains whatever is found after block
                        entry = data[7+len(block):]
                        line = self._file.tell() - len(data)
                        self._index_db[block].append((line, entry))
                        break
                # Avoid reading after ATOOMS block has been found.
                # We assume it is the last block in the file.
                # The single_frame variable is a hint that there are
                # no more frames in the file
                if block == 'ATOMS' and self.single_frame:
                    break
        self._file.seek(0)

    def read_steps(self):
        steps = []
        for idx, _ in self._index_db['TIMESTEP']:
            self._file.seek(idx)
            self._file.readline()
            step = int(self._file.readline())
            steps.append(step)
        self._file.seek(0)
        return steps

    def read_system(self, frame):
        # Read number of particles
        idx, _ = self._index_db['NUMBER OF ATOMS'][frame]
        self._file.seek(idx)
        self._file.readline()
        data = self._file.readline()
        npart = int(data)

        # Build the system
        system = System()
        # First fill in the right number of particles.
        # This is necessary to be able to read them when unsorted
        system.particle = []
        for i in range(npart):
            if self.first_particle > 0 and i < self.first_particle:
                continue
            if self.last_particle > 0 and i >= self.last_particle:
                break
            system.particle.append(Particle())

        # Add cell
        idx, data = self._index_db['BOX BOUNDS'][frame]
        self._file.seek(idx)
        self._file.readline()
        ndim = len(data.split())
        # TODO: parse periodicity
        if ndim == 3:
            # Restricted triclinic: data == 'xy xz yz'
            # Orthogonal cell with PBC: data == 'pp pp pp'
            pass
        if ndim == 6:
            # Restricted triclinic with periodicity info
            ndim = 3
        if ndim == 2:
            # Triclinic, data == 'abc origin'
            raise ValueError('triclinic cells are not supported')

        L, center = [], []
        for _ in range(ndim):
            data = [float(x) for x in self._file.readline().split()]
            if len(data) == 3:
                # Currently triclinic is only supported if not tilted
                if float(data[2]) > 0.0:
                    raise ValueError('tilt not supported')
            L.append(data[1] - data[0])
            center.append((data[1] + data[0]) / 2)
        system.cell = Cell(numpy.array(L), center=numpy.array(center))

        # Read atoms data
        idx, data = self._index_db['ATOMS'][frame]
        fields = data.split()  # fields on a line
        _ = self._file.readline()

        # Add interaction if forces are present
        # In atooms, forces belong to the interaction, not to particles
        if 'fx' in fields or 'fy' in fields or 'fz' in fields:
            # TODO: this won't work with first and last particles
            system.interaction = Interaction()
            system.interaction.forces = numpy.ndarray((npart, ndim))
        else:
            interaction = None

        self.variables = []
        for field in fields:
            if field in ['x', 'xu', 'xs', 'xsu']:
                self.variables.append('particle.position')
            if field == 'vx':
                self.variables.append('particle.velocity')
            if field == 'q':
                self.variables.append('particle.charge')
            if field == 'mass':
                self.variables.append('particle.mass')
            if field == 'type':
                self.variables.append('particle.species')
        self.variables = tuple(self.variables)

        for i in range(npart):
            # Limit reading the ATOMS section if requested
            if self.first_particle > 0 and i < self.first_particle:
                continue
            if self.last_particle > 0 and i >= self.last_particle:
                break
            data = self._file.readline().split()
            # Accept unsorted particles by parsing their id
            if 'id' in fields and not self.ignore_id:
                idx = int(data[0]) - 1
            else:
                idx = i
            # Populate particle's attributes by reading fields
            for j, field in enumerate(fields):
                if field in self._cbk:
                    self._cbk[field](data[j], idx, system)

        return system

    def write_init(self, system):
        assert system.number_of_dimensions in [2, 3], 'can only use lammps with d=2,3'
        f = open(self.filename + '.inp', 'w')
        np = len(system.particle)
        L = system.cell.side
        species_db = distinct_species(system.particle)

        # LAMMPS header
        h = '\n'
        h += "{:d} atoms\n".format(np)
        h += "{:d} atom types\n".format(len(species_db))
        h += "{:.{prec}f} {:.{prec}f} xlo xhi\n".format(-L[0]/2, L[0]/2, prec=self.precision)
        h += "{:.{prec}f} {:.{prec}f} ylo yhi\n".format(-L[1]/2, L[1]/2, prec=self.precision)
        if system.number_of_dimensions == 3:
            h += "{:.{prec}f} {:.{prec}f} zlo zhi\n".format(-L[2]/2, L[2]/2, prec=self.precision)

        # LAMMPS body
        # Masses of species
        m = "\nMasses\n\n"
        for isp in range(len(species_db)):
            # Iterate over particles. Find instances of species and get masses
            for p in system.particle:
                if p.species == species_db[isp]:
                    m += '{:d} {:{prec}f}\n'.format(isp + 1, p.mass, prec=self.precision)
                    break

        # Atom coordinates
        r = "\nAtoms\n\n"
        atom_style = 'atomic'
        # Setup string formatting.
        # This complicated thing is to handle both 2d/3d
        fmt = '{:d} {:d}'  # index and species
        fmt_vel = '{:d}'
        if hasattr(system.particle[0], 'charge'):
            atom_style = 'charge'
            fmt += ' {}'
        if system.number_of_dimensions == 3:
            fmt += ' {:{prec}} {:{prec}} {:{prec}}'
            fmt_vel += ' {:{prec}} {:{prec}} {:{prec}}'
        else:
            fmt += ' {:{prec}} {:{prec}} 0.0'
            fmt_vel += ' {:{prec}} {:{prec}} 0.0'

        # Add internal image info, if present
        fmt += ' {} {} {}'
        _has_image = False
        if hasattr(system.particle[0], '_ix'):
            _has_image = True

        def _image(p):
            if _has_image:
                return [p._ix, p._iy, p._iz]
            return [0, 0, 0]

        fmt += '\n'
        fmt_vel += '\n'

        if atom_style == 'atomic':
            for i, p in enumerate(system.particle):
                isp = species_db.index(p.species) + 1
                r += fmt.format(i+1, isp, *p.position, *_image(p), prec=self.precision)
        elif atom_style == 'charge':
            for i, p in enumerate(system.particle):
                isp = species_db.index(p.species) + 1
                r += fmt.format(i+1, isp, p.charge, *p.position, *_image(p), prec=self.precision)

        v = "\nVelocities\n\n"
        for i, p in enumerate(system.particle):
            v += fmt_vel.format(i+1, *p.velocity, prec=self.precision)

        f.write(h)
        f.write(m)
        f.write(r)
        f.write(v)
        f.close()

    def write_system(self, system, step):
        import warnings
        warnings.warn('trajectory lammps write method not implemented')

    def close(self):
        self._file.close()


class TrajectoryFolderLAMMPS(TrajectoryFolder):

    """
    Multi-file layout LAMMPS format.

    It looks for all files matching a pattern in the input folder path.
    """

    def __init__(self, filename, mode='r', file_pattern='*',
                 step_pattern=r'[a-zA-Z\.]*(\d*)', first_particle=-1, last_particle=-1):
        super().__init__(filename, mode=mode,
                                                     file_pattern=file_pattern,
                                                     step_pattern=step_pattern)
        self.first_particle = first_particle
        self.last_particle = last_particle
        # Small trick to force reading steps from lammps file
        self._steps = None
        # Sort frames according to step read in lammps file
        sorted_steps = sorted(self.steps)
        files_with_steps = [(x, y) for x, y in zip(self.files, self.steps)]
        files_with_steps.sort(key=lambda x: sorted_steps.index(x[1]))
        files = [_[0] for _ in files_with_steps]
        self.files = files
        self._steps = sorted_steps

    def read_steps(self):
        steps = []
        for filename in self.files:
            with TrajectoryLAMMPS(filename, 'r', single_frame=True,
                                  first_particle=self.first_particle,
                                  last_particle=self.last_particle) as th:
                steps.append(th.steps[0])
        return steps

    def read_system(self, frame):
        with TrajectoryLAMMPS(self.files[frame], 'r', single_frame=True,
                              first_particle=self.first_particle,
                              last_particle=self.last_particle) as th:
            return th[0]

    def write_system(self, system, step):
        # We cannot write
        raise NotImplementedError('cannot write lammps folder trajectory')
