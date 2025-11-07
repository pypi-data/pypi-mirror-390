# Robust multi-image displacement for periodic cells (orthorhombic or triclinic).
# This implements the exact nearest-image selection by enumerating integer
# lattice shifts s ∈ ℤ^d within a bounded window and minimizing the real-space
# distance || B (du + s) ||, where:
#
#   - B ∈ ℝ^{d×d} is the box (fractional → real) transform (the `box` argument),
#   - du = ua - ub is the fractional displacement (ua, ub are positions in fractional coords),
#   - The nearest image solves the Closest Vector Problem (CVP):  s* = argmin_s ||B(du + s)||.
#
# Bounding the enumeration window (general triclinic case):
#   The set { y ∈ ℝ^d : || B y || ≤ r_c } is an ellipsoid E with metric S = BᵀB.
#   An axis-aligned bounding box in fractional space has half-widths:
#
#       h_i = r_c * sqrt( ((Bᵀ B)⁻¹)_{ii} ),   for i=1..d.
#
#   Choosing per-axis integer radii r_i ≥ ceil(h_i) guarantees all images within
#   the cutoff r_c are enumerated. A scalar safe bound uses the smallest singular
#   value σ_min(B):
#
#       ||B y|| ≥ σ_min(B) ||y||   ⇒   ||y|| ≤ r_c / σ_min(B)
#
#   so radius ≥ ceil(r_c / σ_min(B)) is also safe (often looser).
#
# Notes:
#   - For fractional_coordinates=True: inputs R are already fractional in [0,1)^d and B = box.
#   - For fractional_coordinates=False: inputs are real; we map to fractional via B⁻¹,
#     enumerate in fractional space, then map back to real.
#   - Enumeration size is static (depends on `radii` or `radius` and dimension), which is
#     JIT-friendly. If the box deforms, pick radii that are safe for the worst-case box.
#
# Usage:
#   disp, shift = periodic_general_multi_image(
#       box, r_cutoff=rc, fractional_coordinates=False, use_per_axis=True)
#
#   # or pre-supply static radii (no runtime SVD/inverse, best for JIT stability):
#   disp, shift = periodic_general_multi_image(
#       box, radii=(rx, ry, rz), fractional_coordinates=False)
#
import jax
import jax.numpy as jnp
import jraph
import numpy as np
from ase import Atoms
from ase.build import make_supercell
from jax_md import partition, space
from nequix.calculator import NequixCalculator
from nequix.data import atomic_numbers_to_indices
from nequix.model import node_graph_idx
from jax import grad
from jax_md.quantity import stress

# multi_image_space.py

from typing import Optional, Sequence, Tuple
from jax import vmap
import jax.numpy as jnp
from jax_md.space import (
  transform,
  inverse,
  periodic_shift,
  pairwise_displacement,
  raw_transform,
)


def periodic_general_multi_image_jax(
  box,
  *,
  radii: Sequence[int],
  fractional_coordinates: bool = True,
  wrapped: bool = True,
):
  # B maps fractional -> real; slice to probed dimension so dim-1/2 probes pass canonicalization.
  def _B(dim):
    B = jnp.asarray(box)
    if B.ndim == 0:
      return jnp.eye(dim, dtype=B.dtype) * B
    if B.ndim == 1:
      return jnp.diag(B[:dim])
    return B[:dim, :dim]

  def _build_shifts(rad):
    ranges = [jnp.arange(-ri, ri + 1, dtype=jnp.int32) for ri in rad]
    grids = jnp.meshgrid(*ranges, indexing='ij')
    return jnp.stack([g.reshape(-1) for g in grids], axis=-1)

  def displacement_fn(Ra, Rb, perturbation=None, **kwargs):
    dim = int(Ra.shape[-1])
    B = _B(dim)
    iB = inverse(B)
    ua = Ra if fractional_coordinates else transform(iB, Ra)
    ub = Rb if fractional_coordinates else transform(iB, Rb)
    du = pairwise_displacement(ua, ub)
    # Use per-dim static radii (truncate/extend as needed).
    base = tuple(int(r) for r in radii)
    rad = (
      base[:dim] if len(base) >= dim else base + (base[-1],) * (dim - len(base))
    )
    shifts = _build_shifts(rad).astype(du.dtype)
    dR_all = vmap(lambda s: transform(B, du + s))(shifts)
    idx = jnp.argmin(jnp.sum(dR_all * dR_all, axis=-1))
    dR = dR_all[idx]
    if perturbation is not None:
      dR = raw_transform(perturbation, dR)
    return dR

  def shift_fn(R, dR, **kwargs):
    if not wrapped:
      return R + dR
    dim = int(R.shape[-1])
    B = _B(dim)
    iB = inverse(B)
    dR_f = transform(iB, dR)
    if fractional_coordinates:
      return periodic_shift(1.0, R, dR_f)
    R_f = transform(iB, R)
    return transform(B, periodic_shift(1.0, R_f, dR_f))

  return displacement_fn, shift_fn


