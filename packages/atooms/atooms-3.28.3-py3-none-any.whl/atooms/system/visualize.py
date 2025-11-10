"""
Visualization functions for particles

Each show() method relies on a specific, optional visualization backend.
"""

# These functions used to belong to system.particle

_palette = [
    "#3c44aa",
    "#f0002f",
    "#f58f20",
    "#940650",
    "#f0e694",
]

def _hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 256 for i in (0, 2, 4))


def show_3dmol(particle, cell=None, radius=1.0, palette=None):
    """Visualize particles in cell using 3dmol http://3dmol.csb.pitt.edu/

    :param particle: sequence of particles to show
    :param cell: cell that encloses the particles
    :param radius: particle radius
    :param palette: to color the particles
    """
    from .particle import distinct_species
    import py3Dmol  # pylint: disable=import-error

    if palette is None:
        palette = ["#466DE8", "#FF4C4C", "#ffe066", "#70c1b3", "#50514f",
                   "#0cce6b", "#c200fb", "#e2a0ff", "#6622cc", "#119822"]
    colors = {}
    for i, s in enumerate(distinct_species(particle)):
        colors[s] = palette[i]
    view = py3Dmol.view()
    view.setBackgroundColor('white')
    for p in particle:
        view.addSphere({'center': {'x': p.position[0], 'y': p.position[1], 'z': p.position[2]},
                        'radius': radius * p.radius, 'color': colors[p.species]})
    if cell is not None:
        view.addBox({'center': {'x': cell.center[0], 'y': cell.center[1], 'z': cell.center[2]},
                     'dimensions': {'w': cell.side[0], 'h': cell.side[1], 'd': cell.side[2]},
                     'wireframe': True, 'color': "#000000"})
    return view


def show_matplotlib(particle, cell, output_file=None, linewidth=2, alpha=0.7,
                    show=False, now=False, outfile=None, axis=(0, 1)):
    """
    Show a snapshot of the `particle`s in the given `cell`, projected on the two
    given `axis`. A matplotlib `Figure` instance is returned for further
    customization or visualization in notebooks.

    :param particle: sequence of particles to show
    :param cell: cell that encloses the particles
    :param output_file: optional file where image is saved (ignored if `None`)
    :param linewidth: particles' circles
    :param alpha: transparency of particles
    :param show: show image immediately
    :param now: show image immediately
    :param axis: project on `axis` (2d list or tuple)
    :param outfile: name of output file  (ignored if `None`)
    """
    import matplotlib.pyplot as plt  # pylint:disable=import-error
    from .particle import distinct_species
    if now:
        show = True
    if output_file is not None:
        outfile = output_file
    color_db = ['b', 'r', 'y', 'g']
    species = distinct_species(particle)
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)
    if cell is not None:
        ax.set_xlim((-cell.side[axis[0]]/2, cell.side[axis[1]]/2))
        ax.set_ylim((-cell.side[axis[0]]/2, cell.side[axis[1]]/2))

    for p in particle:
        pos = [p.position[axis[0]], p.position[axis[1]]]
        c = plt.Circle(pos, p.radius,
                       facecolor='white',
                       edgecolor='black', linewidth=linewidth)
        ax.add_artist(c)
        c = plt.Circle(pos, p.radius,
                       facecolor=color_db[species.index(p.species)],
                       edgecolor=None, alpha=alpha)
        ax.add_artist(c)
    if outfile is not None:
        fig.savefig(outfile, bbox_inches='tight')
    # TODO: show should be True by default
    if show:
        plt.show()
    return fig


