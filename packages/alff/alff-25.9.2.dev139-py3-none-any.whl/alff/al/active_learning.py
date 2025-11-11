from pathlib import Path

from asext.io.readwrite import read_extxyz, write_extxyz
from asext.struct import check_bad_box
from natsort import natsorted
from thkit.display import TextDecor
from thkit.io import read_yaml, write_yaml
from thkit.path import collect_files, make_dir, make_dir_ask_backup

from alff.al.libal_md_ase import OperAlmdAseSevennet, premd_ase_sevenn
from alff.al.libal_md_lammps import OperAlmdLammpsSevennet, premd_lammps_sevenn
from alff.al.mlp_engine.mlp_sevenn import OperAltrainSevennet, pretrain_sevenn
from alff.base import Workflow, logger
from alff.gdata.libgen_gpaw import OperAlGpawSinglepoint
from alff.gdata.util_dataset import merge_extxyz_files, remove_key_in_extxyz
from alff.util.key import (
    DIR_DATA,
    DIR_DFT,
    DIR_MD,
    DIR_TMP_DATA,
    DIR_TRAIN,
    FILE_CHECKPOINT_PATH,
    FILE_COLLECT_DATA,
    FILE_DATAPATH,
    FILE_FRAME_LABEL,
    FILE_ITER_DATA,
    FILE_ITERLOG,
    FILE_TRAJ_MD_CANDIDATE,
    FMT_ITER,
    FMT_STAGE,
    FMT_TASK_DFT,
    SCHEMA_ACTIVE_LEARN,
    FILE_FRAME_unLABEL,
)


#####ANCHOR Stage training
def stage_train(iter_idx, pdict, mdict):
    """This function does:
    - collect data files
    - prepare training args based on MLP engine
    """
    pdict_train = pdict["train"]

    ### Create work_dir folder
    work_dir = f"{iter_str(iter_idx)}/{DIR_TRAIN}"
    make_dir_ask_backup(work_dir)

    logger.info("Collect and prepare dataset")
    ### Collect initial data files: dict[list[str]] = {"init": [], "iter_0": [], ...}
    datadict = {}  # relative to run_dir
    datadict["init"] = natsorted(
        collect_files(pdict_train["init_data_paths"], patterns=["*.extxyz"])
    )

    ### Collect data from previous iterations
    previous_dirs = [f"{iter_str(i)}/{DIR_DATA}" for i in range(iter_idx)]
    datadict["iteration"] = collect_files(previous_dirs, patterns=["*.extxyz"])
    write_yaml(datadict, f"{work_dir}/{FILE_DATAPATH}")

    ### Copy data files to tmp_folder: `copied_data/`
    data_files = [f for value in datadict.values() for f in value]
    data_files = list(set(data_files))  # remove duplicates
    assert len(data_files) > 0, "No data files found"
    merge_extxyz_files(
        extxyz_files=data_files, outfile=f"{work_dir}/{DIR_TMP_DATA}/{FILE_COLLECT_DATA}"
    )

    ### Setup to continue previous train
    continue_train = pdict_train.get("continue_train", True)
    if iter_idx > 0 and continue_train:
        previous_iter = iter_str(iter_idx - 1)
        model_files = read_yaml(f"{previous_iter}/{DIR_TRAIN}/{FILE_CHECKPOINT_PATH}")
        pdict["train"]["init_checkpoints"] = model_files  # relative to run_dir -> change pdict

    ### Prepare train args
    mlp_engine, _ = _get_engines(pdict)
    if mlp_engine == "sevenn":
        pretrain_sevenn(work_dir, pdict, mdict)
        op = OperAltrainSevennet(work_dir, pdict, mdict, mdict_prefix="train")
        op.prepare()
        op.run()
        op.postprocess()
    return


#####ANCHOR Stage MD
def stage_md(iter_idx, pdict, mdict):
    """New stage function for MD tasks, including: pre, run, post MD.
    - Collect initial configurations
    - Prepare MD args
    - Submit MD jobs to remote machines
    - Postprocess MD results
    """
    work_dir = f"{iter_str(iter_idx)}/{DIR_MD}"
    make_dir_ask_backup(work_dir)

    ### Sampling spaces
    sampling_spaces = pdict["md"]["sampling_spaces"]  # list[dict]
    current_space = sampling_spaces[iter_idx]  # dict
    write_yaml(current_space, f"{work_dir}/current_space.yml")

    logger.info("Prepare MD args")
    ### Prepare MD args
    mlp_engine, md_engine = _get_engines(pdict)
    if mlp_engine == "sevenn":
        if md_engine == "ase":
            premd_ase_sevenn(work_dir, pdict, mdict)
            op = OperAlmdAseSevennet(work_dir, pdict, mdict, mdict_prefix="ase")
            op.prepare()
            op.run()
            op.postprocess()
        elif md_engine == "lammps":
            premd_lammps_sevenn(work_dir, pdict, mdict)
            op = OperAlmdLammpsSevennet(work_dir, pdict, mdict, mdict_prefix="lammps")
            op.prepare()
            op.run()
            op.postprocess()
    # elif mlp_engine == "mace":
    #     pre_md_mace(iter_idx, pdict, mdict)
    return


