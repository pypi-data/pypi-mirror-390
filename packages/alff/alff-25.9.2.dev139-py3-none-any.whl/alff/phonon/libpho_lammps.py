from copy import deepcopy
from pathlib import Path

from asext.io.readwrite import extxyz2lmpdata, lmpdump2extxyz, read_extxyz
from thkit.config import validate_config
from thkit.io import write_yaml
from thkit.path import filter_dirs, remove_files_in_paths

from alff.pes.libpes_lammps import OperPESLammpsOptimize
from alff.util.key import (
    FILE_ARG_LAMMPS,
    FILE_FRAME_LABEL,
    RUNFILE_LAMMPS,
    SCHEMA_LAMMPS,
    FILE_FRAME_unLABEL,
)
from alff.util.script_lammps.lammps_code_creator import (
    generate_script_lammps_minimize,
    generate_script_lammps_singlepoint,
    process_lammps_argdict,
)

"""
Notes:
- use `deepcopy` to avoid changing the original dict.
"""


#####ANCHOR Stage 1 - LAMMPS optimize initial structure
class OperPhononLammpsOptimize(OperPESLammpsOptimize):
    ### Can use the same class as OperPESLammpsOptimize.
    ### Notes: Phonon caclulation does not need stress tensor.
    def __init__(self, work_dir, pdict, multi_mdict, mdict_prefix="lammps"):
        super().__init__(work_dir, pdict, multi_mdict, mdict_prefix)
        return


#####ANCHOR Stage 3 - scale and relax
class OperPhononLammpsOptimizeFixbox(OperPESLammpsOptimize):
    """Only need to redefine the prepare() method, to fix box during optimization."""

    def __init__(self, work_dir, pdict, multi_mdict, mdict_prefix="lammps"):
        super().__init__(work_dir, pdict, multi_mdict, mdict_prefix)
        self.op_name = "LAMMPS optimize fixed box"
        return

    def prepare(self):
        """This function does:
        - Prepare lammps_optimize and lammps_input files.
            - Convert extxyz to lmpdata.
            - Copy potential file to work_dir.

        - Prepare the task_list
        - Prepare fordward & backward files
        - Prepare commandlist_list for multi-remote submission
        """
        calc_args = self.pdict["calculator"]["calc_args"]["lammps"]
        optimize_args = self.pdict["optimize_args"]["lammps"]

        ### Prepare lammps_arg for MS fixbox
        lammps_args = {}
        lammps_args["optimize"] = optimize_args
        lammps_args["optimize"].pop("press", None)  # remove press for fixed cell
        lammps_args["structure"] = deepcopy(calc_args)
        origin_pair_coeff_list = deepcopy(lammps_args["structure"].get("pair_coeff", []))

        ### Convert EXTXYZ to LAMMPS data file
        task_dirs = self.task_dirs
        for tdir in task_dirs:
            if Path(f"{tdir}/{FILE_FRAME_LABEL}").is_file():
                continue  # this structure is already labeled, skip it

            lmpdata_name = FILE_FRAME_unLABEL.replace(".extxyz", ".lmpdata")
            lammps_args["structure"]["read_data"] = lmpdata_name
            atom_names, pbc = extxyz2lmpdata(
                extxyz_file=f"{tdir}/{FILE_FRAME_unLABEL}",
                lmpdata_file=f"{tdir}/{lmpdata_name}",
                atom_style="atomic",
            )
            lammps_args["structure"]["pbc"] = pbc
            ### Auto assign atom_names in pair_coeff
            auto_atom_names = calc_args.get("auto_atom_names", False)
            if auto_atom_names:
                pair_coeff_list = [
                    f"{line} {' '.join(atom_names)}" for line in origin_pair_coeff_list
                ]
                lammps_args["structure"]["pair_coeff"] = pair_coeff_list

            lammps_args["extra"] = {"output_script": f"{tdir}/{RUNFILE_LAMMPS}"}
            validate_config(config_dict=lammps_args, schema_file=SCHEMA_LAMMPS)
            write_yaml(lammps_args, f"{tdir}/{FILE_ARG_LAMMPS}")
            tmp_lammps_args = process_lammps_argdict(lammps_args)
            generate_script_lammps_minimize(**tmp_lammps_args)

        ### Copy runfile
        self._prepare_runfile_lammps()
        return


