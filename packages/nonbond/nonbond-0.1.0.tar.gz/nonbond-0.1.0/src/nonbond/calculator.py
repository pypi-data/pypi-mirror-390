import numpy as np
from ase.calculators.calculator import Calculator, all_changes
from ase.units import mol, kcal, eV

import torch
from vesin.torch import NeighborList

from .lj import LJCalculator
from .coul import CoulombCalculator

# Coulomb constant in eV*Å/e²
COULOMB_CONSTANT = 14.399644853


class Nonbond(Calculator):
    """
    ASE Calculator for Lennard-Jones + Coulomb interactions

    The total potential energy is:
    E_total = E_LJ + E_coulomb

    Where:
    E_LJ = sum_i<j 4*epsilon_ij * [(sigma_ij/r_ij)^12 - (sigma_ij/r_ij)^6]
    E_coulomb = sum_i<j k * q_i * q_j / r_ij

    Mixing rules (Lorentz-Berthelot):
    epsilon_ij = sqrt(epsilon_i * epsilon_j)
    sigma_ij = (sigma_i + sigma_j) / 2

    Parameters:
    -----------
    sigma : dict
        LJ sigma parameters by atom type (Å)
        Format: {'H': 2.51, 'O': 3.12}

    epsilon : dict  
        LJ epsilon parameters by atom type (kcal/mol)
        Format: {'H': 0.044, 'O': 0.126}

    rc : float, optional
        Cutoff distance for both LJ and Coulomb interactions (Å)
        Default: 3 * max(sigma) or 10.0 Å

    charge_method : str, optional
        Method for Coulomb interaction calculation ('direct', 'ewald', 'pme', 'p3m')
        Default: None

    accuracy : float, optional
        Accuracy for Long-Range Coulomb Interaction
        Default: 1e-5

    device : str, optional
        Device for calculations ('cpu' or 'cuda')
        Default: 'cpu'
    """

    implemented_properties = [
        "energy",
        "energies",
    ]

    def __init__(
        self,
        epsilon: dict,
        sigma: dict,
        rc: float = 10.0,
        charge_method: str = None,
        accuracy: float = 1e-5,
        device: str = 'cpu',
    ):

        kwargs = {
            'epsilon': epsilon,
            'sigma': sigma,
            'rc': rc,
            'charge_method': charge_method,
            'accuracy': accuracy,
            'device': device,
            'dtype': torch.float64,
        }
        Calculator.__init__(self, **kwargs)

        # Initialize neighbor lists
        self.neighbor_indices, self.neighbor_distances = None, None

        # Cache for parameters
        self.atom_types = None
        self.sigmas = None
        self.epsilons = None
        self.charges = None
        self.atoms = None
        self.positions = None
        self.cell = None

    def calculate(self,
                  atoms=None,
                  properties=None,
                  system_changes=all_changes):
        """Calculate energy"""

        if properties is None:
            properties = self.implemented_properties

        Calculator.calculate(self, atoms, properties, system_changes)

        # ro = self.parameters.ro
        # smooth = self.parameters.smooth

        # Get atom types, 用以分配LJ参数

        self.atoms = atoms
        self._update_parameters()

        self._update_neighbor_list()

        energy, energies = self._calculate_energy()

        self.results['energy'] = energy
        self.results['energies'] = energies

    # 构建邻接列表
    def _update_neighbor_list(self):
        nl = NeighborList(cutoff=self.parameters.rc, full_list=False)
        self.neighbor_indices, self.neighbor_distances = nl.compute(
            points=self.positions,
            box=self.cell,
            periodic=True,
            quantities="Pd")

    def _calculate_energy(self):

        energy = 0.0
        energy_lj = 0.0
        energy_coulomb = 0.0

        # Calculate LJ interactions (always calculated)
        lj_calc = LJCalculator(cutoff=self.parameters.rc, )
        energy_lj, energies_lj = lj_calc.get_lj_energy(self.neighbor_indices,
                                                       self.neighbor_distances,
                                                       self.epsilons, self.sigmas)

        # Calculate Coulomb interactions (if charges are provided)
        if self.parameters.charge_method is not None:
            coulomb_calc = CoulombCalculator(
                method=self.parameters.charge_method,
                cutoff=self.parameters.rc,
                accuracy=self.parameters.accuracy,
                device=self.parameters.device,
                dtype=self.parameters.dtype)
            energy_coulomb, energies_coulomb = coulomb_calc.get_coul_energy(
                self.neighbor_indices, self.neighbor_distances, self.positions, self.cell, self.charges)
        else:
            energy_coulomb = 0.0
            energies_coulomb = torch.zeros_like(energies_lj)

        energy = energy_lj + energy_coulomb
        energies = energies_lj + energies_coulomb

        return energy, energies

    def _update_parameters(self):
        """Update cached parameters for current system"""

        # atom types
        try:
            self.atom_types = self.atoms.get_array('type')
        except KeyError:
            self.atom_types = self.atoms.get_chemical_symbols()

        # Convert energy units from kcal/mol to eV
        convert_factor = kcal / mol / eV
        atom_types = self.atom_types
        self.sigmas = np.array(
            [self.parameters.sigma[atom_type] for atom_type in atom_types])
        self.epsilons = np.array([
            self.parameters.epsilon[atom_type] * convert_factor
            for atom_type in atom_types
        ])

        dtype = self.parameters.dtype
        device = self.parameters.device
        self.positions = torch.tensor(self.atoms.positions,
                                      dtype=dtype,
                                      device=device,
                                      requires_grad=True)
        self.cell = torch.tensor(self.atoms.cell.array,
                                 dtype=dtype,
                                 device=device)
        self.charges = torch.tensor(
            self.atoms.get_initial_charges(), dtype=dtype, device=device).unsqueeze(1)
