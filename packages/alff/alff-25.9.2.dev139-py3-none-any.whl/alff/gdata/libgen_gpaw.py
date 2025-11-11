from copy import deepcopy
from pathlib import Path

from thkit.config import validate_config
from thkit.io import read_yaml, write_yaml
from thkit.path import collect_files, copy_file, filter_dirs, remove_files_in_paths

from alff.al.libal_md_ase import temperature_press_mdarg_ase
from alff.base import RemoteOperation
from alff.gdata.util_dataset import remove_key_in_extxyz
from alff.util.key import (
    FILE_ARG_ASE,
    FILE_FRAME_LABEL,
    FILE_TRAJ_LABEL,
    SCHEMA_ASE_RUN,
    SCRIPT_ASE_PATH,
    FILE_FRAME_unLABEL,
)

"""Note:
- work_dir is a folder relative to the run_dir
- task_dirs are folders relative to the work_dir
"""


#####SECTION Classes for GPAW data generation
#####ANCHOR Stage 1 - GPAW optimize initial structure
class OperGendataGpawOptimize(RemoteOperation):
    """This class does GPAW optimization for a list of structures in `task_dirs`."""

    def __init__(self, work_dir, pdict, multi_mdict, mdict_prefix="gpaw"):
        super().__init__(work_dir, pdict, multi_mdict, mdict_prefix)
        self.op_name = "GPAW optimize"
        self.calc_name = "gpaw"

        ### To filter already run structures
        self.has_files = [FILE_FRAME_unLABEL]
        self.no_files = [FILE_FRAME_LABEL]
        return

    def prepare(self):
        """This function does:
        - Prepare ase_args for GPAW and gpaw_run_file. Note: Must define `pdict.dft.calc_args.gpaw{}` for this function.
        - Prepare the task_list
        - Prepare fordward & backward files
        - Prepare commandlist_list for multi-remote submission
        """
        work_dir = self.work_dir
        pdict = self.pdict

        # calc_args = self.calc_info["calc_args"]
        # optimize_args = self.calc_info["optimize_args"]

        ### Prepare ase_args
        ase_args = deepcopy(pdict.get("dft"))
        ase_args.pop("md", None)  # remove the MD key
        ase_args.setdefault("structure", {})["from_extxyz"] = f"{FILE_FRAME_unLABEL}"
        # for p in dft_task_dirs:
        #     write_yaml(ase_args, f"{p}/{FILE_ARG_ASE}")
        validate_config(config_dict=ase_args, schema_file=SCHEMA_ASE_RUN)
        write_yaml(ase_args, f"{work_dir}/{FILE_ARG_ASE}")

        ### GPAW_runfile
        self.RUNFILE_GPAW = "cli_gpaw_optimize.py"
        self._prepare_runfile_gpaw()
        return

    def _prepare_runfile_gpaw(self):
        work_dir = self.work_dir
        ### GPAW_runfile
        RUNFILE_GPAW = self.RUNFILE_GPAW
        _ = copy_file(
            f"{SCRIPT_ASE_PATH}/{RUNFILE_GPAW}",
            f"{work_dir}/{RUNFILE_GPAW}",
        )

        ### Prepare fordward & backward files
        self.forward_common_files = [RUNFILE_GPAW, FILE_ARG_ASE]  # in work_dir
        self.forward_files = [FILE_FRAME_unLABEL]  # files in task_path
        self.backward_files = [FILE_FRAME_LABEL, "calc*.txt", "*.log"]

        ### Prepare commandlist_list for multi-remote submission
        mdict_list = self.mdict_list
        commandlist_list = []
        for mdict in mdict_list:
            command_list = []
            dft_cmd = mdict.get("command", "python")
            dft_cmd = f"{dft_cmd} ../{RUNFILE_GPAW} ../{FILE_ARG_ASE}"  # `../` to run file in common directory
            command_list.append(dft_cmd)
            commandlist_list.append(command_list)
        self.commandlist_list = commandlist_list
        return

    def postprocess(self):
        """This function does:
        - Remove unlabeled .extxyz files, just keep the labeled ones.
        """
        task_dirs = self.task_dirs
        ### Remove unlabeled extxyz files
        unlabel_paths = filter_dirs(task_dirs, has_files=[FILE_FRAME_unLABEL, FILE_FRAME_LABEL])
        remove_files_in_paths(files=[FILE_FRAME_unLABEL], paths=unlabel_paths)
        ### Remove unwanted keys in extxyz files
        extxyz_dirs = filter_dirs(task_dirs, has_files=[FILE_FRAME_LABEL])
        extxyz_files = [f"{d}/{FILE_FRAME_LABEL}" for d in extxyz_dirs]
        _ = [
            remove_key_in_extxyz(f, ["free_energy", "magmom", "magmoms", "dipole", "momenta"])
            for f in extxyz_files
        ]
        return


