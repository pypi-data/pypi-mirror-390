import textwrap
from copy import deepcopy
from pathlib import Path

# from asext.cell import sort_task_dirs
from asext.io.readwrite import extxyz2lmpdata
from natsort import natsorted
from thkit.config import validate_config
from thkit.io import read_yaml, write_yaml
from thkit.path import collect_files, copy_file, filter_dirs, remove_dirs
from thkit.range import composite_index

from alff.al.mlp_engine.mlp_sevenn import (
    convert_model_7net_to_lammps,
    convert_model_7net_to_lammps_mliap,
)
from alff.base import RemoteOperation, logger
from alff.util.key import (
    ALFF_ROOT,
    DIR_MD,
    DIR_TMP_MODEL,
    DIR_TRAIN,
    FILE_ARG_LAMMPS,
    FILE_CHECKPOINT_PATH,
    FILE_TRAJ_MD,
    RUNFILE_LAMMPS,
    SCHEMA_LAMMPS,
    FILE_FRAME_unLABEL,
)
from alff.util.script_lammps.lammps_code_creator import (
    generate_script_lammps_md,
    process_lammps_argdict,
)


#####ANCHOR pre MD lammps
def premd_lammps_sevenn(work_dir, pdict, mdict):
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

    ### Define LAMMPS args & model files (need convert checkpoint to lammps format)
    if pdict_md.get("model_idx", None) is not None:
        model_files = [model_files[i] for i in pdict_md["model_idx"]]
    # rel_model_files = [Path(p).relative_to(work_dir).as_posix() for p in model_files]

    ### convert checkpoint to lammps_serial
    if pdict_md.get("use_mliap", False):
        convert_model_7net_to_lammps_mliap(
            Path(model_files[0]).name, rundir=Path(model_files[0]).parent, parallel=False
        )
    else:
        convert_model_7net_to_lammps(
            Path(model_files[0]).name, rundir=Path(model_files[0]).parent, parallel=False
        )
    rel_model_file0 = Path(model_files[0]).relative_to(work_dir).as_posix()
    rel_model_file0 = rel_model_file0.replace(Path(rel_model_file0).name, "deployed_serial.pt")
    lammps_args = {}
    if pdict_md.get("dftd3", None):
        damping = pdict_md["dftd3"].get("damping", "damp_zero")
        xc = pdict_md["dftd3"].get("xc", "pbe")
        cutoff = pdict_md["dftd3"].get("cutoff", 9000)
        cnthr = pdict_md["dftd3"].get("cnthr", 1600)
        lammps_args["structure"] = {
            "pair_style": [f"hybrid/overlay e3gnn d3 {cutoff} {cnthr} {damping} {xc}"],
            "pair_coeff": [
                f"* * e3gnn ../{rel_model_file0} placeholder_for_atomnames",
                "* * d3 placeholder_for_atomnames",
            ],
        }
    else:
        lammps_args["structure"] = {
            "pair_style": ["e3gnn"],
            "pair_coeff": [f"* * ../{rel_model_file0} placeholder_for_atomnames"],
        }

    ### convert checkpoint to lammps_parallel (Note: Sevennet raises error with small simulation box < 200 atoms)
    # convert_model_7net_to_lammps(
    #     Path(model_files[0]).name, rundir=Path(model_files[0]).parent, parallel=True
    # )
    # rel_model_file0 = Path(model_files[0]).relative_to(work_dir).as_posix()
    # rel_model_file0 = rel_model_file0.replace(Path(rel_model_file0).name, "deployed_parallel")
    # pt_file_count = sum(
    #     1 for file in Path(f"{work_dir}/{rel_model_file0}").glob("deployed_parallel*.pt")
    # )
    # lammps_args = {}
    # lammps_args["structure"] = {
    #     "pair_style": ["e3gnn/parallel"],
    #     "pair_coeff": [f"* * {pt_file_count} ../{rel_model_file0} placeholder_for_atomnames"],
    # }

    lammps_args.update({"md": md_args})
    task_dirs = temperature_press_mdarg_lammps(
        structure_dirs, temperature_list, press_list, lammps_args
    )
    write_yaml(task_dirs, f"{work_dir}/task_dirs.yml")

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
    from utilal_uncertainty import select_candidate_SevenNet, simple_lmpdump2extxyz
    from glob import glob

    lmpdump_file = "traj_md_label.lmpdump"
    extxyz_file = "{FILE_TRAJ_MD}"

    ### Covert lmpdump to extxyz
    simple_lmpdump2extxyz(lmpdump_file, extxyz_file)

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


