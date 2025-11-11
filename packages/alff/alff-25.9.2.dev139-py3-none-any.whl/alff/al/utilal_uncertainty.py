"""DO NOT import any `alff` libs in this file, since this file will be used remotely."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ase import Atoms
    from ase.calculators.calculator import Calculator

from copy import deepcopy
from pathlib import Path

import numpy as np
from ase.io import read, write
from rich.progress import track


#####ANCHOR Uncertainty estimation
def _assign_calc(struct: Atoms, calc: object) -> Atoms:
    """helper to assign calculator to an Atoms object. Why need this?
    - Avoids modifying the original Atoms object.
    - Avoids return 'NoneType' when directly call '.set_calculator(calc)' in list comprehension.
    """
    struct_copy = deepcopy(struct)
    struct_copy.calc = calc
    return struct_copy


def committee_err_energy(
    struct: Atoms,
    calc_list: list[Calculator],
) -> float:
    """Committee error for energy on a single configuration

    Args:
        struct (Atoms): Atoms object
        calc_list (list[Calculator]): list of ASE's calculators of ML models in the committee.

    Returns:
        e_std (float): standard deviation of the energy
    """
    energies = [_assign_calc(struct, calc).get_potential_energy() for calc in calc_list]
    e_std = np.std(energies)  # shape: (n_models,) --> (1,)
    return e_std


def committee_err_force(
    struct: Atoms,
    calc_list: list[Calculator],
    rel_force: float = None,
) -> tuple[float, float, float]:
    """Committee error for forces on a single configuration

    Args:
        struct (Atoms): Atoms object
        calc_list (list[Calculator]): list of ASE's calculators of ML models in the committee.
        rel_force (float, optional): relative force. Defaults to None.

    Returns:
        f_std_mean (float): mean of the standard deviation of atomic forces in the configuration
        f_std_max (float): maximum of the standard deviation
        f_std_min (float): minimum of the standard deviation
    """
    # Collect all forces into a NumPy array: shape (n_models, n_atoms, 3)
    forces = np.array([_assign_calc(struct, calc).get_forces() for calc in calc_list])

    # Standard deviation per force component across models
    component_f_std = np.std(forces, axis=0)  # (n_atoms, 3)

    # Norm per atom
    f_std = np.linalg.norm(component_f_std, axis=1)  # (n_atoms,)

    if rel_force:
        mean_forces = np.mean(forces, axis=0)  # (n_atoms, 3), mean of forces across models
        f_std /= np.linalg.norm(mean_forces, axis=1) + rel_force

    f_std_mean, f_std_max, f_std_min = np.mean(f_std), np.max(f_std), np.min(f_std)
    return f_std_mean, f_std_max, f_std_min


def committee_err_stress(
    struct: Atoms,
    calc_list: list[Calculator],
    rel_stress: float = None,
) -> tuple[float, float, float]:
    """Committee error for stress on a single configuration

    Args:
        struct (Atoms): Atoms object
        calc_list (list[Calculator]): list of ASE's calculators of ML models in the committee.
        rel_stress (float, optional): relative stress. Defaults to None.

    Returns:
        s_std_mean (float): mean of the standard deviation of the stress in the configuration
        s_std_max (float): maximum of the standard deviation
        s_std_min (float): minimum of the standard deviation
    """
    ## Collect stress: shape (n_models, n_stress_components)
    stresses = np.array([_assign_calc(struct, calc).get_stress() for calc in calc_list])

    s_std = np.std(stresses, axis=0)  # (n_stress_components,)

    if rel_stress:
        s_std /= np.mean(stresses, axis=0) + rel_stress

    s_std_mean, s_std_max, s_std_min = np.mean(s_std), np.max(s_std), np.min(s_std)
    return s_std_mean, s_std_max, s_std_min


def committee_error(
    extxyz_file: str,
    calc_list: list[Calculator],
    rel_force: float = None,
    compute_stress: bool = True,
    rel_stress: float = None,
    outfile: str = "committee_error.txt",
):
    """Calculate committee error for energy, forces and stress for a list of configurations

    Args:
        extxyz_file (str): extended xyz file containing multiples configurations
        calc_list (list[Calculator]): list of ASE's calculators of ML models
        rel_force (float, optional): relative force. Defaults to None.
        compute_stress (bool, optional): whether to compute stress. Defaults to True.
        rel_stress (float, optional): relative stress. Defaults to None.
        outfile (str, optional): output file. Defaults to "committee_error.txt".

    Returns:
        outfile (str): "committee_error.txt" with the following columns: "e_std f_std_mean f_std_max f_std_min s_std_mean s_std_max s_std_min"
    """
    assert len(calc_list) > 0, "No calculators found"

    struct_list = read(extxyz_file, format="extxyz", index=":")

    ### compute committee error
    def _compute_committee_1struct(struct, calc_list, rel_force, compute_stress, rel_stress):
        e_std = committee_err_energy(struct, calc_list)
        f_std_mean, f_std_max, f_std_min = committee_err_force(struct, calc_list, rel_force)
        if compute_stress:
            s_std_mean, s_std_max, s_std_min = committee_err_stress(struct, calc_list, rel_stress)
            return [e_std, f_std_mean, f_std_max, f_std_min, s_std_mean, s_std_max, s_std_min]
        else:
            return [e_std, f_std_mean, f_std_max, f_std_min]

    comm_std = [
        _compute_committee_1struct(struct, calc_list, rel_force, compute_stress, rel_stress)
        for struct in track(struct_list, refresh_per_second=0.1)
    ]

    ### write output
    header = "e_std f_std_mean f_std_max f_std_min" + (
        " s_std_mean s_std_max s_std_min" if compute_stress else ""
    )
    np.savetxt(outfile, np.array(comm_std), fmt="%.6f", header=header, comments="")
    return


def committee_judge(
    committee_error_file: str,
    e_std_hi: float = 0.1,
    e_std_lo: float = 0.0,
    f_std_hi: float = 0.1,
    f_std_lo: float = 0.0,
    s_std_hi: float = None,
    s_std_lo: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Decide whether an configuration is candidate, accurate, or inaccurate based on committee error

    Args:
        committee_error_file (str): committee error file
        e_std_hi (float, optional): energy std high. Defaults to 0.1.
        e_std_lo (float, optional): energy std low. Defaults to 0.05.
        f_std_hi (float, optional): force std high. Defaults to 0.1.
        f_std_lo (float, optional): force std low. Defaults to 0.05.
        s_std_hi (float, optional): stress std high. Defaults to 0.1.
        s_std_lo (float, optional): stress std low. Defaults to 0.05.

    Returns:
        committee_error_file(s): files contain candidate, accurate and inaccurate configurations

    Note:
        - If need to select candidates based on only `energy`, just set `f_std_lo` and `s_std_lo` to a very large values. By this way, the criterion for those terms will never meet.
        - Similarly, if need to select candidates based on only `energy` and `force`, set `s_std_lo` to a very large value. E.g., `s_std_lo=1e6` for selecting candidates based on energy and force.
    """
    comm_arr = np.loadtxt(committee_error_file, skiprows=1, ndmin=2)

    ### Indexing candidate, accurate, inaccurate structures
    if s_std_hi:  # with stress
        e_std, f_std_max, s_std_max = comm_arr[:, 0], comm_arr[:, 2], comm_arr[:, 5]
        accurate_mask = (e_std < e_std_lo) & (f_std_max < f_std_lo) & (s_std_max < s_std_lo)
        inaccurate_mask = (e_std > e_std_hi) | (f_std_max > f_std_hi) | (s_std_max > s_std_hi)
        comm_arr_reduce = np.hstack((e_std[:, None], f_std_max[:, None], s_std_max[:, None]))
    else:  # no stress
        e_std, f_std_max = comm_arr[:, 0], comm_arr[:, 2]
        accurate_mask = (e_std < e_std_lo) & (f_std_max < f_std_lo)
        inaccurate_mask = (e_std > e_std_hi) | (f_std_max > f_std_hi)
        comm_arr_reduce = np.hstack((e_std[:, None], f_std_max[:, None]))

    candidate_mask = ~(inaccurate_mask | accurate_mask)

    candidate_idx = np.where(candidate_mask)[0]
    accurate_idx = np.where(accurate_mask)[0]
    inaccurate_idx = np.where(inaccurate_mask)[0]

    ### Write outputs
    def save_group(suffix: str, idx: np.ndarray):
        if len(idx) > 0:
            data = np.hstack((idx[:, None], comm_arr_reduce[idx]))
            header = "idx e_std f_std_max" + (" s_std_max" if s_std_hi else "")
            fmt_str = "%d " + "%.6f " * (data.shape[1] - 1)
            filename = f"committee_judge_{suffix}.txt"
            np.savetxt(filename, data, fmt=fmt_str, header=header, comments="")
        return

    save_group("candidate", candidate_idx)
    save_group("accurate", accurate_idx)
    save_group("inaccurate", inaccurate_idx)

    with open("committee_judge_summary.txt", "w") as f:
        f.write(f"total_frames: {comm_arr.shape[0]}\n")
        f.write(f"candidates: {len(candidate_idx)}\n")
        f.write(f"accurates: {len(accurate_idx)}\n")
        f.write(f"inaccurates: {len(inaccurate_idx)}\n")
        f.write("criteria:\n")
        f.write(f"  e_std_lo: {e_std_lo}\n  e_std_hi: {e_std_hi}\n")
        f.write(f"  f_std_lo: {f_std_lo}\n  f_std_hi: {f_std_hi}\n")
        f.write(f"  s_std_lo: {s_std_lo}\n  s_std_hi: {s_std_hi}\n")
    return candidate_idx, accurate_idx, inaccurate_idx


