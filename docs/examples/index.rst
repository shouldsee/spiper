
.. _example-usage

*********************************************
Examples
*********************************************

.. _example-workflow-filesync:

Workflow execution as file synchronisation
=============================================

Any workflow can be divided into two parts: code and data. Given 
a data state, one can apply some code to check whether these data
are outdated. Executing any workflow can be abstracted to a chain of 
sequential changes to local/remote files from upstream to downstream.
If all files are up-to-date as checked by the code, then nothing needs
to be updated. 

To write such codes, file states must be explicitly monitored and remembered.
In :mod:`spiper` this is achieved through a set of custom eval-like function
called :obj:`Runner` and functions with a specialised signature called :obj:`Node`
or :obj:`Flow`. :obj:`Runner` would 
extract file dependency graph from the function signatures and use this information
to make runtime decisions as to whether to skip a function evaluation.

.. literalinclude:: ../examples/001_workflow_exec_as_file_sync.py

.. code-block:: none

	##### all files governed by this node #######
	[File('/tmp/some_node/root.some_node.txt')]
	#### files changed in the next execution of this node #######
	[File('/tmp/some_node/root.some_node.txt')]
	#### write some input file ###
	#### actual execution #####
	... running [some_node]
	#### the second execution is skipped ###
	#### files changed in the next execution of this node #######
	[]



.. _example-remote-code:

Running a remote package/function
======================================

Local paths lose meaning once migrated to a difference machine,
whereas remote references such as http:// and ftp:// is independent of 
local machine states. 

.. literalinclude:: ../examples/003_remote_bash.sh.log
	:language: bash


.. literalinclude:: ../examples/07_remote_short.py

There are quite a number of ways to specify a remote object.

.. literalinclude:: ../examples/002_remote_package.py


.. _example-dependency-graph:
Visualising Dependency graph
=============================================

.. literalinclude:: ../examples/03_mock_flow_backup.py

.. _simple-cache:

Creating a cached Node
==========================================

.. literalinclude:: ../examples/01_cache_run_shallow.py

.. _running-remote:

.. _config-layout

Configure directory layout
===============================