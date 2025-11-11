from thkit.io import write_yaml
from thkit.path import collect_files, make_dir_ask_backup

from alff.al.active_learning import _get_engines
from alff.al.mlp_engine.mlp_sevenn import OperAltrainSevennet, pretrain_sevenn
from alff.base import Workflow, logger
from alff.gdata.util_dataset import merge_extxyz_files
from alff.util.key import (
    DIR_TMP_DATA,
    DIR_TRAIN,
    FILE_COLLECT_DATA,
    FILE_DATAPATH,
    SCHEMA_FINETUNE,
)


#####ANCHOR support functions
def stage_train(pdict, mdict):
    """This function does:
    - collect data files
    - prepare training args based on MLP engine
    """
    train_param = pdict["train"]

    ### Create work_dir folder
    work_dir = f"{DIR_TRAIN}"
    make_dir_ask_backup(work_dir)

    logger.info("Collecting data files")
    #### Collect data files
    data_files = collect_files(
        train_param["init_data_paths"], patterns=["*.extxyz", "*.xyz"]
    )  # relative to run_dir
    data_files = list(set(data_files))  # remove duplicates
    assert len(data_files) > 0, "No data files found"
    write_yaml(data_files, f"{work_dir}/{FILE_DATAPATH}")

    ## Copy data files to tmp-folder: `copied_data/`
    merge_extxyz_files(
        extxyz_files=data_files, outfile=f"{work_dir}/{DIR_TMP_DATA}/{FILE_COLLECT_DATA}"
    )

    ### Prepare train args
    mlp_engine, _ = _get_engines(pdict)
    if mlp_engine == "sevenn":
        pretrain_sevenn(work_dir, pdict, mdict)
        op = OperAltrainSevennet(work_dir, pdict, mdict, mdict_prefix="train")
        op.prepare()
        op.run()
        op.postprocess()
    return


#####ANCHOR main loop
class WorkflowFinetune(Workflow):
    """Workflow for fine-tuning the existed ML models or train a new ML model.
    Needs to override `self.stage_list` in base class, because the stages are fixed here.
    """

    def __init__(self, param_file: str, machine_file: str):
        super().__init__(param_file, machine_file, SCHEMA_FINETUNE)
        self.stage_map = {
            "training": stage_train,
        }
        self.wf_name = "FINE-TUNING"
        self.stage_list = ["training"]  # override the stage_list
        return
