.. .. _workflow-filesync:

.. Workflow execution as file synchronisation
.. =============================================

.. Any workflow can be divided into two parts: code and data. Given 
.. a data state, one can apply some code to check whether these data
.. are outdated. Executing any workflow can be abstracted to a chain of 
.. sequential changes to local/remote files from upstream to downstream.
.. If all files are up-to-date as checked by the code, then nothing needs
.. to be updated. 

.. To write such codes, file states must be explicitly monitored and remembered.
.. In :mod:`spiper` this is achieved through a set of custom eval-like function
.. called :obj:`Runner` and functions with a specialised signature called :obj:`Node`
.. or :obj:`Flow`. :obj:`Runner` would 
.. extract file dependency graph from the function signatures and use this information
.. to make runtime decisions as to whether to skip a function evaluation.

.. .. literalinclude:: ../examples/001_workflow_exec_as_file_sync.py
