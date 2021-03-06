CHANGELOG
-------------------------

# 0.1.5
- added runner.is_meta_run for better Flow specification

# 0.1.4
- Fixed a bug in `_types._Runner._run` causing incorrect values of use_cache in get_changed_files.
- [need:test] pulling changes to an executed long pipeline. get_changed_files() should emit correct values 
even if the pipeline has been updated. 
- [need:test] version change in RPO()

# 0.1.3
- improving cli
- adding subcommands:
  - `caller_show_deps` <- `get_all_deps` 
    - print dependencies. options `--plain`
  - `file_show_deps` : print dependencies for parent caller
  - `file_show_log`  : print details fro parent caller
  - `caller_show_log`: print details of a caller including `prefix_named, arg_tuples, sourcecode, sourcefile`
  - need to separate `file` and `caller` commands properly

# 0.1.2
- Adding  `set -euxo pipefail;` to `shell.LoggedShellCommand`
- Adding `["sourcelines","dotname","sourcefile","code"(previously job)]` to `_types.Caller.to_dict()`


# 0.1.1
- [added] `get_all_deps` in runner.py and cli.py
- [added] `_types.CopyFile`, `_types.LinkFile` as `_single_file` Node.
- [removed] `spiper.test.mock.test_tag` in favour for `spiper.tes.mock.test_rpo`

# 0.1.0
- [changed] `prefix_named = '{prefix}.{job_name}-{tag}` instead of
`prefix_named = '{prefix}.{job_name}_{tag}` 
- [changed] indentation for shell.LoggedSingularityCommand()	

# 0.0.9
- [changed] get_changed_files behaviour for FlowFunction().  FlowFunction will always 
be executed with use_cache = False.
- [warn] if _output != [] for FlowFunction()

# 0.0.8
- [changed] funcsig for spiper.shell.LoggedSinuglarityCommand(prefix, cmd, image, log_file). add '--workdir'
- [added] spiper.shell.LoggedSinuglarityCommandList(prefix,cmd,image). returns a cmd_list for singularity exec
- [note] --workdir for singularity is important for providing storage for created temporary files.


# 0.0.7
- [fix] [need:test] check for write access during get_changed_files() and in mock_do(
- [added] spiper._types.Path() wrapper  with check_writable() method


# 0.0.6
- [fix] force Caller.__call__ to cache self if is Node
- [add] spiper._header.Concat
- [add] spiper._header.list_to_string
- [fix] spiper.shell.LoggedSingularityCommand to sniff Files with 
_header.list_to_string
- [add] spiper._header.resolve_spiper to intepret '..subflow..xxx..output..bam'
[need: test]
- [fix] RPO to better intepret pep508 [need: test] [need: use pep508-parser]
- [fix] use pip>=19.0. [need: test expected RPO() func]
