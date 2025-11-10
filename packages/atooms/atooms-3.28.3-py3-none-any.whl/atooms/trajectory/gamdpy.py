"""GAMDPY trajectory format."""

import h5py  # pylint:disable=import-error
import numpy

from atooms.system import System
from atooms.system.particle import Particle
from atooms.system.cell import Cell
from .base import TrajectoryBase


# return f5 hierarchy as string
def _h5_tree(val, pre='', out="", is_root=True):
    if is_root:
        out += "[Root Group]\n"
        for attr_key, attr_val in val.attrs.items():
            if isinstance(attr_val, str):
                if len(attr_val)>100:
                    attr_val = attr_val[:100]
            out += pre + f'@ {attr_key}: {attr_val}\n'
        out += pre + "[Subgroups]\n"

    length = len(val)
    for key, item in val.items():
        length -= 1
        is_last = length == 0
        branch = '└── ' if is_last else '├── '
        new_pre = pre + ('    ' if is_last else '│   ')

        if isinstance(item, h5py.Group):
            out += pre + branch + key + " [Group]\n"
            for attr_key, attr_val in item.attrs.items():
                if isinstance(attr_val, str):
                    if len(attr_val)>100:
                        attr_val = attr_val[:100]
                out += new_pre + f'@ {attr_key}: {attr_val}\n'
            out = _h5_tree(item, new_pre, out, is_root=False)
        else:
            out += pre + branch + key + f' [Dataset] {item.shape}\n'
            for attr_key, attr_val in item.attrs.items():
                if isinstance(attr_val, str):
                    if len(attr_val)>100:
                        attr_val = attr_val[:100]
                out += new_pre + f'@ {attr_key}: {attr_val}\n'
    return out


class _SafeFile(h5py.File):
    # TODO: decorate hdf5 class so that error messages contain the path of the offending file
    def create_group_safe(self, group):
        # TODO: recursively create all h5 groups that do not exist?
        # TODO: redefine create_group unless this is a serious performace issue?
        if group not in self:
            self.create_group(group)


