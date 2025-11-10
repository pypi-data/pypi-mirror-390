import numpy
import f2py_jit

import atooms.system.interaction
from .interaction import Interaction, _check_polydisperse, _setup_extra_args, \
    _normalize_model_entry

class InteractionIntramolecular(Interaction):

    """
    A fortran 90 backend to compute intramolecular interactions.
    """

    def __init__(self, model, neighbor_list=None,
                 inline=True, inline_safe=False, debug=False,
                 parallel=False, search_dir=None, dimensions=None):
        """
        Similar to the basic Interaction constructor
        """
        assert neighbor_list is None, 'cannot pass neighbor_list to InteractionIntramolecular'
        super().__init__(model, interaction='interaction_intramolecular.f90',
                         inline=inline, debug=debug, parallel=parallel,
                         search_dir=search_dir, dimensions=dimensions)
        self.variables = {'box': 'cell.side',
                          'pos': 'particle.position',
                          # We change the name to avoid inteference with ids in
                          # InteractionIntermolecular
                          'mspe': 'molecule.species:int32',
                          'bond': 'topology.bond',
                          'bond_type': 'topology.bond_type',
                          'mol': 'topology.molecule_index',
                          'rad': 'particle.radius'}

    def _setup_f90(self, model, helpers, interaction, inline=True,
                   inline_safe=False, debug=False, parallel=False,
                   search_dir=None):
        import copy
        from atooms.backends.f90.helpers import _merge_source, _normalize_path
        # Make a local copy
        model = copy.deepcopy(model)
        # After this loop, all potentials and cutoffs have a path entry
        # matching an existing fortran source code.
        # model['bond']['type'] = 'bond_' + model['bond']['type']
        for entry in [model["bond"]]:
            _normalize_model_entry(entry, search_dir, 'bond')
        _potential = model['bond']
        potential = _potential.get('path')
        potential = _normalize_path(potential)
        potential_parameters = _potential.get('parameters')
        source = _merge_source(helpers, potential, interaction)
        if inline:
            source = f2py_jit.finline.inline_source(source, ignore='adjust,forces')
        extra_args = _setup_extra_args(debug, parallel)
        uid = f2py_jit.build_module(source,
                                    metadata={"interaction": interaction,
                                              "helpers": helpers,
                                              "debug": debug,
                                              "parallel": parallel,
                                              "potential": [potential, potential_parameters]},
                                    extra_args=extra_args)
        mod = f2py_jit.import_module(uid)
        mod.bond_potential.init(**potential_parameters)
        self._uid = [uid]

    def compute(self, observable, box, pos, mspe, mol, rad, bond, bond_type):
        """
        Compute `observable` from this interaction
        """
        # Check if system is polydisperse (cached)
        if self._polydisperse is None:
            self._polydisperse = _check_polydisperse(mspe, rad)
        self._compute(observable, box, pos, mspe, mol, rad, bond, bond_type)

    def _compute(self, observable, box, pos, ids, mol, rad, bond, bond_type):
        # TODO: check molecular specie layout is F
        self._initialize(observable, pos, ids)
        # Compatibility with C species layout
        # Important: this makes a local copy of ids every time
        if self._species_layout == 'C':
            ids = ids + 1
        # We set the variables to zero for the first interaction,
        # then we cumulate the terms by setting zero to False.
        zero = True
        for uid in self._uid:
            # Load appropriate module according to polydispersity
            assert not self._polydisperse
            _interaction = f2py_jit.import_module(uid)
            f90 = _interaction.interaction_intramolecular
            # Compute the interaction cumulating terms
            if observable in ['forces', 'energy', None]:
                # TODO: do it before!
                bond = numpy.array(bond).T + 1
                # TODO: 1+mol before
                f90.forces_bond(zero, box, pos, ids, 1+mol, rad, bond, bond_type,
                                self.forces, self.energy, self.virial)
            # TODO: not ready yet
            # elif observable == 'energies':
            #     f90.energies(zero, box, pos, ids, rad, self.energies)
            # elif observable == 'gradw':
            #     assert len(self._uid) == 1, 'cannot compute gradw with multiple potentials'
            #     f90.gradw(zero, box, pos, ids, rad, self.gradw)
            # elif observable == 'hessian':
            #     f90.hessian(zero, box, pos, ids, rad, self.hessian)
            zero = False

        if observable in ['forces', 'energy', None]:
            self.energy, self.virial = float(self.energy), float(self.virial)

