import logging
import os
import os.path
from redun import task, File
from redun_psij import JobContext
from typing import Tuple

from example.tasks import (
    fastqc_one,
    fastqc_zip_file,
    multiqc,
    fastq_generator,
    FastqcOutput,
)
from example.util import lazy_map

redun_namespace = "example"

logging.basicConfig(
    filename="example.log",
    level=logging.DEBUG,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)


@task()
def main(
    seqlen: int = 300,
    numseq: int = 1000,
) -> Tuple[File, FastqcOutput, File]:
    job_context = JobContext()
    out_dir = os.path.join(os.getcwd(), "out")

    fastq_file = fastq_generator(seqlen, numseq, out_dir)

    fastqc_output = fastqc_one(
        fastq_file,
        out_dir=out_dir,
        job_context=job_context,
    )

    multiqc_report = multiqc(
        fastqc_files=[lazy_map(fastqc_output, fastqc_zip_file)],
        out_dir=out_dir,
        run="example",
        job_context=job_context,
    )

    return (fastq_file, fastqc_output, multiqc_report)