#####ANCHOR Stage 4 - run MD singlepoint on supercell
class OperPhononLammpsSinglepoint(OperPESLammpsOptimize):
    """Class to run LAMMPS singlepoint calculation, used for phonon calculation.
    Notes: the .postprocess() method returns `set_of_forces`, a 3D array.
    """

    def __init__(self, work_dir, pdict, multi_mdict, mdict_prefix="lammps"):
        super().__init__(work_dir, pdict, multi_mdict, mdict_prefix)
        self.op_name = "LAMMPS optimize"
        ### To filter already run structures
        self.has_files = [FILE_FRAME_unLABEL]
        self.no_files = ["frame_label.lmpdump"]
        return

    def prepare(self):
        """This function does:
        - Prepare lammps_optimize and lammps_input files.
            - Convert extxyz to lmpdata.
            - Copy potential file to work_dir.

        - Prepare the task_list
        - Prepare fordward & backward files
        - Prepare commandlist_list for multi-remote submission
        """
        calc_args = self.pdict["calculator"]["calc_args"]["lammps"]
        optimize_args = self.pdict["optimize_args"]["lammps"]

        ### Prepare lammps_arg for MS simulation
        lammps_args = {}
        lammps_args["structure"] = deepcopy(calc_args)
        origin_pair_coeff_list = deepcopy(lammps_args["structure"].get("pair_coeff", []))

        ### Convert EXTXYZ to LAMMPS data file
        task_dirs = self.task_dirs
        for tdir in task_dirs:
            if Path(f"{tdir}/{FILE_FRAME_LABEL}").is_file():
                continue  # this structure is already labeled, skip it

            lmpdata_name = FILE_FRAME_unLABEL.replace(".extxyz", ".lmpdata")
            lammps_args["structure"]["read_data"] = lmpdata_name
            atom_names, pbc = extxyz2lmpdata(
                extxyz_file=f"{tdir}/{FILE_FRAME_unLABEL}",
                lmpdata_file=f"{tdir}/{lmpdata_name}",
                atom_style="atomic",
            )
            lammps_args["structure"]["pbc"] = pbc
            ### Auto assign atom_names in pair_coeff
            auto_atom_names = calc_args.get("auto_atom_names", False)
            if auto_atom_names:
                pair_coeff_list = [
                    f"{line} {' '.join(atom_names)}" for line in origin_pair_coeff_list
                ]
                lammps_args["structure"]["pair_coeff"] = pair_coeff_list

            lammps_args["extra"] = {"output_script": f"{tdir}/{RUNFILE_LAMMPS}"}
            validate_config(config_dict=lammps_args, schema_file=SCHEMA_LAMMPS)
            write_yaml(lammps_args, f"{tdir}/{FILE_ARG_LAMMPS}")
            tmp_lammps_args = process_lammps_argdict(lammps_args)
            generate_script_lammps_singlepoint(**tmp_lammps_args)

        ### Copy runfile
        self._prepare_runfile_lammps()
        return

    def postprocess(self):
        """This function does:
        - Remove unlabeled .extxyz files, just keep the labeled ones.
        - Convert LAMMPS output to extxyz_labeled.
        """
        task_dirs = self.task_dirs
        ### Convert LAMMPS output to extxyz_labeled
        task_dirs = filter_dirs(task_dirs, has_files=[FILE_FRAME_unLABEL, "frame_label.lmpdump"])
        for task_path in task_dirs:
            lmpdump2extxyz(
                lmpdump_file=f"{task_path}/frame_label.lmpdump",
                extxyz_file=f"{task_path}/{FILE_FRAME_LABEL}",
                original_cell_file=f"{task_path}/conf.lmpdata.original_cell",
            )

        ### Remove unlabeled extxyz files
        unlabel_dirs = filter_dirs(task_dirs, has_files=[FILE_FRAME_unLABEL, FILE_FRAME_LABEL])
        remove_files_in_paths(files=[FILE_FRAME_unLABEL], paths=unlabel_dirs)

        ### Remove lammps input files
        # _ = [Path(f"{p}/{RUNFILE_LAMMPS}").unlink() for p in unlabel_dirs]
        remove_files_in_paths(files=["conf.lmpdata"], paths=unlabel_dirs)

        ### Collect forces to list_of_forces
        labeled_dirs = filter_dirs(task_dirs, has_files=[FILE_FRAME_LABEL])
        set_of_forces = []
        for d in labeled_dirs:
            list_struct = read_extxyz(f"{d}/{FILE_FRAME_LABEL}")
            forces = [struct.calc.results["forces"].tolist() for struct in list_struct]
            set_of_forces.extend(forces)
        # can save by `np.save("set_of_forces.npy", set_of_forces)`
        return set_of_forces
