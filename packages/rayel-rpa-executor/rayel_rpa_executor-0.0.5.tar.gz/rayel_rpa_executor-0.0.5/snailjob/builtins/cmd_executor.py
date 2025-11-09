import json
import subprocess

from ..args import JobArgs
from ..deco import job
from ..schemas import ExecuteResult
from ._script_executor import AbstractScriptExecutor, ScriptParams


class AbstractCMDExecutor(AbstractScriptExecutor):
    def get_script_name(self, job_id: int) -> str:
        return f"cmd_{job_id}.bat"

    def get_run_command(self) -> str:
        return "cmd.exe"

    def get_script_process_builder(self, script_path: str) -> subprocess.Popen:
        return subprocess.Popen([self.get_run_command(), "/c", script_path])


class SnailJobCMDExecutor(AbstractCMDExecutor):
    def job_execute(self, job_args: JobArgs) -> ExecuteResult:
        job_params = job_args.job_params
        script_params = ScriptParams(**json.loads(job_params))
        return self.process(job_args.job_id, script_params)


@job("snailJobCMDJobExecutor")
def executor(job_args: JobArgs) -> ExecuteResult:
    return SnailJobCMDExecutor().job_execute(job_args)
