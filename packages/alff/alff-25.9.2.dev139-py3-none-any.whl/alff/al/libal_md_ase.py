import textwrap
from copy import deepcopy
from pathlib import Path

from thkit.config import validate_config
from thkit.io import read_yaml, write_yaml
from thkit.path import collect_files, copy_file, remove_dirs
from thkit.range import composite_index

from alff.al.libal_md_lammps import _sampling_report
from alff.base import RemoteOperation
from alff.util.key import (
    ALFF_ROOT,
    DIR_MD,
    DIR_TMP_MODEL,
    DIR_TRAIN,
    FILE_ARG_ASE,
    FILE_CHECKPOINT_PATH,
    FILE_TRAJ_MD,
    # FMT_STRUCT,
    SCHEMA_ASE_RUN,
    SCRIPT_ASE_PATH,
    FILE_FRAME_unLABEL,
)


#####ANCHOR pre MD ase
def premd_ase_sevenn(work_dir, pdict, mdict):
    ### note: work_dir = iter_dir/DIR_MD
    """This function does:
    - prepare MD args
        - generate task_dirs for ranges of temperature and press
    """
    pdict_md = pdict["md"]

    ### copy ML_models to work_dir
    iter_dir = Path(work_dir).parent
    checkpoint_files = read_yaml(f"{iter_dir}/{DIR_TRAIN}/{FILE_CHECKPOINT_PATH}")
    model_files = [
        copy_file(p, p.replace(f"{DIR_TRAIN}", f"{DIR_MD}/{DIR_TMP_MODEL}"))
        for p in checkpoint_files
    ]
    write_yaml(model_files, f"{work_dir}/model_files.yml")

    ### collect initial configurations
    space_args = read_yaml(f"{work_dir}/current_space.yml")
    init_struct_paths = pdict_md["init_struct_paths"]
    init_struct_idxs = list(set(composite_index(space_args.get("init_struct_idxs", []))))
    assert max(init_struct_idxs) < len(init_struct_paths), (
        "indices in 'init_struct_idxs' must be smaller than the number of 'init_struct_paths'"
    )

    structure_files = []
    struct_dict = {}  # save structures idx for information
    for idx in init_struct_idxs:
        files = sorted(collect_files(init_struct_paths[idx], patterns=["*.extxyz"]))
        copied_files = [
            copy_file(myfile, f"{work_dir}/idx{idx}_{i}/{FILE_FRAME_unLABEL}")
            for i, myfile in enumerate(files)
        ]
        structure_files.extend(copied_files)
        struct_dict[f"init_struct_idx_{idx}"] = files  # relative to run_dir
    structure_dirs = [Path(fi).parent.as_posix() for fi in structure_files]
    write_yaml(structure_dirs, f"{work_dir}/structure_dirs.yml")
    write_yaml(struct_dict, f"{work_dir}/init_struct_paths.yml")

    ### Prepare MD args
    temperature_list = space_args.get("temps", [])
    press_list = space_args.get("pressures", [])
    current_space_args = deepcopy(space_args)
    for key in ["init_struct_idxs", "temps", "pressures"]:
        current_space_args.pop(key, None)
    md_args = deepcopy(pdict_md.get("common_md_args", {}))
    md_args.update(current_space_args)

    ### Define ASE args & model files
    if pdict_md.get("model_idx", None):
        model_files = [model_files[i] for i in pdict_md["model_idx"]]
    rel_model_files = [Path(p).relative_to(work_dir).as_posix() for p in model_files]

    calc_list = [f"SevenNetCalculator('../{f}')" for f in rel_model_files]
    ase_args = {}
    ase_args.setdefault("calc_args", {})["ase"] = {
        "py_script": [
            "from sevenn.calculator import SevenNetCalculator",
            # f"calc = SevenNetCalculator('../{model_file0}')",
            f"calcs = [{', '.join(calc_list)}]",
            "from ase.calculators.mixing import AverageCalculator",
            "calc = AverageCalculator(calcs)",
        ]
    }
    ase_args.update({"md": md_args})

    task_dirs = temperature_press_mdarg_ase(structure_dirs, temperature_list, press_list, ase_args)
    write_yaml(task_dirs, f"{work_dir}/task_dirs.yml")

    ### ASE_run_file, and model deivation check
    _ = copy_file(
        f"{SCRIPT_ASE_PATH}/cli_ase_md.py",
        f"{work_dir}/cli_ase_md.py",
    )

    ### Write python script for compute committee_error and select candidates
    _ = copy_file(
        f"{ALFF_ROOT}/al/utilal_uncertainty.py",
        f"{work_dir}/{DIR_TMP_MODEL}/utilal_uncertainty.py",
    )
    comm_std = pdict_md.get("committee_std", {})
    e_std_lo = comm_std.get("e_std_lo", 0.0)
    e_std_hi = comm_std.get("e_std_hi", 0.1)
    f_std_lo = comm_std.get("f_std_lo", 0.0)
    f_std_hi = comm_std.get("f_std_hi", 0.1)
    s_std_lo = comm_std.get("s_std_lo", 0.0)
    s_std_hi = comm_std.get("s_std_hi", None)

    pyscript = textwrap.dedent(f"""
    import sys
    sys.path.append("../{DIR_TMP_MODEL}")
    from utilal_uncertainty import select_candidate_SevenNet
    from glob import glob

    extxyz_file = "{FILE_TRAJ_MD}"
    ### Select candidate configurations
    checkpoint_files = glob("../{DIR_TMP_MODEL}/model*/*.pth")
    print(checkpoint_files)
    select_candidate_SevenNet(
        extxyz_file=extxyz_file,
        checkpoint_files=checkpoint_files,
        sevenn_args={{}},
        rel_force=None,
        compute_stress=True,
        rel_stress=None,
        e_std_lo={e_std_lo},
        e_std_hi={e_std_hi},
        f_std_lo={f_std_lo},
        f_std_hi={f_std_hi},
        s_std_lo={s_std_lo},
        s_std_hi={s_std_hi},
    )
    """)
    with open(f"{work_dir}/{DIR_TMP_MODEL}/cli_committee_sevenn.py", "w") as f:
        f.write(pyscript)
    return


