Overview
========

The two main entrypoints are :func:`redun_psij.run_job_1` for running a job which is expected to produce a single file whose path is known in advance (`example run_job_1 usage <https://github.com/AgResearch/redun_psij/blob/main/examples/src/example/tasks/multiqc.py>`_), and :func:`redun_psij.run_job_n` for a job which may produce several files, or files which may be matched after-the-event by globbing (`example run_job_n usage  <https://github.com/AgResearch/redun_psij/blob/main/examples/src/example/tasks/fastqc.py>`_).

Job specs are defined in `Jsonnet <https://jsonnet.org/>`_ as per this `example <https://github.com/AgResearch/redun_psij/blob/main/examples/config/psij-executor.jsonnet>`_.  The colon-separated environment variable ``PSIJ_EXECUTOR_CONFIG_PATH`` is the search path for Jsonnet files, the root configuration being defined in ``psij-executor.jsonnet``. The ``job_attributes`` field is a `PSI/J JobAttributes instance <https://exaworks.org/psij-python/docs/v/0.9.11/.generated/tree.html#jobattributes>`_.
