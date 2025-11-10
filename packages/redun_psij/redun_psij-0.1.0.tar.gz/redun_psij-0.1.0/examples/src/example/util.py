import os.path
from redun import task
from typing import Any, Callable

redun_namespace = "example.util"


def baseroot(path: str) -> str:
    """
    Returns the root of the basename of the path, i.e. without any directories, and without anything
    after the first dot.
    """
    basename = os.path.basename(path)
    if (dot := basename.find(".")) != -1:
        return basename[:dot]
    else:
        return basename


@task()
def lazy_map(x: Any, f: Callable[[Any], Any]) -> Any:
    """Map f over the expression `x`."""
    return f(x)
