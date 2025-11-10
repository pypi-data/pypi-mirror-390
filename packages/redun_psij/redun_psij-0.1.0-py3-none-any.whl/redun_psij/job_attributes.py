from typing import Self


class JobContext:
    """
    Provides a hierarchical job context suitable for inclusion as PSI/J custom attributes
    when running e.g. Slurm jobs.
    """

    def __init__(self, *context: str):
        self._context = list(context)

    def with_sub(self, sub: str) -> Self:
        """Return a new sub-context by extending the previous with a new element.

        Args:
            sub: name of sub-context
        """
        # must copy the existing context so we don't mutate it for others
        context = self._context.copy()
        context.append(sub)
        return type(self)(*context)

    @property
    def custom_attributes(self) -> dict[str, str]:
        """
        Format the context as a comment custom attribute, suitable for a JobSpec, to
        annotate a PSI/J (Slurm) job with the context in the comment field.
        """
        return {"comment": ".".join(self._context)}