class OperAlmdAseSevennet(RemoteOperation):
    """This class runs ASE md for a list of structures in `task_dirs`."""

    def __init__(self, work_dir, pdict, multi_mdict, mdict_prefix="md"):
        super().__init__(work_dir, pdict, multi_mdict, mdict_prefix)
        self.op_name = "ASE md"
        ### To filter already run structures
        self.has_files = ["conf.lmpdata"]  # need to revise this line
        self.no_files = ["committee_error.txt"]
        return

    def prepare(self):
        """This function does:
        - Prepare the task_list
        - Prepare fordward & backward files
        - Prepare commandlist_list for multi-remote submission
        """
        ### Prepare fordward & backward files
        self.forward_common_files = ["cli_ase_md.py", DIR_TMP_MODEL]  # in work_dir
        self.forward_files = [FILE_FRAME_unLABEL, FILE_ARG_ASE]  # all files in task_dirs
        self.backward_files = [
            "calc_*",
            "committee_*",
            "*.extxyz",
        ]  # FILE_TRAJ_MD, FILE_TRAJ_MD_CANDIDATE,
        ### Prepare commandlist_list for multi-remote submission
        mdict_list = self.mdict_list
        commandlist_list = []
        for mdict in mdict_list:
            command_list = []
            md_command = mdict.get("command", "python")
            md_command = f"{md_command} ../cli_ase_md.py {FILE_ARG_ASE}"  # `../` to run file in common directory
            command_list.append(md_command)

            ### compute committee_error
            command = f"""python ../{DIR_TMP_MODEL}/cli_committee_sevenn.py"""
            command_list.append(command)
            commandlist_list.append(command_list)
        self.commandlist_list = commandlist_list
        return

    def postprocess(self):
        work_dir = self.work_dir
        task_dirs = self.task_dirs

        _sampling_report(work_dir, task_dirs)

        ### Clean up
        # md_traj_files = [f"{p}/{FILE_TRAJ_MD}" for p in task_dirs]
        # [Path(f).unlink() for f in md_traj_files if Path(f).exists()]
        return


