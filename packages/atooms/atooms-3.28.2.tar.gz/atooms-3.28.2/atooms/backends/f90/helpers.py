import os

def _normalize_path(path, search_dir=None):
    if not path.endswith('.f90'):
        path = path + '.f90'

    if os.path.exists(path):
        return path
    else:
        if search_dir is None:
            search_dir = os.path.dirname(__file__)
        full_path = os.path.join(search_dir, path)
        if os.path.exists(full_path):
            return full_path
        else:
            raise ValueError('could not find source for {}'.format(path))


def _merge_source(*paths):
    """Merges `sources` into a unique source."""
    merged_src = ''
    for path in paths:
        # Check path existence
        source_path = _normalize_path(path)
        with open(source_path) as fh:
            src = fh.read()
        # Merge sources into a single one
        merged_src += src
    return merged_src

def _check_potential_derivatives(potential, params, r):
    import numpy
    import f2py_jit

    u, w, h = numpy.array(0.0), numpy.array(0.0), numpy.array(0.0)
    u1, w1, h1 = numpy.array(0.0), numpy.array(0.0), numpy.array(0.0)
    u2, w2, h2 = numpy.array(0.0), numpy.array(0.0), numpy.array(0.0)
    path = _normalize_path(potential)
    f90 = f2py_jit.jit(path)
    f90.potential.init(*params)
    f90.potential.compute(1, 1, r**2, u, w, h)

    fail_w, fail_h = True, True
    dr = 1e-2
    tol = 1e-6
    while (fail_w or fail_h) and dr > 1e-14:
        f90.potential.compute(1, 1, (r+dr)**2, u1, w1, h1)
        f90.potential.compute(1, 1, (r-dr)**2, u2, w2, h2)
        w_approx = - (u1 - u2) / (2*dr) / r
        h_approx = - (w1 - w2) / (2*dr) / r
        if fail_w and abs(w - w_approx) < tol:
            fail_w = False
        if fail_h and abs(h - h_approx) < tol:
            fail_h = False
        dr /= 2
    # print('Checks for potential {} pass: {}'.format(potential, not fail_w or not fail_h))
    if fail_w:
        print(w, w_approx, abs(w - w_approx), '# w failed')
        return False
    if fail_h:
        print(w, w_approx, abs(h - h_approx), '# h failed')
        return False
    return True
