import os.path
import subprocess
from redun import task, File

redun_namespace = "example.tasks"


@task()
def fastq_generator(
    seqlen: int,
    numseq: int,
    out_dir: str,
) -> File:
    """Create a random fastq file with specified sequence length and number of sequences."""
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "%d.%d.fastq" % (seqlen, numseq))
    with open(out_path, "w") as out_f:
        _ = subprocess.run(
            ["fastq_generator", "generate_random_fastq_SE", "300", "1000"], stdout=out_f
        )
    return File(out_path)
