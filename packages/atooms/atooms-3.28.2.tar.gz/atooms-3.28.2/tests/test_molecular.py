#!/usr/bin/env python

import numpy
import os
import unittest
from atooms.trajectory import TrajectoryLAMMPS, MolecularTrajectoryLAMMPS
from atooms.trajectory.decorators import _Molecular


class Test(unittest.TestCase):

    def setUp(self):
        """
        Set up the test case by initializing the particle trajectory.
        """
        self.input_file = os.path.join(os.path.dirname(__file__),
                                       '../data/trimer_rho1.2.lammpstrj')
        self.particle_trajectory = TrajectoryLAMMPS(self.input_file)

    def test_trajectory(self):
        """
        Test the creation of the molecular trajectory from the particle trajectory.
        """
        molecular_trajectory = MolecularTrajectoryLAMMPS(self.input_file)
        self.frame_0 = molecular_trajectory[0]
        self.molecule_0 = self.frame_0.molecule[0]
        self.particle_0 = self.frame_0.particle[0]
        self.assertIsNotNone(self.molecule_0)
        self.assertIsNotNone(self.particle_0)
        molecular_trajectory.close()

    def test_decorator(self):
        MolecularTrajectory = _Molecular(TrajectoryLAMMPS)
        molecular_trajectory = MolecularTrajectory(self.input_file)
        self.assertTrue(isinstance(molecular_trajectory, TrajectoryLAMMPS))
        self.assertTrue(isinstance(molecular_trajectory, MolecularTrajectory))
        self.frame_0 = molecular_trajectory[0]
        self.molecule_0 = self.frame_0.molecule[0]
        self.particle_0 = self.frame_0.particle[0]
        self.assertIsNotNone(self.molecule_0)
        self.assertIsNotNone(self.particle_0)
        molecular_trajectory.close()

    def test_center_of_mass(self):
        """
        Test the calculation of the center of mass of the first molecule.
        """
        self.test_trajectory()  # Ensure test_trajectory runs first
        center_of_mass = self.molecule_0.center_of_mass
        self.assertAlmostEqual(center_of_mass[0], 3.129313, places=6)
        self.assertAlmostEqual(center_of_mass[1], 6.057427, places=6)
        self.assertAlmostEqual(center_of_mass[2], 4.262863, places=6)

    def test_position(self):
        """
        Test the position of the first particle in the first frame.
        """
        self.test_trajectory()  # Ensure test_trajectory runs first
        particle_0_position = self.particle_0.position
        self.assertAlmostEqual(particle_0_position[0], 2.96049, places=6)
        self.assertAlmostEqual(particle_0_position[1], 6.62826, places=6)
        self.assertAlmostEqual(particle_0_position[2], 4.19592, places=6)

    def _test_trajectory(self, cls):
        from atooms.core.utils import rmf

        with MolecularTrajectoryLAMMPS(self.input_file) as mth:
            s = mth[0]
        N_mol = len(s.molecule)
        fout = '/tmp/molecular.xyz'
        with _Molecular(cls)(fout, 'w') as mth:
            mth.write(s, 0)
        with _Molecular(cls)(fout) as mth:
            s = mth[0]
        self.assertEqual(len(s.molecule), N_mol)
        rmf(fout)

    def test_trajectory_any(self):
        from atooms.trajectory import TrajectoryXYZ, TrajectoryEXYZ, TrajectoryRam
        self._test_trajectory(TrajectoryXYZ)
        # TODO: fix warning about unclosed file, dont know why
        self._test_trajectory(TrajectoryEXYZ)
        # self._test_trajectory(TrajectoryRam)

    def test_system(self):
        """
        Test the length of the molecule list and particle list
        """
        self.test_trajectory()  # Ensure test_trajectory runs first
        self.assertEqual(len(self.frame_0.molecule), 1000)
        self.assertEqual(len(self.frame_0.particle), 3000)

    def test_unfold(self):
        import numpy
        from atooms.system import Particle, Molecule, System, Cell
        from atooms.trajectory import MolecularTrajectoryXYZ, Unfolded

        finp = '/tmp/test_molecular.xyz'
        molecule = Molecule([Particle(position=[2.9, 2.9], species=1),
                             Particle(position=[2.8, 2.8], species=2)], bond=[[0, 1]])
        s = System(molecule=[molecule], cell=Cell([6.0, 6.0]))
        with MolecularTrajectoryXYZ(finp, 'w') as th:
            th.write(s, 0)
            # This is like entering from the other side
            s.molecule[0].center_of_mass += numpy.array([-5.8, 0.0])
            th.write(s, 1)
        with Unfolded(MolecularTrajectoryXYZ(finp)) as th:
            self.assertEqual(th[1].molecule[0].particle[0].position[0], 3.1)
            self.assertEqual(th[1].molecule[0].particle[0].position[1], 2.9)
            self.assertAlmostEqual(th[1].molecule[0].orientation[0][0], th[0].molecule[0].orientation[0][0])
            self.assertAlmostEqual(th[1].molecule[0].orientation[0][1], th[0].molecule[0].orientation[0][1])


    def _setup(self):
        from atooms.system import Particle, Molecule, System, Cell
        from atooms.system.topology import Topology

        molecules = []
        for i in range(2):
            molecules.append(Molecule([Particle(position=[1.0, i], species=1),
                                       Particle(position=[2.2, i], species=1)],
                                      bond=[[0, 1]]))
        s = System(particle=[Particle(position=[0.0, 0.0], species=1)],
                   molecule=molecules, cell=Cell([6.0, 6.0]))
        s.topology = Topology(s.molecule, s.particle)
        return s
            
    def test_intra(self):
        from atooms.backends.f90.interaction_molecular import InteractionIntramolecular
        from atooms.backends.f90.interaction_molecular import InteractionIntermolecular

        s = self._setup()
        model = {'bond': {'type': 'harmonic',
                          'parameters': {'epsilon': [[1.0]], 'sigma': [[1.0]]}}}
        interaction = InteractionIntramolecular(model)

        box = s.cell.side
        pos = s.view('particle.position', order='F')
        mspe = s.view('molecule.species', dtype='int32')
        mol = s.view('topology.molecule_index')
        bond = s.topology.bond
        bond_type = s.topology.bond_type
        rad = s.view('particle.radius')
        interaction.compute('forces', box, pos, mspe, mol, rad, bond, bond_type)
        self.assertAlmostEqual(interaction.energy, 0.04)

    def test_inter(self):
        from atooms.backends.f90.interaction_molecular import InteractionIntramolecular
        from atooms.backends.f90.interaction_molecular import InteractionIntermolecular

        s = self._setup()
        model = {'potential': {'type': 'lennard_jones',
                               'parameters': {'epsilon': [[1.0]], 'sigma': [[1.0]]}},
                 'cutoff': {'type': 'cut',
                            'parameters': {'rcut': [[2.5]]}}
                 }
        interaction = InteractionIntermolecular(model)

        box = s.cell.side
        pos = s.view('particle.position', order='F')
        ids = s.view('particle.species')
        mol = s.topology.molecule_index
        rad = s.view('particle.radius')
        
        interaction.compute('forces', box, pos, ids, rad, mol)
        self.assertAlmostEqual(interaction.energy, -1.0052474)
        
    def test_interaction(self):
        from atooms.system import Interaction
        from atooms.backends.f90.interaction_molecular import InteractionIntramolecular
        from atooms.backends.f90.interaction_molecular import InteractionIntermolecular

        s = self._setup()
        model_intra = {'bond': {'type': 'harmonic',
                          'parameters': {'epsilon': [[1.0]], 'sigma': [[1.0]]}}}
        model_inter = {'potential': {'type': 'lennard_jones',
                               'parameters': {'epsilon': [[1.0]], 'sigma': [[1.0]]}},
                 'cutoff': {'type': 'cut',
                            'parameters': {'rcut': [[2.5]]}}
                 }
        intra = InteractionIntramolecular(model_intra, debug=True)
        inter = InteractionIntermolecular(model_inter, debug=True)
        s.interaction = Interaction()
        s.interaction.add(inter)
        s.interaction.add(intra)
        s.compute_interaction('forces')
        s.potential_energy(per_particle=True)
        s.interaction.term[0].energy
        s.interaction.term[1].energy
        self.assertAlmostEqual(s.interaction.energy, -0.965247427)

    def test_interaction_molecular(self):
        from atooms.backends.f90.interaction_molecular import InteractionMolecular

        s = self._setup()
        model = {
            'bond': {'type': 'harmonic',
                     'parameters': {'epsilon': [[1.0]], 'sigma': [[1.0]]}},
            'angle': {'type': 'harmonic',
                      'parameters': {'epsilon': [[1.0]], 'sigma': [[1.0]]}},
            'potential': {'type': 'lennard_jones',
                           'parameters': {'epsilon': [[1.0]], 'sigma': [[1.0]]}},
            'cutoff': {'type': 'cut',
                       'parameters': {'rcut': [[2.5]]}}
        }
        s.interaction = InteractionMolecular(model)
        s.compute_interaction('forces')
        s.potential_energy(per_particle=True)
        self.assertAlmostEqual(s.interaction.energy, -0.965247427)
        
        
    def test_molecule_species(self):
        from atooms.system import Particle, Molecule, System, Cell, Topology

        molecules = []
        for i in range(2):
            molecules.append(Molecule([Particle(position=[1.0, i], species=0),
                                       Particle(position=[2.2, i], species=1)],
                                      species=i,
                                      bond=[[0, 1]]))
            
        s = System(molecule=molecules, cell=Cell([6.0, 6.0]))
        s.topology = Topology(s.molecule, s.particle)
        mspe = s.view('molecule.species')
        mspe[0], mspe[1] = mspe[1].copy(), mspe[0].copy()
        self.assertEqual(s.molecule[0].species, 1)
        self.assertEqual(s.molecule[1].species, 0)
        mspe = s.view('molecule.species')
        #print(s.view('topology.molecule_species'))
        #print(s.topology.molecule_species[0])
        self.assertEqual(mspe[0], 1)
        self.assertEqual(mspe[1], 0)
        spe = s.view('particle.species')
        spe[0], spe[-1] = 3, 3
        self.assertEqual(s.particle[0].species, 3)
        self.assertEqual(s.particle[-1].species, 3)
        self.assertEqual(s.molecule[0].particle[0].species, 3)
        self.assertEqual(s.molecule[-1].particle[-1].species, 3)
        molecules = []
        for i in range(1):
            molecules.append(Molecule([Particle(position=[1.0, i], species=0),
                                       Particle(position=[2.2, i], species=1)],
                                      species=i,
                                      bond=[[0, 1]]))

        s = System(molecule=molecules, cell=Cell([6.0, 6.0]))
        mspe = s.view('molecule.species')
        mspe[0] = 3
        self.assertEqual(s.molecule[0].species, 3)

    def test_molecule_types(self):
        from atooms.system import Particle, Molecule, Cell, Topology, System

        molecules = []
        for i in range(2):
            molecules.append(Molecule([Particle(position=[1.2, i], species=0),
                                       Particle(position=[2.,  i], species=1),
                                       Particle(position=[3.2, i], species=0)],
                                      species=1,
                                      bond_type=[1, 2],
                                      bond=[[0, 1], [1, 2]],
                                      angle_type=[1],
                                      angle=[[0, 1, 2]]))
            
        s = System(molecule=molecules, cell=Cell([6.0, 6.0]))
        # print(s.view('molecule.angle_type'))
        # print(s.view('molecule.bond_type'))
        # TODO: fix species index... Fortran runtime error: Index '3' of dimension 1 of array 'spe' above upper bound of 2
        s.topology = Topology(s.molecule, s.particle)
        self.assertTrue(numpy.all(s.view('topology.bond_type') ==
                                  numpy.array([1,2, 1,2])))

        from atooms.system import Interaction
        from atooms.backends.f90.interaction_molecular import InteractionIntramolecular
        model = {'bond': {'type': 'harmonic',
                          'parameters': {'epsilon': [[1.0, 1.0]],
                                         'sigma': [[1.0, 1.0]]}}}
        intra = InteractionIntramolecular(model, debug=True)
        s.interaction = Interaction()
        s.interaction.add(intra)
        s.compute_interaction('forces')
        self.assertAlmostEqual(s.potential_energy(), 0.08)
         
    def test_debug(self):
        from f2py_jit import jit
        src = """
subroutine hello(x, i, z, y)
real(8), intent(in) :: x, z
integer, intent(in) :: i
real(8), intent(inout) :: y
!print*, x, i
y = x*i
end subroutine hello
"""
        # Casting integers is no problem...
        y = numpy.array(0.0)
        f90 = jit(src)
        f90.hello(1.0, 2, 0.0, y)
        # print(y)

    def tearDown(self):
        self.particle_trajectory.close()


if __name__ == '__main__':
    unittest.main()
