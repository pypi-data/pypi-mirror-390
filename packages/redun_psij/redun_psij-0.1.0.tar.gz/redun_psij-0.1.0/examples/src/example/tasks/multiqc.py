"""This module wraps MultiQC to generate a report from FastQC and BCLConvert reports."""

import logging
import os.path
from redun import task, File

from redun_psij import run_job_1, Job1Spec, JobContext

logger = logging.getLogger(__name__)

MULTIQC_TOOL_NAME = "multiqc"

redun_namespace = "example.tasks"


def _multiqc_job_spec(
    fastqc_in_paths: list[str],
    out_dir: str,
    out_path: str,
    job_context: JobContext,
) -> Job1Spec:
    """
    Generate a MultiQC report from FastQC and BCLConvert reports.

    Args:
        fastqc_in_paths (list[str]): List of input paths for FastQC reports.
        out_dir (str): Output directory for the MultiQC report.
        out_path (str): Output path for the MultiQC report.
    """

    log_path = out_path.removesuffix(".html") + ".log"

    out_report = out_path

    return Job1Spec(
        tool=MULTIQC_TOOL_NAME,
        args=[
            "multiqc",
            "--no-clean-up",
            "--interactive",
            "--force",
            "--outdir",
            out_dir,
            "--filename",
            out_report,
        ]
        + fastqc_in_paths,
        stdout_path=log_path,
        stderr_path=log_path,
        custom_attributes=job_context.custom_attributes,
        expected_path=out_report,
    )


@task()
def multiqc(
    fastqc_files: list[File],
    out_dir: str,
    run: str,
    job_context: JobContext,
) -> File:
    """Run MultiQC aggregating FastQC reports."""
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "%s_multiqc_report.html" % run)
    return run_job_1(
        _multiqc_job_spec(
            fastqc_in_paths=[fastqc_file.path for fastqc_file in fastqc_files],
            out_dir=out_dir,
            out_path=out_path,
            job_context=job_context,
        ),
    )