#####ANCHOR Select configurations
def select_candidate(
    extxyz_file: str,
    calc_list: list[Calculator],
    rel_force: float = None,
    compute_stress: bool = True,
    rel_stress: float = None,
    e_std_hi: float = 0.1,
    e_std_lo: float = 0.0,
    f_std_hi: float = 0.1,
    f_std_lo: float = 0.0,
    s_std_hi: float = None,
    s_std_lo: float = 0.0,
):
    """Select candidate configurations for DFT calculation

    Returns:
        extxyz_file (str): candidate configurations

    Note: See parameters in functions `committee_error` and `committee_judge`.
    """
    committee_error(
        extxyz_file=extxyz_file,
        calc_list=calc_list,
        rel_force=rel_force,
        compute_stress=compute_stress,
        rel_stress=rel_stress,
        outfile="committee_error.txt",
    )

    candidate_idx, accurate_idx, inaccurate_idx = committee_judge(
        committee_error_file="committee_error.txt",
        e_std_hi=e_std_hi,
        e_std_lo=e_std_lo,
        f_std_hi=f_std_hi,
        f_std_lo=f_std_lo,
        s_std_hi=s_std_hi,
        s_std_lo=s_std_lo,
    )

    ### Select candidates from the extxyz file
    if len(candidate_idx) > 0:
        struct_list = read(extxyz_file, format="extxyz", index=":")
        selected_structs = [struct_list[i] for i in candidate_idx]
        filename = f"{Path(extxyz_file).stem}_candidate.extxyz"
        write(filename, selected_structs, format="extxyz")
    return