#####ANCHOR Stage DFT
def stage_dft(iter_idx, pdict, mdict):
    """New stage function for DFT tasks, including: pre, run, post DFT."""
    work_dir = f"{iter_str(iter_idx)}/{DIR_DFT}"
    make_dir_ask_backup(work_dir)

    logger.info("Prepare DFT tasks")
    ### Copy candidate extxyz from previous MD
    structure_dirs = read_yaml(f"{iter_str(iter_idx)}/{DIR_MD}/task_dirs.yml")
    extxyz_files = collect_files(structure_dirs, patterns=[FILE_TRAJ_MD_CANDIDATE])
    merge_extxyz_files(extxyz_files=extxyz_files, outfile=f"{work_dir}/md_candidates.extxyz")

    ### Create dft task_dirs
    struct_list = read_extxyz(f"{work_dir}/md_candidates.extxyz", index=":")
    dft_task_dirs = [None] * len(struct_list)
    bad_box_list = [None] * len(struct_list)
    for i, struct in enumerate(struct_list):
        is_bad = check_bad_box(
            struct, criteria={"length_ratio": 20, "wrap_ratio": 0.6, "tilt_ratio": 0.6}
        )
        if not is_bad:
            new_dir = f"{work_dir}/dft_{i:{FMT_TASK_DFT}}"  # relative to run_dir
            make_dir(new_dir, backup=False)
            struct.write(f"{new_dir}/{FILE_FRAME_unLABEL}", format="extxyz")
            dft_task_dirs[i] = new_dir
        else:
            bad_box_list[i] = struct

    dft_task_dirs = [d for d in dft_task_dirs if d is not None]
    task_dirs = dft_task_dirs
    write_yaml(task_dirs, f"{work_dir}/task_dirs.yml")

    ### Write bad box struct
    bad_box_list = [a for a in bad_box_list if a is not None]
    if len(bad_box_list) > 0:
        filename = f"{work_dir}/found_{len(bad_box_list)}_badbox_struct.extxyz"
        write_extxyz(filename, bad_box_list)
        logger.warning(f"Found {len(bad_box_list)} bad-box struct, see file:\n\t'{filename}'")

    ### Submit remote jobs
    op = OperAlGpawSinglepoint(work_dir, pdict, mdict, mdict_prefix="gpaw")
    op.prepare()
    op.run()
    op.postprocess()

    ### Collect DFT labeled data
    data_outdir = Path(work_dir).parent / DIR_DATA
    _collect_dft_label_data(structure_dirs=dft_task_dirs, data_outdir=data_outdir)
    return


def _collect_dft_label_data(
    structure_dirs,
    data_outdir,
):
    """Collect DFT labeled data from `structure_dirs` to file `work_dir/DIR_DATA/FILE_ITER_DATA`.

    Args:
        structure_dirs (list): List of structure directories to collect data from.
        data_outdir (str): The working directory to store collected data.

    Raises:
        RuntimeError: If no data is generated in this iteration.
    """
    logger.info(f"Collect DFT labeled data on the path: {data_outdir}")
    ### Collect DFT labeled extxyz files
    extxyz_files = collect_files(structure_dirs, patterns=[FILE_FRAME_LABEL])
    if len(extxyz_files) > 0:
        data_file = f"{data_outdir}/{FILE_ITER_DATA}"
        merge_extxyz_files(extxyz_files=extxyz_files, outfile=data_file)
        ### Remove unwanted keys
        remove_key_in_extxyz(
            data_file, key_list=["free_energy", "magmom", "magmoms", "dipole", "momenta"]
        )
    else:
        raise RuntimeError(
            "No data generated in this iteration. Check the preceding MD/DFT stages."
        )
    return


