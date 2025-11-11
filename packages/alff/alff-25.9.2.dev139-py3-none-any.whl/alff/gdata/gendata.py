import shutil
from pathlib import Path

from asext.cell import make_triangular_cell_extxyz
from asext.io.readwrite import read_extxyz, write_extxyz
from asext.struct import (
    perturb_struct,
    strain_struct,
)
from thkit.io import read_yaml, write_yaml
from thkit.path import (
    collect_files,
    copy_file,
    list_paths,
    make_dir,
    make_dir_ask_backup,
)
from thkit.range import composite_strain_points

from alff.base import Workflow, logger
from alff.gdata.libgen_gpaw import (
    OperGendataGpawAIMD,
    OperGendataGpawOptimize,
    # OperGendataGpawSinglepoint,
)
from alff.gdata.util_dataset import merge_extxyz_files, remove_key_in_extxyz
from alff.util.ase_tool import build_struct
from alff.util.key import (
    DIR_GENDATA,
    DIR_MAKE_STRUCT,
    DIR_STRAIN,
    FILE_FRAME_LABEL,
    FILE_ITER_DATA,
    FILE_TRAJ_LABEL,
    FMT_STRUCT,
    SCHEMA_GENDATA,
    FILE_FRAME_unLABEL,
)
from alff.util.tool import mk_struct_dir


#####ANCHOR Stage 1 - build structure
def make_structure(pdict, mdict):
    """
    Build structures based on input parameters
    """
    ### Define work_dir
    struct_startdir = mk_struct_dir(pdict)
    make_dir_ask_backup(struct_startdir)
    work_dir = f"{struct_startdir}/{DIR_MAKE_STRUCT}"

    logger.info(f"Working on the path: {work_dir}")
    write_yaml(pdict, f"{struct_startdir}/param.yml")

    ### Build structures
    struct_args = pdict["structure"]
    from_extxyz = struct_args.get("from_extxyz", False)
    if from_extxyz:
        ### will generate a list of configurations from all frames in all extxyz files)
        logger.info(f"Use structures from extxyz files: {from_extxyz}")
        extxyz_files = collect_files(from_extxyz, patterns=["*.extxyz"])
        merge_extxyz_files(extxyz_files=extxyz_files, outfile=f"{work_dir}/tmp_structs_from_extxyz")
        struct_list = read_extxyz(f"{work_dir}/tmp_structs_from_extxyz", index=":")
        for i, struct in enumerate(struct_list):
            write_extxyz(f"{work_dir}/struct_{i:{FMT_STRUCT}}/{FILE_FRAME_unLABEL}", struct)
        Path(f"{work_dir}/tmp_structs_from_extxyz").unlink()  # clean
    else:
        logger.info("Build structures from scratch")
        struct_args = pdict["structure"].get("from_scratch")
        struct = build_struct(struct_args)
        write_extxyz(f"{work_dir}/struct_{0:{FMT_STRUCT}}/{FILE_FRAME_unLABEL}", struct)

    ### Save structure_dirs (relative to run_dir)
    structure_dirs = list_paths(work_dir, patterns=["struct_*/"])
    write_yaml(structure_dirs, f"{work_dir}/structure_dirs.yml")

    ### Normalize the cell to upper/lower triangular form
    triangular_form = pdict["structure"].get("make_triangular_form", None)
    if triangular_form is not None:
        logger.info(f"Normalize the cell to '{triangular_form}' triangular form")
        for d in structure_dirs:
            extxyz_files = collect_files(d, patterns=[FILE_FRAME_unLABEL, FILE_FRAME_LABEL])
            _ = [
                make_triangular_cell_extxyz(extxyz_file, form=triangular_form)
                for extxyz_file in extxyz_files
            ]
    return


#####ANCHOR Stage 2 - DFT optimize
def optimize_structure(pdict, mdict):
    """
    Optimize the structures
    """
    logger.info("Optimize the structures")
    ### Define work_dir
    struct_startdir = mk_struct_dir(pdict)
    work_dir = f"{struct_startdir}/{DIR_MAKE_STRUCT}"
    _ = copy_file(f"{work_dir}/structure_dirs.yml", f"{work_dir}/task_dirs.yml")
    _ = read_yaml(f"{work_dir}/task_dirs.yml")

    op = OperGendataGpawOptimize(work_dir, pdict, mdict, mdict_prefix="gpaw")
    op.prepare()
    op.run()
    op.postprocess()
    return