def remove_inaccurate(
    extxyz_file: str,
    calc_list: list[Calculator],
    rel_force: float = None,
    compute_stress: bool = True,
    rel_stress: float = None,
    e_std_hi: float = 0.1,
    e_std_lo: float = 0.0,
    f_std_hi: float = 0.1,
    f_std_lo: float = 0.0,
    s_std_hi: float = None,
    s_std_lo: float = 0.0,
):
    """Remove inaccurate configurations based on committee error. This is used to revise the dataset.

    Returns:
        extxyz_file (str): revise configurations

    Note: See parameters in functions `committee_error` and `committee_judge`.
    """
    committee_error(
        extxyz_file=extxyz_file,
        calc_list=calc_list,
        rel_force=rel_force,
        compute_stress=compute_stress,
        rel_stress=rel_stress,
        outfile="committee_error.txt",
    )

    candidate_idx, accurate_idx, inaccurate_idx = committee_judge(
        committee_error_file="committee_error.txt",
        e_std_hi=e_std_hi,
        e_std_lo=e_std_lo,
        f_std_hi=f_std_hi,
        f_std_lo=f_std_lo,
        s_std_hi=s_std_hi,
        s_std_lo=s_std_lo,
    )
    select_idx = np.concatenate((candidate_idx, accurate_idx))

    ### Eliminate inaccurate confs from the extxyz file
    struct_list = read(extxyz_file, format="extxyz", index=":")
    if len(select_idx) > 0:
        selected_structs = [struct_list[i] for i in select_idx]
        filename = f"{Path(extxyz_file).stem}_selected.extxyz"
        write(filename, selected_structs, format="extxyz")

    if len(inaccurate_idx) > 0:
        inacc_structs = [struct_list[i] for i in inaccurate_idx]
        filename = f"{Path(extxyz_file).stem}_inaccurate.extxyz"
        write(filename, inacc_structs, format="extxyz")
    return


