# Boost Trajectory factory class with callbacks

import copy
from atooms.trajectory import Trajectory as __Trajectory
from atooms.trajectory.factory import TrajectoryFactory
from atooms.system import System


def _wrap_system(system):
    from atooms.trajectory.decorators import change_species
    new_system = System()
    new_system.update(system)
    new_system = change_species(new_system, 'F')
    return new_system


Trajectory = copy.deepcopy(__Trajectory)
Trajectory.register_callback(_wrap_system)

# Trajectory = TrajectoryFactory()
# for key in __Trajectory.formats:
#     new_name = __Trajectory.formats[key].__name__
#     old_cls = __Trajectory.formats[key]
#     cls = type(new_name, (old_cls, ), dict(old_cls.__dict__))
#     cls.add_class_callback(_wrap_system)
#     cls.add_self_callback(_add_interaction)
#     Trajectory.add(cls)

# # Lock the xyz format
# Trajectory.suffixes['xyz'] = Trajectory.formats['xyz']