#####ANCHOR Stage 3 - run DFT singlepoint
class OperGendataGpawSinglepoint(OperGendataGpawOptimize):
    def __init__(self, work_dir, pdict, multi_mdict, mdict_prefix="gpaw"):
        super().__init__(work_dir, pdict, multi_mdict, mdict_prefix)
        self.op_name = "GPAW singlepoint"
        return

    def prepare(self):
        work_dir = self.work_dir
        pdict = self.pdict

        ### Prepare ase_args
        ase_args = deepcopy(pdict.get("dft"))
        ase_args.pop("md", None)  # remove the MD key
        ase_args.setdefault("structure", {})["from_extxyz"] = f"{FILE_FRAME_unLABEL}"
        write_yaml(ase_args, f"{work_dir}/{FILE_ARG_ASE}")
        validate_config(config_dict=ase_args, schema_file=SCHEMA_ASE_RUN)

        ### GPAW_runfile
        self.RUNFILE_GPAW = "cli_gpaw_singlepoint.py"
        self._prepare_runfile_gpaw()
        return


#####ANCHOR Stage 3 - run AIMD
class OperGendataGpawAIMD(OperGendataGpawOptimize):
    def __init__(self, work_dir, pdict, multi_mdict, mdict_prefix="gpaw"):
        super().__init__(work_dir, pdict, multi_mdict, mdict_prefix)
        self.op_name = "GPAW aimd"
        return

    def prepare(self):
        """Refer to the `pregen_gpaw_optimize()` function.
        Note:
        - structure_dirs: contains the optimized structures without scaling.
        - strain_structure_dirs: contains the scaled structures.
        """
        work_dir = self.work_dir
        pdict = self.pdict
        ### Prepare ASE_arg for ranges of temperature and stress
        ase_args = deepcopy(pdict.get("dft"))  # deepcopy to avoid modifying `pdict`
        space_args = pdict.get("sampling_space", {})

        ### Prepare task paths scaled structures
        strain_structure_dirs = read_yaml(f"{work_dir}/strain_structure_dirs.yml")
        strain_structure_dirs = filter_dirs(
            strain_structure_dirs,
            has_files=[FILE_FRAME_unLABEL],
            no_files=[FILE_TRAJ_LABEL],
        )  # eliminate the labelled structures from previous runs

        strain_args = space_args.get("strain", {})
        task_dirs1 = []
        if strain_args:
            temperature_list1 = strain_args.get("temps", [])
            task_dirs1 = temperature_press_mdarg_ase(
                strain_structure_dirs, temperature_list1, [], ase_args
            )

        ### Prepare task paths for unscaled structures:
        ### generate from the optimized structures (labelled), so need to copy the unlabelled ones.
        ## normlize the cell to avoid error in NPT run
        temp_press_args = space_args.get("temp_press", {})
        temperature_list2 = temp_press_args.get("temps", [])
        press_list = temp_press_args.get("pressures", [])
        task_dirs2 = []
        if temp_press_args:
            structure_dirs = read_yaml(f"{work_dir}/structure_dirs.yml")
            structure_files = [
                copy_file(f"{p}/{FILE_FRAME_LABEL}", f"{p}_tmp/{FILE_FRAME_unLABEL}")
                for p in structure_dirs
            ]
            structure_dirs = [Path(f).parent for f in structure_files]
            # _ = [make_triangular_cell_extxyz(f"{p}/{FILE_FRAME_unLABEL}") for p in structure_dirs]
            task_dirs2 = temperature_press_mdarg_ase(
                structure_dirs, temperature_list2, press_list, ase_args
            )

        task_dirs = task_dirs1 + task_dirs2
        write_yaml(set(task_dirs), f"{work_dir}/task_dirs.yml")

        ### GPAW_runfile
        self.RUNFILE_GPAW = "cli_gpaw_aimd.py"
        self._prepare_runfile_gpaw()
        return

    def postprocess(self):
        """Refer to the `postgen_gpaw_optimize()` function."""
        task_dirs = self.task_dirs
        ### Remove unlabeled extxyz files
        unwant_files = collect_files(task_dirs, patterns=[FILE_FRAME_unLABEL])
        _ = [Path(f).unlink() for f in unwant_files]
        ### Remove unwanted keys in extxyz files
        extxyz_files = collect_files(task_dirs, patterns=[FILE_TRAJ_LABEL])
        _ = [
            remove_key_in_extxyz(f, ["free_energy", "magmom", "magmoms", "dipole", "momenta"])
            for f in extxyz_files
        ]
        return


#####SECTION Classes for GPAW active learning
class OperAlGpawSinglepoint(OperGendataGpawOptimize):
    def __init__(self, work_dir, pdict, multi_mdict, mdict_prefix="gpaw"):
        super().__init__(work_dir, pdict, multi_mdict, mdict_prefix)
        self.op_name = "GPAW singlepoint"
        return

    def prepare(self):
        work_dir = self.work_dir
        pdict = self.pdict

        ### Prepare ase_args
        ase_args = deepcopy(pdict.get("dft"))
        ase_args.pop("md", None)  # remove the MD key
        ase_args.setdefault("structure", {})["from_extxyz"] = f"{FILE_FRAME_unLABEL}"
        write_yaml(ase_args, f"{work_dir}/{FILE_ARG_ASE}")
        validate_config(config_dict=ase_args, schema_file=SCHEMA_ASE_RUN)

        ### GPAW_runfile
        self.RUNFILE_GPAW = "cli_gpaw_singlepoint.py"
        self._prepare_runfile_gpaw()
        return

    def postprocess(self):
        """Do post DFT tasks"""
        ### Ref collect data in gendata
        # Nothing to do here
        return