class OperAlmdLammpsSevennet(RemoteOperation):
    """This class runs LAMMPS md for a list of structures in `task_dirs`."""

    def __init__(self, work_dir, pdict, multi_mdict, mdict_prefix="md"):
        super().__init__(work_dir, pdict, multi_mdict, mdict_prefix)
        self.op_name = "LAMMPS md"
        ### To filter already run structures
        self.has_files = ["conf.lmpdata"]
        self.no_files = ["committee_error.txt"]
        return

    def prepare(self):
        """This function does:
        - Prepare the task_list
        - Prepare fordward & backward files
        - Prepare commandlist_list for multi-remote submission
        """
        ### Prepare fordward & backward files
        self.forward_common_files = [DIR_TMP_MODEL]  # in work_dir
        self.forward_files = ["conf.lmpdata", RUNFILE_LAMMPS]  # all files in task_dirs
        self.backward_files = [
            "*_stress_value.txt",
            "committee_*",
            "*.extxyz",
        ]  # FILE_TRAJ_MD, FILE_TRAJ_MD_CANDIDATE,

        ### Prepare commandlist_list for multi-remote submission
        mdict_list = self.mdict_list
        commandlist_list = []
        for mdict in mdict_list:
            command_list = []
            md_command = mdict.get("command", "lmp_mpi")
            md_command = f"{md_command} -in {RUNFILE_LAMMPS}"
            command_list.append(md_command)

            ### compute committee_error
            command = (
                f"""(python ../{DIR_TMP_MODEL}/cli_committee_sevenn.py || :)"""  # not care if error
            )
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
def _sampling_report(work_dir: str, task_dirs: str) -> None:
    """Generate sampling report for all task_dirs."""
    not_run_structs = filter_dirs(task_dirs, no_files=["committee_judge_summary.txt"])
    run_structs = filter_dirs(task_dirs, has_files=["committee_judge_summary.txt"])
    not_ok_structs = [
        p
        for p in run_structs
        if (_sampling_evaluation(f"{p}/committee_judge_summary.txt") == "notok")
    ]
    bad_structs = [
        p
        for p in run_structs
        if (_sampling_evaluation(f"{p}/committee_judge_summary.txt") == "bad")
    ]
    bad_structs.extend(not_run_structs)

    ### Write report
    [Path(f).unlink() for f in collect_files(work_dir, patterns=["md_warning_*.txt"])]

    if len(not_ok_structs) > 0:
        filename = f"{work_dir}/md_warning_{len(not_ok_structs)}_not_enough_sampling.txt"
        write_yaml(natsorted(not_ok_structs), filename)
        logger.warning(
            f"There are {len(not_ok_structs)} structures need more sampling, see file:\n\t'{filename}'"
        )
    if len(bad_structs) > 0:
        filename = f"{work_dir}/md_warning_{len(bad_structs)}_bad_sampling.txt"
        write_yaml(natsorted(bad_structs), filename)
        logger.warning(
            f"There are {len(bad_structs)} structures with bad sampling, see file:\n\t'{filename}'"
        )
    return


def _sampling_evaluation(summary_file: str) -> str:
    """
    Check if the sampling result is good enough.
    Args:
        file (str): The text file summarizing the sampling result.
    Returns:
        str: "ok", "notok", or "bad"
    """
    d = read_yaml(summary_file)
    result = "ok"
    if (d["inaccurates"] >= d["accurates"]) and (d["inaccurates"] >= d["candidates"]):
        if d["accurates"] == 0 and d["candidates"] == 0:
            result = "bad"
        else:
            result = "notok"
    return result


