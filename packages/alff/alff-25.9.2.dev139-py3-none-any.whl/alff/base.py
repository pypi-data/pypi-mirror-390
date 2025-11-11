import asyncio
from abc import ABC, abstractmethod
from pathlib import Path

from thkit.config import loadconfig, validate_config
from thkit.display import TextDecor
from thkit.io import read_yaml
from thkit.jobman.helper import _parse_multi_mdict, check_remote_connection, validate_machine_config
from thkit.jobman.submit import alff_submit_job_multi_remotes
from thkit.path import filter_dirs

from alff.util.key import FILE_LOG_ALFF, FMT_STAGE
from alff.util.tool import alff_info_shorttext, init_alff_logger

logger = init_alff_logger()


#####ANCHOR Baseclass for workflow
class Workflow(ABC):
    """Base class for workflows.

    Workflow is the central part of ALFF. Each workflow contains list of stages to be executed.

    Subclass should reimplement:
        - `__init__()`: initialize the workflow, need to override these attributes:
            - self.stage_map
            - self.wf_name
        - `run()`: the main function to run the workflow. The default implementation is a loop over stages in `self.stage_map`, just for simple workflow. For complex workflow (e.g. with iteration like active learning), need to reimplement the `.run()` function.

    Example:
        ```python
        class WorkflowExample(Workflow):
            def __init__(self, param_file: str, machine_file: str):
                super().__init__(param_file, machine_file, SCHEMA_EXAMPLE)
                self.stage_map = {
                    "stage_name1": stage_function1,
                    "stage_name2": stage_function2,
                    "stage_name3": stage_function3,
                }
                self.wf_name = "Name of the workflow"
                return
        ```

    Notes:
        - `mdict` in this class is a single dictionary containing multiple remote machines, and will be parsed as `mdict_list` in `RemoteOperation` class.
    """

    def __init__(self, param_file: str, machine_file: str, schema_file: str = ""):
        self.param_file = param_file
        self.machine_file = machine_file
        self.schema_file = schema_file
        self._validate_config()
        self.pdict = loadconfig(self.param_file)
        self.mdict = loadconfig(self.machine_file)
        self.stage_list = self._load_stage_list()
        self._check_remote_connection()

        ### Need to define in 'subclass.__init__()'
        self.stage_map = {}
        self.wf_name = "workflow_name"
        return

    def run(self):
        """The main function to run the workflow. This default implementation works for simple workflow,
        for more complex workflow (e.g. with iteration like active learning), need to reimplement this `.run()` function.
        """
        self._print_intro()

        stage_map = self.stage_map
        stage_list = self.stage_list
        ### main loop
        for i, (stage_name, stage_func) in enumerate(stage_map.items()):
            if stage_name in stage_list:
                logtext = f" stage_{i:{FMT_STAGE}}: {stage_name} "
                logger.info(TextDecor(logtext).fill_left(margin=20, length=52))
                stage_func(self.pdict, self.mdict)

        self._print_outro()
        return

    def _load_stage_list(self):
        stage_list = self.pdict.get("stages", [])
        return stage_list

    def _validate_config(self):
        validate_config(config_file=self.param_file, schema_file=self.schema_file)
        validate_machine_config(self.machine_file)
        return

    def _check_remote_connection(self):
        """Check connection to all remote machines defined in `machine_file`."""
        check_remote_connection(self.machine_file)
        return

    def _update_config(self):
        pdict = self.pdict if self.pdict is not None else {}
        mdict = self.mdict if self.mdict is not None else {}
        self.pdict = pdict.update(loadconfig(self.param_file))
        self.mdict = mdict.update(loadconfig(self.machine_file))
        return

    def _print_intro(self):
        print(TextDecor(alff_info_shorttext()).make_color("blue"))
        logger.info(f"Start {self.wf_name}")
        logger.info(f"Logfile: {FILE_LOG_ALFF}")
        return

    def _print_outro(self):
        logger.info("FINISHED !")
        return