#####ANCHOR Select configurations based on MLP engine
def select_candidate_SevenNet(
    extxyz_file: str,
    checkpoint_files: list,
    sevenn_args: dict = {},
    rel_force: float = None,
    compute_stress: bool = True,
    rel_stress: float = None,
    e_std_hi: float = 0.1,
    e_std_lo: float = 0.0,
    f_std_hi: float = 0.1,
    f_std_lo: float = 0.0,
    s_std_hi: float = None,
    s_std_lo: float = 0.0,
):
    """Select candidate configurations for DFT calculation using SevenNet models.

    Args:
        extxyz_file (str): extended xyz file containing multiples configurations
        checkpoint_files (list): list of checkpoint_files files SevenNet models
        sevenn_args (dict, optional): arguments for SevenNetCalculator. Defaults to {}.

    Returns:
        extxyz_file (str): candidate configurations
    """
    from sevenn.sevennet_calculator import SevenNetCalculator

    assert len(checkpoint_files) > 0, "No checkpoint files found"

    calc_list = [SevenNetCalculator(model_file, **sevenn_args) for model_file in checkpoint_files]
    select_candidate(
        extxyz_file=extxyz_file,
        calc_list=calc_list,
        rel_force=rel_force,
        compute_stress=compute_stress,
        rel_stress=rel_stress,
        e_std_hi=e_std_hi,
        e_std_lo=e_std_lo,
        f_std_hi=f_std_hi,
        f_std_lo=f_std_lo,
        s_std_hi=s_std_hi,
        s_std_lo=s_std_lo,
    )
    return


def remove_inaccurate_SevenNet(
    extxyz_file: str,
    checkpoint_files: list,
    sevenn_args: dict = {},
    rel_force: float = None,
    compute_stress: bool = True,
    rel_stress: float = None,
    e_std_hi: float = 0.1,
    e_std_lo: float = 0.0,
    f_std_hi: float = 0.1,
    f_std_lo: float = 0.0,
    s_std_hi: float = None,
    s_std_lo: float = 0.0,
):
    """Remove inaccurate configurations based on committee error, using SevenNet models.

    Args:
        extxyz_file (str): extended xyz file containing multiples configurations
        checkpoint_files (list): list of checkpoint_files files SevenNet models
        sevenn_args (dict, optional): arguments for SevenNetCalculator. Defaults to {}.

    Returns:
        extxyz_file (str): revised configurations
    """
    from sevenn.sevennet_calculator import SevenNetCalculator

    assert len(checkpoint_files) > 0, "No checkpoint files found"

    calc_list = [SevenNetCalculator(model_file, **sevenn_args) for model_file in checkpoint_files]
    remove_inaccurate(
        extxyz_file=extxyz_file,
        calc_list=calc_list,
        rel_force=rel_force,
        compute_stress=compute_stress,
        rel_stress=rel_stress,
        e_std_hi=e_std_hi,
        e_std_lo=e_std_lo,
        f_std_hi=f_std_hi,
        f_std_lo=f_std_lo,
        s_std_hi=s_std_hi,
        s_std_lo=s_std_lo,
    )
    return


#####ANCHOR convert format
def simple_lmpdump2extxyz(
    lmpdump_file: str,
    extxyz_file: str,
):
    """Convert LAMMPS dump file to extended xyz file. This is very simple version, only convert atomic positions, but not stress tensor."""
    struct_list = read(lmpdump_file, format="lammps-dump-text", index=":")
    write(extxyz_file, struct_list, format="extxyz")
    return