def radii_from_box_cutoff(
  box, r_cutoff, *, per_axis=True, safety=0.0, dim_default=3
):
  # Normalize box to matrix B (fractional → real)
  B = jnp.asarray(box)
  if B.ndim == 0:
    B = jnp.eye(dim_default, dtype=B.dtype) * B
  elif B.ndim == 1:
    B = jnp.diag(B)
  # else: already (d, d)

  rc = float(r_cutoff) * (1.0 + float(safety))
  if per_axis:
    S = B.T @ B
    invS = jnp.linalg.inv(S)
    h = rc * jnp.sqrt(jnp.clip(jnp.diag(invS), 0.0, jnp.inf))
    r = jnp.ceil(h + 0.5).astype(jnp.int32)
    return tuple(int(x) for x in r)  # (rx, ry, rz)
  svals = jnp.linalg.svd(B, compute_uv=False)
  r = jnp.ceil(rc / svals[-1] + 0.5).astype(jnp.int32)
  return tuple([int(r)] * B.shape[0])  # (r, r, r)


# Same as nequip
def neighbor_list_featurizer(displacement_fn):
  def featurize(species, positions, neighbor):
    graph = partition.to_jraph(
      neighbor, nodes={'species': species, 'positions': positions}
    )
    mask = partition.neighbor_list_mask(neighbor, True)
    Rb = graph.nodes['positions'][graph.senders]
    Ra = graph.nodes['positions'][graph.receivers]
    d = jax.vmap(displacement_fn)
    dR = d(Ra, Rb)
    dR = jnp.where(
      mask[:, None], dR, 1.0
    )  # set masked edges to displacement of 1
    return graph._replace(edges=dR)

  return featurize


def nequix_neighborlist(displacement_fn, box, model):
  neighbor_fn = partition.neighbor_list(
    displacement_fn,
    box,
    model.cutoff,
    format=partition.Sparse,
    fractional_coordinates=True,
    disable_cell_list=True,
  )
  featurizer = neighbor_list_featurizer(displacement_fn)

  # if np.any(np.diag(box) < model.cutoff * 2):
  #     raise ValueError(
  #         f"each dimension of the cell {np.diag(box)} must be at least twice the long-range cutoff distance ({model.cutoff} Å)."
  #     )

  def energy_fn(positions, neighbor, species):
    graph = featurizer(species, positions, neighbor)
    node_energies = model.node_energies(
      graph.edges, graph.nodes['species'], graph.senders, graph.receivers
    )
    # compute total energies across each subgraph
    graph_energies = jraph.segment_sum(
      node_energies,
      node_graph_idx(graph),
      num_segments=graph.n_node.shape[0],
      indices_are_sorted=True,
    )
    return graph_energies[0, 0]

  return neighbor_fn, energy_fn


if __name__ == '__main__':
  atoms = Atoms(
    symbols=['Si'] * 8,
    cell=[
      [5.467220385087693, 0.0, 0.0],
      [0.0, 5.467220385087693, 0.0],
      [0.0, 0.0, 5.467220385087693],
    ],
    scaled_positions=[
      [0.0, 0.0, 0.5],
      [0.75, 0.75, 0.75],
      [0.0, 0.5, 0.0],
      [0.75, 0.25, 0.25],
      [0.5, 0.0, 0.0],
      [0.25, 0.75, 0.25],
      [0.5, 0.5, 0.5],
      [0.25, 0.25, 0.75],
    ],
    pbc=True,
  )
  calc = NequixCalculator('nequix-mp-1')

  model, config = calc.model, calc.config
  atoms = make_supercell(atoms, np.eye(3) * 1)
  cell = atoms.cell.astype(np.float32)
  atoms.calc = calc
  E_ase = atoms.get_potential_energy()
  print('ASE calc eV/atom', E_ase / len(atoms))

  # displacement_fn, _ = space.periodic_general(cell.T, fractional_coordinates=True)
  radii = radii_from_box_cutoff(
    cell.T, r_cutoff=model.cutoff, per_axis=True, safety=0.5
  )
  displacement_fn, _ = periodic_general_multi_image_jax(
    cell.T, fractional_coordinates=True, radii=radii
  )
  print('radii', radii)
  neighbor_fn, energy_fn = nequix_neighborlist(displacement_fn, cell, model)

  atom_indices = atomic_numbers_to_indices(config['atomic_numbers'])
  species = np.array(
    [atom_indices[n] for n in atoms.get_atomic_numbers()]
  ).astype(np.int32)
  positions = atoms.get_scaled_positions().astype(np.float32)
  nbrs = neighbor_fn.allocate(positions)
  E_jax = energy_fn(positions, nbrs, species)
  print('jax-md eV/atom', E_jax / len(atoms))

F_ase = atoms.get_forces()
F_jax = -grad(energy_fn, argnums=0)(positions, nbrs, species)
print(np.allclose(E_ase, E_jax, atol=1e-5))
print(np.allclose(F_ase, F_jax, atol=1e-5))
print(F_ase)
print(F_jax)
