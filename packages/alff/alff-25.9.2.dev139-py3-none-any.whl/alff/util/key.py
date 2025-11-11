import time

from alff import ALFF_ROOT

#####ANCHOR logging
time_str = time.strftime("%y%m%d_%H%M%S")  # "%y%b%d" "%Y%m%d"
DIR_LOG = "log"
FILE_LOG_ALFF = f"{DIR_LOG}/{time_str}_alff.log"
# FILE_LOG_DISPATCH = FILE_LOG_ALFF  # FILE_LOG_ALFF.replace("alff", "dispatch")
FILE_ITERLOG = "_alff.iter"


#####SECTION Keys
## Some keys are used in multiple processes, so they are defined here for consistency and easy modification.
#####ANCHOR Keys for active learning
### folder names
DIR_TRAIN = "00_train"
DIR_MD = "01_md"
DIR_DFT = "02_dft"
DIR_DATA = "03_data"
DIR_TMP = "tmp_dir"
DIR_TMP_DATA = "copy_data"
DIR_TMP_MODEL = "copy_model"

FILE_DATAPATH = "data_paths.yml"
FILE_MODELPATH = "model_paths.yml"
FILE_CHECKPOINT_PATH = "checkpoint_paths.yml"
FILE_ARG_TRAIN = "arg_train.yml"

FILE_TRAJ_MD = "traj_md.extxyz"  # trajectory by MD, no label
FILE_TRAJ_MD_CANDIDATE = FILE_TRAJ_MD.replace(".extxyz", "_candidate.extxyz")

FILE_ITER_DATA = "data_label.extxyz"
FILE_COLLECT_DATA = "collect_data_label.extxyz"

### format
FMT_ITER = "04d"
FMT_STAGE = "02d"
FMT_MODEL = "02d"
FMT_STRUCT = "05d"
FMT_TASK_MD = "06d"
FMT_TASK_DFT = "06d"

### templates/schema
RUNFILE_LAMMPS = "cli_lammps.lmp"
FILE_ARG_LAMMPS = "arg_lammps.yml"
FILE_ARG_ASE = "arg_ase.yml"

SCRIPT_ASE_PATH = f"{ALFF_ROOT}/util/script_ase"
SCHEMA_ASE_RUN = f"{ALFF_ROOT}/util/script_ase/schema_ase_run.yml"
SCHEMA_LAMMPS = f"{ALFF_ROOT}/util/script_lammps/schema_lammps.yml"

SCHEMA_ACTIVE_LEARN = f"{ALFF_ROOT}/al/schema_active_learn.yml"
SCHEMA_FINETUNE = f"{ALFF_ROOT}/al/schema_finetune.yml"


#####ANCHOR keys for data_generation
### folder names
DIR_MAKE_STRUCT = "00_make_structure"
DIR_STRAIN = "01_strain"
DIR_GENDATA = "02_gendata"

FILE_FRAME_unLABEL = "conf.extxyz"
FILE_FRAME_LABEL = "conf_label.extxyz"
FILE_TRAJ_LABEL = "traj_label.extxyz"  # trajectory by DFT aimd, with label

### templates/schema
SCHEMA_ASE_BUILD = f"{ALFF_ROOT}/util/script_ase/schema_ase_build.yml"
SCHEMA_GENDATA = f"{ALFF_ROOT}/gdata/schema_gendata.yml"
SCHEMA_PHONON = f"{ALFF_ROOT}/phonon/schema_phonon.yml"
SCHEMA_ELASTIC = f"{ALFF_ROOT}/elastic/schema_elastic.yml"
SCHEMA_PES_SCAN = f"{ALFF_ROOT}/pes/schema_pes_scan.yml"


#####ANCHOR keys for phonon calculation
DIR_SUPERCELL = "01_supercell"
DIR_PHONON = "02_phonon"
FILE_PHONOPYwFORCES = "phonopy_with_forces.yml"


#####ANCHOR keys for elastic calculation
DIR_ELASTIC = "02_elastic"


#####ANCHOR keys for pes_scan
DIR_SCAN = "01_scan"
DIR_PES = "02_pes"


#####!SECTION