#####ANCHOR Stage 3 - scale and perturb
def sampling_space(pdict, mdict):
    """
    Scale and perturb the structures.
    - Save 2 lists of paths: original and scaled structure paths
    """
    ### Define work_dir
    struct_startdir = mk_struct_dir(pdict)
    work_dir = f"{struct_startdir}/{DIR_STRAIN}"
    make_dir(work_dir, backup=False)

    ### Copy/symlink files from structure_paths (unlabeled or labeled)
    structure_paths = read_yaml(f"{struct_startdir}/{DIR_MAKE_STRUCT}/structure_dirs.yml")
    structure_files = [
        copy_labeled_structure(p, p.replace(f"{DIR_MAKE_STRUCT}", f"{DIR_STRAIN}"))
        for p in structure_paths
    ]

    ### Scale and perturb the structures
    space_arg = pdict.get("sampling_space", {})
    if space_arg:
        logger.info(f"Explore sampling spaces on the path: {work_dir}")

    strain_arg = space_arg.get("strain", {})
    strain_x_list = composite_strain_points(strain_arg.get("strain_x", []))
    strain_y_list = composite_strain_points(strain_arg.get("strain_y", []))
    strain_z_list = composite_strain_points(strain_arg.get("strain_z", []))

    strain_structure_files = strain_x_dim(structure_files, strain_x_list)
    strain_structure_files = strain_y_dim(strain_structure_files, strain_y_list)
    strain_structure_files = strain_z_dim(strain_structure_files, strain_z_list)

    ### perturb (removed)
    # perturb_num = strain_arg.get("perturb_num", 0)
    # perturb_disp = strain_arg.get("perturb_disp", 0.001)
    # structure_files = perturb_structure(structure_files, perturb_num, perturb_disp)

    ### Save structure_paths (relative to run_dir)
    strain_structure_dirs = sorted([Path(p).parent.as_posix() for p in strain_structure_files])
    write_yaml(strain_structure_dirs, f"{work_dir}/strain_structure_dirs.yml")

    structure_dirs = [Path(p).parent.as_posix() for p in structure_files]
    write_yaml(structure_dirs, f"{work_dir}/structure_dirs.yml")
    return


#####ANCHOR Stage 4 - run DFTsinglepoint
def run_dft(pdict, mdict):
    """
    Run DFT calculations
    """
    ### Define work_dir
    struct_startdir = mk_struct_dir(pdict)
    work_dir = f"{struct_startdir}/{DIR_STRAIN}"
    task_dirs = read_yaml(f"{work_dir}/task_dirs.yml")

    logger.info("Run AIMD calculations")

    op = OperGendataGpawAIMD(work_dir, pdict, mdict, mdict_prefix="gpaw")
    op.prepare()
    op.run()
    op.postprocess()
    return


#####ANCHOR Stage 5 - Collect data
def collect_data(pdict, mdict):
    """
    Collect data from DFT simulations
    """
    ### Define work_dir
    struct_startdir = mk_struct_dir(pdict)
    work_dir = f"{struct_startdir}/{DIR_GENDATA}"
    make_dir(work_dir, backup=False)
    logger.info(f"Collect data on the path: {work_dir}")

    ### Collect data
    data_files = collect_files(
        f"{struct_startdir}/{DIR_STRAIN}", patterns=[FILE_FRAME_LABEL, FILE_TRAJ_LABEL]
    )
    if len(data_files) > 0:
        merge_extxyz_files(extxyz_files=data_files, outfile=f"{work_dir}/{FILE_ITER_DATA}")
        ### Remove unwanted keys
        remove_key_in_extxyz(f"{work_dir}/{FILE_ITER_DATA}", key_list=["timestep", "momenta"])
    return


#####ANCHOR main loop
class WorkflowGendata(Workflow):
    """Workflow for generate initial data for training ML models."""

    def __init__(self, param_file: str, machine_file: str):
        super().__init__(param_file, machine_file, SCHEMA_GENDATA)
        self.stage_map = {
            "make_structure": make_structure,
            "optimize_structure": optimize_structure,
            "sampling_space": sampling_space,
            "run_dft": run_dft,
            "collect_data": collect_data,
        }
        self.wf_name = "DATA GENERATION"
        return


