### REFs
# SevenNet inputs: https://github.com/MDIL-SNU/SevenNet/blob/main/example_inputs/training/input_full.yml

from thkit.pkg import check_package

check_package(
    "sevenn",
    auto_install=True,
    git_repo="https://github.com/MDIL-SNU/SevenNet@main",
)

import random
import shutil
import subprocess
from pathlib import Path

from ase.io import read
from natsort import natsorted
from thkit.io import write_yaml
from thkit.path import copy_file, list_paths, make_dir

from alff.al.mlp_engine.util_mlp import suggest_num_epochs
from alff.base import RemoteOperation, logger
from alff.gdata.util_dataset import split_extxyz_dataset
from alff.util.key import (
    DIR_TMP_DATA,
    FILE_ARG_TRAIN,
    FILE_CHECKPOINT_PATH,
    FILE_COLLECT_DATA,
    FMT_MODEL,
)


#####ANCHOR Active-learning: Training using SEVENNET
def pretrain_sevenn(work_dir, pdict, mdict):
    """This function prepares:
    - prepare SEVENN args
    - establish train tasks (one folder for each training model)
    - Save all common_files in DIR_TMP_DATA for convenience in transferring files
    """
    pdict_train = pdict["train"]

    logger.info("Split dataset")
    ### Split dataset
    train_ratio = pdict_train.get("trainset_ratio", 1)
    valid_ratio = pdict_train.get("validset_ratio", 0)
    split_extxyz_dataset(
        f"{work_dir}/{DIR_TMP_DATA}/{FILE_COLLECT_DATA}",
        train_ratio=train_ratio,
        valid_ratio=valid_ratio,
        outfile_prefix=f"{work_dir}/{DIR_TMP_DATA}/data",
    )
    Path(f"{work_dir}/{DIR_TMP_DATA}/{FILE_COLLECT_DATA}").unlink()  # delete

    logger.info("Build graph data")
    if Path(f"{work_dir}/{DIR_TMP_DATA}/sevenn_data").exists():
        shutil.rmtree(f"{work_dir}/{DIR_TMP_DATA}/sevenn_data")
    ### Preprocess dataset: `sevenn graph_build`
    ## ref: https://github.com/MDIL-SNU/SevenNet/blob/main/sevenn/main/sevenn_graph_build.py
    sevenn_args = pdict_train["sevenn_args"]
    n_cores = pdict_train.get("num_cores_buildgraph", 8)
    cutoff = sevenn_args["model"].get("cutoff")
    ase_kwargs = sevenn_args["data"].get("data_format_args", "")
    if ase_kwargs:
        ase_kwargs = [f"{k}={v}" for k, v in ase_kwargs.items() if v]
        ase_kwargs = f"--kwargs {' '.join(ase_kwargs)}"

    build_cmd = f"sevenn_graph_build {DIR_TMP_DATA}/data_trainset.extxyz {cutoff} --num_cores {n_cores} --out {DIR_TMP_DATA} --filename graph_trainset.pt {ase_kwargs}"
    subprocess.run(build_cmd, cwd=work_dir, shell=True, check=True)
    if valid_ratio > 0:
        build_cmd = f"sevenn_graph_build {DIR_TMP_DATA}/data_validset.extxyz {cutoff} --num_cores {n_cores} --out {DIR_TMP_DATA} --filename graph_validset.pt {ase_kwargs}"
        subprocess.run(build_cmd, cwd=work_dir, shell=True, check=True)

    logger.info("Prepare training args")
    ### SEVENN args (note: use preprocess-data, see run section below)
    # sevenn_args = pdict_train["sevenn_args"]
    sevenn_args["data"]["load_trainset_path"] = [f"../{DIR_TMP_DATA}/sevenn_data/graph_trainset.pt"]
    if valid_ratio > 0:
        sevenn_args["data"]["load_validset_path"] = [
            f"../{DIR_TMP_DATA}/sevenn_data/graph_validset.pt"
        ]

    ### Guess num_epochs
    num_grad_updates = pdict_train.get("num_grad_updates", None)
    if num_grad_updates:
        list_atoms = read(
            f"{work_dir}/{DIR_TMP_DATA}/data_trainset.extxyz",
            format="extxyz",
            index=":",
        )
        dataset_size = len(list_atoms)
        batch_size = sevenn_args["data"]["batch_size"]
        num_epochs = suggest_num_epochs(dataset_size, batch_size, num_grad_updates)
        sevenn_args["train"]["epoch"] = num_epochs
        if sevenn_args["train"].get("scheduler", None) == "linearlr":
            sevenn_args["train"]["scheduler_param"]["total_iters"] = num_epochs

    ### Copy init_checkpoints to DIR_TMP_DATA
    init_checkpoints = natsorted(pdict_train.get("init_checkpoints", []))
    if init_checkpoints:
        _ = [
            copy_file(fi, f"{work_dir}/{DIR_TMP_DATA}/init_checkpoint_{i}.pth")
            for i, fi in enumerate(init_checkpoints)
        ]

    logger.info("Prepare train tasks")
    ### Prepare train tasks (one folder for each training model)
    num_models = pdict_train["num_models"]
    task_dirs = [None] * num_models
    for i in range(num_models):
        model_path = Path(f"{work_dir}/model_{i:{FMT_MODEL}}")
        make_dir(model_path, backup=False)
        ### Set more args privately for each model
        sevenn_args["train"]["random_seed"] = random.randrange(2**16)
        if (
            init_checkpoints and Path(f"{work_dir}/{DIR_TMP_DATA}/init_checkpoint_{i}.pth").exists()
        ):  # continue training
            tmp_dict = {
                "reset_optimizer": True,
                "reset_scheduler": True,
                "checkpoint": f"../{DIR_TMP_DATA}/init_checkpoint_{i}.pth",
                "reset_epoch": True,
            }
            sevenn_args["train"]["continue"] = tmp_dict

        write_yaml(sevenn_args, f"{model_path}/{FILE_ARG_TRAIN}")
        task_dirs[i] = model_path.as_posix()
    ### save task_dirs (relative to run_dir)
    write_yaml(task_dirs, f"{work_dir}/task_dirs.yml")
    return