class TrajectoryGAMDPY(TrajectoryBase):

    """GAMDPY trajectory format (https://libraries.io/pypi/gamdpy)"""

    suffix = 'h5'

    def __init__(self, filename, mode='r'):
        super().__init__(filename, mode)

        # a trajectory can be composed by multiple blocks
        self._n_timeblocks = None
        self._n_tbsteps = None
        self._system = None
        # this is because particles could have non-zero images event in the initial frame
        self._initial_images = None
        # TODO: move this to write mode
        self.variables = ['particle.position', 'particle.velocity', 'particle.position_unfolded']
        # self.variables = ['particle.position', 'particle.velocity', 'particle.position_unfolded', 'particle.im']

        if self.mode == 'r':
            self._file = h5py.File(self.filename, mode)

        elif self.mode == 'w':
            self._file = _SafeFile(self.filename, mode)

        else:
            raise ValueError('Specify mode (r/w) for file %s (invalid: %s)' % (self.filename, self.mode))

    def read_timestep(self):
        group_name = '/'
        dt = self._file[group_name].attrs['dt']
        return dt

    def read_steps(self):
        """Read steps from gamdpy trajectory_saver attributes in .h5 file"""
        group_name = '/trajectory_saver'
        try:
            s = self._file[group_name].attrs['steps']
        except:
            s = self._file[group_name + '/steps']
        try:
            # TODO: write those in write_init() and make them 'mandatory'
            self._n_timeblocks = self._file[group_name].attrs['num_timeblocks']
            self._n_tbsteps = self._file[group_name].attrs['steps_per_timeblock']
        except:
            group_name = '/trajectory_saver'
            pos = numpy.array(self._file[group_name + '/positions'])
            self._n_timeblocks = pos.shape[0]
            self._n_tbsteps = pos.shape[1]
        # we must know this not to write the same configuration twice
        if self._n_timeblocks > 1 and s[-1] == self._n_tbsteps:
            self._overlapping_steps = True
        steps = []
        for i_timeblock in range(self._n_timeblocks):
            for step in s:
                temp = step + self._n_tbsteps*i_timeblock
                steps.append(int(temp))
        return [int(a) for a in numpy.unique(steps)]

    def read_block_size(self):
        # TODO: fix get_block_size() in atooms.postprocessing
        # so we don't have to rely on this, which is sloppy
        group_name = '/trajectory_saver'
        try:
            s = self._file[group_name + '/steps']
        except:
            s = self._file[group_name].attrs['steps']
        try:
            # TODO: write those in write_init() and make them 'mandatory'
            self.n_timeblocks = self._file[group_name].attrs['num_timeblocks']
            self.n_tbsteps = self._file[group_name].attrs['steps_per_timeblock']
        except:
            group_name = '/trajectory_saver'
            pos = numpy.array(self._file[group_name + '/positions'])
            self.n_timeblocks = pos.shape[0]
            self.n_tbsteps = pos.shape[1]
        # we must kwnow this not to write the same configuration twice
        self._overlapping_steps = False
        if self.n_timeblocks>1 and s[-1]==self.n_tbsteps:
            self._overlapping_steps = True
        if not self._overlapping_steps:
            return len(s)
        else:
            return len(s)-1
    
    def read_init(self):
        # read particles
        group_name = '/initial_configuration'

        box = self._file[group_name].attrs['simbox_data']
        ptype = self._file[group_name + '/ptype']
        spe = [str(v) for v in ptype]
        scalars = self._file[group_name + '/scalars']
        scalar_columns = list(scalars.attrs['scalar_columns'])
        mas = scalars[:,scalar_columns.index('m')]

        vectors = self._file[group_name + '/vectors']
        vector_columns = list(vectors.attrs['vector_columns'])
        pos = vectors[vector_columns.index('r'),:,:] # pos = value[0,:,:]
        vel = vectors[vector_columns.index('v'),:,:] # vel = value[1,:,:]

        # images are not mandatory
        try:
            r_im = self._file[group_name + '/r_im']
            self._initial_images = r_im # this attribute is useful for now
        except:
            # self._initial_images = None
            pass

        n = len(spe)
        particle = []
        for i in range(n):
            p = Particle(species=spe[i],
                         mass=mas[i],
                         position=pos[i, :],
                         velocity=vel[i, :])
            p.im=r_im[i,:]

        self._system = System(particle, Cell(box))
        return self._system

    def read_system(self, frame):
        # read the static properties from initial configuration
        group_name = '/initial_configuration'
        box = self._file[group_name].attrs['simbox_data']
        ptype = self._file[group_name + '/ptype']
        spe = [str(v) for v in ptype]
        scalars = self._file[group_name + '/scalars']
        scalar_columns = list(scalars.attrs['scalar_columns'])
        mas = scalars[:,scalar_columns.index('m')]
        n = len(spe)

        # determine indexes to retrieve system from gamdpy arrays
        idx_timeblock = frame // (self.block_size) 
        idx_config = frame % (self.block_size)
        # this takes care of whether there are overlapping steps or not
        if self._overlapping_steps:
            if frame in [-1, self.__len__()-1]:
                idx_timeblock = -1
                idx_config = -1

        # read positions and images
        group_name = '/trajectory_saver'
        dset_pos = self._file[group_name + '/positions']
        dset_img = self._file[group_name + '/images']
        pos = numpy.array(dset_pos[idx_timeblock, idx_config, :, :], dtype='float64')
        try:
            # again, img not mandatory, probably to fix
            img = numpy.array(dset_img[idx_timeblock, idx_config, :, :], dtype='int64')
        except:
            img = numpy.zeros(shape=pos.shape, dtype='int64')
        # oops!a gamdpy does not save velocities currently...
        # dset_vel = self._file[group_name + '/velocities']
        # vel = numpy.array(dset_vel[idx_timeblock, idx_config, :, :], dtype='float64')
        vel = numpy.zeros(shape=pos.shape, dtype='float64')

        # compute unfolded positions
        pos_unf = numpy.zeros(shape=pos.shape, dtype='float64')
        img_current = numpy.zeros(shape=pos.shape, dtype='int64')
        for i in range(len(pos)):
            img_current[i,:] = img[i,:] - self._initial_images[i,:]
            pos_unf[i,:] = pos[i,:] + img_current[i,:]*box[:]
            # pos_unf[i,:] = pos[i,:] + img[i,:]*box[:]     # images can be non-zero in the first (saved) frame!

        particle = []
        for i in range(n):
            p = Particle(species=spe[i],
                         mass=mas[i],
                         position=pos[i, :],
                         velocity=vel[i, :])
            p.im=img_current[i,:]
            # redundancy here, which is better to store? We should probably write images
            p.position_unfolded=pos_unf[i, :]
            particle.append(p)

        return System(particle, cell=Cell(box))

    def write_timestep(self, value):
        self._file.create_group_safe('/')
        self._file['/'].attrs['dt'] = value

    def write_block_size(self, value):
        self._file.create_group_safe('/')
        self._file.create_group_safe('/trajectory_saver')
        self._file['/trajectory_saver'].attrs['num_timeblocks'] = value

    def write_init(self, system):
        group_name = '/initial_configuration'
        self._file.create_group_safe(group_name)

        # cell is an attribute in /initial_configuration
        if system.cell is not None:
            self._file[group_name].attrs['simbox_data'] = system.cell.side
            self._file[group_name].attrs['simbox_name'] = 'Orthorombic'

        # Particle (initial configuration)
        if system.particle is not None:
            # species, positions/velocieties/forces are datasets
            ptype = [int(p.species) for p in system.particle]
            vectors = numpy.zeros(shape=(3, len(system.particle), 3))
            r_im = numpy.zeros(shape=(len(system.particle), 3))
            pos = numpy.array([p.position for p in system.particle])
            vectors[0, :, :] = pos
            # img = numpy.array([p.im for p in system.particle])
            # r_im[:,:] = img
            try:
                img = numpy.array([p.im for p in system.particle])
                r_im[:, :] = img
            except AttributeError:
                r_im[:, :] = numpy.zeros(shape=pos.shape)
            self._file[group_name].create_dataset('ptype', data=ptype, dtype=numpy.int32)
            self._file[group_name].create_dataset('vectors', data=vectors, dtype=numpy.float32)
            self._file[group_name].create_dataset('r_im', data=r_im, dtype=numpy.int32)
            # this 'decorates' the vectors dataset
            self._file[group_name + '/vectors'].attrs['vector_columns'] = ['r', 'v', 'f']

            # mass is a scalar
            scalars = numpy.zeros(shape=(len(system.particle), 1))
            scalars[:,0] = [p.mass for p in system.particle]
            self._file[group_name].create_dataset('scalars', data=scalars, dtype=numpy.int32)
            self._file[group_name + '/scalars'].attrs['scalar_columns'] = ['m']

        # we must create now the trajectory_saver group with reshapable positions and images
        group_name = '/trajectory_saver'
        self._file.create_group_safe(group_name)
        self._file[group_name].create_dataset('steps', data=numpy.array([]), dtype=numpy.int32)
        # self._file[group_name].attrs['steps'] = numpy.array([], dtype='int32')

        if system.particle is not None:
            ndim = system.number_of_dimensions
            # gamdpy here is redundant, it stores the initial configuration also here
            shape = (1, 1, len(system.particle), ndim)
            maxshape = (1, None, len(system.particle), ndim) # for now stricly only one timeblock
            positions = numpy.zeros(shape=shape, dtype='float32')
            images = numpy.zeros(shape=shape, dtype='int32')
            positions[0, 0, :, :] = pos
            images[0, 0, :, :] = r_im
            self._file[group_name].create_dataset('positions', data=positions, shape=shape, maxshape=maxshape, dtype=numpy.float32)
            self._file[group_name].create_dataset('images', data=images, shape=shape, maxshape=maxshape, dtype=numpy.int32)
            self._first_frame = True

    def write_system(self, system, step):
        from copy import deepcopy

        # TODO: generalise writing also multiple timeblocks
        group_name = '/trajectory_saver'
        self._file.create_group_safe(group_name)
        old_steps = numpy.array(self._file[group_name + '/steps'])
        new_steps = list(deepcopy(old_steps))
        # TODO: why on earth is this int32?!
        new_steps.append(numpy.int32(step))
        del self._file[group_name + '/steps']
        self._file[group_name].create_dataset('steps', data=numpy.array(new_steps), dtype=numpy.int32)
        # self._file[group_name].attrs['steps'] = numpy.array(new_steps)

        if system.particle is not None and not self._first_frame:
            ndim = system.number_of_dimensions
            # TODO: there seems to be a bug where an extra frame is written; the following solution can't work
            # if system.particle is not None and step!=0:

            # this reshaping is in order *not* to read and write all the arrays every time
            pos = self._file[group_name + '/positions']
            new_shape = (1, pos.shape[1]+1, len(system.particle), ndim)
            pos.resize((new_shape))
            pos[0, -1, :, :] = numpy.array([p.position[:] for p in system.particle], dtype='float32')

            img = self._file[group_name + '/images']
            new_shape = (1, img.shape[1] + 1, len(system.particle), ndim)
            img.resize((new_shape))
            # img[0,-1,:,:] = numpy.array([p.im[:] for p in system.particle], dtype='int32')
            try:
                img[0, -1, :, :] = numpy.array([p.im[:] for p in system.particle], dtype='int32')
            except AttributeError:
                img[0, -1, :, :] = numpy.zeros(shape=(len(system.particle), ndim))
        else:
            self._first_frame = False


        if system.cell is not None:
            # update cell; it should be possible to read updated cell from gamdpy
            pass

    def __str__(self):
        return _h5_tree(self._file)