class InteractionIntermolecular(Interaction):

    """
    A fortran 90 backend to compute intermolecular interactions.
    """

    def __init__(self, model, neighbor_list=None,
                 inline=True, inline_safe=False, debug=False,
                 parallel=False, search_dir=None, dimensions=None):
        """
        Similar to the basic Interaction constructor
        """
        super().__init__(model, interaction='interaction_intermolecular.f90')
        self.variables = {'box': 'cell.side',
                          'pos': 'particle.position',
                          'ids': 'particle.species:int32',
                          'mol': 'topology.molecule_index',
                          'rad': 'particle.radius'}

    def _setup_f90(self, model, helpers, interaction, inline=True,
                   inline_safe=False, debug=False, parallel=False,
                   search_dir=None):
        import copy
        from atooms.backends.f90.helpers import _merge_source, _normalize_path
        # Make a local copy
        model = copy.deepcopy(model)
        # TOOO: We were supposed to have a list of potentials and
        # cutoffs, support both a single dict and list of dicts
        for entry in [model["potential"]]:
            _normalize_model_entry(entry, search_dir, 'twobody')
        for entry in [model["cutoff"]]:
            _normalize_model_entry(entry, search_dir, 'cutoff')
        _potential = model['potential']
        potential = _potential.get('path')
        potential = _normalize_path(potential)
        potential_parameters = _potential.get('parameters')
        _cutoff = model['cutoff']
        cutoff = _cutoff.get('path')
        cutoff = _normalize_path(cutoff)
        cutoff_parameters = _cutoff.get('parameters')        
        source = _merge_source(helpers, potential, cutoff, interaction)
        if inline:
            source = f2py_jit.finline.inline_source(source, ignore='adjust,forces')
        extra_args = _setup_extra_args(debug, parallel)
        uid = f2py_jit.build_module(source,
                                    metadata={"interaction": interaction,
                                              "helpers": helpers,
                                              "parallel": parallel,
                                              "potential": [potential, potential_parameters],
                                              "cutoff": [cutoff, cutoff_parameters]},
                                    extra_args=extra_args)
        mod = f2py_jit.import_module(uid)
        mod.potential.init(**potential_parameters)
        mod.cutoff.init(**cutoff_parameters)
        self._uid = [uid]

    def compute(self, observable, box, pos, ids, rad, mol):
        """
        Compute `observable` from this interaction
        """
        # Check if system is polydisperse (cached)
        if self._polydisperse is None:
            self._polydisperse = _check_polydisperse(ids, rad)
        self._compute(observable, box, pos, ids, rad, mol)

    def _compute(self, observable, box, pos, ids, rad, mol):
        self._initialize(observable, pos, ids)
        # Compatibility with C species layout
        # Important: this makes a local copy of ids every time
        if self._species_layout == 'C':
            ids = ids + 1
        # We set the variables to zero for the first interaction,
        # then we cumulate the terms by setting zero to False.
        zero = True
        for uid in self._uid:
            # Load appropriate module according to polydispersity
            assert not self._polydisperse
            _interaction = f2py_jit.import_module(uid)
            f90 = _interaction.interaction_intermolecular
            # Compute the interaction cumulating terms
            if observable in ['forces', 'energy', None]:
                # TODO: 1+mol do it before...
                # assert ids.shape[0] == pos.shape[1]
                f90.forces(zero, box, pos, ids, rad, 1+mol, self.forces, self.energy, self.virial)
            # TODO: not ready yet
            # elif observable == 'energies':
            #     f90.energies(zero, box, pos, ids, rad, self.energies)
            # elif observable == 'gradw':
            #     assert len(self._uid) == 1, 'cannot compute gradw with multiple potentials'
            #     f90.gradw(zero, box, pos, ids, rad, self.gradw)
            # elif observable == 'hessian':
            #     f90.hessian(zero, box, pos, ids, rad, self.hessian)
            zero = False

        if observable in ['forces', 'energy', None]:
            self.energy, self.virial = float(self.energy), float(self.virial)

class InteractionMolecular(atooms.system.interaction.Interaction):

    """
    A fortran 90 backend to compute molecular interactions, including
    both intra- and inter-molecular terms.
    """

    def __init__(self, model, neighbor_list=None,
                 inline=True, inline_safe=False, debug=False,
                 parallel=False, search_dir=None, dimensions=None):
        """
        Similar to the basic Interaction constructor

        Example
        -------

        Setup a molecular forcefield with both intramolecular and
        intermolecular terms

        .. code-block:: python

           model = {
            'bond': {'type': 'harmonic',
                     'parameters': {'epsilon': [[1.0]], 'sigma': [[1.0]]}},
            'angle': {'type': 'harmonic',
                      'parameters': {'epsilon': [[1.0]], 'sigma': [[1.0]]}},
            'potential': [{'type': 'lennard_jones',
                           'parameters': {'epsilon': [[1.0]], 'sigma': [[1.0]]}}],
            'cutoff': [{'type': 'cut',
                        'parameters': {'rcut': [[2.5]]}}]
           }
           interaction = InteractionMolecular(model)
        """
        from atooms.system import Interaction

        # Unpack model dictionary
        model_intra, model_inter = {}, {}
        for key, value in model.items():
            if key in ['bond', 'angle', 'dihedral', 'improper']:
                model_intra[key] = value
            if key in ['potential', 'cutoff']:
                model_inter[key] = value

        # Setup interaction terms
        intra = InteractionIntramolecular(model_intra, inline=inline,
                                          inline_safe=inline_safe,
                                          debug=debug, parallel=parallel,
                                          search_dir=search_dir, dimensions=dimensions)                                          
        inter = InteractionIntermolecular(model_inter,
                                          neighbor_list=neighbor_list, inline=inline,
                                          inline_safe=inline_safe, debug=debug,
                                          parallel=parallel, search_dir=search_dir,
                                          dimensions=dimensions)
        super().__init__(intra, inter)
           