#####ANCHOR Baseclass for remote operation
class RemoteOperation(ABC):
    """Base class for operations on remote machines.

    Each operation includes atleast 3 methods:
        - prepare
        - run
        - postprocess

    Subclass must reimplement these methods:
        - `__init__()`: initialize the operation, need to override these attributes:
        - `prepare()`: prepare all things needed for the run() method.
        - `postprocess()`: postprocess after the run() method.

    Notes:
        - Before using this class, must prepare file `work_dir/task_dirs.yml`
        - All paths (`work_dir`, `task_dirs`,...) are in POSIX format, and relative to `run_dir` (not `work_dir`).
        - All `abtractmethod` must be reimplemented in subclasses.
        - Do not change the `run()` method unless you know what you are doing.
    """

    def __init__(self, work_dir, pdict, multi_mdict, mdict_prefix=""):
        ### Need to reimplement in subclass __init__()
        self.op_name = "Name of the operation"
        ## To filter already run structures
        self.has_files: list[str] = []
        self.no_files: list[str] = []

        ### Need to reimplement in subclass prepare()
        self.commandlist_list: list[list[str]] = []
        self.forward_files: list[str] = []
        self.backward_files: list[str] = []
        self.forward_common_files: list[str] = []
        self.backward_common_files: list[str] = []  # rarely used

        ### Do not change this part
        self.work_dir = work_dir
        self.mdict_prefix: str = mdict_prefix
        self.pdict = pdict
        self.mdict_list = self._load_multi_mdict(multi_mdict)
        self.task_dirs = self._load_task_dirs()
        return

    @abstractmethod
    def prepare(self):
        """Prepare all things needed for the `run()` method."""
        pass

    def run(self):
        """Function to submit jobs to remote machines.
        Note:
            - Orginal `taks_dirs` is relative to `run_dir`, and should not be changed. But the sumbmission function needs `taks_dirs` relative path to `work_dir`, so we make temporary change here.
        """
        logger.info(f"Run remote operation [{self.op_name}]")

        task_dirs_need_run = self._filter_task_dirs()
        if len(task_dirs_need_run) == 0:
            logger.warning("No tasks found for remote jobs.")
            return
        else:
            logger.info(
                f"Select {len(task_dirs_need_run)}/{len(self.task_dirs)} tasks for remote run."
            )
        rel_task_dirs = [Path(p).relative_to(self.work_dir).as_posix() for p in task_dirs_need_run]

        ### Submit jobs
        asyncio.run(
            alff_submit_job_multi_remotes(
                mdict_list=self.mdict_list,
                commandlist_list=self.commandlist_list,
                work_dir=self.work_dir,
                task_dirs=rel_task_dirs,
                forward_files=self.forward_files,
                backward_files=self.backward_files,
                forward_common_files=self.forward_common_files,
                backward_common_files=self.forward_common_files,
                logger=logger,
            )
        )
        return

    @abstractmethod
    def postprocess(self):
        """Postprocess after the `run()` method."""
        pass

    def _load_task_dirs(self) -> list[str]:
        """Load task directories from `work_dir/task_dirs.yml`."""
        task_dirs_file = Path(self.work_dir) / "task_dirs.yml"
        if not task_dirs_file.exists():
            raise FileNotFoundError(f"File {task_dirs_file} not found. Please prepare it first.")
        task_dirs = read_yaml(task_dirs_file)
        return task_dirs

    def _load_multi_mdict(self, multi_mdict) -> list[dict]:
        """Load multiple mdicts from the mdict_list."""
        mdict_list = _parse_multi_mdict(multi_mdict, self.mdict_prefix)
        return mdict_list

    def _filter_task_dirs(self):
        """Function to filter already run structures."""
        task_dirs_need_run = filter_dirs(
            self.task_dirs,
            has_files=self.has_files,
            no_files=self.no_files,
        )
        return task_dirs_need_run


#####ANCHOR Support classes/functions
