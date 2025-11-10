#!/usr/bin/env python

import sys
import random
import copy
import numpy
import unittest
from atooms.system import *


class Test(unittest.TestCase):

    def setUp(self):
        N = 100
        L = 10.0
        random.seed(1)
        self.ref = System()
        self.ref.cell = Cell([L, L, L])
        self.ref.particle = []
        self.ref.thermostat = Thermostat(1.0)
        self.ref.barostat = Barostat(1.0)
        self.ref.reservoir = Reservoir(1.0)
        while len(self.ref.particle) <= N:
            pos = [(random.random() - 0.5) * L,
                   (random.random() - 0.5) * L,
                   (random.random() - 0.5) * L]
            self.ref.particle.append(Particle(position=pos))

    def test_dict(self):
        pos = self.ref['position'].copy()
        self.ref['position'] = pos*2
        self.assertEqual(self.ref['position'][0, 0], pos[0, 0]*2)
        self.assertEqual(self.ref['position'][0, 0], self.ref.particle[0].position[0])

    def test_ndim(self):
        system = System()
        self.assertEqual(system.number_of_dimensions, 0)
        system.cell = Cell([2.0, 2.0])
        self.assertEqual(system.number_of_dimensions, 2)
        particle = Particle(position=[0, 0])
        self.assertEqual(particle.velocity.shape[0], 2)

    def test_density(self):
        system = copy.copy(self.ref)
        density_old = system.density
        system.density = density_old * 1.1
        self.assertAlmostEqual(system.density, density_old * 1.1)

        # When there are no particles, density is zero
        system = System()
        self.assertAlmostEqual(system.density, 0.0)

    def test_density_cluster(self):
        system = copy.deepcopy(self.ref)
        system.cell = None
        self.assertAlmostEqual(system.density, 0.1, 1)

    def test_temperature(self):
        system = copy.copy(self.ref)
        system.set_temperature(1.0)
        self.assertAlmostEqual(system.temperature, 1.0)
        system.scale_velocities(1.0)
        self.assertAlmostEqual(system.temperature, 1.0)

        # Pathological case
        system.particle = system.particle[0: 1]
        self.assertAlmostEqual(system.temperature, 2.0 / system.number_of_dimensions * system.kinetic_energy())

        # Empty system
        system = System()
        self.assertAlmostEqual(system.temperature, 0.0)

    def _test_cm(self, order='F'):
        system = copy.copy(self.ref)
        system.set_temperature(1.0)
        system.view('position', order=order)
        system.view('velocity', order=order)
        for i in range(system.number_of_dimensions):
            self.assertAlmostEqual(system.center_of_mass('velocity')[i], system.cm_velocity[i])
            self.assertAlmostEqual(system.center_of_mass('position')[i], system.cm_position[i])
        system.fix_momentum()
        for i in range(system.number_of_dimensions):
            self.assertAlmostEqual(system.center_of_mass('velocity')[i], 0.0)
        pos_cm = system.cm_position
        for p in system.particle:
            p.position -= pos_cm
        for i in range(system.number_of_dimensions):
            self.assertAlmostEqual(system.center_of_mass('position')[i], 0.0)

    def test_cm(self):
        self._test_cm('C')
        self._test_cm('F')

    def test_pbc_center(self):
        system = copy.copy(self.ref)
        # Move the center of the cell so that positions are within 0 and L
        system.cell.center = system.cell.side / 2
        for p in system.particle:
            p.position += system.cell.side / 2
        # Check that distances are the same
        for i in range(len(system.particle)):
            self.assertAlmostEqual(sum(self.ref.particle[0].distance(self.ref.particle[i], self.ref.cell)**2),
                                   sum(system.particle[0].distance(system.particle[i], system.cell)**2))
        # Move one particle out of the box and fold it back
        pos = copy.copy(system.particle[0].position)
        system.particle[0].position += system.cell.side
        system.particle[0].fold(system.cell)
        self.assertAlmostEqual(pos[0], system.particle[0].position[0])
        self.assertAlmostEqual(pos[1], system.particle[0].position[1])
        self.assertAlmostEqual(pos[2], system.particle[0].position[2])

    def test_fold(self):
        system = copy.copy(self.ref)
        pos = copy.copy(system.particle[0].position)
        system.particle[0].position += system.cell.side
        system.particle[0].fold(system.cell)
        self.assertAlmostEqual(pos[0], system.particle[0].position[0])
        self.assertAlmostEqual(pos[1], system.particle[0].position[1])
        self.assertAlmostEqual(pos[2], system.particle[0].position[2])

    def test_overlaps(self):
        from atooms.system.particle import overlaps
        system = copy.copy(self.ref)
        for p in system.particle:
            p.radius = 1e-10
        pos = copy.copy(system.particle[1].position)
        system.particle[0].position = pos
        ov, ipart = overlaps(system.particle, system.cell)
        self.assertTrue(ov)
        self.assertEqual(ipart, [(0, 1)])

    def test_dump(self):
        self.assertEqual(self.ref.dump('spe')[-1],
                         self.ref.dump('particle.species')[-1])
        self.assertAlmostEqual(self.ref.dump('pos')[-1][-1],
                               self.ref.dump('particle.position')[-1][-1])
        self.assertAlmostEqual(self.ref.dump('vel')[-1][-1],
                               self.ref.dump('particle.velocity')[-1][-1])

    def test_species(self):
        system = copy.copy(self.ref)
        npart = len(system.particle)
        for p in system.particle[0: 10]:
            p.species = 'B'
        for p in system.particle[10: 30]:
            p.species = 'C'
        from atooms.system.particle import composition, distinct_species
        self.assertEqual(distinct_species(system.particle), ['A', 'B', 'C'])
        self.assertEqual(system.distinct_species, ['A', 'B', 'C'])
        self.assertEqual(composition(system.particle)['A'], npart - 30)
        self.assertEqual(composition(system.particle)['B'], 10)
        self.assertEqual(composition(system.particle)['C'], 20)

        # Unhashable numpy scalars
        for p in system.particle:
            p.species = numpy.array(1)
        self.assertEqual(system.distinct_species, [numpy.array(1)])
        for p in system.particle:
            p.species = numpy.array('A')
        self.assertEqual(system.distinct_species, [numpy.array('A')])

    def test_concentration(self):
        system = System(N=100)
        system.set_concentration({'A': 0.2, 'B': 0.8})
        self.assertEqual(system.composition, {'A': 20, 'B': 80})
        system.set_concentration({'A': 1/3, 'B': 2/3})
        self.assertEqual(system.composition, {'A': 33, 'B': 67})
        system = System(N=101)
        system.set_concentration({'A': 0.2, 'B': 0.8})
        self.assertEqual(system.composition, {'A': 20, 'B': 81})
        system = System(N=250)
        system.set_concentration({'A': 0.2, 'B': 0.7, 'C': 0.1})
        self.assertEqual(system.composition, {'A': 50, 'B': 175, 'C': 25})

        def _():
            system.set_concentration({'A': 0.1, 'B': 1.0})
        self.assertRaises(AssertionError, _)

    def test_species_layout(self):
        system = copy.copy(self.ref)
        for p in system.particle[0: 10]:
            p.species = 'B'
        for p in system.particle[10: 30]:
            p.species = 'C'
        self.assertTrue(system.species_layout == 'A')
        system.species_layout = 'C'
        self.assertTrue(system.species_layout == 'C')
        system.species_layout = 'F'
        self.assertTrue(system.species_layout == 'F')
        system.species_layout = 'A'
        self.assertTrue(system.species_layout == 'A')

    def test_packing(self):
        import math
        system = copy.copy(self.ref)
        self.assertAlmostEqual(system.packing_fraction * 6 / math.pi, system.density)

    def test_gyration(self):
        from atooms.system.particle import gyration_radius
        system = copy.copy(self.ref)

        # Ignore cell
        rg1 = gyration_radius(system.particle, method='N1')
        rg2 = gyration_radius(system.particle, method='N2')
        self.assertAlmostEqual(rg1, rg2)

        # With PBC all estimates are different but bounds must be ok
        rg1 = gyration_radius(system.particle, system.cell, method='min')
        rg2 = gyration_radius(system.particle, system.cell, method='N1')
        rg3 = gyration_radius(system.particle, system.cell, method='N2')
        self.assertLessEqual(rg1, rg2)
        self.assertLessEqual(rg3, rg2)

        # Equilateral triangle
        system.particle = [Particle(), Particle(), Particle()]
        system.particle[0].position = numpy.array([0.0, 0.0, 0.0])
        system.particle[1].position = numpy.array([1.0, 0.0, 0.0])
        system.particle[2].position = numpy.array([0.5, 0.5*3**0.5, 0])
        # Put the triangle across the cell
        system.particle[0].position -= 1.01*system.cell.side/2
        system.particle[1].position -= 1.01*system.cell.side/2
        system.particle[2].position -= 1.01*system.cell.side/2
        system.particle[0].fold(system.cell)
        system.particle[1].fold(system.cell)
        system.particle[2].fold(system.cell)
        rg1 = gyration_radius(system.particle, system.cell, method='min')
        rg2 = gyration_radius(system.particle, system.cell, method='N1')
        rg3 = gyration_radius(system.particle, system.cell, method='N2')
        self.assertAlmostEqual(rg1, 0.57735026919)
        self.assertAlmostEqual(rg2, 0.57735026919)
        self.assertAlmostEqual(rg3, 0.57735026919)

    def test_interaction(self):
        from atooms.system.interaction import InteractionBase
        system = copy.copy(self.ref)
        self.assertAlmostEqual(system.potential_energy(), 0.0)
        system.interaction = InteractionBase()
        system.interaction.compute('energy', system.dump('position'))
        self.assertAlmostEqual(system.potential_energy(), 0.0)
        self.assertAlmostEqual(system.potential_energy(normed=True), 0.0)
        self.assertAlmostEqual(system.total_energy(), system.kinetic_energy())

    def test_interaction_add(self):
        from atooms.system.interaction import InteractionBase
        x, y = InteractionBase(), InteractionBase()
        x.energy, y.energy = 1., 1.
        z = sum([x, y])
        self.assertAlmostEqual(z.energy, 2.)
        # Setting energy to None in one interaction obliterates
        # the calculation of the sum of the energies
        y.energy = None
        z = x + y
        self.assertEqual(z.energy, None)

    def test_interaction_terms(self):
        from atooms.system.interaction import InteractionBase, Interaction
        x, y = InteractionBase(), InteractionBase()
        z = Interaction(x, y)
        w = Interaction()
        w.add(x)
        w.add(y)
        w.compute('forces', position=numpy.array([[1.]]))
        self.assertAlmostEqual(w.energy, 0.0)
        self.assertTrue(w.forces is not None)

    def test_interaction_terms_via_system(self):
        from atooms.system.interaction import InteractionBase, Interaction
        system = copy.copy(self.ref)
        system.interaction = Interaction(InteractionBase())
        system.compute_interaction('forces')
        self.assertAlmostEqual(system.potential_energy(), 0.0)

    def test_interaction_wall(self):
        from atooms.simulation import Simulation, Scheduler
        from atooms.backends.f90 import Interaction as InteractionParticle

        model = {
            "potential": [
                {
                    "type": "lennard_jones",
                    "parameters": {"epsilon": [[1.0]], "sigma": [[1.0]]}
                }
            ],
            "cutoff": [
                {
                    "type": "cut_shift",
                    "parameters": {"rcut": [[2.5]]}
                }
            ]
        }

        N = 9
        L = 10.0
        system = System()
        # We still define a big supercell, but we should not need it
        system.cell = Cell([L * 10, L * 10, L * 10])
        system.particle = []
        for i in range(N):
            system.particle.append(Particle(position=[1 + i, 1 + i, 0.0],
                                            velocity=numpy.random.normal(0.0, 0.1, 3),
                                            species=1))
        system.wall = [
            Wall([+1, 0, 0], [0, 0, 0]),
            Wall([-1, 0, 0], [L, 0, 0]),
            Wall([0, +1, 0], [0, 0, 0]),
            Wall([0, -1, 0], [0, L, 0]),
        ]

        # Particle-wall potential
        def inverse_power(rsq, u, w, h, sigma=1.0, epsilon=1.0, exponent=12):
            u[:] = epsilon * (sigma**2 / rsq[:])**(exponent // 2)
            w[:] = exponent * u[:] / rsq[:]

        # We have two interaction terms
        system.interaction = Interaction()
        system.interaction.add(InteractionWall(system.wall, inverse_power))
        system.interaction.add(InteractionParticle(model))
        self.assertAlmostEqual(system.potential_energy(per_particle=True), 0.07016883058835639)

    def test_interaction_field(self):
        from atooms.system.interaction import InteractionField, Interaction

        system = copy.copy(self.ref)

        def gravitational_field(pos, mass, g=9.81):
            u = mass[:] * g * pos[-1, :]
            grad = numpy.zeros_like(pos)
            grad[-1, :] = mass[:] * g
            return u, grad, None
        system.interaction = InteractionField(gravitational_field,
                                              variables={'pos': 'particle.position',
                                                         'mass': 'particle.mass'})
        system.compute_interaction('forces')
        # print(system.potential_energy())
        # print(system.interaction.forces[:, 0])
        self.assertAlmostEqual(system.interaction.forces[0, 0], 0)
        self.assertAlmostEqual(system.interaction.forces[1, 0], 0)
        self.assertAlmostEqual(system.interaction.forces[2, 0], -9.81)

    def test_overlap(self):
        from atooms.system.particle import self_overlap, collective_overlap
        sys1 = copy.deepcopy(self.ref)
        sys2 = copy.deepcopy(self.ref)
        sys1.particle = sys1.particle[:int(len(sys1.particle) / 2)]
        sys2.particle = sys2.particle[int(len(sys2.particle) / 2):]
        self.assertEqual(0, self_overlap(sys1.particle, sys2.particle, 0.001))
        self.assertEqual(0, collective_overlap(sys1.particle, sys2.particle, 0.001, sys1.cell.side))
        sys1.particle = sys1.particle
        sys2.particle = sys1.particle
        self.assertEqual(1, self_overlap(sys1.particle, sys2.particle, 0.001))
        self.assertEqual(1, collective_overlap(sys1.particle, sys2.particle, 0.001, sys1.cell.side))

    def test_overlap_random(self):
        # This test may fail from time to time
        from atooms.system.particle import collective_overlap
        N = 1000
        L = 5.0
        sys = [System(), System()]
        sys[0].cell = Cell([L, L, L])
        sys[1].cell = Cell([L, L, L])
        sys[0].particle = []
        sys[1].particle = []
        for _ in range(N):
            pos = [(random.random() - 0.5) * L,
                   (random.random() - 0.5) * L,
                   (random.random() - 0.5) * L]
            sys[0].particle.append(Particle(position=pos))
        for _ in range(N):
            pos = [(random.random() - 0.5) * L,
                   (random.random() - 0.5) * L,
                   (random.random() - 0.5) * L]
            sys[1].particle.append(Particle(position=pos))
        a = 0.3
        q_rand = ((a**3 * 4./3*3.1415) * N / sys[0].cell.volume)
        self.assertTrue(abs(q_rand - collective_overlap(sys[0].particle, sys[1].particle, a, sys[0].cell.side)) < 0.5)

    def test_view(self):
        import numpy
        from atooms.system import Particle, System

        p = [Particle(), Particle()]
        s = System(p)
        pos = s.dump("pos", order='F', view=True)

        # Modify the dumped array in place preserves the view
        pos[:, 0] += 1.0
        self.assertTrue((p[0].position == pos[:, 0]).all())
        self.assertTrue(numpy.may_share_memory(p[0].position, pos[:, 0]))
        # Modify the position array in place preserves the view
        p[0].position *= 2
        self.assertTrue((p[0].position == pos[:, 0]).all())
        self.assertTrue(numpy.may_share_memory(p[0].position, pos[:, 0]))
        # Modify the position array in place preserves the view
        p[0].position[:] = p[0].position[:] + 4
        self.assertTrue((p[0].position == pos[:, 0]).all())
        self.assertTrue(numpy.may_share_memory(p[0].position, pos[:, 0]))
        pos[:, 0] = pos[:, 0] + 1.0
        self.assertTrue((p[0].position == pos[:, 0]).all())
        self.assertTrue(numpy.may_share_memory(p[0].position, pos[:, 0]))
        # Reassining the position will of course destroy the view
        p[0].position = p[0].position * 2
        self.assertFalse((p[0].position == pos[:, 0]).all())
        self.assertFalse(numpy.may_share_memory(p[0].position, pos[:, 0]))

    def test_view_new(self):
        self.skipTest('')
        import numpy
        from atooms.system import Particle, System

        p = [Particle(), Particle()]
        s = System(p)
        pos = s._view("pos", order='F')

        # Modify the dumped array in place preserves the view
        pos[:, 0] += 1.0
        self.assertTrue((p[0].position == pos[:, 0]).all())
        self.assertTrue(numpy.may_share_memory(p[0].position, pos[:, 0]))
        # Modify the position array in place preserves the view
        p[0].position *= 2
        self.assertTrue((p[0].position == pos[:, 0]).all())
        self.assertTrue(numpy.may_share_memory(p[0].position, pos[:, 0]))
        # Modify the position array in place preserves the view
        p[0].position[:] = p[0].position[:] + 4
        self.assertTrue((p[0].position == pos[:, 0]).all())
        self.assertTrue(numpy.may_share_memory(p[0].position, pos[:, 0]))
        pos[:, 0] = pos[:, 0] + 1.0
        self.assertTrue((p[0].position == pos[:, 0]).all())
        self.assertTrue(numpy.may_share_memory(p[0].position, pos[:, 0]))
        # Reassining the position will of course destroy the view
        p[0].position = p[0].position * 2
        self.assertFalse((p[0].position == pos[:, 0]).all())
        self.assertFalse(numpy.may_share_memory(p[0].position, pos[:, 0]))

    def test_view_clear(self):
        import numpy
        from atooms.system import Particle, System

        p = [Particle(), Particle()]
        s = System(p)

        # We check that particle positions are views on dump array
        pos = s.dump("pos", order='F', view=True)
        self.assertTrue((p[0].position == pos[:, 0]).all())
        self.assertTrue(numpy.may_share_memory(p[0].position, pos[:, 0]))

        # We should get the same dump array
        pos = s.dump("pos", order='F', view=True)
        self.assertTrue((p[0].position == pos[:, 0]).all())
        self.assertTrue(numpy.may_share_memory(p[0].position, pos[:, 0]))

        # We clear the dump array
        pos1 = s.dump("pos", order='F', view=True, clear=True)
        pos1 += 1
        self.assertFalse((p[0].position == pos[:, 0]).all())
        self.assertFalse(numpy.may_share_memory(p[0].position, pos[:, 0]))

    def test_dump_cbk(self):
        """
        Make sure that applying callbacks or changing the particle array
        size creates a new dump.
        """
        import numpy
        from atooms.system import Particle, System

        p = [Particle(), Particle()]
        s = System(p)
        pos1 = s.view("pos", order='C')
        pos2 = s.view("pos", order='F')
        self.assertEqual(pos1.shape, (2, 3))
        self.assertEqual(pos2.shape, (3, 2))

        for view in [False, True]:
            p = [Particle(), Particle()]
            s = System(p)
            pos1 = s.dump("pos", view=view)

            def cbk(system):
                s = copy.copy(system)
                s.particle = [system.particle[0]]
                return s
            s = cbk(s)
            pos2 = s.dump('pos', view=view)
            self.assertEqual(pos1.shape, (2, 3))
            self.assertEqual(pos2.shape, (1, 3))
            # Grandcanonical
            s.particle.append(Particle())
            self.assertEqual(s.dump('pos', view=view).shape, (2, 3))
            # Reassign particle
            # Expected failure with view = True
            if not view:
                s.particle[0] = Particle(position=[1.0, 1.0, 1.0])
                self.assertEqual(s.dump('pos', view=view)[0][0], 1.0)

    def test_dump_cbk_new(self):
        """
        Make sure that applying callbacks or changing the particle array
        size creates a new dump.
        """
        self.skipTest('')
        import numpy
        from atooms.system import Particle, System

        for view in [False, True]:
            p = [Particle(), Particle()]
            s = System(p)
            if view:
                pos1 = s._view("pos")
            else:
                pos1 = s._dump("pos")

            def cbk(system):
                s = copy.copy(system)
                s.particle = [system.particle[0]]
                return s
            s = cbk(s)
            if view:
                pos2 = s._view('pos')
            else:
                pos2 = s._dump('pos')
            self.assertEqual(pos1.shape, (2, 3))
            self.assertEqual(pos2.shape, (1, 3))
            # Grandcanonical
            s.particle.append(Particle())
            if view:
                self.assertEqual(s._view('pos').shape, (2, 3))
            else:
                self.assertEqual(s._dump('pos').shape, (2, 3))
            # Reassign particle
            # Expected failure with view = True
            # But it should work with dump... not if we have dump = view.copy()
            if not view:
                s.particle[0] = Particle(position=[1.0, 1.0, 1.0])
                self.assertEqual(s._dump('pos')[0][0], 1.0)

    def test_slab(self):
        from atooms.system import Particle, System

        s = System(N=256)
        s.density = 1.0
        slabs = s.slab(axis=2, width=1.0)
        slabs = s.slab(axis=2, n=5)
        # slabs[-1].show(now=True)

    def test_dump_species(self):
        """
        Make sure that changing species in the dump is reflected in the
        particle species and viceversa.
        """
        import numpy
        from atooms.system import Particle, System

        view = True
        p = [Particle(), Particle()]
        s = System(p)
        spe = s.dump("particle.species", view=True)
        spe[0] = 'B'
        self.assertEqual(spe[0], s.particle[0].species)
        # With this syntax, the numpy scalar preserves the view!
        # We should upgrade species to property and hide this inside
        s.particle[0].species[()] = 'C'
        self.assertEqual(spe[0], s.particle[0].species)

    def test_dumps(self):
        """Check that dump order does not matter"""
        import numpy
        from atooms.system import Particle, System

        p = [Particle(), Particle()]
        s = System(p)
        # View, dump, view: we should preserve the view and get a copy of the dump
        pos1 = s.dump("pos", view=True)
        pos1[0, 0] = 0.0
        pos2 = s.dump('pos', view=False)
        pos2[0, 0] = 1.0
        pos3 = s.dump("pos", view=True)
        self.assertNotAlmostEqual(pos1[0, 0], pos2[0, 0])
        self.assertAlmostEqual(pos1[0, 0], pos3[0, 0])
        self.assertFalse(numpy.may_share_memory(pos1, pos2))
        self.assertTrue(numpy.may_share_memory(pos1, pos3))

    def test_dump_flatten(self):
        """Check that flattening a dump does not change successive views"""
        import numpy
        from atooms.system import Particle, System

        p = [Particle(), Particle()]
        s = System(p)
        self.assertEqual(len(s.dump('pos', view=True).shape), 2)
        self.assertEqual(len(s.dump('pos', view=False, flat=True).shape), 1)
        self.assertEqual(len(s.dump('pos', view=True).shape), 2)
        self.assertEqual(len(s.dump('pos', view=False, flat=True).shape), 1)

    def test_dump_fail(self):
        """Check that dump fails on unknown attributes"""
        for what in ['whatever', 'particle.whatever', 'cell.whatever']:
            try:
                self.ref.dump(what)
            except AttributeError:
                pass

    def test_decimate(self):
        from atooms.system import Particle, System
        from atooms.system.particle import composition, decimate
        p = [Particle(species='A')]*20 + [Particle(species='B')]*10
        pnew = decimate(p, 12)
        x = composition(pnew)
        self.assertEqual(x['A'], 8)
        self.assertEqual(x['B'], 4)

    @unittest.skipIf(sys.version_info.major == 2, 'skip show() tests with python 2')
    def test_show(self):
        self.skipTest('')
        N = 3
        L = 5.0
        system = System()
        system.cell = Cell([L, L, L])
        system.particle = []
        for _ in range(N):
            pos = (numpy.random.random(len(system.cell.side)) - 0.5) * system.cell.side
            p = Particle(position=pos)
            system.particle.append(p)

        try:
            system.show(backend='')
        except ValueError:
            pass
        try:
            system.show(backend='matplotlib')
            system.show(backend='ovito')
            system.show(backend='3dmol')
        except ImportError:
            self.skipTest('missing backend')

    def test_rotate(self):
        """Rotate particles so that the principal axis is along the y axis"""
        from atooms.system import Particle, Cell
        from atooms.system.particle import rotate
        p1, p2, p3 = Particle(position=[0.0, 0.0, 0.0]), Particle(position=[1.0, 0.0, 0.0]), Particle(position=[2.0, 0.0, 0.0])
        particle = [p1, p2, p3]
        cell = Cell(side=[10.0, 10.0, 10.0])
        rotated = rotate(particle, cell)
        self.assertAlmostEqual(rotated[0].position[1], 0, 6)
        self.assertAlmostEqual(rotated[1].position[1], 1, 6)
        self.assertAlmostEqual(rotated[2].position[1], 2, 6)

    def test_init(self):
        """Test __init__() syntax"""
        self.assertEqual(len(System(N=1).particle), 1)
        self.assertEqual(len(System(N=10).particle), 10)
        self.assertEqual(len(System(N=100).particle), 100)
        self.assertEqual(System(N=10).composition, {'A': 10})
        self.assertEqual(System(N={'B': 4}).composition, {'B': 4})
        self.assertEqual(System(N={'Si': 4, 'O': 2}).composition, {'Si': 4, 'O': 2})
        self.assertEqual(System(N={'A': 4, 'B': 10, 'C': 2}).composition, {'A': 4, 'B': 10, 'C': 2})
        self.assertAlmostEqual(System(N={'Si': 10, 'O': 20}).concentration['Si'], 10/30.)
        self.assertAlmostEqual(System(N={'Si': 10, 'O': 20}).concentration['O'], 20/30.)

    def test_replicate(self):
        s = System(N=2**3, d=2)
        L = s.cell.side[0]
        for p in s.particle:
            p.radius = 0.1
        s.replicate(3, 0)
        x = s.dump('pos', order='F')
        self.assertAlmostEqual(min(x[0, :]), -max(x[0, :]))
        self.assertAlmostEqual(s.cell.side[0], L * 3)

        s = System(N=2**3, d=3)
        L = s.cell.side[0]
        s.replicate(4, 1)
        x = s.dump('pos', order='F')
        self.assertAlmostEqual(min(x[1, :]), -max(x[1, :]))
        self.assertAlmostEqual(s.cell.side[1], L * 4)
        # s.show(outfile='1.png')

    def test_molecule(self):
        from atooms.system.molecule import Molecule
        particle = [Particle(position=[0.00000, -0.06556, 0.00000], species=1),  # , charge=-0.834),
                    Particle(position=[0.75695, 0.52032, 0.00000], species=2),  # , charge=-0.417),
                    Particle(position=[-0.75695, 0.52032, 0.00000], species=2)]  # , charge=-0.417)]
        molecule = Molecule(particle, bond=[(0, 0), (0, 1)], angle=[(1, 0, 2)])
        self.assertTrue(all(numpy.isclose(molecule.center_of_mass, [0., 0.32502667, 0.])))
        molecule.center_of_mass = [0., 0., 0.]
        self.assertTrue(all(numpy.isclose(molecule.center_of_mass, [0., 0., 0.])))

        from atooms.system.particle import _lattice
        lattice = _lattice(4)
        cell = Cell(numpy.ones(3))

        molecules = []
        for p in lattice:
            m = Molecule(particle, bond=[(0, 0), (0, 1)], angle=[(1, 0, 2)])
            m.center_of_mass = p.position
            molecules.append(m)

        system = System(molecule=molecules)
        self.assertEqual(len(system.particle), 12)
        self.assertEqual(len(system.molecule), 4)
        self.assertTrue(all(numpy.isclose(system.dump('molecule.center_of_mass')[0],
                                          [0.25, -0.25, -0.25])))
        self.assertEqual(system.dump('molecule.species')[0], 1) # '122'
        self.assertTrue(numpy.all(numpy.isclose(system.dump('particle.position')[0],
                                                [0.25, -0.64058667, -0.25])))
        self.assertTrue(numpy.all(numpy.isclose(system.dump('molecule.bond')[0],
                                                [[0, 0], [0, 1]])))
        self.assertTrue(numpy.all(numpy.isclose(system.dump('molecule.orientation')[0],
                                                system.dump('molecule.orientation')[1])))
        self.assertTrue(all(numpy.isclose(system.dump('molecule.orientation')[0][0],
                                          [0, -0.39058667, 0])))
        # print(system.dump('molecule.orientation')[0])
        # This was in commit 27893294 and failed
        # [-0.75695, 0.58588, 0])))

        # Check custom orientation vectors
        self.assertTrue(numpy.all([system.molecule[0].orientation_vector('CM-1'),
                                   system.molecule[0].orientation_vector('CM-2'),
                                   system.molecule[0].orientation_vector('CM-3')] ==
                                  system.molecule[0].orientation))

        # Just a formal test that vector product is parsed, I have not checked
        # it is correct (it gives [0., 0., 0.88696373])
        system.molecule[0].orientation_vector('1-2x2-3')
        o = system.molecule[0].orientation_vector('1-2x2-3', normed=True)
        self.assertAlmostEqual(numpy.linalg.norm(o), 1.0)

        self.assertTrue(numpy.all(system.molecule[0].custom_orientation(['1-2']) ==
                                  numpy.array([system.molecule[0].orientation_vector('1-2')])))

        # This test assumes there are no pbc involved
        self.assertTrue(numpy.all(system.molecule[0].orientation_vector('e2e') ==
                                  system.molecule[0].particle[len(particle)-1].position -
                                  system.molecule[0].particle[0].position))

        # print(system.dump('molecule.orientation')[0])

        # This is how it could look like
        try:
            from atooms.backends.f90 import InteractionMolecular
            interaction = InteractionMolecular(model)
            bnds = system.view('molecule.bond')
            angs = system.view('molecule.angle')
            interaction.compute('forces', box, pos, ids, bnds, angs)  # , dihs, imps)
        except:
            pass

    def test_molecule_2d(self):
        from atooms.system.molecule import Molecule
        particle = [Particle(position=[0.00000, -0.06556], species=1),
                    Particle(position=[0.75695, 0.52032], species=2),
                    Particle(position=[-0.75695, 0.52032], species=2)]
        molecule = Molecule(particle, bond=[(0, 0), (0, 1)], angle=[(1, 0, 2)])
        self.assertTrue(all(numpy.isclose(molecule.center_of_mass, [0., 0.32502667])))
        molecule.center_of_mass = [0., 0.]
        self.assertTrue(all(numpy.isclose(molecule.center_of_mass, [0., 0.])))

        # Test without cell
        from atooms.system.particle import _lattice
        lattice = _lattice(4, d=2, spacing=3.0)
        cell = Cell([5.0, 5.0])
        molecules = []
        for p in lattice:
            m = Molecule(particle, bond=[(0, 0), (0, 1)], angle=[(1, 0, 2)])
            m.center_of_mass = p.position
            molecules.append(m)

        system = System(molecule=molecules)
        for p in system.particle:
            p.radius = 0.1
        system.cell = cell
        # system.show(now=True)

        # Test with cell
        from atooms.system.particle import _lattice
        lattice = _lattice(4, d=2, spacing=3.0)
        cell = Cell([5.0, 5.0])
        m = Molecule(particle, bond=[(0, 0), (0, 1)], angle=[(1, 0, 2)], cell=cell)
        m.center_of_mass = numpy.array([2.0, 0.0])
        system = System(molecule=[m], cell=cell)
        for p in system.particle:
            p.radius = 0.1

        # Show molecule and its orientations
        try:
            import matplotlib.pyplot as plt
            fig = system.show()
            ax = fig.axes[0]
            ax.plot(*m.center_of_mass, 'o', color='black')
            for o in m.orientation:
                ax.arrow(*m.center_of_mass, *o, color='black')
            # plt.show()
        except ImportError:
            pass

    def test_molecule_2d_pbc(self):
        from atooms.system.molecule import Molecule
        from atooms.system.particle import _lattice, Particle

        L = 5.0
        particle = [Particle(position=[x, 0.0]) for x in [-1.0, 0.0, 1.0, L/2-0.1]]
        particle = [Particle(position=[x, 0.0]) for x in [-L/2+1, -L/2+0.1, L/2-0.5]]
        # m.center_of_mass = numpy.array([0.0, 0.0])
        lattice = _lattice(4, d=2, spacing=3.0)
        cell = Cell([L, L])
        m = Molecule(particle, cell=cell, bond=[(i, i+1) for i in range(len(particle)-1)])

        # m.center_of_mass = numpy.array([0.0, 0.0])
        system = System(molecule=[m], cell=cell)
        for p in system.particle:
            p.radius = 0.1

        e2e = m.orientation_vector('e2e')
        try:
            import matplotlib.pyplot as plt
            fig = system.show()
            ax = fig.axes[0]
            ax.plot(*m.center_of_mass, 'o', color='black')
            ax.arrow(*m.particle[0].position, *e2e, color='black')
            # for o in m.orientation:
            #    ax.arrow(*m.center_of_mass, *o, color='black')
            plt.show()
        except ImportError:
            pass


if __name__ == '__main__':
    unittest.main()
