import numpy

class Topology:

    """
    Topology of a molecular system.

    Examples
    --------

    Find the topology of a `System` instance

    .. code-block:: python

       topology = Topology(system.molecule, system.particle)

    The topology provides bonds, angles and torsion angles as lists of
    pairs, triplets and quadruplets of particle indices

    .. code-block:: python

       topology.bond
       topology.angle
       topology.dihedral

    The index of the molecule to which a particle belongs is
    available as a list

    .. code-block:: python

       topology.molecule_index

    If the particle is not bonded to any molecule, the `molecule_index` 
    is `-1`.
    """
    
    def __init__(self, molecule, particle):
        """
        Initialize the topology from molecules in the list `molecule` and whose
        particles are included in the `particle` list. The `particle` list may
        include particles that are not part of any molecule.
        """
        # Most general (but less efficient) approach: look for the particles
        # pointed to by the bond in the system.particle list
        bonds, bonds_type = [], []
        for m in molecule:
            for b, bt in zip(m.bond, m.bond_type):
                p_0 = m.particle[b[0]]
                p_1 = m.particle[b[1]]
                i_0 = particle.index(p_0)
                i_1 = particle.index(p_1)
                bonds.append((i_0, i_1))
                bonds_type.append(bt)

        angles, angles_type = [], []
        for m in molecule:
            for b, bt in zip(m.angle, m.angle_type):
                p_0 = m.particle[b[0]]
                p_1 = m.particle[b[1]]
                p_2 = m.particle[b[2]]
                i_0 = particle.index(p_0)
                i_1 = particle.index(p_1)
                i_2 = particle.index(p_2)
                angles.append((i_0, i_1, i_2))
                angles_type.append(bt)

        self.bond = bonds
        self.angle = angles
        self.bond_type = bonds_type
        self.angle_type = angles_type
        self.dihedral = []
        self.improper = []

        self.molecule_index = - numpy.ones(len(particle), dtype=int)
        for im, m in enumerate(molecule):
            for p in m.particle:
                ip = particle.index(p)
                self.molecule_index[ip] = im

    def as_dict(self):
        """
        Return the topology as a dictionary of topological attributes
        """
        return {'bond': self.bond, 'angle': self.angle,
                'bond_type': self.bond_type, 'angle_type': self.angle_type,
                'dihedral': self.dihedral, 'improper': self.improper}
