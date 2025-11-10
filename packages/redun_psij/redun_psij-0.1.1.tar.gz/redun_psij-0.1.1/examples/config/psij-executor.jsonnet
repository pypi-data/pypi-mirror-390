// PSI/J executor configuration, i.e. values which have no effect on pipeline ouput, only performance, etc.
//
// To view the equivalent JSON simply feed this file to jsonnet

local job_prefix = 'example.';
local executor = 'slurm';
local queue_name = 'compute';

// custom_attributes need to have an executor prefix, which is done by customised
local customised(attrs) = { [executor + '.' + k]: attrs[k] for k in std.objectFields(attrs) };

local tool_default(job_prefix) = {
  executor: executor,
  job_prefix: job_prefix,
  job_attributes: {
    queue_name: queue_name,
    duration: {
      // fields are Python datetime.timedelta
      hours: 1,
    },
    custom_attributes: customised({
      // all string-valued
      ntasks: '1',
      'cpus-per-task': '1',
      mem: '1G',
    }),
  },
};

{
  tools: {
    fastqc: tool_default(job_prefix) {
      job_attributes+: {
        custom_attributes+: customised({
          mem: '4G',
        }),
      },
    },

    multiqc: tool_default(job_prefix),
  },
}