class OperAltrainSevennet(RemoteOperation):
    def __init__(self, work_dir, pdict, multi_mdict, mdict_prefix="train"):
        super().__init__(work_dir, pdict, multi_mdict, mdict_prefix)
        self.op_name = "Training"
        ### To filter already run structures
        self.has_files = [FILE_ARG_TRAIN]
        self.no_files = ["checkpoint_best.pth"]
        return

    def prepare(self):
        """This function does:
        - Prepare the task_list
        - Prepare fordward & backward files
        - Prepare commandlist_list for multi-remote submission
        """
        pdict = self.pdict
        ### Prepare fordward & backward files
        self.forward_common_files = [DIR_TMP_DATA]
        self.forward_files = [FILE_ARG_TRAIN]  # all files in task_path
        self.backward_files = [
            "checkpoint_*.pth",  # "checkpoint_*.pth",  "checkpoint_best.pth"
            "log*.sevenn",
            "lc.csv",
        ]
        ### Prepare commandlist_list for multi-remote submission
        mdict_list = self.mdict_list
        commandlist_list = []
        for mdict in mdict_list:
            command_list = []
            train_command = mdict.get("command", "sevenn")
            if train_command == "sevenn":
                # train_command = f"{train_command} {FILE_ARG_TRAIN} --enable_cueq"
                train_command = f"{train_command} {FILE_ARG_TRAIN}"
                distributed_args = pdict["train"].get("distributed", None)
                if distributed_args:  ## run distributed training (MPI)
                    cluster_type = distributed_args.get("cluster_type", "slurm")  # SLURM or SGE
                    if cluster_type == "slurm":
                        gpu_per_node = mdict["resources"].get("gpu_per_node", 0)
                        command_list.extend(
                            [
                                "export WORLD_SIZE=$SLURM_NTASKS",
                                "export RANK=$SLURM_PROCID",
                                "export LOCAL_RANK=$SLURM_LOCALID",
                            ]
                        )
                        if distributed_args["distributed_backend"] == "nccl":
                            train_command = f"torchrun --standalone --nproc_per_node {gpu_per_node} --no_python {train_command} --distributed --distributed_backend='nccl'"

                    elif cluster_type == "sge":
                        gpu_per_node = distributed_args.get("gpu_per_node", 0)
                        if distributed_args["distributed_backend"] == "mpi":
                            train_command = f"mpirun -np $NSLOTS {train_command} --distributed --distributed_backend='mpi'"
                        elif distributed_args["distributed_backend"] == "nccl":
                            train_command = f"torchrun --standalone --nnodes $NSLOTS --nproc_per_node {gpu_per_node} --no_python {train_command} --distributed --distributed_backend='nccl'"
                        elif distributed_args["distributed_backend"] == "gloo":
                            # command_list.append("export WORLD_SIZE=$NSLOTS \nexport RANK=-1")
                            train_command = f"torchrun --standalone --nnodes $NSLOTS --nproc_per_node cpu --no_python {train_command} --distributed --distributed_backend='gloo'"
                    else:
                        command_list.extend(
                            [
                                "export WORLD_SIZE=$(DPDISPATCHER_NUMBER_NODE*DPDISPATCHER_CPU_PER_NODE)",
                                "export RANK=$SLURM_PROCID",
                                "export LOCAL_RANK=$SLURM_LOCALID",
                            ]
                        )
                        train_command = f"torchrun --standalone --nproc_per_node $DPDISPATCHER_GPU_PER_NODE --no_python {train_command} --distributed --distributed_backend='nccl'"
            command_list.append(train_command)
            commandlist_list.append(command_list)
        self.commandlist_list = commandlist_list
        return

    def postprocess(self):
        """Collect the best checkpoint files and save them in FILE_CHECKPOINT_PATH"""
        work_dir = self.work_dir
        task_dirs = self.task_dirs

        ### find the latest checkpoint file
        best_checkpoint_files = [None] * len(task_dirs)
        for i, task_dir in enumerate(task_dirs):
            checkpoint_files = list_paths(task_dir, patterns=["checkpoint_*.pth"])
            checkpoint_files = natsorted(checkpoint_files)
            best_checkpoint_files[i] = checkpoint_files[-1]
            _ = [Path(f).unlink() for f in checkpoint_files[:-1]]  # remove old checkpoints

        write_yaml(best_checkpoint_files, f"{work_dir}/{FILE_CHECKPOINT_PATH}")
        return


