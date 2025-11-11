import argparse

from alff.al.active_learning import WorkflowActiveLearning
from alff.al.finetune import WorkflowFinetune
from alff.elastic.elastic import WorkflowElastic
from alff.gdata.gendata import WorkflowGendata
from alff.pes.pes_scan import WorkflowPes
from alff.phonon.phonon import WorkflowPhonon


#####ANCHOR Processes
def alff_al():
    """CLI for active learning"""
    param_file, machine_file = get_cli_args()
    wf = WorkflowActiveLearning(param_file, machine_file)
    wf.run()
    return


def alff_finetune():
    """CLI for fine-tuning"""
    param_file, machine_file = get_cli_args()
    wf = WorkflowFinetune(param_file, machine_file)
    wf.run()
    return


def alff_gen():
    """CLI for data generation"""
    param_file, machine_file = get_cli_args()
    wf = WorkflowGendata(param_file, machine_file)
    wf.run()
    return


def alff_phonon():
    """CLI for phonon calculation"""
    param_file, machine_file = get_cli_args()
    wf = WorkflowPhonon(param_file, machine_file)
    wf.run()
    return


def alff_pes():
    """CLI for PES scanning calculation"""
    param_file, machine_file = get_cli_args()
    wf = WorkflowPes(param_file, machine_file)
    wf.run()
    return


def alff_elastic():
    """CLI for elastic constants calculation"""
    param_file, machine_file = get_cli_args()
    wf = WorkflowElastic(param_file, machine_file)
    wf.run()
    return


def convert_chgnet_to_xyz():
    """CLI for converting the MPCHGNet dataset to XYZ format"""
    from alff.gdata.convert_mpchgnet_to_xyz import run_convert

    run_convert()
    return


#####ANCHOR Helper functions
def get_cli_args():
    """Get arguments from the command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "param_file",
        type=str,
        help="The file contains setting parameters for the generator",
    )
    parser.add_argument(
        "machine_file",
        type=str,
        help="The file contains settings of the machine that running the generator",
    )
    args = parser.parse_args()
    param_file = args.param_file
    machine_file = args.machine_file
    return param_file, machine_file