#####ANCHOR helper functions
def temperature_press_mdarg_ase(
    struct_dirs: list,
    temperature_list: list = [],
    press_list: list = [],
    ase_argdict: dict = {},
) -> list:
    """
    Generate the task_dirs for ranges of temperatures and stresses.

    Args:
        struct_dirs (list): List of dirs contains configuration files.
        temperature_list (list): List of temperatures.
        press_list (list): List of stresses.
        ase_argdict (dict): See [ase.md schema](https://thangckt.github.io/alff_doc/schema/config_ase/)
    """
    ase_args = deepcopy(ase_argdict)  # avoid modifying original dict
    ase_args.setdefault("structure", {})["from_extxyz"] = f"{FILE_FRAME_unLABEL}"
    task_dirs = []
    counter = 0
    for struct_path in struct_dirs:
        if temperature_list:
            for temp in temperature_list:  # temperature range
                if press_list:
                    for press in press_list:  # stress range
                        if isinstance(press, list):
                            press_str = "_".join([f"{s:.1f}" for i, s in enumerate(press) if i < 3])
                        else:
                            press_str = f"{press:.1f}"

                        new_dir = f"{struct_path}_t{temp:.0f}_s{press_str}"
                        # new_dir = new_dir.replace("idx", f"md_{counter:{FMT_STRUCT}}_id")
                        new_dir = new_dir.replace("idx", "md_id")  # remove counter
                        copy_file(
                            f"{struct_path}/{FILE_FRAME_unLABEL}",
                            f"{new_dir}/{FILE_FRAME_unLABEL}",
                        )
                        ### udpate ase_md_args
                        tmp_md = {"temp": temp, "press": press, "ensemble": "NPT"}
                        ase_args["md"].update(tmp_md)

                        validate_config(config_dict=ase_args, schema_file=SCHEMA_ASE_RUN)
                        write_yaml(ase_args, f"{new_dir}/{FILE_ARG_ASE}")
                        ### save path
                        task_dirs.append(new_dir)
                        counter += 1
                else:
                    new_dir = f"{struct_path}_t{temp:.0f}"
                    # new_dir = new_dir.replace("idx", f"md_{counter:{FMT_STRUCT}}_id")
                    new_dir = new_dir.replace("idx", "md_id")  # remove counter
                    copy_file(
                        f"{struct_path}/{FILE_FRAME_unLABEL}",
                        f"{new_dir}/{FILE_FRAME_unLABEL}",
                    )
                    ### udpate ase_md_args
                    tmp_md = {"temp": temp, "ensemble": "NVT"}
                    ase_args["md"].update(tmp_md)
                    validate_config(config_dict=ase_args, schema_file=SCHEMA_ASE_RUN)
                    write_yaml(ase_args, f"{new_dir}/{FILE_ARG_ASE}")
                    ### save path
                    task_dirs.append(new_dir)
                    counter += 1
        else:
            new_dir = f"{struct_path}"
            # new_dir = new_dir.replace("idx", f"md_{counter:{FMT_STRUCT}}_id")
            new_dir = new_dir.replace("idx", "md_id")  # remove counter
            ### update ase_md_args
            tmp_md = {"ensemble": "NVE"}
            ase_args["md"].update(tmp_md)
            validate_config(config_dict=ase_args, schema_file=SCHEMA_ASE_RUN)
            write_yaml(ase_args, f"{new_dir}/{FILE_ARG_ASE}")
            ### save path
            task_dirs.append(new_dir)
            counter += 1
    ### delete the original dirs (replaced by temp_press dirs)
    _ = [remove_dirs(p) for p in struct_dirs if p not in task_dirs]
    return task_dirs