#####ANCHOR fine-tuning
### reuse pretrain_sevenn() and OperAltrainSevennet


#####ANCHOR Support functions
def convert_model_7net_to_lammps(
    checkpoint_file: str, rundir: str = "./", parallel: bool = False
) -> None:
    """Convert SevenNet model to LAMMPS model
    Args:
        checkpoint_file (str): path to the checkpoint file
        parallel (bool): whether to convert to parallel model
        rundir (str): path to the directory where the checkpoint file is located
    """
    py_command = f"sevenn_get_model {checkpoint_file}"  # add -p for parallel model
    if parallel:
        py_command += " -p"
        if Path(f"{rundir}/deployed_parallel").exists():
            shutil.rmtree(f"{rundir}/deployed_parallel")

    subprocess.run(py_command, cwd=rundir, shell=True, check=True)
    return


def convert_model_7net_to_lammps_mliap(
    checkpoint_file: str, rundir: str = "./", parallel: bool = False
) -> None:
    ### See https://github.com/MDIL-SNU/SevenNet/issues/246
    """Convert SevenNet_MLIAP model to LAMMPS model
    Args:
        checkpoint_file (str): path to the checkpoint file
        parallel (bool): whether to convert to parallel model
        rundir (str): path to the directory where the checkpoint file is located
    """
    py_command = f"sevenn-prepare-lmp-mliap {checkpoint_file}"  # add -p for parallel model
    if parallel:
        py_command += " -p"
        if Path(f"{rundir}/deployed_parallel").exists():
            shutil.rmtree(f"{rundir}/deployed_parallel")

    subprocess.run(py_command, cwd=rundir, shell=True, check=True)
    return