#####ANCHOR Helper functions
def copy_labeled_structure(src_dir: str, dest_dir: str):
    """
    Copy labeled structures
        - First, try copy labeled structure if it exists.
        - If there is no labeled structure, copy the unlabeled structure.
    """
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    if Path(f"{src_dir}/{FILE_FRAME_LABEL}").is_file():
        new_path = shutil.copy2(f"{src_dir}/{FILE_FRAME_LABEL}", f"{dest_dir}/{FILE_FRAME_LABEL}")
    elif Path(f"{src_dir}/{FILE_FRAME_unLABEL}").is_file():
        new_path = shutil.copy2(
            f"{src_dir}/{FILE_FRAME_unLABEL}", f"{dest_dir}/{FILE_FRAME_unLABEL}"
        )
    return new_path


def strain_x_dim(struct_files: list[str], strain_x_list: list[float]):
    """
    Scale the x dimension of the structures
    """
    new_struct_files = struct_files.copy()
    for strain_x in strain_x_list:
        for struct_file in struct_files:
            struct_list = read_extxyz(struct_file)
            struct_list_scaled = [
                strain_struct(atoms, strains=[strain_x, 1, 1]) for atoms in struct_list
            ]
            new_filename = f"{Path(struct_file).parent}_x{strain_x}/{FILE_FRAME_unLABEL}"
            write_extxyz(new_filename, struct_list_scaled)
            new_struct_files.append(new_filename)
    return new_struct_files


def strain_y_dim(struct_files: list[str], strain_y_list: list[float]):
    """
    Scale the y dimension of the structures
    """
    new_struct_files = struct_files.copy()
    for strain_y in strain_y_list:
        for struct_file in struct_files:
            struct_list = read_extxyz(struct_file)
            struct_list_scaled = [
                strain_struct(atoms, strains=[1, strain_y, 1]) for atoms in struct_list
            ]
            new_filename = f"{Path(struct_file).parent}_y{strain_y}/{FILE_FRAME_unLABEL}"
            write_extxyz(new_filename, struct_list_scaled)
            new_struct_files.append(new_filename)
    return new_struct_files


def strain_z_dim(struct_files: list[str], strain_z_list: list[float]):
    """
    Scale the z dimension of the structures
    """
    new_struct_files = struct_files.copy()
    for strain_z in strain_z_list:
        for struct_file in struct_files:
            struct_list = read_extxyz(struct_file)
            struct_list_scaled = [
                strain_struct(atoms, strains=[1, 1, strain_z]) for atoms in struct_list
            ]
            new_filename = f"{Path(struct_file).parent}_z{strain_z}/{FILE_FRAME_unLABEL}"
            write_extxyz(new_filename, struct_list_scaled)
            new_struct_files.append(new_filename)
    return new_struct_files


def perturb_structure(struct_files: list, perturb_num: int, perturb_disp: float):
    """
    Perturb the structures
    """
    new_struct_files = struct_files.copy()
    for idx in range(perturb_num):
        for struct_file in struct_files:
            struct_list = read_extxyz(struct_file)
            struct_list_perturbed = [
                perturb_struct(atoms, std_disp=perturb_disp) for atoms in struct_list
            ]
            new_filename = f"{Path(struct_file).parent}_p{idx:03d}/{FILE_FRAME_unLABEL}"
            write_extxyz(new_filename, struct_list_perturbed)
            new_struct_files.append(new_filename)
    return new_struct_files


def _total_struct_num(pdict: dict):
    space_arg = pdict.get("sampling_space", {})
    len_x = len(space_arg.get("strain_x", []))
    len_y = len(space_arg.get("strain_y", []))
    len_z = len(space_arg.get("strain_z", []))
    len_temp = len(space_arg.get("temperature", []))
    len_stress = len(space_arg.get("stress", []))

    total_confs = (len_temp * len_stress) * (
        (len_x * len_y * len_z)
        + (len_x * len_y)
        + (len_x * len_z)
        + (len_y * len_z)
        + len_x
        + len_y
        + len_z
        + 1
    )
    return total_confs