def temperature_press_mdarg_lammps(
    struct_dirs: list,
    temperature_list: list = [],
    press_list: list = [],
    lammps_argdict: dict = {},
) -> list:
    """
    Generate the task_dirs for ranges of temperatures and stresses.

    Args:
        struct_dirs (list): List of dirs contains configuration files.
        temperature_list (list): List of temperatures.
        press_list (list): List of stresses.
        lammps_argdict (dict): See [lammps.md schema](https://thangckt.github.io/alff_doc/schema/config_lammps/)
    """
    lammps_args = deepcopy(lammps_argdict)  # avoid modifying original dict
    lammps_args["structure"].update({"read_data": "conf.lmpdata"})
    list_pair_coeff_original = deepcopy(lammps_args["structure"]["pair_coeff"])  # to avoid changing
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
                        ### Convert extxyz to lammps_data
                        atom_names, pbc = extxyz2lmpdata(
                            extxyz_file=f"{new_dir}/{FILE_FRAME_unLABEL}",
                            lmpdata_file=f"{new_dir}/conf.lmpdata",
                            atom_style="atomic",
                        )
                        # TODO need to rotate the stress tensor
                        ### udpate lammps_md_args
                        list_pair_coeff = [
                            txt.replace("placeholder_for_atomnames", " ".join(atom_names))
                            for txt in list_pair_coeff_original
                        ]
                        lammps_args["structure"]["pair_coeff"] = list_pair_coeff
                        lammps_args["structure"]["pbc"] = pbc
                        lammps_args["extra"] = {"output_script": f"{new_dir}/{RUNFILE_LAMMPS}"}

                        tmp_md = {"temp": temp, "press": press, "ensemble": "NPT"}
                        lammps_args["md"].update(tmp_md)

                        validate_config(config_dict=lammps_args, schema_file=SCHEMA_LAMMPS)
                        write_yaml(lammps_args, f"{new_dir}/{FILE_ARG_LAMMPS}")
                        tmp_lammps_args = process_lammps_argdict(lammps_args)
                        generate_script_lammps_md(**tmp_lammps_args)
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
                    ### Convert extxyz to lammps_data
                    atom_names, pbc = extxyz2lmpdata(
                        extxyz_file=f"{new_dir}/{FILE_FRAME_unLABEL}",
                        lmpdata_file=f"{new_dir}/conf.lmpdata",
                        atom_style="atomic",
                    )
                    ### udpate lammps_md_args
                    list_pair_coeff = [
                        txt.replace("placeholder_for_atomnames", " ".join(atom_names))
                        for txt in list_pair_coeff_original
                    ]
                    lammps_args["structure"]["pair_coeff"] = list_pair_coeff
                    lammps_args["structure"]["pbc"] = pbc
                    lammps_args["extra"] = {"output_script": f"{new_dir}/{RUNFILE_LAMMPS}"}

                    tmp_md = {"temp": temp, "ensemble": "NVT"}
                    lammps_args["md"].update(tmp_md)

                    validate_config(config_dict=lammps_args, schema_file=SCHEMA_LAMMPS)
                    write_yaml(lammps_args, f"{new_dir}/{FILE_ARG_LAMMPS}")
                    tmp_lammps_args = process_lammps_argdict(lammps_args)
                    generate_script_lammps_md(**tmp_lammps_args)
                    ### save path
                    task_dirs.append(new_dir)
                    counter += 1
        else:
            new_dir = f"{struct_path}"
            # new_dir = new_dir.replace("idx", f"md_{counter:{FMT_STRUCT}}_id")
            new_dir = new_dir.replace("idx", "md_id")  # remove counter
            ### Convert extxyz to lammps_data
            atom_names, pbc = extxyz2lmpdata(
                extxyz_file=f"{new_dir}/{FILE_FRAME_unLABEL}",
                lmpdata_file=f"{new_dir}/conf.lmpdata",
                atom_style="atomic",
            )
            ### udpate lammps_md_args
            list_pair_coeff = [
                txt.replace("placeholder_for_atomnames", " ".join(atom_names))
                for txt in list_pair_coeff_original
            ]
            lammps_args["structure"]["pair_coeff"] = list_pair_coeff
            lammps_args["structure"]["pbc"] = pbc
            lammps_args["extra"] = {"output_script": f"{new_dir}/{RUNFILE_LAMMPS}"}

            tmp_md = {"ensemble": "NVE"}
            lammps_args["md"].update(tmp_md)

            validate_config(config_dict=lammps_args, schema_file=SCHEMA_LAMMPS)
            write_yaml(lammps_args, f"{new_dir}/{FILE_ARG_LAMMPS}")
            tmp_lammps_args = process_lammps_argdict(lammps_args)
            generate_script_lammps_md(**tmp_lammps_args)
            ### save path
            task_dirs.append(new_dir)
            counter += 1
    ### delete the original dirs (replaced by temp_press dirs)
    _ = [remove_dirs(p) for p in struct_dirs if p not in task_dirs]
    return task_dirs
