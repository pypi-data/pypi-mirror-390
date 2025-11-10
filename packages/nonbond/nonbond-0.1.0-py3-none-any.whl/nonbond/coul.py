from torchpme.tuning import tune_ewald, tune_pme, tune_p3m
import torchpme
import torch
from torchpme.prefactors import eV_A

class CoulombCalculator:
    """
    Coulomb Calculator
    """
    
    def __init__(self, 
                 method: str = 'direct',
                 cutoff: float = 10.0,
                 accuracy: float = 1e-5,
                 device: str = 'cpu',
                 dtype: torch.dtype = torch.float64,
                 ):

        self.method = method.lower()
        self.cutoff = cutoff
        self.accuracy = accuracy
        self.device = device
        self.dtype = dtype

        # 验证方法
        valid_methods = ['direct', 'ewald', 'pme', 'p3m']
        if self.method not in valid_methods:
            raise ValueError(f"Unsupported method: {method}. Valid methods: {valid_methods}")

        # 通用参数
        self.neighbor_indices, self.neighbor_distances = None, None
        self.positions = None
        self.cell = None
        self.charges = None
        
        #结果
        self.energy = None
        self.energies = None
        # self.forces = None
    
    def get_coul_energy(self, 
                        neighbor_indices: torch.Tensor, 
                        neighbor_distances: torch.Tensor,
                        positions: torch.Tensor,
                        cell: torch.Tensor,
                        charges: torch.Tensor,
                        ) -> float:
    
        self.positions = positions
        self.cell = cell
        self.charges = charges

        self.neighbor_indices, self.neighbor_distances = neighbor_indices, neighbor_distances
        
        if self.method == 'direct':
            self._direct_coulomb()
        else:
            self._long_range_coulomb()
           
        return self.energy, self.energies
    


    def _optimize_params(self):
        neighbor_indices, neighbor_distances = self.neighbor_indices, self.neighbor_distances
        if self.method == 'ewald':
            return tune_ewald(
                charges=self.charges,
                cell=self.cell,
                positions=self.positions,
                cutoff=self.cutoff,
                accuracy=self.accuracy,
                neighbor_indices=neighbor_indices,
                neighbor_distances=neighbor_distances,
            )
        elif self.method == 'pme':
            return tune_pme(
                charges=self.charges,
                cell=self.cell,
                positions=self.positions,
                cutoff=self.cutoff,
                accuracy=self.accuracy,
                neighbor_indices=neighbor_indices,
                neighbor_distances=neighbor_distances,
            )
        elif self.method == 'p3m':
            return tune_p3m(
                charges=self.charges,
                cell=self.cell,
                positions=self.positions,
                cutoff=self.cutoff,
                accuracy=self.accuracy,
                neighbor_indices=neighbor_indices,
                neighbor_distances=neighbor_distances,
            )
        else:
            raise RuntimeError("_optimize_params called for unsupported method")

    
    
    def _long_range_coulomb(self) -> float:
        """长程库伦相互作用计算 (带缓存)"""
        smearing, params, _ = self._optimize_params()
        prefactor = eV_A
        if self.method == 'ewald':
            base_calc = torchpme.EwaldCalculator(
                potential=torchpme.CoulombPotential(smearing),
                **params,
                prefactor=prefactor
            )
        elif self.method == 'pme':
            base_calc = torchpme.PMECalculator(
                potential=torchpme.CoulombPotential(smearing),
                **params,
                prefactor=prefactor
            )
        elif self.method == 'p3m':
            base_calc = torchpme.P3MCalculator(
                potential=torchpme.CoulombPotential(smearing),
                **params,
                prefactor=prefactor
            )
        else:
            raise RuntimeError("Unsupported method for long range")

        calculator = base_calc
        neighbor_indices, neighbor_distances = self.neighbor_indices, self.neighbor_distances
        calculator.to(device=self.device, dtype=self.dtype)
        potentials = calculator.forward(
            self.charges, self.cell, self.positions, neighbor_indices, neighbor_distances
        )
        energies = self.charges * potentials
        energy = torch.sum(energies)
        # energy.backward()
        # forces = -self.positions.grad
        
        self.energy = energy.item()
        self.energies = energies
        # self.forces = forces
    
    def _direct_coulomb(self):
        COULOMB_CONSTANT = 14.399644853  # eV·Å/e²
        neighbor_indices, neighbor_distances = self.neighbor_indices, self.neighbor_distances
        qi = self.charges[neighbor_indices[:, 0]].flatten()
        qj = self.charges[neighbor_indices[:, 1]].flatten()
        rij = neighbor_distances.flatten()
        # 避免除零
        mask = rij > 1e-12
        if not torch.all(mask):
            qi = qi[mask]; qj = qj[mask]; rij = rij[mask]
        energies = (COULOMB_CONSTANT * qi * qj / rij)
        energy = energies.sum().item()
        
        self.energy = energy
        self.energies = energies
    
