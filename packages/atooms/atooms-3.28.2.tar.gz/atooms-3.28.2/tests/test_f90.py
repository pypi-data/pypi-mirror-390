import os
import unittest
from atooms.trajectory import Trajectory
from atooms.system import System, Particle, Cell
from atooms.backends.f90 import Interaction, NeighborList, VerletList


class Test(unittest.TestCase):

    def setUp(self):
        self.fileinp = os.path.join(os.path.dirname(__file__), '../data/lj_N256_rho1.0.xyz')
        self.trajectory = Trajectory(self.fileinp)
        self.model = {
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

    # TODO: restore when molecular terms are added
    # def test_harmonic_bending(self):
    #     import numpy
    #     from math import pi
    #     angle = 30
    #     model = {
    #         "potential": [
    #             {
    #                 "type": "harmonic_bending",
    #                 "parameters": {"theta0": [[[angle / 360 * 2*pi]]], "k": [[[1.0]]]}
    #             }
    #         ],
    #         "cutoff": [
    #             {
    #                 "type": "cut",
    #                 "parameters": {"rcut": [[2.5]]}
    #             }
    #         ]
    #     }
    #     # x, y = numpy.cos(angle / 360 * 2*pi), numpy.sin(angle / 360 * 2*pi)
    #     # particles = [Particle(position=[0.0, 0.0, 0.0], species=1),
    #     #              Particle(position=[1.0, 0.0, 0.0], species=1),
    #     #              Particle(position=[x, y, 0.0], species=1)]
    #     # cell = Cell([10., 10., 10.])
    #     # system = System(particles, cell)
    #     # system.interaction = Interaction(model, inline=False)
    #     # print(system.potential_energy())
    #     # #self.assertAlmostEqual(system.potential_energy(), 0.0)
    #     # self.assertLess(sum(system.interaction.forces[:, 0]**2), 1e-10)

    #     angle = 60
    #     dx = 0.1
    #     model["potential"][0]["parameters"]["theta0"] = [[[angle / 360 * 2*pi]]]
    #     x, y = numpy.cos(angle / 360 * 2*pi), numpy.sin(angle / 360 * 2*pi)
    #     particles = [Particle(position=[-x+dx, y, 0.0], species=1),
    #                  Particle(position=[0.0, 0.0, 0.0], species=1),
    #                  Particle(position=[x-dx, y, 0.0], species=1)]
    #     cell = Cell([10., 10., 10.])
    #     system = System(particles, cell)
    #     system.interaction = Interaction(model)
    #     system.potential_energy()
    #     self.assertAlmostEqual(system.interaction.forces[0, 0], -system.interaction.forces[0, 2])
    #     self.assertAlmostEqual(system.interaction.forces[0, 1], 0.0)
    #     ref = [[0.2, 0.0, 0.0], [0.9, 0.0, 0.0], [x+0.1, y, 0.0]]

    #     # for i in range(3):
    #     #     dx = 1e-5
    #     #     system.particle[0].position[i] = ref[0][i]
    #     #     u0 = system.potential_energy()
    #     #     system.particle[0].position[i] += dx/2
    #     #     f0 = system.interaction.forces[i, 0]
    #     #     system.particle[0].position[i] += dx/2
    #     #     u1 = system.potential_energy()
    #     #     f = - (u1 - u0) / dx
    #     #     self.assertAlmostEqual(f, f0, places=3)

    #     for i, p in enumerate(system.particle):
    #         p.position[:] = ref[i]

    #     dx = 1e-5
    #     for i in range(3):
    #         system.particle[i].position[0] = ref[i][0]
    #         u0 = system.potential_energy()
    #         system.particle[i].position[0] += dx/2
    #         f0 = system.interaction.forces[0, i]
    #         system.particle[i].position[0] += dx/2
    #         u1 = system.potential_energy()
    #         f = - (u1 - u0) / dx
    #         #self.assertAlmostEqual(f, f0, places=3)
    #         print(f, f0)
    #     return

    #     angle = 60.0
    #     model = {
    #         "potential": [
    #             {
    #                 "type": "harmonic_bending",
    #                 "parameters": {"theta0": [[[angle / 360 * 2*pi]]], "k": [[[1.0]]]}
    #             }
    #         ],
    #         "cutoff": [
    #             {
    #                 "type": "cut",
    #                 "parameters": {"rcut": [[1.01]]}
    #             }
    #         ]
    #     }
    #     x, y = numpy.cos(angle / 360 * 2*pi), numpy.sin(angle / 360 * 2*pi)
    #     particles = [Particle(position=[0.0, 0.0, 0.0], species=1),
    #                  Particle(position=[1.0, 0.0, 0.0], species=1),
    #                  Particle(position=[x, y, 0.0], species=1),
    #                  Particle(position=[-x, y, 0.0], species=1),
    #                  ]
    #     cell = Cell([10., 10., 10.])
    #     system = System(particles, cell)
    #     system.interaction = Interaction(model, inline=True)
    #     # TODO: bug in inline, rjk becomes zero because j is replaced twice with k
    #     # I fixed the offending vars
    #     # ! inline: distance
    #     # ! local: []
    #     # ! dummy: ['j', 'k', 'pos', 'rjk']
    #     # ! vars: ['i', 'j', 'pos', 'rij']
    #     # rjk = pos(:,k) - pos(:,k)
    #     self.assertAlmostEqual(system.potential_energy(), 0.0)

    def test_debug(self):
        from f2py_jit.finline import inline_source
        # The problem is that we first replace i with j, and then k with j (being the
        # second argument. One way to solve the problem is to ensure all local variables
        # are prefixed with _ or something.
        src = """

  pure subroutine distance(i,j,pos,rij)
    integer, intent(in) :: i, j
    double precision, intent(in)    :: pos(:,:)
    double precision, intent(inout) :: rij(:)
    rij = pos(:,i) - pos(:,j)
  end subroutine distance

  subroutine forces()
    double  precision :: pos(:,:)
    integer                         :: i, j, k, jj, isp, jsp, ksp
    double precision                :: rjk(size(pos,1))
    !call distance(jj,k,pos,rjk)  ! OK
    call distance(j,k,pos,rjk)  ! FAILS
end subroutine forces
"""
        inline_source(src)

    def test_collinear(self):
        particles = [Particle(position=[0.0, 0.0, 0.0], species=1),
                     Particle(position=[1.0, 0.0, 0.0], species=1),
                     Particle(position=[2.0, 0.0, 0.0], species=1)]
        cell = Cell([10., 10., 10.])
        system = System(particles, cell)
        system.interaction = Interaction(self.model)
        self.assertAlmostEqual(system.potential_energy(), -0.01257276409199999)

    def test_energy(self):
        from atooms.trajectory.decorators import change_species
        system = self.trajectory[0]
        system.interaction = Interaction(self.model)
        system = change_species(system, 'F')
        system.compute_interaction('energy')
        self.assertAlmostEqual(system.potential_energy(per_particle=True, cache=True), -3.8079776291909284)
        system.compute_interaction('energies')
        self.assertAlmostEqual(system.potential_energy(cache=True), sum(system.interaction.energies) / 2)

    def test_species_layout_cast(self):
        from atooms.trajectory.decorators import change_species
        system = self.trajectory[0]
        system.interaction = Interaction(self.model)
        # Tolerate string species, they will be cast as int
        for p in system.particle:
            p.species = '1'
        self.assertAlmostEqual(system.potential_energy(per_particle=True), -3.8079776291909284)

    def test_species_layout_C(self):
        system = self.trajectory[0]
        system.interaction = Interaction(self.model)
        for p in system.particle:
            p.species = '0'
        self.assertAlmostEqual(system.potential_energy(per_particle=True), -3.8079776291909284)
        self.assertAlmostEqual(system.potential_energy(per_particle=True, cache=False), -3.8079776291909284)
        self.assertAlmostEqual(system.potential_energy(per_particle=True, cache=False), -3.8079776291909284)
        system = self.trajectory[0]
        system.interaction = Interaction(self.model, neighbor_list=VerletList())
        for p in system.particle:
            p.species = '0'
        self.assertAlmostEqual(system.potential_energy(per_particle=True), -3.8079776291909284)

    def test_species_layout_A(self):
        # This will fail
        system = self.trajectory[0]
        system.interaction = Interaction(self.model)
        with self.assertRaises(ValueError):
            system.potential_energy(per_particle=True)

    def test_derivatives(self):
        from atooms.trajectory.decorators import change_species
        system = self.trajectory[0]
        system.interaction = Interaction(self.model)
        system = change_species(system, 'F')
        system.compute_interaction("forces")
        self.assertAlmostEqual(system.interaction.forces[0, 0], 65.3083639139375)
        system.compute_interaction('gradw')
        self.assertAlmostEqual(system.interaction.gradw[0, 0], -71505.20734345658)
        system.compute_interaction('hessian')
        self.assertAlmostEqual(system.interaction.hessian[0, 0, 0, 0], 963.3891474196369)

    def test_multiple(self):
        """Test with multiple potentials: compute two LJ interactions with epsilons that sum up to 1"""
        from atooms.trajectory.decorators import change_species
        model = {
            "cutoff": [
                {"type": "cut_shift", "parameters": {"rcut": [[2.5]]}},
                {"type": "cut_shift", "parameters": {"rcut": [[2.5]]}}
            ],
            "potential": [
                {"type": "lennard_jones", "parameters": {"epsilon": [[0.8]], "sigma": [[1.0]]}},
                {"type": "lennard_jones", "parameters": {"epsilon": [[0.2]], "sigma": [[1.0]]}}
            ]
        }
        system = self.trajectory[0]
        system.interaction = Interaction(model)
        system = change_species(system, 'F')
        self.assertAlmostEqual(system.potential_energy(per_particle=True), -3.8079776291909284)
        self.assertAlmostEqual(system.interaction.forces[0, 0], 65.3083639139375)
        # This is not possible yet
        # system.compute_interaction('gradw')
        # self.assertAlmostEqual(system.interaction.gradw[0, 0], -71505.20734345658)
        system.compute_interaction('hessian')
        self.assertAlmostEqual(system.interaction.hessian[0, 0, 0, 0], 963.3891474196369)

    def test_neighbors(self):
        from atooms.trajectory.decorators import change_species
        system = self.trajectory[0]
        system.interaction = Interaction(self.model)
        system.interaction.neighbor_list = VerletList()
        system = change_species(system, 'F')
        self.assertAlmostEqual(system.potential_energy(per_particle=True), -3.8079776291909284)
        self.assertAlmostEqual(system.interaction.forces[0, 0], 65.3083639139375)
        # This is not implemented yet
        # system.compute_interaction('gradw')
        # self.assertAlmostEqual(system.interaction.gradw[0, 0], -71505.20734345658)
        system.compute_interaction('hessian')
        self.assertAlmostEqual(system.interaction.hessian[0, 0, 0, 0], 963.3891474196369)
        system.compute_interaction('energies')
        self.assertAlmostEqual(system.potential_energy(cache=True), sum(system.interaction.energies) / 2)

    def test_neighbors_update(self):
        system = self.trajectory[0]
        system.interaction = Interaction(self.model)
        system.interaction.neighbor_list = VerletList()
        system.species_layout = 'F'
        self.assertAlmostEqual(system.potential_energy(per_particle=True), -3.8079776291909284)
        nmax = system.interaction.neighbor_list.neighbors.shape[0]
        system.density *= 1.5
        system.potential_energy(per_particle=True)
        self.assertTrue(system.interaction.neighbor_list.neighbors.shape[0], nmax)

    def test_neighbors_lattice(self):
        import random
        import numpy
        random.seed(1)
        # This will be a perfect simple cubic
        s = System(N=125)
        s.density = 1.0
        s.species_layout = 'F'
        nl_sann = NeighborList(2.0, method='sann')
        nl_sann.compute(s.dump('box'), s.dump('pos', order='F'), s.dump('species'))
        nl = NeighborList([[1.1]], full=True)
        nl.compute(s.dump('box'), s.dump('pos', order='F'), s.dump('species'))
        i = 0
        # for j in range(nl_sann.number_neighbors[i]):
        #     print(nl_sann.distances[j, i]**0.5, nl_sann.neighbors[j, i])
        # print()
        # for j in range(nl.number_neighbors[i]):
        #     print(nl.distances[j, i]**0.5, nl.neighbors[j, i])
        nn = sorted(nl.neighbors[0:nl.number_neighbors[i], i])
        nn_sann = sorted(nl_sann.neighbors[0:nl_sann.number_neighbors[i], i])
        self.assertEqual(nn, nn_sann)
        self.assertTrue(numpy.all(nl.distances[0:nl_sann.number_neighbors[i]] < 1.1))
        self.assertEqual(len(nn), 6)

    def test_neighbors_lattice_binning(self):
        self.skipTest('timings are unreliable')
        import random
        import numpy
        for d, N in [(2, 10000), (3, 20000)]:
            random.seed(1)
            s = System(N=N, d=d)
            s.composition = {'A': N//2, 'B': N//2}
            s.density = 1.0
            s.species_layout = 'F'
            s.interaction = Interaction(self.model)
            s.interaction.neighbor_list = VerletList(binning=True)
            from atooms.core.utils import Timer
            with Timer(output=None) as timer1:
                epot_0 = s.potential_energy(per_particle=True)
            s.interaction.neighbor_list = VerletList(binning=False)
            with Timer(output=None) as timer2:
                epot_1 = s.potential_energy(per_particle=True)
            self.assertLess(timer1.wall_time, timer2.wall_time)
            self.assertAlmostEqual(epot_0, epot_1, places=7)
            # print(timer1.wall_time, timer2.wall_time)

    def test_sort(self):
        src = """
  SUBROUTINE sort(neighbor, distance, sortneighbor, distancesorted)
    ! Parameters
    INTEGER(8), INTENT(inout) :: neighbor(:)
    REAL(8), INTENT(inout) :: distance(:)
    INTEGER(8), INTENT(out) :: sortneighbor(size(neighbor))
    REAL(8), INTENT(out) :: distancesorted(size(neighbor))
    ! Variables
    INTEGER(8) :: i, imin, j, n_tmp
    REAL(8)    :: d_tmp
    ! Computation
    DO i=1,size(neighbor)
      imin = i
      DO j=i+1,size(neighbor)
        IF (distance(j) < distance(imin)) THEN
          imin = j
        END IF
        d_tmp = distance(i)
        n_tmp = neighbor(i)
        distance(i) = distance(imin)
        neighbor(i) = neighbor(imin)
        distance(imin) = d_tmp
        neighbor(imin) = n_tmp
        distancesorted(i) = distance(i)
        sortneighbor(i) = neighbor(i)
     END DO
     if (i == size(neighbor)) sortneighbor(i) = neighbor(i)
     if (i == size(neighbor)) distancesorted(i) = distance(i)
     print*, 'sort', i, imin, neighbor(i), sortneighbor(i)
    END DO
  END SUBROUTINE   
"""
        src = """
 subroutine insertion_sort(n, x, ns, xs)
    implicit none
    integer(8), intent(inout) :: n(:)
    real(8), intent(inout) :: x(:)
    integer(8), intent(out) :: ns(size(n))
    real(8), intent(out) :: xs(size(n))
    integer(8) :: i,j
    integer(8) :: temp
    real(8) :: temp_x

    ns = n
    xs = x
    do i=2,size(ns)
       temp=ns(i)
       temp_x=xs(i)
       do j=i-1,1,-1
          if (xs(j) <= temp_x) exit
          ns(j+1)=ns(j)
          xs(j+1)=xs(j)
       enddo
       ns(j+1)=temp
       xs(j+1)=temp_x
    enddo
  end subroutine insertion_sort
"""
        import f2py_jit
        import numpy
        f90 = f2py_jit.jit(src)
        n = numpy.array([1, 2, 3, 4])
        x = numpy.array([2.0, 3.0, 1.0, 1.1])
        ns, xs = f90.insertion_sort(n, x)
        # print(ns, xs)

    @unittest.skip('broken test')
    def test_neighbors(self):
        from atooms.trajectory.decorators import change_species
        rcut = [[1.5]]
        system = self.trajectory[0]
        system.neighbor_list = NeighborList(rcut)
        system.species_layout = 'F'
        system.compute_neighbor_list()
        self.assertEqual(list(system.particle[0].neighbors), [17, 32, 52, 91, 109, 112, 121, 140, 149, 162, 181, 198, 231, 247, 256])

    def test_parallel(self):
        from atooms.trajectory import Trajectory, change_species
        from atooms.simulation import Simulation, Scheduler, write_config, write_thermo

        def main(parallel, neighbor):
            fileinp = os.path.join(os.path.dirname(__file__), '../data/lj_N1000_rho1.0.xyz')
            self.trajectory.close()
            self.trajectory = Trajectory(fileinp)
            system = self.trajectory[-1]
            system.species_layout = 'F'
            system.interaction = Interaction(self.model, parallel=parallel)
            if neighbor:
                system.interaction.neighbor_list = VerletList(skin=0.3, parallel=parallel, update='periodic', update_period=1)
            system.compute_interaction()
            return system.potential_energy(per_particle=True, cache=True)

        # Note that threads should be set from outside
        u_p = main(True, True)
        u_s = main(False, True)
        self.assertTrue(abs(u_p - u_s) < 1e-10)
        u_p = main(True, False)
        u_s = main(False, False)
        self.assertTrue(abs(u_p - u_s) < 1e-10)

    def test_polydisperse(self):
        fileinp = os.path.join(os.path.dirname(__file__), '../data/lj_poly_N250.xyz')
        trajectory = Trajectory(fileinp)
        model = {
            "cutoff": [{
                "type": "cut_shift", "parameters": {"rcut": [[1.25]]}
            }],
            "potential": [{
                "type": "lennard_jones",
                "parameters": {"sigma": [[1.0]],
                               "epsilon": [[1.0]]}
            }],
        }
        system = trajectory[0]
        system.species_layout = 'F'
        system.interaction = Interaction(model)
        self.assertAlmostEqual(system.potential_energy(per_particle=True), 0.2677241464681521)
        self.assertAlmostEqual(system.interaction.forces[0, 0], 0.826650238231295)
        trajectory.close()

    def test_cutoff(self):
        import f2py_jit
        for cut in ["cut", "cut_shift", "cut_shift_linear",
                    "linear_cut_shift", "quadratic_cut_shift",
                    "cut_shift_quadratic"]:
            self.model['cutoff'][0]['type'] = cut
            self.model['cutoff'][0]['parameters']['rcut'][0] = 1.25
            interaction = Interaction(self.model)
            f90 = f2py_jit.import_module(interaction._uid[0])
            # The logical is returned as integer
            self.assertEqual(f90.cutoff.is_zero(1, 1, (1.25-0.01)**2), 0)
            self.assertEqual(f90.cutoff.is_zero(1, 1, (1.25+0.01)**2), 1)

        # For cubic spline we must change the name of parameter
        # How could this test work before??
        for cut in ["cubic_spline"]:
            self.model['cutoff'][0]['type'] = cut
            del self.model['cutoff'][0]['parameters']['rcut']
            self.model['cutoff'][0]['parameters']['rspl'] = [2.5]
            interaction = Interaction(self.model)
            f90 = f2py_jit.import_module(interaction._uid[0])
            # The logical is returned as integer
            # print(f90.cutoff.rcut_)
            self.assertEqual(f90.cutoff.is_zero(1, 1, (3.2)**2), 0)
            self.assertEqual(f90.cutoff.is_zero(1, 1, (3.3)**2), 1)
            
    def test_potential_derivatives(self):
        from atooms.backends.f90.helpers import _check_potential_derivatives as _check
        self.assertTrue(_check('twobody_gaussian', [1.0, 1.0], 1.0))
        self.assertTrue(_check('twobody_harmonic', [1.0, 1.0], 1.0))
        self.assertTrue(_check('twobody_yukawa', [1.0, 1.0, 0.0], 1.0))
        self.assertTrue(_check('twobody_lennard_jones', [1.0, 1.0], 1.0))
        self.assertTrue(_check('twobody_inverse_power', [12, 1.0, 1.0], 1.0))
        self.assertTrue(_check('twobody_sum_inverse_power', [[12], [1.0], [1.0]], 1.0))

    def test_interaction_field_total(self):
        import numpy
        from atooms.backends.f90 import Interaction as InteractionParticle
        from atooms.system.interaction import InteractionField, Interaction

        system = self.trajectory[0]
        system.species_layout = 'F'

        def gravitational_field(pos, mass, g=9.81):
            u = mass[:] * g * pos[-1, :]
            grad = numpy.zeros_like(pos)
            grad[-1, :] = mass[:] * g
            return u, grad, None
        system.interaction = Interaction()
        system.interaction.add(InteractionParticle(self.model))
        system.interaction.add(InteractionField(gravitational_field,
                                                variables={'pos': 'particle.position',
                                                           'mass': 'particle.mass'}))
        system.compute_interaction('forces')

    def test_helpers(self):
        """Test that unrolling works for d=2 and d=3"""
        import sys
        from atooms.core.utils import Timer

        if sys.version_info.major == 3 and sys.version_info.minor >= 6:
            self.skipTest('manual loop unrolling is ineffective with 3.6')

        # Check 3d
        system = self.trajectory[0]
        system.species_layout = 'F'
        system.interaction = Interaction(self.model)
        with Timer(output=None) as timer1:
            u1 = system.compute_interaction('energy')
        system.interaction = Interaction(self.model, dimensions=3)
        with Timer(output=None) as timer2:
            u2 = system.compute_interaction('energy')
        self.assertAlmostEqual(u1, u2)
        # print(timer2.wall_time, timer1.wall_time)
        self.assertLess(timer2.wall_time, timer1.wall_time)

        # Check 2d (could be refactored)
        system.cell.side = system.cell.side[:2]
        # system.cell.origin = system.cell.origin[:2]
        for p in system.particle:
            p.position = p.position[:2]
            p.velocity = p.velocity[:2]
        system.interaction = Interaction(self.model)
        with Timer(output=None) as timer1:
            u1 = system.compute_interaction('energy')
        system.interaction = Interaction(self.model, dimensions=2)
        with Timer(output=None) as timer2:
            u2 = system.compute_interaction('energy')
        self.assertAlmostEqual(u1, u2)
        # print(timer2.wall_time, timer1.wall_time)

    def tearDown(self):
        self.trajectory.close()


if __name__ == '__main__':
    unittest.main()