def show_ovito(particle, cell, output_file=None, color='species',
               radius=0.5, viewport=None, callback=None, tmpdir=None,
               camera_dir=(0, 1, 0), camera_pos=(0, -10, 0),
               size=(640, 480), zoom=True, perspective=False,
               color_map='viridis', color_normalize=False, outfile=None):
    """
    Render image of particles in cell using ovito. The image is returned for
    visualization in jupyter notebooks.

    :param particle:
    :param cell:
    :param output_file:
    :param color:
    :param radius:
    :param viewport:
    :param callback:
    :param tmpdir:
    :param camera_dir:
    :param camera_pos:
    :param size:
    :param zoom:
    :param perspective:
    :param color_map:
    :param color_normalize:
    :param outfile:
    """
    import os
    from ovito.vis import Viewport, TachyonRenderer  # pylint: disable=no-name-in-module,import-error

    import tempfile
    from atooms.core.utils import mkdir

    if output_file is not None:
        outfile = output_file

    # Color coding
    color_attr = [getattr(p, color) for p in particle]
    is_discrete = isinstance(color_attr[0], (str, int))
    # Corresponding color system
    if is_discrete:
        # Discrete attribute
        color_db = sorted(list(set(color_attr)))
        color_db.sort()
        palette = [_hex_to_rgb(c) for c in _palette]
        colors = []
        for p in particle:
            colors.append(palette[color_db.index(getattr(p, color))])
    else:
        # Continuous attribute
        try:
            # Try with matplotlib
            import matplotlib
            import matplotlib.cm
            colormap = matplotlib.cm.get_cmap(color_map)
            if color_normalize:
                norm = matplotlib.colors.Normalize()
                norm.autoscale(color_attr)
                colors = colormap(norm(color_attr))
            else:
                colors = colormap(color_attr)
        except ImportError:
            # Fallback
            if color_normalize:
                c_min, c_max = min(color_attr), max(color_attr)
                if c_min != c_max:
                    colors = [[(c - c_min) / (c_max - c_min), 0.3,
                               (c_max - c) / (c_max - c_min)] for c in color_attr]
            else:
                colors = [[c, 0.3, c] for c in color_attr]

    # Make sure dirname exists
    if outfile is not None:
        mkdir(os.path.dirname(outfile))

    # Ovito stuff. Can be customized by client code.
    from ovito.pipeline import StaticSource, Pipeline  # pylint: disable=import-error
    from ovito.data import DataCollection, SimulationCell, Particles  # pylint: disable=import-error
    # from ovito.modifiers import CreateBondsModifier  # pylint: disable=import-error

    data = DataCollection()
    _cell = SimulationCell(pbc=(False, False, False))
    _cell[0, 0] = cell.side[0]
    _cell[1, 1] = cell.side[1]
    _cell[2, 2] = cell.side[2]
    _cell[:, 3] = -cell.side/2
    _cell.vis.enabled = True
    _cell.vis.line_width = 0.02
    # _cell.vis.rendering_color = (1.0, 1.0, 1.0)
    data.objects.append(_cell)

    # Create a Particles object
    # Scale radii by input radius
    particles = Particles()
    particles.create_property('Position', data=[p.position for p in particle])
    particles.create_property('Radius', data=[p.radius*2*radius for p in particle])
    particles.create_property('Color', data=colors)  # [[1,0,0], [1,0,0], [1,0,0]])
    data.objects.append(particles)

    # Create a new Pipeline with a StaticSource as data source:
    pipeline = Pipeline(source=StaticSource(data=data))

    # Apply client code callback
    if callback:
        callback(pipeline)
    pipeline.add_to_scene()

    # Define viewport
    if viewport:
        vp = viewport
    else:
        if perspective:
            vp = Viewport(type=Viewport.Type.Perspective, camera_dir=camera_dir, camera_pos=camera_pos)
        else:
            vp = Viewport(type=Viewport.Type.Ortho, camera_dir=camera_dir, camera_pos=camera_pos)

    # Render
    if zoom:
        vp.zoom_all()
    if outfile is None:
        fh = tempfile.NamedTemporaryFile('w', dir=tmpdir, suffix='.png', delete=False)
        outfile = fh.name

    vp.render_image(filename=outfile,
                    size=size,
                    renderer=TachyonRenderer())

    # Scene is a singleton, so we must clear it
    pipeline.remove_from_scene()

    # Try to display the image (e.g. in a jupyter notebook)
    try:
        from IPython.display import Image
        return Image(outfile)
    except ImportError:
        return outfile