#####ANCHOR Active Learning loop
class WorkflowActiveLearning(Workflow):
    """Workflow for active learning.
    Note: Need to redefine `.run()` method, since the Active Learning workflow is different from the base class.
    """

    def __init__(self, param_file: str, machine_file: str):
        super().__init__(param_file, machine_file, SCHEMA_ACTIVE_LEARN)
        self.stage_map = {
            "ml_train": stage_train,
            "md_explore": stage_md,
            "dft_label": stage_dft,
        }
        self.wf_name = "ACTIVE LEARNING"
        return

    def run(self):
        self._print_intro()
        pdict = self.pdict
        mdict = self.mdict
        stage_map = self.stage_map

        ### main loop
        iter_log = read_iterlog()  # check iter_record
        if iter_log[1] > -1:
            logger.info(
                f"continue from iter_{iter_log[0]:{FMT_ITER}} stage_{iter_log[1]:{FMT_STAGE}}"
            )

        sampling_spaces = pdict["md"].get("sampling_spaces", [])
        for iter_idx in range(len(sampling_spaces)):
            if iter_idx < iter_log[0]:  # skip recoded iter
                continue

            logger.info(breakline_iter(iter_idx))
            for stage_idx, (stage_name, stage_func) in enumerate(stage_map.items()):
                if stage_idx <= iter_log[1]:  # skip recoded stage, only 1 time
                    continue
                self._update_config()  # update if config changes
                logger.info(breakline_stage(iter_idx, stage_idx, stage_name))
                stage_func(iter_idx, pdict, mdict)
                write_iterlog(iter_idx, stage_idx, stage_name)
            iter_log[1] = -1  # reset stage_idx

        ### Training the last data
        if iter_idx == range(len(sampling_spaces))[-1]:  # continue from last iter
            iter_idx += 1
            stage_list = ["training"]
            for stage_idx, stage_name in enumerate(stage_list):
                if stage_idx <= iter_log[1]:  # skip recoded stage, only 1 time
                    continue
                logger.info(f"{breakline_stage(iter_idx, stage_idx, stage_name)} (last train)")
                stage_func = stage_map[stage_name]
                stage_func(iter_idx, pdict, mdict)
                write_iterlog(iter_idx, stage_idx, f"{stage_name} (last train)")

        self._print_outro()
        return


#####ANCHOR Helper functions
def _get_engines(pdict) -> tuple[str]:
    mlp_engine = pdict.get("train", {}).get("mlp_engine", "sevenn")
    md_engine = pdict.get("md", {}).get("md_engine", "ase")

    avail_mlp_engines = ["mace", "sevenn"]
    avail_md_engines = ["ase", "lammps"]
    if mlp_engine not in avail_mlp_engines:
        raise ValueError(
            f"Unknown mlp_engine '{mlp_engine}'. Supported engines are: {avail_mlp_engines}"
        )
    if md_engine not in avail_md_engines:
        raise ValueError(
            f"Unknown md_engine '{md_engine}'. Supported engines are: {avail_md_engines}"
        )
    return (mlp_engine, md_engine)


def write_iterlog(iter_idx: int, stage_idx: int, stage_name: str, last_iter: bool = True) -> None:
    """Write the current iteration and stage to the iter log file.
    If `last_iter` is True, only the last iteration is saved.
    """
    header = "## 1st-column is the iteration index \n## 2nd-column is the stage index: \n\t# 0 ml_train \n\t# 1 md_explore \n\t# 2 dft_label \n\n"
    Path(FILE_ITERLOG).parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    if last_iter:
        with open(FILE_ITERLOG, "w") as f:
            f.write(f"{header}")
            f.write(f"{iter_idx:d} {stage_idx:d} \t# {stage_name}\n")
    else:
        with open(FILE_ITERLOG, "a") as f:
            f.write(f"{iter_idx:d} {stage_idx:d} \t# {stage_name}\n")
    return


def read_iterlog() -> list[int]:
    """Read the last line of the iter log file."""
    iter_log = [0, -1]
    if Path(FILE_ITERLOG).is_file():
        with open(FILE_ITERLOG) as f:
            lines = f.readlines()
        lines = [line.partition("#")[0].strip() for line in lines if line.partition("#")[0]]
        if len(lines) > 0:
            iter_log = [int(x) for x in lines[-1].split()]
    return iter_log


def iter_str(iter_idx: int) -> str:
    return f"iter_{iter_idx:{FMT_ITER}}"


def breakline_iter(iter_idx: int) -> str:
    text = f" {iter_str(iter_idx)} "
    return TextDecor(text).fill_left(margin=20, fill_left="=", length=52)


def breakline_stage(iter_idx: int, stage_idx: int, stage_name: str) -> str:
    text = f" {iter_str(iter_idx)} stage_{stage_idx:{FMT_STAGE}} {stage_name} "
    return TextDecor(text).fill_left(margin=20, fill_left="-", length=52)
