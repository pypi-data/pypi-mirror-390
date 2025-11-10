import numpy

__all__ = ['report_simulation', 'report_stats', 'report_system',
           'report_trajectory']


def report_trajectory(trajectory):
    """Return a dict with information about a `trajectory` instance."""
    db = {
        'frames': len(trajectory),
        'steps': trajectory.steps[-1],
        'duration': trajectory.times[-1]
    }
    if len(trajectory) > 1:
        db['timestep'] = trajectory.timestep
        db['grandcanonical'] = trajectory.grandcanonical
        db['block size'] = trajectory.block_size
        if trajectory.block_size == 1:
            db['steps_between_frames'] = trajectory.steps[1]-trajectory.steps[0]
            db['time_between_frames'] = trajectory.times[1]-trajectory.times[0]
        else:
            db['block steps'] = trajectory.steps[trajectory.block_size-1]
            db['block'] = [trajectory.steps[i] for i in range(trajectory.block_size)]
    return db

def report_system(system):
    """Return a dict with information about a `system` instance."""
    db = {
        'number_of_particles': len(system.particle),
        'number_of_species': len(system.distinct_species),
        'species': [numpy.asarray(_).item() for _ in system.distinct_species],
        'composition': [system.composition[numpy.asarray(_).item()] for _ in system.distinct_species],
        'concentration': [system.concentration[numpy.asarray(_).item()] for _ in system.distinct_species],
        'size_dispersion': float(numpy.std([p.radius for p in system.particle]) / numpy.mean([p.radius for p in system.particle])),
        'density': float(round(system.density, 10)),
        'cm_velocity_norm': float(numpy.sum(system.center_of_mass('velocity')**2)**0.5)
    }
    if system.cell is not None:
        db['cell_side'] = [_.item() for _ in system.cell.side]
        db['cell_volume'] = system.cell.volume.item()
    return db

def report_simulation(simulation):
    """Return a dict with information about a `simulation` instance."""
    # TODO: the simulation instance should provide its params as dict
    db = {
        'backend': str(simulation.backend.__class__),
        'rmsd': simulation.rmsd.item() if hasattr(simulation.rmsd, 'item') else simulation.rmsd,
        'steps': simulation.current_step,
        'wall_time': simulation.wall_time(),
        'TSP': simulation.wall_time(per_step=True, per_particle=True)
    }
    if hasattr(simulation.backend, 'timestep'):
        db['timestep'] = simulation.backend.timestep
    if hasattr(simulation.backend, 'partial_rmsd'):
        db['partial_rmsd'] = simulation.backend.partial_rmsd
    return db

def report_stats(data, ignore=('steps',)):
    """Return a dict with stats about a `data` dictionary with time series."""
    db = {}
    keys = [key for key in data if key not in ignore]
    for key in keys:
        key.replace(' ', '_')
        db[f'mean_{key}'] = numpy.mean(data[key]).item()
    for key in keys:
        key.replace(' ', '_')
        db[f'std_{key}'] = numpy.std(data[key]).item()
    return db
