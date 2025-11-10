import os
import glob
import json

from .interaction import Interaction
from .interaction_molecular import InteractionMolecular
from .interaction_molecular import InteractionIntermolecular, InteractionIntramolecular
from .neighbor_list import NeighborList
from .verlet_list import VerletList
from .trajectory import Trajectory

# TODO: these functions were moved from atooms-models, check whether they are useful

def _available():
    """Pretty print the available potentials"""
    print('Available potentials:')
    for potential in _database_potential:
        print('- ', potential)

    print('Available cutoffs:')
    for what in _database_cutoff:
        print('- ', what)

def _potential(name, parameters, args='-O3 -ffast-math', verbose=False):
    """Get a potential from database"""
    from .helpers import _normalize_path
    import f2py_jit

    path = _normalize_path(name)
    extra_args = '--opt="{} {}"'.format('-ffree-form -ffree-line-length-none ', args)
    uid = f2py_jit.build_module(path, extra_args=extra_args, verbose=verbose)
    module = f2py_jit.import_module(uid)
    module.potential.setup(**parameters)

    class Potential():
        pass
    potential = Potential()
    potential.parameters = parameters
    potential.compute = module.potential.compute
    # if vectorize:
    #     if hasattr(module.potential, 'compute_vector'):
    #         potential.compute = module.potential.compute_vector
    #     else:
    #         raise ValueError('cannot vectorize {}'.format(name))
    # else:
    #     potential.compute = module.potential.compute
    return potential

def _add(path):
    """
    Add all f90 files in `path` to the global `database`
    """
    for _path in glob.glob(os.path.join(path, '*.f90')):
        # Be forgiving
        if not os.path.exists(_path):
            continue
        # Potential name is file basename
        name = os.path.basename(_path)[:-4]
        # Determine whether this is a potential or a cutoff
        with open(_path) as fh:
            line = fh.readline()
            if 'potential' in line:
                _database_potential[name] = ''
            elif 'cutoff' in line:
                _database_cutoff[name] = ''


# Singleton
_database_potential = {}
_database_cutoff = {}

# By default, load all json files in module path
_add(os.path.join(os.path.dirname(__file__)))
