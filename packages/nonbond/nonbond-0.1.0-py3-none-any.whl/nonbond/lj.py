
import torch

device = "cpu"
dtype = torch.float64

class LJCalculator:
    def __init__(self, 
                 cutoff: float = 10.0,
                 ):
        self.cutoff = cutoff

    def get_lj_energy(self, neighbor_indices, neighbor_distances, epsilon, sigma):

        if neighbor_indices.numel() == 0:
            return 0.0

        sigma_t = torch.as_tensor(sigma, device=device, dtype=dtype)
        eps_t = torch.as_tensor(epsilon, device=device, dtype=dtype)

        i_idx = neighbor_indices[:, 0].to(device=device)
        j_idx = neighbor_indices[:, 1].to(device=device)
        r = neighbor_distances.to(device=device, dtype=dtype)

        sigma_ij = 0.5 * (sigma_t[i_idx] + sigma_t[j_idx])           
        epsilon_ij = torch.sqrt(eps_t[i_idx] * eps_t[j_idx])         

        # (sigma/r)^n 
        inv_r = sigma_ij / r          # (sigma_ij / r)
        inv_r2 = inv_r * inv_r
        inv_r6 = inv_r2 * inv_r2 * inv_r2
        inv_r12 = inv_r6 * inv_r6

        pair_energy = 4.0 * epsilon_ij * (inv_r12 - inv_r6)  # (n_pairs,)
        energies = pair_energy
        energy = pair_energy.sum().item()

        return energy, energies
