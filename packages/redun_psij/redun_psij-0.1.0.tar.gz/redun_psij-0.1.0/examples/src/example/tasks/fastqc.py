import logging
import os.path
from dataclasses import dataclass
from redun import task, File

from redun_psij import run_job_n, JobNSpec, ExpectedPaths, JobContext
from example.util import baseroot

logger = logging.getLogger(__name__)

FASTQC_TOOL_NAME = "fastqc"

redun_namespace = "example.tasks"


@dataclass
class FastqcOutput:
    html: File
    zip: File


def fastqc_zip_files(fastqc_outputs: list[FastqcOutput]) -> list[File]:
    return [fastqc_output.zip for fastqc_output in fastqc_outputs]


def fastqc_zip_file(fastqc_output: FastqcOutput) -> File:
    return fastqc_output.zip


# keys for job spec
_HTML = "html"
_ZIP = "zip"


def _fastqc_job_spec(
    in_path: str, out_dir: str, job_context: JobContext, num_threads: int = 2
) -> JobNSpec:
    basename = os.path.basename(in_path).removesuffix(".gz").removesuffix(".fastq")
    log_path = os.path.join(
        out_dir,
        "%s_fastqc.log"
        % os.path.basename(in_path).removesuffix(".gz").removesuffix(".fastq"),
    )
    zip_out_path = os.path.join(out_dir, "%s%s" % (basename, "_fastqc.zip"))
    html_out_path = os.path.join(out_dir, "%s%s" % (basename, "_fastqc.html"))
    return JobNSpec(
        tool=FASTQC_TOOL_NAME,
        args=[
            "fastqc",
            "-t",
            str(num_threads),
            "-o",
            out_dir,
            in_path,
        ],
        stdout_path=log_path,
        stderr_path=log_path,
        custom_attributes=job_context.custom_attributes,
        cwd=out_dir,
        expected_paths=ExpectedPaths(
            required={_HTML: html_out_path, _ZIP: zip_out_path}
        ),
    )


@task()
def fastqc_one(fastq_file: File, out_dir: str, job_context: JobContext) -> FastqcOutput:
    """Run fastqc on a single file."""
    os.makedirs(out_dir, exist_ok=True)

    result = run_job_n(
        _fastqc_job_spec(
            in_path=fastq_file.path,
            out_dir=out_dir,
            job_context=job_context.with_sub(baseroot(fastq_file.path)),
        )
    )

    return FastqcOutput(
        html=result.expected_files[_HTML],
        zip=result.expected_files[_ZIP],
    )
